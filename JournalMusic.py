import sys
import sqlite3
import time
import pygame
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QPushButton, QLabel, QMessageBox, QInputDialog, QWidget
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

class Journal:
    DB_FILE = 'journal.db'

    def __init__(self):
        self.conn = self.create_connection()
        self.create_table()

    def create_connection(self):
        """Create a database connection."""
        try:
            return sqlite3.connect(Journal.DB_FILE)
        except sqlite3.Error as e:
            print(f"Error connecting to database: {e}")
        return None

    def create_table(self):
        """Create the journal_entries table if it doesn't exist."""
        try:
            with self.conn:
                self.conn.execute('''
                    CREATE TABLE IF NOT EXISTS journal_entries (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        number INTEGER,
                        title TEXT,
                        content TEXT,
                        date TEXT
                    )
                ''')
        except sqlite3.Error as e:
            print(f"Error creating table: {e}")

    def add_new_entry(self, title, content):
        """Add a new journal entry."""
        entry_date = time.strftime("%d-%m-%Y", time.localtime())
        entry_number = self.get_next_entry_number()

        if entry_number:
            try:
                with self.conn:
                    self.conn.execute('''
                        INSERT INTO journal_entries (number, title, content, date)
                        VALUES (?, ?, ?, ?)
                    ''', (entry_number, title, content, entry_date))
                return f"Entry #{entry_number} added successfully."
            except sqlite3.Error as e:
                return f"Error saving entry to the database: {e}"
        else:
            return "Failed to determine next entry number."

    def get_next_entry_number(self):
        """Get the next available entry number from the database."""
        try:
            cursor = self.conn.cursor()
            cursor.execute('SELECT MAX(number) FROM journal_entries')
            result = cursor.fetchone()
            return (result[0] or 0) + 1
        except sqlite3.Error as e:
            print(f"Error retrieving entry count: {e}")
            return None

    def get_all_entries(self):
        """Get all journal entries."""
        try:
            cursor = self.conn.cursor()
            cursor.execute('SELECT * FROM journal_entries')
            rows = cursor.fetchall()
            return rows
        except sqlite3.Error as e:
            return []

    def edit_entry(self, entry_number, new_title, new_content):
        """Edit the title or content of an existing entry."""
        try:
            with self.conn:
                self.conn.execute('''
                    UPDATE journal_entries
                    SET title = ?, content = ?
                    WHERE number = ?
                ''', (new_title, new_content, entry_number))
            return f"Entry #{entry_number} updated successfully."
        except sqlite3.Error as e:
            return f"Error updating entry: {e}"

    def delete_entry(self, entry_number):
        """Delete an entry by its number."""
        try:
            with self.conn:
                self.conn.execute('DELETE FROM journal_entries WHERE number = ?', (entry_number,))
            return f"Entry #{entry_number} deleted successfully."
        except sqlite3.Error as e:
            return f"Error deleting entry: {e}"

class JournalApp(QMainWindow):
    TITLE_MAX_LENGTH = 50

    def __init__(self):
        super().__init__()

        self.journal = Journal()

        # Initialize pygame for playing music
        pygame.mixer.init()
        pygame.mixer.music.load("/Users/pedritos22/Desktop/relaxing_music.mp3")  # Load your relaxing music file here
        pygame.mixer.music.set_volume(0.5)  # Set volume (0.0 to 1.0)
        pygame.mixer.music.play(-1)  # Play the music indefinitely

        # Set window title and dimensions
        self.setWindowTitle("Journal Manager")
        self.setGeometry(300, 200, 600, 400)
        self.setStyleSheet("background-color: #2C2C2C; color: #D3D3D3;")

        # Main layout
        self.main_widget = QWidget(self)
        self.setCentralWidget(self.main_widget)
        self.main_layout = QVBoxLayout(self.main_widget)

        # Title Label
        self.title_label = QLabel("Journal Manager", self)
        self.title_label.setFont(QFont("Arial", 20, QFont.Bold))
        self.title_label.setAlignment(Qt.AlignCenter)
        self.main_layout.addWidget(self.title_label)

        # Add Entry Button
        self.add_entry_btn = QPushButton("Add Entry", self)
        self.add_entry_btn.setFont(QFont("Arial", 14))
        self.add_entry_btn.setStyleSheet(
            "background-color: #4A90E2; color: white; border: 1px solid #3A80C2; border-radius: 10px;"
        )
        self.add_entry_btn.clicked.connect(self.add_entry)
        self.main_layout.addWidget(self.add_entry_btn)

        # Show Entries Button
        self.show_entries_btn = QPushButton("Show All Entries", self)
        self.show_entries_btn.setFont(QFont("Arial", 14))
        self.show_entries_btn.setStyleSheet(
            "background-color: #4A90E2; color: white; border: 1px solid #3A80C2; border-radius: 10px;"
        )
        self.show_entries_btn.clicked.connect(self.show_entries)
        self.main_layout.addWidget(self.show_entries_btn)

        # Edit Entry Button
        self.edit_entry_btn = QPushButton("Edit Entry", self)
        self.edit_entry_btn.setFont(QFont("Arial", 14))
        self.edit_entry_btn.setStyleSheet(
            "background-color: #F39C12; color: white; border: 1px solid #D68C10; border-radius: 10px;"
        )
        self.edit_entry_btn.clicked.connect(self.edit_entry)
        self.main_layout.addWidget(self.edit_entry_btn)

        # Delete Entry Button
        self.delete_entry_btn = QPushButton("Delete Entry", self)
        self.delete_entry_btn.setFont(QFont("Arial", 14))
        self.delete_entry_btn.setStyleSheet(
            "background-color: #E74C3C; color: white; border: 1px solid #D43F3A; border-radius: 10px;"
        )
        self.delete_entry_btn.clicked.connect(self.delete_entry)
        self.main_layout.addWidget(self.delete_entry_btn)

        # Footer Label
        self.footer_label = QLabel("Yournal™", self)
        self.footer_label.setAlignment(Qt.AlignCenter)
        self.footer_label.setStyleSheet("color: #AAB8C2;")
        self.main_layout.addWidget(self.footer_label)

    def add_entry(self):
        title, ok1 = QInputDialog.getText(self, "Add Entry", f"Enter the title (Max {JournalApp.TITLE_MAX_LENGTH} characters):")
        if ok1 and len(title) > JournalApp.TITLE_MAX_LENGTH:
            QMessageBox.warning(self, "Warning", f"Title cannot exceed {JournalApp.TITLE_MAX_LENGTH} characters!")
            return
        content, ok2 = QInputDialog.getMultiLineText(self, "Add Entry", "Enter the content:")
        if ok1 and ok2 and title and content:
            result = self.journal.add_new_entry(title, content)
            QMessageBox.information(self, "Result", result)
        else:
            QMessageBox.warning(self, "Warning", "Title or content cannot be empty!")

    def show_entries(self):
        entries = self.journal.get_all_entries()
        if entries:
            entry_list = "\n".join([f"#{row[1]} | {row[2]} | {row[3]} | {row[4]}" for row in entries])
            QMessageBox.information(self, "All Entries", entry_list)
        else:
            QMessageBox.information(self, "All Entries", "No entries found.")

    def edit_entry(self):
        entry_number, ok = QInputDialog.getInt(self, "Edit Entry", "Enter the entry number to edit:")
        if ok:
            new_title, ok1 = QInputDialog.getText(self, "Edit Entry", f"Enter the new title (Max {JournalApp.TITLE_MAX_LENGTH} characters):")
            if ok1 and len(new_title) > JournalApp.TITLE_MAX_LENGTH:
                QMessageBox.warning(self, "Warning", f"Title cannot exceed {JournalApp.TITLE_MAX_LENGTH} characters!")
                return
            new_content, ok2 = QInputDialog.getMultiLineText(self, "Edit Entry", "Enter the new content:")
            if ok1 and ok2:
                result = self.journal.edit_entry(entry_number, new_title, new_content)
                QMessageBox.information(self, "Result", result)
            else:
                QMessageBox.warning(self, "Warning", "Nothing to update!")

    def delete_entry(self):
        entry_number, ok = QInputDialog.getInt(self, "Delete Entry", "Enter the entry number to delete:")
        if ok:
            result = self.journal.delete_entry(entry_number)
            QMessageBox.information(self, "Result", result)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    journal_app = JournalApp()
    journal_app.show()
    sys.exit(app.exec_())
