import tkinter as tk
from tkinter import messagebox
import sqlite3

# Task class remains the same
class Task:
    def __init__(self, description, completed=False):
        self.description = description
        self.completed = completed

    def mark_completed(self):
        self.completed = True

    def __str__(self):
        status = "[X]" if self.completed else "[ ]"
        return f"{status} {self.description}"


class TaskList:
    def __init__(self):
        # Connect to the SQLite database (or create it)
        self.conn = sqlite3.connect('tasks.db')
        self.cursor = self.conn.cursor()
        # Create a table for tasks if it doesn't exist
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                description TEXT NOT NULL,
                completed INTEGER NOT NULL
            )
        ''')
        self.conn.commit()
        self.load_tasks()

    def load_tasks(self):
        # Load tasks from the database
        self.tasks = []
        self.cursor.execute("SELECT id, description, completed FROM tasks")
        rows = self.cursor.fetchall()
        for row in rows:
            task = Task(row[1], bool(row[2]))
            self.tasks.append(task)

    def add_task(self, description):
        task = Task(description)
        self.tasks.append(task)
        # Insert the task into the database
        self.cursor.execute("INSERT INTO tasks (description, completed) VALUES (?, ?)", (description, 0))
        self.conn.commit()

    def complete_task(self, index):
        if 0 <= index < len(self.tasks):
            self.tasks[index].mark_completed()
            # Update the database
            self.cursor.execute("UPDATE tasks SET completed = 1 WHERE id = ?", (index + 1,))
            self.conn.commit()
        else:
            messagebox.showerror("Błąd", "Nieprawidłowy indeks zadania.")

    def remove_completed_tasks(self):
        # Remove completed tasks from both the list and the database
        self.tasks = [task for task in self.tasks if not task.completed]
        self.cursor.execute("DELETE FROM tasks WHERE completed = 1")
        self.conn.commit()

    def show_tasks(self):
        return [str(task) for task in self.tasks]

    def close(self):
        # Close the database connection
        self.conn.close()


# UI Code
class TaskApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Task List Manager")

        # Task list object
        self.task_list = TaskList()

        # UI Elements
        self.frame = tk.Frame(root)
        self.frame.pack(pady=10)

        self.task_entry = tk.Entry(self.frame, width=40)
        self.task_entry.grid(row=0, column=0, padx=5)

        self.add_button = tk.Button(self.frame, text="Dodaj zadanie", command=self.add_task)
        self.add_button.grid(row=0, column=1, padx=5)

        self.tasks_box = tk.Listbox(self.frame, width=50, height=10)
        self.tasks_box.grid(row=1, column=0, columnspan=2, pady=10)

        self.complete_button = tk.Button(self.frame, text="Oznacz jako wykonane", command=self.complete_task)
        self.complete_button.grid(row=2, column=0, padx=5)

        self.remove_button = tk.Button(self.frame, text="Usuń wykonane zadania", command=self.remove_completed_tasks)
        self.remove_button.grid(row=2, column=1, padx=5)

        self.update_task_list()

        # Close the database connection when the app closes
        root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def add_task(self):
        task_description = self.task_entry.get()
        if task_description:
            self.task_list.add_task(task_description)
            self.task_entry.delete(0, tk.END)
            self.update_task_list()
        else:
            messagebox.showwarning("Puste zadanie", "Wprowadź opis zadania.")

    def complete_task(self):
        try:
            selected_index = self.tasks_box.curselection()[0]
            self.task_list.complete_task(selected_index)
            self.update_task_list()
        except IndexError:
            messagebox.showwarning("Błąd", "Wybierz zadanie do oznaczenia.")

    def remove_completed_tasks(self):
        self.task_list.remove_completed_tasks()
        self.update_task_list()

    def update_task_list(self):
        self.tasks_box.delete(0, tk.END)
        for task in self.task_list.show_tasks():
            self.tasks_box.insert(tk.END, task)

    def on_closing(self):
        self.task_list.close()
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = TaskApp(root)
    root.mainloop()
