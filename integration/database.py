import sqlite3
from datetime import datetime

class DataLogger:
    def __init__(self, db_file):
        self.conn = sqlite3.connect(db_file, check_same_thread=False)
        self._create_tables()

    def _create_tables(self):
        """Initialise the main results table."""
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS probe_runs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                max_depth_mm REAL,
                max_weight_kg REAL,
                compaction_pa REAL
            )
        """)
        self.conn.commit()

    def log_run(self, max_depth, max_weight, compaction_pa):
        """Insert a completed test run."""
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.conn.execute(
            "INSERT INTO probe_runs (timestamp, max_depth_mm, max_weight_kg, compaction_pa) VALUES (?, ?, ?, ?)",
            (ts, max_depth, max_weight, compaction_pa)
        )
        self.conn.commit()

    def close(self):
        self.conn.close()
