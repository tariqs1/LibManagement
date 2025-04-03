import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk


class LibraryManagement:
    def __init__(self, master):
        self.master = master
        self.master.title("UWM CS557 Library Management System")
        self.master.geometry("800x600")  # Default window size
        self.master.state("zoomed")  # Start in fullscreen mode

        # Load background image
        self.bg_image = Image.open("images/library-outside.jpg")

        # Background label
        self.bg_label = tk.Label(self.master)
        self.bg_label.place(relwidth=1, relheight=1)

        # Resize background dynamically
        self.update_background()

        # Create a semi-transparent frame for the login box
        self.frame = tk.Frame(self.master, bg='#2C3E50', bd=5)
        self.frame.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.4, relheight=0.5)  # Adjusts with window size

        # Title
        self.login_label = tk.Label(self.frame, text="Library Management System",
                                    font=("Helvetica", 20, "bold"), bg='#2C3E50', fg='white')
        self.login_label.pack(pady=20)

        # Username
        self.username_entry = tk.Entry(self.frame, font=("Helvetica", 14), width=30, bd=2, relief="flat", fg="gray")
        self.username_entry.insert(0, "Username")
        self.username_entry.bind("<FocusIn>", self.clear_entry)
        self.username_entry.pack(pady=10, ipady=5)

        # Password
        self.password_entry = tk.Entry(self.frame, font=("Helvetica", 14), width=30, bd=2, relief="flat", fg="gray")
        self.password_entry.insert(0, "Password")
        self.password_entry.bind("<FocusIn>", self.clear_entry)
        self.password_entry.pack(pady=10, ipady=5)

        # Buttons
        self.login_button = tk.Button(self.frame, text="Login", command=self.login,
                                      font=("Helvetica", 14, "bold"), bg='#3498DB', fg='white', bd=0, relief="flat")
        self.login_button.pack(pady=10, ipadx=50, ipady=5)

        self.register_button = tk.Button(self.frame, text="Register", command=self.register,
                                         font=("Helvetica", 14, "bold"), bg='#2ECC71', fg='white', bd=0, relief="flat")
        self.register_button.pack(pady=10, ipadx=50, ipady=5)

        self.master.bind("<Configure>", self.resize_background)

    def update_background(self):
        # Resize the background image dynamically to fit the window
        width = self.master.winfo_width() or 800
        height = self.master.winfo_height() or 600
        self.bg_resized = self.bg_image.resize((width, height), Image.Resampling.LANCZOS)
        self.bg_photo = ImageTk.PhotoImage(self.bg_resized)

        # store the reference img
        self.bg_label.config(image=self.bg_photo)
        self.bg_label.image = self.bg_photo

    def resize_background(self, event):
        # Update background when window is resized
        self.update_background()

        self.username = ""
        self.password = ""
        self.librarians = []

    def clear_entry(self, event):
       # Clears the placeholder text when the user clicks on the entry field.
        widget = event.widget
        if widget.get() in ["Username", "Password"]:
            widget.delete(0, tk.END)
            widget.config(fg="black")  # Change text color to normal
            if widget == self.password_entry:
                widget.config(show="*")  # Mask password

    def login(self):
        self.username = self.username_entry.get()
        self.password = self.password_entry.get()
        for librarian in self.librarians:
            if self.username == librarian[0] and self.password == librarian[1]:
                self.username_entry.delete(0, tk.END)
                self.password_entry.delete(0, tk.END)
                self.login_label.destroy()
                self.username_entry.destroy()
                self.password_entry.destroy()
                self.login_button.destroy()
                self.register_button.destroy()
                self.library_management_screen()
                self.bg_label.destroy()
                self.frame.destroy()

                return
        messagebox.showerror("Error", "Invalid username or password")

    def register(self):
        self.username = self.username_entry.get()
        self.password = self.password_entry.get()
        self.librarians.append([self.username, self.password])
        self.username_entry.delete(0, tk.END)
        self.password_entry.delete(0, tk.END)

    def library_management_screen(self):
        self.add_book_label = tk.Label(self.master, text="Add Book", font=("Helvetica", 16), bg='#708090', fg='white')
        self.add_book_label.pack()
        self.add_book_entry = tk.Entry(self.master, font=("Helvetica", 12))
        self.add_book_entry.pack()
        self.add_book_button = tk.Button(self.master, text="Add Book", command=self.add_book, font=("Helvetica", 12))
        self.add_book_button.pack()
        self.remove_book_label = tk.Label(self.master, text="Remove Book", font=("Helvetica", 16), bg='#708090',
                                          fg='white')
        self.remove_book_label.pack()
        self.remove_book_entry = tk.Entry(self.master, font=("Helvetica", 12))
        self.remove_book_entry.pack()
        self.remove_book_button = tk.Button(self.master, text="Remove Book", command=self.remove_book,
                                            font=("Helvetica", 12))
        self.remove_book_button.pack()
        self.issue_book_label = tk.Label(self.master, text="Issue Book", font=("Helvetica", 16), bg='#708090',
                                         fg='white')
        self.issue_book_label.pack()
        self.issue_book_entry = tk.Entry(self.master, font=("Helvetica", 12))
        self.issue_book_entry.pack()
        self.issue_book_button = tk.Button(self.master, text="Issue Book", command=self.issue_book,
                                           font=("Helvetica", 12))
        self.issue_book_button.pack()
        self.view_books_button = tk.Button(self.master, text="View Books", command=self.view_books,
                                           font=("Helvetica", 12))
        self.view_books_button.pack()

    def add_book(self):
        book = self.add_book_entry.get()
        self.books.append(book)
        messagebox.showinfo("Success", "Book added successfully")
        self.add_book_entry.delete(0, tk.END)

    def remove_book(self):
        book = self.remove_book_entry.get()
        if book in self.books:
            self.books.remove(book)
            messagebox.showinfo("Success", "Book removed successfully")
        else:
            messagebox.showerror("Error", "Book not found")
        self.remove_book_entry.delete(0, tk.END)

    def issue_book(self):
        book = self.issue_book_entry.get()
        if book in self.books:
            self.lend_list.append(book)
            self.books.remove(book)
            messagebox.showinfo("Success", "Book issued successfully")
        else:
            messagebox.showerror("Error", "Book not found")
        self.issue_book_entry.delete(0, tk.END)

    def view_books(self):
        message = "\n".join(self.books)
        messagebox.showinfo("Books", message)


if __name__ == "__main__":
    root = tk.Tk()
    app = LibraryManagement(root)
    root.mainloop()
