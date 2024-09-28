import time
import os

class JournalEntry:
    entry_count = 0

    def __init__(self, number, title="text", content="text", date=None):
        self.number = number
        self.title = title
        self.content = content
        self.date = date

    @classmethod
    def add_entry(cls):
        entry_title = input("Podaj tytuł wpisu: ")
        entry_content = input("Podaj treść wpisu: ")
        entry_date = str(time.strftime("%d-%m-%Y", time.localtime()))
        cls.entry_count += 1
        new_entry = cls(number=cls.entry_count, title=entry_title, content=entry_content, date=entry_date)
        return new_entry

    def show_entry(self):
        print(f"Entry #{self.number}")
        print(f"Title: {self.title}")
        print(f"Date: {self.date}")
        print(f"Content: {self.content}")
        print("-" * 40)


class Journal:
    def __init__(self):
        self.entries = []
        self.load_existing_entries()

    def load_existing_entries(self):
        files = [f for f in os.listdir() if f.startswith("entry_") and f.endswith(".txt")]
        if files:
            existing_numbers = [int(f.split('_')[1].split('.')[0]) for f in files]
            max_number = max(existing_numbers)
            JournalEntry.entry_count = max_number
            print(f"Załadowano {len(files)} wpisów. Kontynuacja od numeru {max_number + 1}.")

            for file_name in files:
                with open(file_name, 'r', encoding='utf-8') as file:
                    number = int(file.readline().split('#')[1].strip())
                    title = file.readline().split(": ")[1].strip()
                    date = file.readline().split(": ")[1].strip()
                    content = file.readline().split(": ")[1].strip()
                    entry = JournalEntry(number=number, title=title, content=content, date=date)
                    self.entries.append(entry)
        else:
            print("Nie znaleziono istniejących wpisów. Rozpoczęcie od numeru 1.")

    def add_new_entry(self):
        new_entry = JournalEntry.add_entry()
        self.entries.append(new_entry)
        print(f"Dodano wpis o numerze: {new_entry.number}")
        self.save_entry_to_file(new_entry)

    def save_entry_to_file(self, entry):
        file_name = f"entry_{entry.number}.txt"
        with open(file_name, 'w', encoding='utf-8') as file:
            file.write(f"Entry #{entry.number}\n")
            file.write(f"Title: {entry.title}\n")
            file.write(f"Date: {entry.date}\n")
            file.write(f"Content: {entry.content}\n")
        print(f"Wpis zapisano do pliku: {file_name}")

    def show_all_entries(self):
        if not self.entries:
            print("Dziennik jest pusty.")
        else:
            print("Wpisy w dzienniku:")
            for entry in self.entries:
                entry.show_entry()


# Tworzenie obiektu Journal i ładowanie istniejących wpisów
my_journal = Journal()

# Dodawanie nowego wpisu
my_journal.add_new_entry()

# Dodawanie kolejnego wpisu
my_journal.add_new_entry()

# Wyświetlenie wszystkich wpisów w dzienniku
my_journal.show_all_entries()
