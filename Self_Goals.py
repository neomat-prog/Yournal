import sys
import sqlite3
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QPushButton,
    QLineEdit, QListWidget, QMessageBox, QWidget, QLabel, QInputDialog  # Import QInputDialog here
)
from PyQt5.QtCore import Qt


class Task:
    def __init__(self, id, description, completed=False):
        self.id = id
        self.description = description
        self.completed = completed

    def mark_completed(self):
        self.completed = True

    def __str__(self):
        status = "[X]" if self.completed else "[ ]"
        return f"{status} {self.description}"


class TaskList:
    def __init__(self):
        self.conn = sqlite3.connect('tasks.db')
        self.cursor = self.conn.cursor()
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
        self.tasks = []
        self.cursor.execute("SELECT id, description, completed FROM tasks")
        rows = self.cursor.fetchall()
        for row in rows:
            task = Task(row[0], row[1], bool(row[2]))
            self.tasks.append(task)

    def add_task(self, description):
        task = Task(None, description)
        self.tasks.append(task)
        self.cursor.execute("INSERT INTO tasks (description, completed) VALUES (?, ?)", (description, 0))
        self.conn.commit()
        return task.id  # Return the ID of the newly added task

    def complete_tasks(self, indices):
        for index in indices:
            if 0 <= index < len(self.tasks):
                task_id = self.tasks[index].id
                self.tasks[index].mark_completed()
                self.cursor.execute("UPDATE tasks SET completed = 1 WHERE id = ?", (task_id,))
        self.conn.commit()

    def remove_completed_tasks(self, indices):
        for index in sorted(indices, reverse=True):
            task_id = self.tasks[index].id
            self.cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
            del self.tasks[index]
        self.conn.commit()

    def edit_task(self, index, new_description):
        if 0 <= index < len(self.tasks):
            task_id = self.tasks[index].id
            self.cursor.execute("UPDATE tasks SET description = ? WHERE id = ?", (new_description, task_id))
            self.tasks[index].description = new_description
            self.conn.commit()

    def show_tasks(self):
        return [str(task) for task in self.tasks]

    def close(self):
        self.conn.close()


class TaskApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Task List Manager")
        self.setGeometry(300, 200, 500, 400)

        self.main_widget = QWidget(self)
        self.setCentralWidget(self.main_widget)
        self.main_layout = QVBoxLayout(self.main_widget)

        self.task_list = TaskList()

        # Title label
        self.title_label = QLabel("Task List", self)
        self.title_label.setAlignment(Qt.AlignCenter)
        self.main_layout.addWidget(self.title_label)

        self.task_entry = QLineEdit(self)
        self.task_entry.setPlaceholderText("Enter a new task...")
        self.main_layout.addWidget(self.task_entry)

        self.add_button = QPushButton("Add Task", self)
        self.add_button.clicked.connect(self.add_task)
        self.add_button.setShortcut("Ctrl+A")  # Keyboard shortcut for adding tasks
        self.main_layout.addWidget(self.add_button)

        self.task_list_widget = QListWidget(self)
        self.task_list_widget.setSelectionMode(QListWidget.MultiSelection)
        self.update_task_list()
        self.main_layout.addWidget(self.task_list_widget)

        self.button_layout = QHBoxLayout()

        self.complete_button = QPushButton("Complete Selected Tasks", self)
        self.complete_button.clicked.connect(self.complete_selected_tasks)
        self.complete_button.setShortcut("Ctrl+C")  # Keyboard shortcut for completing tasks
        self.button_layout.addWidget(self.complete_button)

        self.remove_button = QPushButton("Remove Selected Tasks", self)
        self.remove_button.clicked.connect(self.remove_selected_tasks)
        self.remove_button.setShortcut("Ctrl+R")  # Keyboard shortcut for removing tasks
        self.button_layout.addWidget(self.remove_button)

        self.edit_button = QPushButton("Edit Selected Task", self)
        self.edit_button.clicked.connect(self.edit_selected_task)
        self.edit_button.setShortcut("Ctrl+E")  # Keyboard shortcut for editing tasks
        self.button_layout.addWidget(self.edit_button)

        self.main_layout.addLayout(self.button_layout)

    def add_task(self):
        task_description = self.task_entry.text().strip()
        if task_description and len(task_description) <= 100:
            task_id = self.task_list.add_task(task_description)
            self.task_entry.clear()
            self.update_task_list()
            QMessageBox.information(self, "Success", f"Task '{task_description}' added successfully.")
        else:
            QMessageBox.warning(self, "Invalid Task", "Please enter a valid task description (1-100 characters).")

    def complete_selected_tasks(self):
        selected_items = self.task_list_widget.selectedItems()
        if selected_items:
            indices = [self.task_list_widget.row(item) for item in selected_items]
            self.task_list.complete_tasks(indices)
            self.update_task_list()
            QMessageBox.information(self, "Success", "Selected tasks marked as completed. Good Job!")
        else:
            QMessageBox.warning(self, "Error", "Select at least one task to mark as completed.")

    def remove_selected_tasks(self):
        selected_items = self.task_list_widget.selectedItems()
        if selected_items:
            confirmation = QMessageBox.question(
                self,
                "Confirm Deletion",
                "Are you sure you want to remove the selected tasks?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            if confirmation == QMessageBox.Yes:
                indices = [self.task_list_widget.row(item) for item in selected_items]
                self.task_list.remove_completed_tasks(indices)
                self.update_task_list()
                QMessageBox.information(self, "Success", "Selected tasks removed successfully.")
        else:
            QMessageBox.warning(self, "Error", "Select at least one task to remove.")

    def edit_selected_task(self):
        selected_items = self.task_list_widget.selectedItems()
        if selected_items:
            index = self.task_list_widget.row(selected_items[0])  # Edit only the first selected item
            new_description, ok = QInputDialog.getText(self, "Edit Task", "New Task Description:")
            if ok and new_description.strip():
                self.task_list.edit_task(index, new_description)
                self.update_task_list()
                QMessageBox.information(self, "Success", "Task edited successfully.")
            else:
                QMessageBox.warning(self, "Invalid Task", "Please enter a valid task description.")
        else:
            QMessageBox.warning(self, "Error", "Select a task to edit.")

    def update_task_list(self):
        self.task_list_widget.clear()
        for task in self.task_list.show_tasks():
            self.task_list_widget.addItem(task)

    def closeEvent(self, event):
        self.task_list.close()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TaskApp()
    window.show()
    sys.exit(app.exec_())

