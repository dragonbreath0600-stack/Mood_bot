import sqlite3
import os


class Database:

    def __init__(self):
        os.makedirs("database", exist_ok=True)
        self.db_path = "database.db"
        self._init_db()

    def _get_conn(self):
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        return conn

    def _init_db(self):
        conn = self._get_conn()
        try:
            with open("schema.sql", "r", encoding="utf-8") as f:
                conn.executescript(f.read())
            conn.commit()
        finally:
            conn.close()

    def add_user(self, user_id):
        conn = self._get_conn()
        try:
            conn.execute("INSERT OR IGNORE INTO users (user_id) VALUES (?)", (user_id,))
            conn.commit()
        finally:
            conn.close()

    def add_entry(self, user_id, mood, work_hours, sleep_hours, comment=None):
        conn = self._get_conn()
        try:
            conn.execute(
                "INSERT OR IGNORE INTO mood (user_id, entry_date, mood, hours_work, hours_sleep, comment) VALUES (?, date('now'), ?, ?, ?, ?)",
                (user_id, mood, work_hours, sleep_hours, comment)
            )
            conn.commit()
        finally:
            conn.close()

    def get_entries(self, user_id, days):
        conn = self._get_conn()
        try:
            cursor = conn.execute(
                "SELECT entry_date, mood, hours_work, hours_sleep, comment FROM mood WHERE user_id=? AND entry_date >= date('now', ?) ORDER BY entry_date DESC",
                (user_id, f"-{days} days")
            )
            return cursor.fetchall()
        finally:
            conn.close()

    def set_reminder(self, user_id, time_str):
        conn = self._get_conn()
        try:
            conn.execute("UPDATE users SET reminder_time=? WHERE user_id=?", (time_str, user_id))
            conn.commit()
        finally:
            conn.close()

    def clear_user_data(self, user_id):
        conn = self._get_conn()
        try:
            conn.execute("DELETE FROM mood WHERE user_id=?", (user_id,))
            conn.commit()
        finally:
            conn.close()