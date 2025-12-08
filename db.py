import os
import json
import psycopg2
from psycopg2.extras import RealDictCursor, Json
from contextlib import contextmanager

DATABASE_URL = os.getenv('DATABASE_URL')

def get_connection():
    """Get a database connection"""
    if not DATABASE_URL:
        raise Exception("DATABASE_URL not set")
    return psycopg2.connect(DATABASE_URL)

@contextmanager
def get_cursor():
    """Context manager for database cursor"""
    conn = get_connection()
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        yield cursor
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()
        conn.close()

def init_database():
    """Initialize database tables"""
    with get_cursor() as cursor:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS runtime_data (
                key TEXT PRIMARY KEY,
                data JSONB NOT NULL,
                updated_at TIMESTAMP DEFAULT NOW()
            )
        """)
        print("[DB] Database tables initialized")

def save_data(key: str, data: dict):
    """Save data to database"""
    with get_cursor() as cursor:
        cursor.execute("""
            INSERT INTO runtime_data (key, data, updated_at)
            VALUES (%s, %s, NOW())
            ON CONFLICT (key) 
            DO UPDATE SET data = %s, updated_at = NOW()
        """, (key, Json(data), Json(data)))

def load_data(key: str, default=None):
    """Load data from database"""
    try:
        with get_cursor() as cursor:
            cursor.execute("SELECT data FROM runtime_data WHERE key = %s", (key,))
            result = cursor.fetchone()
            if result:
                return result['data']
            return default if default is not None else {}
    except Exception as e:
        print(f"[DB] Error loading {key}: {e}")
        return default if default is not None else {}

def migrate_json_to_db(json_file: str, db_key: str):
    """Migrate a JSON file to the database"""
    if os.path.exists(json_file):
        try:
            with open(json_file, 'r') as f:
                data = json.load(f)
            
            existing = load_data(db_key)
            if not existing:
                save_data(db_key, data)
                print(f"[DB] Migrated {json_file} to database key '{db_key}'")
            else:
                print(f"[DB] Key '{db_key}' already exists in database, skipping migration")
            return True
        except Exception as e:
            print(f"[DB] Error migrating {json_file}: {e}")
            return False
    return False

def is_db_available():
    """Check if database is available"""
    if not DATABASE_URL:
        return False
    try:
        conn = get_connection()
        conn.close()
        return True
    except Exception as e:
        print(f"[DB] Database not available: {e}")
        return False
