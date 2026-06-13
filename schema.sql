CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    reminder_time TEXT DEFAULT '21:00'
);

CREATE TABLE IF NOT EXISTS mood (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    entry_date DATE DEFAULT CURRENT_DATE,
    mood INTEGER NOT NULL,
    hours_work REAL,
    hours_sleep REAL,
    comment TEXT,
    UNIQUE(user_id, entry_date),
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

