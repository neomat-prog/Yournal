import sqlite3
import time
import tkinter as tk
from tkinter import messagebox, simpledialog, Scrollbar, Text


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
        self.root.geometry("600x400")
        self.root.config(bg="#F0F0F0")

        # Main Frame
        self.main_frame = tk.Frame(self.root, bg="#F0F0F0")
        self.main_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        # Title label
        title_label = tk.Label(self.main_frame, text="Journal Application", font=("Arial", 18), bg="#F0F0F0")
        title_label.grid(row=0, column=0, columnspan=3, pady=10)

        # Add Entry Form (Title + Content)
        self.title_label = tk.Label(self.main_frame, text="Title", bg="#F0F0F0", font=("Arial", 12))
        self.title_label.grid(row=1, column=0, sticky=tk.W)
        self.title_entry = tk.Entry(self.main_frame, width=40, font=("Arial", 12))
        self.title_entry.grid(row=1, column=1, padx=10)

        self.content_label = tk.Label(self.main_frame, text="Content", bg="#F0F0F0", font=("Arial", 12))
        self.content_label.grid(row=2, column=0, sticky=tk.W)
        self.content_text = tk.Text(self.main_frame, height=5, width=40, font=("Arial", 12))
        self.content_text.grid(row=2, column=1, padx=10)

        # Add Entry Button
        self.add_entry_btn = tk.Button(self.main_frame, text="Add Entry", command=self.add_entry, bg="#007BFF", fg="white", font=("Arial", 12))
        self.add_entry_btn.grid(row=3, column=1, sticky=tk.W, pady=10)

        # Entry Actions
        self.show_entries_btn = tk.Button(self.main_frame, text="Show All Entries", command=self.show_entries, bg="#28A745", fg="white", font=("Arial", 12))
        self.show_entries_btn.grid(row=4, column=0, padx=5, pady=5)

        self.edit_entry_btn = tk.Button(self.main_frame, text="Edit Entry", command=self.edit_entry, bg="#FFC107", fg="white", font=("Arial", 12))
        self.edit_entry_btn.grid(row=4, column=1, sticky=tk.W, padx=5, pady=5)

        self.delete_entry_btn = tk.Button(self.main_frame, text="Delete Entry", command=self.delete_entry, bg="#DC3545", fg="white", font=("Arial", 12))
        self.delete_entry_btn.grid(row=5, column=0, padx=5, pady=5)

        # Entry Display Area
        self.entry_display = Text(self.main_frame, height=8, width=60, font=("Arial", 12))
        self.entry_display.grid(row=6, column=0, columnspan=2, pady=10)
        self.entry_display.config(state=tk.DISABLED)  # Read-only text area

        # Scrollbar for Entry Display
        self.scrollbar = Scrollbar(self.main_frame, command=self.entry_display.yview)
        self.scrollbar.grid(row=6, column=2, sticky="ns")
        self.entry_display['yscrollcommand'] = self.scrollbar.set

    def add_entry(self):
        """Add a new journal entry."""
        title = self.title_entry.get().strip()
        content = self.content_text.get("1.0", tk.END).strip()
        if title and content:
            result = self.journal.add_new_entry(title, content)
            messagebox.showinfo("Result", result)
            self.title_entry.delete(0, tk.END)
            self.content_text.delete("1.0", tk.END)
        else:
            messagebox.showwarning("Warning", "Title or content cannot be empty!")

    def show_entries(self):
        """Show all journal entries in the display area."""
        self.entry_display.config(state=tk.NORMAL)
        self.entry_display.delete("1.0", tk.END)

        entries = self.journal.get_all_entries()
        if entries:
            for row in entries:
                self.entry_display.insert(tk.END, f"#{row[1]} | {row[2]} | {row[3]} | {row[4]}\n")
        else:
            self.entry_display.insert(tk.END, "No entries found.\n")
        self.entry_display.config(state=tk.DISABLED)

    def edit_entry(self):
        """Edit an existing journal entry."""
        entry_number = simpledialog.askinteger("Input", "Enter the entry number to edit:")
        if entry_number:
            new_title = simpledialog.askstring("Input", "Enter the new title (leave blank to keep current):")
            new_content = simpledialog.askstring("Input", "Enter the new content (leave blank to keep current):")
            if new_title or new_content:
                result = self.journal.edit_entry(entry_number, new_title or "", new_content or "")
                messagebox.showinfo("Result", result)
                self.show_entries()
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
            self.show_entries()
        else:
            messagebox.showwarning("Warning", "Entry number cannot be empty!")


if __name__ == "__main__":
    root = tk.Tk()
    app = JournalApp(root)
    root.mainloop()
