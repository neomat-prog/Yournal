import time

class JournalEntry:
    entry_count = 0  # Atrybut klasy, aby śledzić liczbę wpisów

    def __init__(self, number, title="text", content="text", date=None):
        self.number = number
        self.title = title
        self.content = content
        self.date = date

    @classmethod
    def add_entry(cls):
        """Metoda klasy do dodania nowego wpisu dziennikowego."""
        # Pobranie danych od użytkownika
        entry_title = input("Podaj tytuł wpisu: ")
        entry_content = input("Podaj treść wpisu: ")

        # Aktualna data w formacie "dd-mm-yyyy"
        entry_date = time.strftime("%d-%m-%Y", time.localtime())

        # Zwiększenie licznika wpisów i utworzenie nowego wpisu
        cls.entry_count += 1
        new_entry = cls(number=cls.entry_count, title=entry_title, content=entry_content, date=entry_date)

        return new_entry

    def show_entry(self):
        """Wyświetla informacje o wpisie."""
        print(f"Entry #{self.number}")
        print(f"Title: {self.title}")
        print(f"Date: {self.date}")
        print(f"Content: {self.content}")
        print("-" * 40)


class Journal:
    def __init__(self):
        self.entries = []  # Lista do przechowywania wpisów dziennika

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



user_journal = Journal()


user_journal.add_new_entry()
user_journal.add_new_entry()
user_journal.show_all_entries()
