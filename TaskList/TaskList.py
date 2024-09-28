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
        print(f"Zadanie '{description}' zostało dodane do listy.")

    def complete_task(self, index):
        if 0 <= index < len(self.tasks):
            self.tasks[index].mark_completed()
            print(f"Zadanie nr {index + 1} zostało oznaczone jako wykonane.")
        else:
            print("Nieprawidłowy indeks zadania. Spróbuj ponownie.")

    def show_tasks(self):
        if not self.tasks:
            print("Lista zadań jest pusta.")
        else:
            print("Lista zadań:")
            for idx, task in enumerate(self.tasks):
                print(f"{idx + 1}. {task}")

    def remove_completed_tasks(self):
        self.tasks = [task for task in self.tasks if not task.completed]
        print("Wszystkie wykonane zadania zostały usunięte.")

task_list = TaskList()

task_list.add_task("Nauka Pythona")
task_list.add_task("Zrobić zakupy")
task_list.add_task("Zadzwonić do przyjaciela")

task_list.show_tasks()

task_list.complete_task(1)

task_list.show_tasks()

task_list.remove_completed_tasks()

task_list.show_tasks()
