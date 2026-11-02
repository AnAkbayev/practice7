# Practice 7 — Python & PostgreSQL PhoneBook

A console-based PhoneBook application built with Python and PostgreSQL using `psycopg2`.

## Features

- Create the `contacts` table automatically on application startup.
- Import contacts from a CSV file (`first_name,phone` headers).
- Add a contact interactively from the console.
- Display all contacts.
- Search by a partial first name and/or phone-number prefix.
- Update a contact's first name and/or phone number by contact ID.
- Delete contacts by exact first name or exact phone number.
- Use parameterized SQL queries to protect against SQL injection.
- Commit successful operations and roll back failed transactions.

## Project structure

```text
Practice7/
├── phonebook.py
├── config.py
├── connect.py
├── schema.sql
├── contacts.csv
├── .env.example
├── requirements.txt
├── .gitignore
└── README.md
```

## 1. Requirements

- Python 3.9+
- PostgreSQL
- pip

## 2. Create the PostgreSQL database

Start the PostgreSQL server, then open `psql` or pgAdmin and run:

```sql
CREATE DATABASE phonebook_db;
```

The application creates the `contacts` table automatically. Alternatively, connect to
`phonebook_db` and execute the SQL in `schema.sql`.

Example using the terminal:

```bash
psql -U postgres -c "CREATE DATABASE phonebook_db;"
```

## 3. Install Python dependencies

Open a terminal in the `Practice7` directory:

```bash
python -m venv .venv
```

Activate the environment:

**Windows (PowerShell):**
```powershell
.venv\Scripts\Activate.ps1
```

**macOS / Linux:**
```bash
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

## 4. Configure the database connection

Copy `.env.example` to `.env` and set your PostgreSQL username and password.

**Windows (PowerShell):**
```powershell
Copy-Item .env.example .env
```

**macOS / Linux:**
```bash
cp .env.example .env
```

Edit `.env`:

```env
PGHOST=localhost
PGPORT=5432
PGDATABASE=phonebook_db
PGUSER=postgres
PGPASSWORD=your_postgres_password
```

Both `phonebook.py` and `config.py` load `.env` automatically using
`python-dotenv`. The real `.env` file is excluded from Git by `.gitignore`.

Never commit your real `.env` file or database password to GitHub.

## 5. Test the connection

```bash
python connect.py
```

A successful run prints the PostgreSQL server version.

## 6. Run the PhoneBook

```bash
python phonebook.py
```

Choose an option from the menu:

| Option | Operation |
|---|---|
| 1 | Show all contacts |
| 2 | Add a contact from console |
| 3 | Import contacts from CSV |
| 4 | Search by name and/or phone prefix |
| 5 | Update a contact by ID |
| 6 | Delete all contacts with an exact name |
| 7 | Delete by exact phone number |
| 0 | Exit |

For CSV import, use the included `contacts.csv` or provide another file path.
The CSV must be UTF-8 and contain the column headers `first_name` and `phone`.
If a phone number already exists, its contact name is updated instead of creating
a duplicate.

## 7. Example CSV format

```csv
first_name,phone
Alice,+7-701-111-11-11
Bob,+7-702-222-22-22
```

Phone numbers are stored as text, not numeric values, so leading `+`, zeros,
spaces, and hyphens are preserved.

## 8. Database design

The project uses one relational table:

| Column | Type | Constraints | Purpose |
|---|---|---|---|
| `id` | `BIGSERIAL` | Primary key | Unique contact identifier |
| `first_name` | `VARCHAR(100)` | NOT NULL | Contact's first name |
| `phone` | `VARCHAR(30)` | NOT NULL, UNIQUE | Contact phone number |
| `created_at` | `TIMESTAMPTZ` | NOT NULL, default current timestamp | Creation time |

The unique constraint on `phone` prevents duplicate phone numbers.

## 9. CRUD operations demonstrated

- **Create:** `INSERT INTO contacts ...`
- **Read:** `SELECT ... FROM contacts ...`
- **Update:** `UPDATE contacts SET ... WHERE id = ...`
- **Delete:** `DELETE FROM contacts WHERE ...`

All user-provided values are passed as query parameters rather than concatenated
into SQL strings. The connection context commits successful transactions and
rolls back if an exception occurs.

## 10. Troubleshooting

- **Connection refused:** ensure PostgreSQL is running and `PGHOST` / `PGPORT` are correct.
- **Password authentication failed:** check `PGUSER`, `PGPASSWORD`, and PostgreSQL authentication settings.
- **Database does not exist:** create `phonebook_db` using the SQL above.
- **No module named psycopg2:** activate your virtual environment and run `pip install -r requirements.txt`.
- **CSV header error:** the first row must contain `first_name,phone`.
- **CSV encoding issue:** save the file as UTF-8. The importer also accepts a UTF-8 BOM.

## 11. Push to GitHub

Create a repository on GitHub, then run these commands from the directory containing
`Practice7` (or upload the folder using GitHub's web interface):

```bash
git init
git add Practice7
git commit -m "Add Practice7 - PhoneBook with PostgreSQL"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPOSITORY.git
git push -u origin main
```

Replace the remote URL with your own GitHub repository URL.

## Learning resources

- PostgreSQL + Python tutorial: https://neon.com/postgresql/postgresql-python
- psycopg2 documentation: https://www.psycopg.org/docs/
- PostgreSQL documentation: https://www.postgresql.org/docs/
- Python CSV module: https://docs.python.org/3/library/csv.html
