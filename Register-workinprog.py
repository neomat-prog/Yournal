import sqlite3
import time
import tkinter as tk
from tkinter import messagebox, simpledialog

class LogInDB:
    DB_FILE = 'login_database.db'

    def __init__(self):
        self.conn = self.create_connection()
        self.create_table()

    def create_connection(self):
        """Create a database connection."""
        try:
            return sqlite3.connect(self.DB_FILE)  # Zmieniono na self.DB_FILE
        except sqlite3.Error as e:
            print(f"Error connecting to database: {e}")
        return None

    def create_table(self):
        """Create the logins table if it doesn't exist."""
        try:
            with self.conn:
                self.conn.execute('''
                    CREATE TABLE IF NOT EXISTS logins (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT,
                        password TEXT
                    )
                ''')
        except sqlite3.Error as e:
            print(f"Error creating table: {e}")

    def add_new_login(self):
        """Add a new login pair."""
        username = str(input("Ustaw Login: "))
        password = str(input("Ustaw Hasło: "))

        if username:
            try:
                with self.conn:
                    self.conn.execute('''
                        INSERT INTO logins (username, password)
                        VALUES (?, ?)
                    ''', (username, password))  # Zmieniono z login na username
                return f"User {username} registered successfully."
            except sqlite3.Error as e:
                return f"Error registering login to the database: {e}"
        else:
            return "Login cannot be empty."

    def get_all_logins(self):
        """Get all logins."""
        try:
            cursor = self.conn.cursor()
            cursor.execute('SELECT * FROM logins')
            rows = cursor.fetchall()
            return rows
        except sqlite3.Error as e:
            return []

    def change_password(self, username, password):
        """Zmiana hasła"""
        passwordcheck = str(input("Aby zmienić hasło najpierw podaj aktualne: "))
        if passwordcheck == password:
            newpassword = str(input("Wprowadź nowe hasło: "))
            if newpassword:
                password = newpassword
                try:
                    with self.conn:
                        self.conn.execute('''
                            UPDATE logins
                            SET password = ?
                            WHERE username = ?
                        ''', (password, username))
                    return f"Password updated successfully."
                except sqlite3.Error as e:
                    return f"Error updating entry: {e}"
            else:
                print("Error: Password cannot be blank.")
        else:
            print("Error: Wrong Password.")


# Utworzenie instancji klasy LogInDB
db = LogInDB()  # Utwórz instancję klasy LogInDB

# Wywołanie metod na instancji
db.get_all_logins()

'''    
    def delete_entry(self, entry_number):
        """Delete an entry by its number."""
        try:
            with self.conn:
                self.conn.execute('DELETE FROM journal_entries WHERE number = ?', (entry_number,))
            return f"Entry #{entry_number} deleted successfully."
        except sqlite3.Error as e:
            return f"Error deleting entry: {e}"
            '''