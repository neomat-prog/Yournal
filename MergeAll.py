import sys
import tkinter as tk
from tkinter import ttk
from Self_Goals import TaskApp  # Ensure TaskApp is properly defined
from Journal import JournalApp  # Ensure JournalApp is defined
from PyQt5.QtWidgets import QApplication

class MainApp:
    def __init__(self, master):
        self.master = master
        self.master.title("We_Move")
        self.master.geometry("400x300")
        self.master.configure(bg='#F7E3D3')

        # Title label
        title_label = tk.Label(self.master, text="We_Move", font=("Helvetica", 28, "bold"), bg='#F7E3D3', fg='#5D3F3F')
        title_label.pack(pady=20)

        # Create a frame for buttons for better alignment
        button_frame = tk.Frame(self.master, bg='#F7E3D3')
        button_frame.pack(pady=10)

        # Create two buttons to launch the applications
        journal_button = ttk.Button(button_frame, text="Journal", command=self.open_journal_app)
        journal_button.pack(pady=10, ipadx=20, ipady=10, padx=10)

        task_button = ttk.Button(button_frame, text="Self Goals", command=self.open_task_app)
        task_button.pack(pady=10, ipadx=20, ipady=10, padx=10)

        # Style the buttons
        style = ttk.Style()
        style.configure("TButton",
                        font=("Helvetica", 14, "bold"),
                        background='#FF8C69',
                        foreground='white',
                        borderwidth=0,
                        relief='flat')

        # Apply a hover effect
        style.map("TButton",
                  background=[("active", "#FF7B57")])  # Change color on hover

    def open_journal_app(self):
        # Start the PyQt5 application
        self.master.withdraw()  # Hide the Tkinter window
        app = QApplication(sys.argv)

        # Create the JournalApp instance and show it
        journal_app = JournalApp()
        journal_app.show()

        # To keep the Tkinter window hidden while PyQt5 is running
        app.exec_()

        # Re-show the Tkinter window when the PyQt app is closed
        self.master.deiconify()

    def open_task_app(self):
        try:
            # Open Task App in a new window using PyQt5
            app = QApplication(sys.argv)
            task_app = TaskApp()  # Create the TaskApp instance
            task_app.show()
            self.master.withdraw()  # Hide the Tkinter window
            app.exec_()  # Run the PyQt5 application loop
            self.master.deiconify()  # Re-show the Tkinter window when done
        except Exception as e:
            print(f"Error opening task app: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = MainApp(root)
    root.mainloop()

