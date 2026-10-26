import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3


# ---------------- DATABASE CONNECTION ----------------

conn = sqlite3.connect("student_results.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS students (
    roll_no TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    python_marks INTEGER NOT NULL,
    maths_marks INTEGER NOT NULL,
    computer_marks INTEGER NOT NULL,
    total INTEGER NOT NULL,
    percentage REAL NOT NULL,
    grade TEXT NOT NULL
)
""")

conn.commit()


# ---------------- HELPER FUNCTIONS ----------------

def calculate_result(python_marks, maths_marks, computer_marks):
    total = python_marks + maths_marks + computer_marks
    percentage = total / 3

    if percentage >= 90:
        grade = "A+"
    elif percentage >= 80:
        grade = "A"
    elif percentage >= 70:
        grade = "B"
    elif percentage >= 60:
        grade = "C"
    elif percentage >= 50:
        grade = "D"
    else:
        grade = "F"

    return total, percentage, grade


def clear_fields():
    roll_entry.delete(0, tk.END)
    name_entry.delete(0, tk.END)
    python_entry.delete(0, tk.END)
    maths_entry.delete(0, tk.END)
    computer_entry.delete(0, tk.END)
    roll_entry.focus()


def validate_marks():
    roll_no = roll_entry.get().strip()
    name = name_entry.get().strip()

    if not roll_no or not name:
        messagebox.showerror(
            "Input Error",
            "Please enter both Roll Number and Student Name."
        )
        return None

    try:
        python_marks = int(python_entry.get())
        maths_marks = int(maths_entry.get())
        computer_marks = int(computer_entry.get())

        marks = [python_marks, maths_marks, computer_marks]

        if any(mark < 0 or mark > 100 for mark in marks):
            messagebox.showerror(
                "Invalid Marks",
                "Marks must be between 0 and 100."
            )
            return None

        return roll_no, name, python_marks, maths_marks, computer_marks

    except ValueError:
        messagebox.showerror(
            "Input Error",
            "Enter valid whole-number marks for all subjects."
        )
        return None


# ---------------- ADD STUDENT ----------------

def add_student():
    data = validate_marks()

    if data is None:
        return

    roll_no, name, py_marks, math_marks, comp_marks = data

    total, percentage, grade = calculate_result(
        py_marks, math_marks, comp_marks
    )

    try:
        cursor.execute("""
        INSERT INTO students
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            roll_no, name, py_marks, math_marks, comp_marks,
            total, percentage, grade
        ))

        conn.commit()

        messagebox.showinfo(
            "Success",
            f"Student added successfully!\n"
            f"Total: {total}/300\n"
            f"Percentage: {percentage:.2f}%\n"
            f"Grade: {grade}"
        )

        clear_fields()
        display_students()

    except sqlite3.IntegrityError:
        messagebox.showerror(
            "Duplicate Roll Number",
            "This roll number already exists."
        )


# ---------------- DISPLAY STUDENTS ----------------

def display_students():
    for item in student_table.get_children():
        student_table.delete(item)

    cursor.execute("""
        SELECT roll_no, name, python_marks, maths_marks,
               computer_marks, total, percentage, grade
        FROM students
        ORDER BY roll_no
    """)

    for student in cursor.fetchall():
        student_table.insert(
            "", tk.END,
            values=(
                student[0], student[1], student[2],
                student[3], student[4], student[5],
                f"{student[6]:.2f}", student[7]
            )
        )


# ---------------- SEARCH STUDENT ----------------

def search_student():
    roll_no = roll_entry.get().strip()

    if not roll_no:
        messagebox.showwarning(
            "Search",
            "Enter a Roll Number to search."
        )
        return

    cursor.execute(
        "SELECT * FROM students WHERE roll_no = ?",
        (roll_no,)
    )

    student = cursor.fetchone()

    if student:
        clear_fields()

        roll_entry.insert(0, student[0])
        name_entry.insert(0, student[1])
        python_entry.insert(0, student[2])
        maths_entry.insert(0, student[3])
        computer_entry.insert(0, student[4])

        messagebox.showinfo(
            "Student Found",
            f"Name: {student[1]}\n"
            f"Total: {student[5]}/300\n"
            f"Percentage: {student[6]:.2f}%\n"
            f"Grade: {student[7]}"
        )
    else:
        messagebox.showinfo(
            "Not Found",
            "No student found with this roll number."
        )


# ---------------- DELETE STUDENT ----------------

def delete_student():
    roll_no = roll_entry.get().strip()

    if not roll_no:
        messagebox.showwarning(
            "Delete",
            "Enter a Roll Number to delete."
        )
        return

    cursor.execute(
        "SELECT name FROM students WHERE roll_no = ?",
        (roll_no,)
    )

    student = cursor.fetchone()

    if not student:
        messagebox.showinfo(
            "Not Found",
            "Student record does not exist."
        )
        return

    confirm = messagebox.askyesno(
        "Confirm Delete",
        f"Delete the record of {student[0]}?"
    )

    if confirm:
        cursor.execute(
            "DELETE FROM students WHERE roll_no = ?",
            (roll_no,)
        )

        conn.commit()
        clear_fields()
        display_students()

        messagebox.showinfo(
            "Deleted",
            "Student record deleted successfully."
        )


# ---------------- GUI DESIGN ----------------

root = tk.Tk()
root.title("Student Result Management System")
root.geometry("1100x650")
root.configure(bg="#eef2f7")

title_label = tk.Label(
    root,
    text="STUDENT RESULT MANAGEMENT SYSTEM",
    font=("Arial", 20, "bold"),
    bg="#243b55",
    fg="white",
    pady=15
)
title_label.pack(fill=tk.X)

form_frame = tk.LabelFrame(
    root,
    text="Student Details",
    font=("Arial", 12, "bold"),
    bg="#eef2f7",
    padx=15,
    pady=15
)
form_frame.pack(fill=tk.X, padx=20, pady=15)

tk.Label(
    form_frame, text="Roll Number:",
    bg="#eef2f7"
).grid(row=0, column=0, padx=5, pady=8, sticky="w")

roll_entry = tk.Entry(form_frame, width=20)
roll_entry.grid(row=0, column=1, padx=5, pady=8)

tk.Label(
    form_frame, text="Student Name:",
    bg="#eef2f7"
).grid(row=0, column=2, padx=5, pady=8, sticky="w")

name_entry = tk.Entry(form_frame, width=20)
name_entry.grid(row=0, column=3, padx=5, pady=8)

tk.Label(
    form_frame, text="Python Marks:",
    bg="#eef2f7"
).grid(row=1, column=0, padx=5, pady=8, sticky="w")

python_entry = tk.Entry(form_frame, width=20)
python_entry.grid(row=1, column=1, padx=5, pady=8)

tk.Label(
    form_frame, text="Maths Marks:",
    bg="#eef2f7"
).grid(row=1, column=2, padx=5, pady=8, sticky="w")

maths_entry = tk.Entry(form_frame, width=20)
maths_entry.grid(row=1, column=3, padx=5, pady=8)

tk.Label(
    form_frame, text="Computer Marks:",
    bg="#eef2f7"
).grid(row=2, column=0, padx=5, pady=8, sticky="w")

computer_entry = tk.Entry(form_frame, width=20)
computer_entry.grid(row=2, column=1, padx=5, pady=8)


# ---------------- BUTTONS ----------------

button_frame = tk.Frame(root, bg="#eef2f7")
button_frame.pack(pady=5)

tk.Button(
    button_frame, text="Add Student",
    command=add_student, width=15,
    bg="#198754", fg="white"
).grid(row=0, column=0, padx=5)

tk.Button(
    button_frame, text="Search Student",
    command=search_student, width=15,
    bg="#0d6efd", fg="white"
).grid(row=0, column=1, padx=5)

tk.Button(
    button_frame, text="Delete Student",
    command=delete_student, width=15,
    bg="#dc3545", fg="white"
).grid(row=0, column=2, padx=5)

tk.Button(
    button_frame, text="Clear Fields",
    command=clear_fields, width=15
).grid(row=0, column=3, padx=5)

tk.Button(
    button_frame, text="Refresh Records",
    command=display_students, width=15,
    bg="#6c757d", fg="white"
).grid(row=0, column=4, padx=5)


# ---------------- STUDENT TABLE ----------------

table_frame = tk.LabelFrame(
    root,
    text="Student Records",
    font=("Arial", 12, "bold"),
    bg="#eef2f7",
    padx=10,
    pady=10
)
table_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

columns = (
    "Roll", "Name", "Python", "Maths",
    "Computer", "Total", "Percentage", "Grade"
)

student_table = ttk.Treeview(
    table_frame,
    columns=columns,
    show="headings"
)

for column in columns:
    student_table.heading(column, text=column)
    student_table.column(column, width=115, anchor="center")

scrollbar = ttk.Scrollbar(
    table_frame,
    orient=tk.VERTICAL,
    command=student_table.yview
)

student_table.configure(yscrollcommand=scrollbar.set)

student_table.pack(
    side=tk.LEFT, fill=tk.BOTH, expand=True
)

scrollbar.pack(side=tk.RIGHT, fill=tk.Y)


# ---------------- START APPLICATION ----------------

display_students()

def close_application():
    conn.close()
    root.destroy()

root.protocol("WM_DELETE_WINDOW", close_application)
root.mainloop()
