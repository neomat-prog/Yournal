import sqlite3
import time

class JournalEntry:
    entry_count = 0  # Class attribute to track the number of entries

    def __init__(self, number, title="text", content="text", date=None):
        self.number = number
        self.title = title
        self.content = content
        self.date = date

    @classmethod
    def add_entry(cls):
        """Class method to add a new journal entry."""
        # Get user input
        entry_title = input("Enter entry title: ")
        entry_content = input("Enter entry content: ")

        # Current date in "dd-mm-yyyy" format
        entry_date = time.strftime("%d-%m-%Y", time.localtime())

        # Increment entry count and create a new entry
        cls.entry_count += 1
        new_entry = cls(number=cls.entry_count, title=entry_title, content=entry_content, date=entry_date)

        return new_entry

    def show_entry(self):
        """Displays entry information."""
        print(f"Entry #{self.number}")
        print(f"Title: {self.title}")
        print(f"Date: {self.date}")
        print(f"Content: {self.content}")
        print("-" * 40)


class Journal:
    def __init__(self):
        self.entries = []  # List to store journal entries
        self.conn = sqlite3.connect('journal.db')  # Connect to the database
        self.create_table()

    def create_table(self):
        """Create the journal entries table if it doesn't exist."""
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

    def add_new_entry(self):
        new_entry = JournalEntry.add_entry()
        self.entries.append(new_entry)
        print(f"Added entry with number: {new_entry.number}")

        self.save_entry_to_db(new_entry)

    def save_entry_to_db(self, entry):
        """Save journal entry to the database."""
        with self.conn:
            self.conn.execute('''
                INSERT INTO journal_entries (number, title, content, date)
                VALUES (?, ?, ?, ?)
            ''', (entry.number, entry.title, entry.content, entry.date))
        print(f"Entry #{entry.number} saved to the database.")

    def show_all_entries(self):
        """Display all journal entries from the database."""
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM journal_entries')
        rows = cursor.fetchall()

        if not rows:
            print("The journal is empty.")
        else:
            print("Journal Entries:")
            for row in rows:
                entry = JournalEntry(number=row[1], title=row[2], content=row[3], date=row[4])
                entry.show_entry()

    def __del__(self):
        """Close the database connection when the object is destroyed."""
        self.conn.close()


# Usage
user_journal = Journal()

user_journal.add_new_entry()
user_journal.add_new_entry()
user_journal.show_all_entries()

