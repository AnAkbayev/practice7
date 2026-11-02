"""
Console PhoneBook application backed by PostgreSQL.

Run:
    python phonebook.py

The database table is created automatically on startup.
Connection settings are read from environment variables (see .env.example).
"""
import csv
import os
import sys
from contextlib import contextmanager
from typing import Optional

import psycopg2
from dotenv import load_dotenv
from psycopg2 import Error
from psycopg2.extras import execute_values


load_dotenv()  # Load settings from the local .env file, if it exists.


CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS contacts (
    id BIGSERIAL PRIMARY KEY,
    first_name VARCHAR(100) NOT NULL,
    phone VARCHAR(30) NOT NULL UNIQUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);
"""

INSERT_SQL = """
INSERT INTO contacts (first_name, phone)
VALUES (%s, %s)
ON CONFLICT (phone) DO UPDATE
SET first_name = EXCLUDED.first_name;
"""


def get_connection():
    """Create and return a PostgreSQL connection."""
    return psycopg2.connect(
        host=os.getenv("PGHOST", "localhost"),
        port=os.getenv("PGPORT", "5432"),
        dbname=os.getenv("PGDATABASE", "phonebook_db"),
        user=os.getenv("PGUSER", "postgres"),
        password=os.getenv("PGPASSWORD", ""),
    )


@contextmanager
def database():
    """Connection context: commit on success, rollback on error, always close."""
    conn = get_connection()
    try:
        with conn:
            with conn.cursor() as cur:
                yield cur
    finally:
        conn.close()


def initialize_database():
    with database() as cur:
        cur.execute(CREATE_TABLE_SQL)


def normalize_contact(first_name: str, phone: str):
    first_name = first_name.strip()
    phone = phone.strip()
    if not first_name:
        raise ValueError("Name cannot be empty.")
    if not phone:
        raise ValueError("Phone number cannot be empty.")
    if len(first_name) > 100:
        raise ValueError("Name must be 100 characters or fewer.")
    if len(phone) > 30:
        raise ValueError("Phone must be 30 characters or fewer.")
    return first_name, phone


def add_contact(first_name: str, phone: str):
    first_name, phone = normalize_contact(first_name, phone)
    with database() as cur:
        cur.execute(INSERT_SQL, (first_name, phone))


def import_csv(file_path: str):
    """Import rows from CSV with headers: first_name,phone."""
    inserted = 0
    skipped = 0
    with open(file_path, "r", encoding="utf-8-sig", newline="") as csv_file:
        reader = csv.DictReader(csv_file)
        required = {"first_name", "phone"}
        if not reader.fieldnames or not required.issubset(set(reader.fieldnames)):
            raise ValueError("CSV must contain the headers: first_name,phone")

        rows = []
        for line_number, row in enumerate(reader, start=2):
            try:
                rows.append(normalize_contact(row.get("first_name", ""), row.get("phone", "")))
            except ValueError as exc:
                print(f"Skipping CSV line {line_number}: {exc}")
                skipped += 1

    if rows:
        with database() as cur:
            execute_values(
                cur,
                """
                INSERT INTO contacts (first_name, phone)
                VALUES %s
                ON CONFLICT (phone) DO UPDATE
                SET first_name = EXCLUDED.first_name
                """,
                rows,
            )
        inserted = len(rows)

    return inserted, skipped


def list_contacts():
    with database() as cur:
        cur.execute(
            "SELECT id, first_name, phone FROM contacts ORDER BY first_name, id"
        )
        return cur.fetchall()


def search_contacts(name: Optional[str] = None, phone_prefix: Optional[str] = None):
    """Search by partial name and/or phone prefix."""
    query = "SELECT id, first_name, phone FROM contacts WHERE TRUE"
    params = []

    if name:
        query += " AND first_name ILIKE %s"
        params.append(f"%{name.strip()}%")
    if phone_prefix:
        query += " AND phone LIKE %s"
        params.append(f"{phone_prefix.strip()}%")

    query += " ORDER BY first_name, id"
    with database() as cur:
        cur.execute(query, params)
        return cur.fetchall()


def update_contact(contact_id: int, first_name: Optional[str] = None,
                   phone: Optional[str] = None):
    """Update either or both fields for a contact selected by its ID."""
    if first_name is None and phone is None:
        raise ValueError("Provide a new name, a new phone number, or both.")

    assignments = []
    values = []
    if first_name is not None:
        first_name = first_name.strip()
        if not first_name or len(first_name) > 100:
            raise ValueError("Name must contain 1–100 characters.")
        assignments.append("first_name = %s")
        values.append(first_name)
    if phone is not None:
        phone = phone.strip()
        if not phone or len(phone) > 30:
            raise ValueError("Phone must contain 1–30 characters.")
        assignments.append("phone = %s")
        values.append(phone)

    values.append(contact_id)
    query = f"UPDATE contacts SET {', '.join(assignments)} WHERE id = %s"
    with database() as cur:
        cur.execute(query, values)
        return cur.rowcount


def delete_by_name(name: str):
    with database() as cur:
        cur.execute("DELETE FROM contacts WHERE first_name ILIKE %s", (name.strip(),))
        return cur.rowcount


def delete_by_phone(phone: str):
    with database() as cur:
        cur.execute("DELETE FROM contacts WHERE phone = %s", (phone.strip(),))
        return cur.rowcount


def print_contacts(contacts):
    if not contacts:
        print("No contacts found.")
        return
    print(f"\n{'ID':<6} {'NAME':<24} PHONE")
    print("-" * 52)
    for contact_id, first_name, phone in contacts:
        print(f"{contact_id:<6} {first_name:<24} {phone}")
    print()


def prompt_optional(prompt: str):
    value = input(prompt).strip()
    return value if value else None


def menu():
    print("""
========== PHONEBOOK ==========
1. Show all contacts
2. Add a contact from console
3. Import contacts from CSV
4. Search contacts
5. Update a contact
6. Delete contact(s) by name
7. Delete a contact by phone
0. Exit
===============================
""")


def main():
    try:
        initialize_database()
    except Error as exc:
        print(f"Could not connect to PostgreSQL: {exc}")
        print("Check your PostgreSQL service and settings in .env / environment variables.")
        sys.exit(1)

    print("PhoneBook is ready.")
    while True:
        menu()
        choice = input("Choose an option: ").strip()
        try:
            if choice == "1":
                print_contacts(list_contacts())

            elif choice == "2":
                name = input("First name: ")
                phone = input("Phone: ")
                add_contact(name, phone)
                print("Contact saved.")

            elif choice == "3":
                path = input("CSV file path [contacts.csv]: ").strip() or "contacts.csv"
                inserted, skipped = import_csv(path)
                print(f"Processed {inserted} valid row(s); skipped {skipped} invalid row(s).")
                print("Existing phone numbers are updated rather than duplicated.")

            elif choice == "4":
                name = prompt_optional("Name contains (Enter to skip): ")
                prefix = prompt_optional("Phone starts with (Enter to skip): ")
                if name is None and prefix is None:
                    print("Enter at least one search filter.")
                else:
                    print_contacts(search_contacts(name, prefix))

            elif choice == "5":
                contact_id = int(input("Contact ID to update: "))
                name = prompt_optional("New first name (Enter to keep unchanged): ")
                phone = prompt_optional("New phone (Enter to keep unchanged): ")
                changed = update_contact(contact_id, name, phone)
                print("Contact updated." if changed else "Contact ID not found.")

            elif choice == "6":
                name = input("Exact name to delete: ").strip()
                if input(f"Delete all contacts named '{name}'? (y/N): ").lower() == "y":
                    print(f"Deleted {delete_by_name(name)} contact(s).")

            elif choice == "7":
                phone = input("Exact phone number to delete: ").strip()
                if input(f"Delete contact with phone '{phone}'? (y/N): ").lower() == "y":
                    deleted = delete_by_phone(phone)
                    print("Contact deleted." if deleted else "Phone number not found.")

            elif choice == "0":
                print("Goodbye!")
                break
            else:
                print("Unknown option. Try again.")

        except (ValueError, OSError, Error) as exc:
            print(f"Operation failed: {exc}")


if __name__ == "__main__":
    main()
