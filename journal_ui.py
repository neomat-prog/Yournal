import sqlite3
import time
import tkinter as tk
from tkinter import messagebox, simpledialog


class JournalEntry:
    def __init__(self, number, title="text", content="text", date=None):
        self.number = number
        self.title = title
        self.content = content
        self.date = date


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


class JournalApp:
    def __init__(self, root):
        self.journal = Journal()
        self.root = root
        self.root.title("Journal Manager")

        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(padx=10, pady=10)

        # Add Entry Button
        self.add_entry_btn = tk.Button(self.main_frame, text="Add Entry", command=self.add_entry)
        self.add_entry_btn.grid(row=0, column=0, padx=10, pady=5)

        # Show Entries Button
        self.show_entries_btn = tk.Button(self.main_frame, text="Show All Entries", command=self.show_entries)
        self.show_entries_btn.grid(row=0, column=1, padx=10, pady=5)

        # Edit Entry Button
        self.edit_entry_btn = tk.Button(self.main_frame, text="Edit Entry", command=self.edit_entry)
        self.edit_entry_btn.grid(row=1, column=0, padx=10, pady=5)

        # Delete Entry Button
        self.delete_entry_btn = tk.Button(self.main_frame, text="Delete Entry", command=self.delete_entry)
        self.delete_entry_btn.grid(row=1, column=1, padx=10, pady=5)

    def add_entry(self):
        """Add a new journal entry."""
        title = simpledialog.askstring("Input", "Enter the title:")
        content = simpledialog.askstring("Input", "Enter the content:")
        if title and content:
            result = self.journal.add_new_entry(title, content)
            messagebox.showinfo("Result", result)
        else:
            messagebox.showwarning("Warning", "Title or content cannot be empty!")

    def show_entries(self):
        """Show all journal entries in a popup."""
        entries = self.journal.get_all_entries()
        if entries:
            entry_list = "\n".join([f"#{row[1]} | {row[2]} | {row[3]} | {row[4]}" for row in entries])
            messagebox.showinfo("All Entries", entry_list)
        else:
            messagebox.showinfo("All Entries", "No entries found.")

    def edit_entry(self):
        """Edit an existing journal entry."""
        entry_number = simpledialog.askinteger("Input", "Enter the entry number to edit:")
        if entry_number:
            new_title = simpledialog.askstring("Input", "Enter the new title (leave blank to keep current):")
            new_content = simpledialog.askstring("Input", "Enter the new content (leave blank to keep current):")
            if new_title or new_content:
                result = self.journal.edit_entry(entry_number, new_title or "", new_content or "")
                messagebox.showinfo("Result", result)
            else:
                messagebox.showwarning("Warning", "Nothing to update!")
        else:
            messagebox.showwarning("Warning", "Entry number cannot be empty!")

    def delete_entry(self):
        """Delete an existing journal entry."""
        entry_number = simpledialog.askinteger("Input", "Enter the entry number to delete:")
        if entry_number:
            result = self.journal.delete_entry(entry_number)
            messagebox.showinfo("Result", result)
        else:
            messagebox.showwarning("Warning", "Entry number cannot be empty!")


if __name__ == "__main__":
    root = tk.Tk()
    app = JournalApp(root)
    root.mainloop()
