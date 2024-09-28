import sys
import sqlite3
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QPushButton,
    QLineEdit, QListWidget, QMessageBox, QWidget
)
from PyQt5.QtCore import Qt


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


# TaskList with database integration
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
            QMessageBox.warning(None, "Error", "Invalid task index.")

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


# PyQt5 Main Window
class TaskApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Task List Manager")
        self.setGeometry(300, 200, 400, 300)

        # Main layout
        self.main_widget = QWidget(self)
        self.setCentralWidget(self.main_widget)
        self.main_layout = QVBoxLayout(self.main_widget)

        # Task list object
        self.task_list = TaskList()

        # Task entry input field
        self.task_entry = QLineEdit(self)
        self.task_entry.setPlaceholderText("Enter a new task...")
        self.main_layout.addWidget(self.task_entry)

        # Add task button
        self.add_button = QPushButton("Add Task", self)
        self.add_button.clicked.connect(self.add_task)
        self.main_layout.addWidget(self.add_button)

        # Task list display
        self.task_list_widget = QListWidget(self)
        self.update_task_list()
        self.main_layout.addWidget(self.task_list_widget)

        # Complete and remove task buttons
        self.button_layout = QHBoxLayout()

        self.complete_button = QPushButton("Complete Task", self)
        self.complete_button.clicked.connect(self.complete_task)
        self.button_layout.addWidget(self.complete_button)

        self.remove_button = QPushButton("Remove Completed Tasks", self)
        self.remove_button.clicked.connect(self.remove_completed_tasks)
        self.button_layout.addWidget(self.remove_button)

        self.main_layout.addLayout(self.button_layout)

    def add_task(self):
        task_description = self.task_entry.text()
        if task_description:
            self.task_list.add_task(task_description)
            self.task_entry.clear()
            self.update_task_list()
        else:
            QMessageBox.warning(self, "Empty Task", "Please enter a task description.")

    def complete_task(self):
        selected_item = self.task_list_widget.currentRow()
        if selected_item != -1:
            self.task_list.complete_task(selected_item)
            self.update_task_list()
        else:
            QMessageBox.warning(self, "Error", "Select a task to mark as completed.")

    def remove_completed_tasks(self):
        self.task_list.remove_completed_tasks()
        self.update_task_list()

    def update_task_list(self):
        self.task_list_widget.clear()
        for task in self.task_list.show_tasks():
            self.task_list_widget.addItem(task)

    def closeEvent(self, event):
        # Close the database connection when the app is closed
        self.task_list.close()
        event.accept()


# Running the application
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TaskApp()
    window.show()
    sys.exit(app.exec_())
