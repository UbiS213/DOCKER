import os
from flask import Flask
import psycopg2
from psycopg2.extras import RealDictCursor

app = Flask(__name__)

APP_ENV = os.environ.get('APP_ENV', 'development')
SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-key')
DATABASE_URL = os.environ.get('DATABASE_URL', 'postgresql://user:password@db:5432/mydb')

app.config['SECRET_KEY'] = SECRET_KEY

def get_db_connection():
    return psycopg2.connect(DATABASE_URL)

def init_db():
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS notes (
                    id SERIAL PRIMARY KEY,
                    text TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT NOW()
                );
            """)
        conn.commit()

@app.route('/')
def index():
    return {
        'app_env': APP_ENV,
        'message': 'Hello from Swarm v2!',
        'secret_key_set': bool(SECRET_KEY)
    }

@app.route('/notes')
def list_notes():
    with get_db_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT * FROM notes ORDER BY id DESC;")
            notes = cur.fetchall()
    return {'notes': notes}

@app.route('/notes/add/<text>')
def add_note(text):
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("INSERT INTO notes (text) VALUES (%s) RETURNING id;", (text,))
            new_id = cur.fetchone()[0]
        conn.commit()
    return {'added': new_id, 'text': text}

@app.route('/debug')
def debug():
    if APP_ENV != 'development':
        return {'error': 'debug endpoint disabled in production'}, 403
    return {'env': dict(os.environ)}

if __name__ == '__main__':
    init_db()
    debug_mode = APP_ENV == 'development'
    app.run(host='0.0.0.0', port=5000, debug=debug_mode)
