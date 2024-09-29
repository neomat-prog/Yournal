import sqlite3
from cryptography.fernet import Fernet
import tkinter as tk
from tkinter import messagebox

# Stały klucz do szyfrowania i deszyfrowania
KEY = b'G1uOU6RQF_8jEBb-uDd9grbU8SPhXZcWxv1Whtw3PpA='  # Stały klucz

# Obiekt Fernet do szyfrowania i deszyfrowania haseł
cipher = Fernet(KEY)

# Nazwa lokalnej bazy danych SQLite
DATABASE_NAME = "users.db"

# Zmienna globalna przechowująca nazwę aktualnie zalogowanego użytkownika
logged_in_user = None


def connect_to_db(database_name):
    """Funkcja łącząca z lokalną bazą danych SQLite."""
    try:
        return sqlite3.connect(database_name)
    except sqlite3.Error as e:
        print(f"Błąd połączenia z bazą danych: {e}")
        return None


def register_user(username, password):
    """Funkcja rejestrująca nowego użytkownika z szyfrowaniem hasła."""
    conn = connect_to_db(DATABASE_NAME)
    if not conn:
        return False

    cursor = conn.cursor()
    
    # Tworzenie tabeli, jeśli nie istnieje
    cursor.execute("""CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT NOT NULL UNIQUE,
                        password BLOB NOT NULL
                    );""")

    # Sprawdzanie, czy użytkownik już istnieje
    try:
        cursor.execute("SELECT username FROM users WHERE username = ?", (username,))
        if cursor.fetchone():
            messagebox.showerror("Błąd", f"Użytkownik '{username}' już istnieje.")
            return False
    except Exception as e:
        messagebox.showerror("Błąd", f"Błąd przy sprawdzaniu użytkownika: {e}")
        return False

    # Szyfrowanie hasła
    encrypted_password = cipher.encrypt(password.encode())

    try:
        # Wstawianie nowego użytkownika
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, encrypted_password))
        conn.commit()
        messagebox.showinfo("Sukces", f"Użytkownik {username} został zarejestrowany.")
        return True
    except Exception as e:
        messagebox.showerror("Błąd", f"Błąd przy rejestracji: {e}")
        return False
    finally:
        cursor.close()
        conn.close()


def login_user(username, password):
    """Funkcja logowania użytkownika z odszyfrowaniem hasła."""
    global logged_in_user
    conn = connect_to_db(DATABASE_NAME)
    if not conn:
        return False

    cursor = conn.cursor()

    try:
        # Pobieranie hasła dla danego użytkownika
        cursor.execute("SELECT password FROM users WHERE username = ?", (username,))
        result = cursor.fetchone()
        if result:
            encrypted_password = result[0]
            # Deszyfrowanie hasła
            decrypted_password = cipher.decrypt(encrypted_password).decode()
            if decrypted_password == password:
                messagebox.showinfo("Sukces", "Zalogowano pomyślnie!")
                logged_in_user = username  # Zapisanie nazwy zalogowanego użytkownika
                return True
            else:
                messagebox.showerror("Błąd", "Niepoprawne hasło.")
                return False
        else:
            messagebox.showerror("Błąd", "Użytkownik nie istnieje.")
            return False
    except Exception as e:
        messagebox.showerror("Błąd", f"Błąd przy logowaniu: {e}")
        return False
    finally:
        cursor.close()
        conn.close()


def logout_user():
    """Funkcja wylogowująca aktualnie zalogowanego użytkownika."""
    global logged_in_user
    if logged_in_user:
        messagebox.showinfo("Wylogowanie", f"Wylogowano użytkownika: {logged_in_user}")
        logged_in_user = None
    else:
        messagebox.showwarning("Brak zalogowanego użytkownika", "Nikt nie jest zalogowany.")


def show_registered_users():
    """Funkcja wyświetlająca zarejestrowanych użytkowników oraz ich haseł."""
    conn = connect_to_db(DATABASE_NAME)
    if not conn:
        return

    cursor = conn.cursor()

    try:
        # Pobieranie wszystkich użytkowników z bazy danych
        cursor.execute("SELECT username, password FROM users")
        users = cursor.fetchall()

        if users:
            user_list = "Lista zarejestrowanych użytkowników:\n\n"
            user_list += "{:<20} | {:<}\n".format("Nazwa użytkownika", "Zaszyfrowane hasło")
            user_list += "-" * 70 + "\n"
            for user in users:
                username, encrypted_password = user
                user_list += f"{username:<20} | {encrypted_password}\n"
            messagebox.showinfo("Zarejestrowani użytkownicy", user_list)
        else:
            messagebox.showinfo("Brak użytkowników", "Brak zarejestrowanych użytkowników.")
    except Exception as e:
        messagebox.showerror("Błąd", f"Błąd przy wyświetlaniu użytkowników: {e}")
    finally:
        cursor.close()
        conn.close()


def show_main_menu():
    """Funkcja wyświetlająca główne menu."""
    clear_window()

    tk.Label(root, text="Panel Główny", font=("Arial", 16, 'bold')).pack(pady=20)

    button_width = 30  # Ustawienie stałej szerokości przycisków

    btn_register = tk.Button(root, text="Rejestracja", command=show_register_window, bg="#4CAF50", fg="white", font=("Arial", 10, 'bold'), width=button_width, relief=tk.FLAT)
    btn_register.pack(pady=10)

    btn_login = tk.Button(root, text="Logowanie", command=show_login_window, bg="#4CAF50", fg="white", font=("Arial", 10, 'bold'), width=button_width, relief=tk.FLAT)
    btn_login.pack(pady=10)

    btn_logout = tk.Button(root, text="Wylogowanie", command=logout_user, bg="#4CAF50", fg="white", font=("Arial", 10, 'bold'), width=button_width, relief=tk.FLAT)
    btn_logout.pack(pady=10)

    btn_show_users = tk.Button(root, text="Zarejestrowani Użytkownicy", command=show_registered_users, bg="#4CAF50", fg="white", font=("Arial", 10, 'bold'), width=button_width, relief=tk.FLAT)
    btn_show_users.pack(pady=10)

    btn_exit = tk.Button(root, text="Wyjście", command=root.quit, bg="#4CAF50", fg="white", font=("Arial", 10, 'bold'), width=button_width, relief=tk.FLAT)
    btn_exit.pack(pady=10)


def show_register_window():
    """Funkcja wyświetlająca okno rejestracji."""
    clear_window()

    tk.Label(root, text="Rejestracja", font=("Arial", 16, 'bold')).pack(pady=20)

    frame = tk.Frame(root, bg="#f0f0f0")
    frame.pack(pady=10)

    tk.Label(frame, text="Nazwa użytkownika:", bg="#f0f0f0", font=("Arial", 10)).grid(row=0, column=0, padx=10, pady=10, sticky='w')
    entry_username = tk.Entry(frame, font=("Arial", 10))
    entry_username.grid(row=0, column=1, padx=10, pady=10)

    tk.Label(frame, text="Hasło:", bg="#f0f0f0", font=("Arial", 10)).grid(row=1, column=0, padx=10, pady=10, sticky='w')
    entry_password = tk.Entry(frame, show='*', font=("Arial", 10))
    entry_password.grid(row=1, column=1, padx=10, pady=10)

    button_width = 30  # Ustawienie stałej szerokości przycisków w oknie rejestracji

    btn_register = tk.Button(frame, text="Zarejestruj", command=lambda: on_register(entry_username.get(), entry_password.get()), bg="#4CAF50", fg="white", font=("Arial", 10, 'bold'), width=button_width, relief=tk.FLAT)
    btn_register.grid(row=2, columnspan=2, pady=20)

    btn_back = tk.Button(frame, text="Powrót do panelu głównego", command=show_main_menu, bg="#FF5722", fg="white", font=("Arial", 10, 'bold'), width=button_width, relief=tk.FLAT)
    btn_back.grid(row=3, columnspan=2, pady=5)


def on_register(username, password):
    """Funkcja obsługująca rejestrację użytkownika."""
    if username and password:
        register_user(username, password)
        show_main_menu()  # Powrót do głównego menu po rejestracji
    else:
        messagebox.showwarning("Błąd", "Proszę podać zarówno nazwę użytkownika, jak i hasło.")


def show_login_window():
    """Funkcja wyświetlająca okno logowania."""
    clear_window()

    tk.Label(root, text="Logowanie", font=("Arial", 16, 'bold')).pack(pady=20)

    frame = tk.Frame(root, bg="#f0f0f0")
    frame.pack(pady=10)

    tk.Label(frame, text="Nazwa użytkownika:", bg="#f0f0f0", font=("Arial", 10)).grid(row=0, column=0, padx=10, pady=10, sticky='w')
    entry_username = tk.Entry(frame, font=("Arial", 10))
    entry_username.grid(row=0, column=1, padx=10, pady=10)

    tk.Label(frame, text="Hasło:", bg="#f0f0f0", font=("Arial", 10)).grid(row=1, column=0, padx=10, pady=10, sticky='w')
    entry_password = tk.Entry(frame, show='*', font=("Arial", 10))
    entry_password.grid(row=1, column=1, padx=10, pady=10)

    button_width = 30  # Ustawienie stałej szerokości przycisków w oknie logowania

    btn_login = tk.Button(frame, text="Zaloguj", command=lambda: on_login(entry_username.get(), entry_password.get()), bg="#4CAF50", fg="white", font=("Arial", 10, 'bold'), width=button_width, relief=tk.FLAT)
    btn_login.grid(row=2, columnspan=2, pady=20)

    btn_back = tk.Button(frame, text="Powrót do panelu głównego", command=show_main_menu, bg="#FF5722", fg="white", font=("Arial", 10, 'bold'), width=button_width, relief=tk.FLAT)
    btn_back.grid(row=3, columnspan=2, pady=5)


def on_login(username, password):
    """Funkcja obsługująca logowanie użytkownika."""
    if username and password:
        if login_user(username, password):
            show_main_menu()  # Powrót do głównego menu po zalogowaniu
        else:
            messagebox.showwarning("Błąd", "Proszę sprawdzić nazwę użytkownika i hasło.")
    else:
        messagebox.showwarning("Błąd", "Proszę podać zarówno nazwę użytkownika, jak i hasło.")


def clear_window():
    """Funkcja czyszcząca zawartość okna."""
    for widget in root.winfo_children():
        widget.destroy()


def main():
    """Główna funkcja uruchamiająca aplikację."""
    global root
    root = tk.Tk()
    root.title("Rejestracja i Logowanie")
    root.geometry("500x400")  # Ustawienie szerszego rozmiaru głównego okna
    root.configure(bg="#f0f0f0")  # Ustawienie tła głównego okna

    show_main_menu()  # Wyświetlenie głównego menu na starcie

    root.mainloop()


if __name__ == "__main__":
    main()
