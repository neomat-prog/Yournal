import sys
import sqlite3
import time
import pygame
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QPushButton, QLabel, QMessageBox,
    QInputDialog, QWidget, QDialog, QListWidget, QListWidgetItem, QTextEdit, QComboBox
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
                        mood TEXT,
                        date TEXT
                    )
                ''')
        except sqlite3.Error as e:
            print(f"Error creating table: {e}")

    def add_new_entry(self, title, content, mood):
        """Add a new journal entry."""
        entry_date = time.strftime("%d-%m-%Y", time.localtime())
        entry_number = self.get_next_entry_number()

        if entry_number:
            try:
                with self.conn:
                    self.conn.execute('''
                        INSERT INTO journal_entries (number, title, content, mood, date)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (entry_number, title, content, mood, entry_date))
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
            cursor.execute('SELECT * FROM journal_entries ORDER BY number')
            rows = cursor.fetchall()
            return rows
        except sqlite3.Error as e:
            return []

    def get_entry_by_number(self, entry_number):
        """Get a specific journal entry by its number."""
        try:
            cursor = self.conn.cursor()
            cursor.execute('SELECT * FROM journal_entries WHERE number = ?', (entry_number,))
            return cursor.fetchone()
        except sqlite3.Error as e:
            return None

    def edit_entry(self, entry_number, new_title=None, new_content=None, new_mood=None):
        """Edit the title, content, or mood of an existing entry."""
        try:
            with self.conn:
                self.conn.execute('''
                    UPDATE journal_entries
                    SET title = ?, content = ?, mood = ?
                    WHERE number = ?
                ''', (new_title, new_content, new_mood, entry_number))
            return f"Entry #{entry_number} updated successfully."
        except sqlite3.Error as e:
            return f"Error updating entry: {e}"

    def delete_entry(self, entry_number):
        """Delete an entry by its number."""
        try:
            with self.conn:
                self.conn.execute('DELETE FROM journal_entries WHERE number = ?', (entry_number,))
            self.renumber_entries()  # Renumber entries after deletion
            return f"Entry #{entry_number} deleted successfully."
        except sqlite3.Error as e:
            return f"Error deleting entry: {e}"

    def renumber_entries(self):
        """Renumber the entries after a deletion."""
        try:
            entries = self.get_all_entries()
            for index, entry in enumerate(entries):
                new_number = index + 1
                with self.conn:
                    self.conn.execute('''
                        UPDATE journal_entries
                        SET number = ?
                        WHERE id = ?
                    ''', (new_number, entry[0]))  # entry[0] is the id
        except sqlite3.Error as e:
            print(f"Error renumbering entries: {e}")


class JournalApp(QMainWindow):
    TITLE_MAX_LENGTH = 50
    MOODS = ["Happy", "Sad", "Relaxed", "Angry", "Excited", "Anxious", "Bored", "Grateful"]  # List of moods

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
        self.title_label.setFont(QFont("Arial", 24, QFont.Bold))  # Increased font size
        self.title_label.setAlignment(Qt.AlignCenter)
        self.main_layout.addWidget(self.title_label)

        # Add Entry Button
        self.add_entry_btn = QPushButton("Add Entry", self)
        self.add_entry_btn.setFont(QFont("Arial", 16))  # Increased font size
        self.add_entry_btn.setStyleSheet(
            "background-color: #4A90E2; color: white; border: 1px solid #3A80C2; border-radius: 10px;"
        )
        self.add_entry_btn.clicked.connect(self.add_entry)
        self.main_layout.addWidget(self.add_entry_btn)

        # Footer Label
        self.footer_label = QLabel("Yournal™", self)
        self.footer_label.setAlignment(Qt.AlignCenter)
        self.footer_label.setStyleSheet("color: #AAB8C2; font-size: 14px;")
        self.main_layout.addWidget(self.footer_label)

        # Journal Entries List
        self.entry_list = QListWidget()
        self.entry_list.itemClicked.connect(self.show_entry_details)  # Show entry details on click
        self.main_layout.addWidget(self.entry_list)

        # Load entries on startup
        self.load_entries()

    def load_entries(self):
        """Load all entries into the list widget."""
        self.entry_list.clear()  # Clear the current list
        entries = self.journal.get_all_entries()
        for entry in entries:
            item = QListWidgetItem(f"Entry #{entry[1]}: {entry[2]} - Mood: {entry[4]} (Date: {entry[5]})")
            item.setData(Qt.UserRole, entry)  # Store the entire entry for later use
            self.entry_list.addItem(item)

    def add_entry(self):
        """Show a dialog to add a new journal entry."""
        dialog = QDialog(self)
        dialog.setWindowTitle("Add New Entry")
        dialog.setGeometry(300, 200, 400, 400)

        layout = QVBoxLayout(dialog)

        # Text edit for the title
        title_edit = QTextEdit()
        title_edit.setFixedHeight(40)
        layout.addWidget(QLabel(f"Title (Max {JournalApp.TITLE_MAX_LENGTH} characters):"))
        layout.addWidget(title_edit)

        # Text edit for the content
        content_edit = QTextEdit()
        layout.addWidget(QLabel("Content:"))
        layout.addWidget(content_edit)

        # Mood selection with ComboBox
        mood_combo = QComboBox()
        mood_combo.addItems(JournalApp.MOODS)
        layout.addWidget(QLabel("Mood:"))
        layout.addWidget(mood_combo)

        # Add button
        add_btn = QPushButton("Add Entry")
        add_btn.clicked.connect(lambda: self.save_entry(title_edit, content_edit, mood_combo))
        layout.addWidget(add_btn)

        dialog.exec_()

    def save_entry(self, title_edit, content_edit, mood_combo):
        """Save the new journal entry."""
        title = title_edit.toPlainText()[:JournalApp.TITLE_MAX_LENGTH]
        content = content_edit.toPlainText()
        mood = mood_combo.currentText()
        result = self.journal.add_new_entry(title, content, mood)
        QMessageBox.information(self, "Entry Status", result)
        self.load_entries()  # Refresh the entry list after adding

    def show_entry_details(self, item):
        """Show the details of the clicked entry."""
        entry = item.data(Qt.UserRole)  # Get the full entry data
        if entry:
            self.show_entry_dialog(entry)

    def show_entry_dialog(self, entry):
        """Show a dialog for viewing or editing the entry."""
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Entry #{entry[1]}")
        dialog.setGeometry(300, 200, 400, 400)

        layout = QVBoxLayout(dialog)

        # Display the title
        title_label = QLabel(f"Title: {entry[2]}")
        layout.addWidget(title_label)

        # Display the content
        content_text = QTextEdit()
        content_text.setText(entry[3])
        layout.addWidget(QLabel("Content:"))
        layout.addWidget(content_text)

        # Mood selection with ComboBox
        mood_combo = QComboBox()
        mood_combo.addItems(JournalApp.MOODS)
        mood_combo.setCurrentText(entry[4])
        layout.addWidget(QLabel("Mood:"))
        layout.addWidget(mood_combo)

        # Edit button
        edit_btn = QPushButton("Edit Entry")
        edit_btn.clicked.connect(lambda: self.edit_entry(entry[1], content_text.toPlainText(), mood_combo.currentText(), dialog))
        layout.addWidget(edit_btn)

        # Delete button
        delete_btn = QPushButton("Delete Entry")
        delete_btn.clicked.connect(lambda: self.delete_entry(entry[1], dialog))
        layout.addWidget(delete_btn)

        dialog.exec_()

    def edit_entry(self, entry_number, new_content, new_mood, dialog):
        """Edit the existing journal entry."""
        result = self.journal.edit_entry(entry_number, new_content=new_content, new_mood=new_mood)
        QMessageBox.information(self, "Entry Status", result)
        dialog.accept()  # Close the dialog
        self.load_entries()  # Refresh the entry list after editing

    def delete_entry(self, entry_number, dialog):
        """Delete the specified journal entry."""
        result = self.journal.delete_entry(entry_number)
        QMessageBox.information(self, "Entry Status", result)
        dialog.accept()  # Close the dialog
        self.load_entries()  # Refresh the entry list after deletion


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = JournalApp()
    window.show()
    sys.exit(app.exec_())











