"""Small reusable PostgreSQL connection helper."""
import psycopg2
from config import DB_CONFIG


def get_connection():
    return psycopg2.connect(**DB_CONFIG)


if __name__ == "__main__":
    try:
        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT version();")
                print("Connected successfully:")
                print(cursor.fetchone()[0])
    except psycopg2.Error as error:
        print(f"Database connection failed: {error}")
