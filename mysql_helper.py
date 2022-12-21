import mysql.connector
from typing import Optional


class MySqlDatabase:
    def __init__(self, host, user, password, database):
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.connection = None
        self.cursor = None

    def connect(self):
        self.connection = mysql.connector.connect(
            host=self.host,
            user=self.user,
            password=self.password,
            database=self.database
        )
        if not self.connection.is_connected():
            raise Exception("Could not connect to database")

        self.cursor = self.connection.cursor(buffered=True)

        self.create_task_table()

    def create_task_table(self):
        self.execute("""
            CREATE TABLE IF NOT EXISTS todo (
                id INT AUTO_INCREMENT PRIMARY KEY,
                task_type VARCHAR(255),
                task VARCHAR(255),
                requested_by VARCHAR(255),
                completed BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

    def disconnect(self):
        if self.connection:
            self.connection.close()

    def execute(self, query: str, values: Optional[list] = None):
        if not self.connection:
            self.connect()

        self.cursor.execute(query, values)
        self.connection.commit()
        return self.cursor.lastrowid

    def fetch(self, query, values=None):
        if not self.connection:
            self.connect()
        self.cursor.execute(query, values)
        return self.cursor.fetchall()

    def fetch_one(self, query, values=None):
        if not self.connection:
            self.connect()
        self.cursor.execute(query, values)
        return self.cursor.fetchone()
