import tkinter as tk
from tkinter import messagebox

class Task:
    def __init__(self, description):
        self.description = description
        self.completed = False

    def mark_completed(self):
        self.completed = True

    def __str__(self):
        status = "[X]" if self.completed else "[ ]"
        return f"{status} {self.description}"


class TaskList:
    def __init__(self):
        self.tasks = []

    def add_task(self, description):
        task = Task(description)
        self.tasks.append(task)

    def complete_task(self, index):
        if 0 <= index < len(self.tasks):
            self.tasks[index].mark_completed()
        else:
            messagebox.showerror("Błąd", "Nieprawidłowy indeks zadania.")

    def show_tasks(self):
        return [str(task) for task in self.tasks]

    def remove_completed_tasks(self):
        self.tasks = [task for task in self.tasks if not task.completed]


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


if __name__ == "__main__":
    root = tk.Tk()
    app = TaskApp(root)
    root.mainloop()
