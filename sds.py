import sqlite3
import time
import tkinter as tk
from tkinter import messagebox, simpledialog

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
    TITLE_MAX_LENGTH = 50

    def __init__(self, root):
        self.journal = Journal()
        self.root = root
        self.root.title("Journal Manager")
        self.root.configure(bg='#DEF9C4')  # Dark background for Instagram-like feel

        # Main Frame
        self.main_frame = tk.Frame(self.root, bg='#DEF9C4')
        self.main_frame.pack(fill="both", expand=True)

        # Title Label (Instagram-inspired style)
        title_label = tk.Label(self.main_frame, text="Journal Manager", font=("Kozuka Gothic Pr6N B", 32, "bold"),
                               bg='#DEF9C4', fg='#468585')
        title_label.pack(pady=(20, 10))

        # Add Entry Button (Rounded corners effect with padding)
        self.add_entry_btn = tk.Button(self.main_frame, text="Add Entry", command=self.add_entry, 
                                       bg='#9CDBA6', fg='white', font=("Helvetica", 14, "bold"), 
                                       relief='flat', bd=0, padx=20, pady=10)
        self.add_entry_btn.pack(pady=10, ipadx=30, ipady=10)

        # Show Entries Button
        self.show_entries_btn = tk.Button(self.main_frame, text="Show All Entries", command=self.show_entries, 
                                          bg='#9CDBA6', fg='white', font=("Helvetica", 14, "bold"), 
                                          relief='flat', bd=0, padx=20, pady=10)
        self.show_entries_btn.pack(pady=10, ipadx=30, ipady=10)

        # Edit Entry Button
        self.edit_entry_btn = tk.Button(self.main_frame, text="Edit Entry", command=self.edit_entry, 
                                        bg='#9CDBA6', fg='white', font=("Helvetica", 14, "bold"), 
                                        relief='flat', bd=0, padx=20, pady=10)
        self.edit_entry_btn.pack(pady=10, ipadx=30, ipady=10)

        # Delete Entry Button
        self.delete_entry_btn = tk.Button(self.main_frame, text="Delete Entry", command=self.delete_entry, 
                                          bg='#9CDBA6', fg='white', font=("Helvetica", 14, "bold"), 
                                          relief='flat', bd=0, padx=20, pady=10)
        self.delete_entry_btn.pack(pady=10, ipadx=30, ipady=10)

        # Footer Label
        footer_label = tk.Label(self.main_frame, text="Yournal ©", font=("Helvetica", 10),
                                bg='#DEF9C4', fg='gray')
        footer_label.pack(side="bottom", pady=20)

    def add_entry(self):
        """Add a new journal entry with a title character limit."""
        title = simpledialog.askstring("Input", f"Enter the title (Max {JournalApp.TITLE_MAX_LENGTH} characters):")
        if title and len(title) > JournalApp.TITLE_MAX_LENGTH:
            messagebox.showwarning("Warning", f"Title cannot exceed {JournalApp.TITLE_MAX_LENGTH} characters!")
            return
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
        """Edit an existing journal entry with title character limit."""
        entry_number = simpledialog.askinteger("Input", "Enter the entry number to edit:")
        if entry_number:
            new_title = simpledialog.askstring("Input", f"Enter the new title (Max {JournalApp.TITLE_MAX_LENGTH} characters):")
            if new_title and len(new_title) > JournalApp.TITLE_MAX_LENGTH:
                messagebox.showwarning("Warning", f"Title cannot exceed {JournalApp.TITLE_MAX_LENGTH} characters!")
                return
            new_content = simpledialog.askstring("Input", "Enter the new content:")
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

    # Set window size and make it non-resizable
    root.geometry("400x600")
    root.resizable(False, False)

    # Start the main event loop
    root.mainloop()
