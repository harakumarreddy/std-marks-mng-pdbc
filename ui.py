
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import csv, os
from datetime import datetime

import db

def run_app():
    # create tables first (safe)
    try:
        db.create_tables()
    except Exception as e:
        messagebox.showerror("DB Error", f"Could not create/connect to DB:\n{e}")
        return

    root = tk.Tk()
    app = StudentApp(root)
    root.geometry('920x520')
    root.title('Student Marks Management (MySQL)')
    root.mainloop()

class StudentApp:
    def __init__(self, root):
        self.root = root
        self.selected_student_id = None
        self.setup_ui()
        self.populate_tree()

    def setup_ui(self):
        frm = ttk.Frame(self.root, padding=10)
        frm.pack(fill='x')

        ttk.Label(frm, text='Roll No:').grid(row=0, column=0, sticky='w')
        self.roll_var = tk.StringVar()
        ttk.Entry(frm, textvariable=self.roll_var, width=15).grid(row=0, column=1, sticky='w')

        ttk.Label(frm, text='Name:').grid(row=0, column=2, sticky='w', padx=(10,0))
        self.name_var = tk.StringVar()
        ttk.Entry(frm, textvariable=self.name_var, width=25).grid(row=0, column=3, sticky='w')

        ttk.Label(frm, text='Class:').grid(row=0, column=4, sticky='w', padx=(10,0))
        self.class_var = tk.StringVar()
        ttk.Entry(frm, textvariable=self.class_var, width=10).grid(row=0, column=5, sticky='w')

        ttk.Label(frm, text='Math:').grid(row=1, column=0, sticky='w', pady=(8,0))
        self.math_var = tk.StringVar()
        ttk.Entry(frm, textvariable=self.math_var, width=10).grid(row=1, column=1, sticky='w', pady=(8,0))

        ttk.Label(frm, text='Science:').grid(row=1, column=2, sticky='w', padx=(10,0), pady=(8,0))
        self.science_var = tk.StringVar()
        ttk.Entry(frm, textvariable=self.science_var, width=10).grid(row=1, column=3, sticky='w', pady=(8,0))

        ttk.Label(frm, text='English:').grid(row=1, column=4, sticky='w', padx=(10,0), pady=(8,0))
        self.english_var = tk.StringVar()
        ttk.Entry(frm, textvariable=self.english_var, width=10).grid(row=1, column=5, sticky='w', pady=(8,0))

        btn_frame = ttk.Frame(self.root, padding=(10,5))
        btn_frame.pack(fill='x')
        ttk.Button(btn_frame, text='Add Student', command=self.add_student).pack(side='left')
        ttk.Button(btn_frame, text='Update Selected', command=self.update_student).pack(side='left', padx=(6,0))
        ttk.Button(btn_frame, text='Delete Selected', command=self.delete_student).pack(side='left', padx=(6,0))
        ttk.Button(btn_frame, text='Clear Form', command=self.clear_form).pack(side='left', padx=(6,0))
        ttk.Button(btn_frame, text='Export CSV', command=self.export_csv).pack(side='right')

        search_frame = ttk.Frame(self.root, padding=10)
        search_frame.pack(fill='x')
        ttk.Label(search_frame, text='Search:').pack(side='left')
        self.search_var = tk.StringVar()
        s_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=30)
        s_entry.pack(side='left', padx=(6,0))
        s_entry.bind('<Return>', lambda e: self.perform_search())
        ttk.Button(search_frame, text='Go', command=self.perform_search).pack(side='left', padx=(6,0))
        ttk.Button(search_frame, text='Show All', command=self.populate_tree).pack(side='left', padx=(6,0))

        tree_frame = ttk.Frame(self.root, padding=10)
        tree_frame.pack(fill='both', expand=True)
        cols = ('id','roll','name','class','math','science','english','total','average','grade')
        self.tree = ttk.Treeview(tree_frame, columns=cols, show='headings')
        for c in cols:
            self.tree.heading(c, text=c.title())
            if c in ('name',):
                self.tree.column(c, width=160)
            elif c in ('roll','class'):
                self.tree.column(c, width=80)
            else:
                self.tree.column(c, width=70)
        self.tree.pack(fill='both', expand=True, side='left')
        self.tree.bind('<<TreeviewSelect>>', self.on_tree_select)

        vsb = ttk.Scrollbar(tree_frame, orient='vertical', command=self.tree.yview)
        self.tree.configure(yscroll=vsb.set)
        vsb.pack(side='right', fill='y')

    def add_student(self):
        roll = self.roll_var.get().strip()
        name = self.name_var.get().strip()
        cls = self.class_var.get().strip()
        if not roll or not name:
            messagebox.showwarning('Validation', 'Roll and Name are required')
            return
        try:
            math = int(self.math_var.get()) if self.math_var.get().strip()!='' else 0
            science = int(self.science_var.get()) if self.science_var.get().strip()!='' else 0
            english = int(self.english_var.get()) if self.english_var.get().strip()!='' else 0
        except ValueError:
            messagebox.showwarning('Validation', 'Marks must be integers')
            return
        ok, err = db.add_student(roll, name, cls, math, science, english)
        if not ok:
            messagebox.showerror('Error', f'Could not add student: {err}')
            return
        messagebox.showinfo('Added', 'Student added successfully')
        self.clear_form()
        self.populate_tree()

    def update_student(self):
        if not self.selected_student_id:
            messagebox.showwarning('Select', 'Select a student to update')
            return
        roll = self.roll_var.get().strip()
        name = self.name_var.get().strip()
        cls = self.class_var.get().strip()
        if not roll or not name:
            messagebox.showwarning('Validation', 'Roll and Name are required')
            return
        try:
            math = int(self.math_var.get()) if self.math_var.get().strip()!='' else 0
            science = int(self.science_var.get()) if self.science_var.get().strip()!='' else 0
            english = int(self.english_var.get()) if self.english_var.get().strip()!='' else 0
        except ValueError:
            messagebox.showwarning('Validation', 'Marks must be integers')
            return
        ok = db.update_student(self.selected_student_id, roll, name, cls, math, science, english)
        if not ok:
            messagebox.showerror('Error', 'Could not update (maybe duplicate roll?)')
            return
        messagebox.showinfo('Updated', 'Student updated successfully')
        self.clear_form()
        self.populate_tree()

    def delete_student(self):
        if not self.selected_student_id:
            messagebox.showwarning('Select', 'Select a student to delete')
            return
        if messagebox.askyesno('Confirm', 'Are you sure you want to delete the selected student?'):
            db.delete_student(self.selected_student_id)
            messagebox.showinfo('Deleted', 'Student deleted')
            self.clear_form()
            self.populate_tree()

    def clear_form(self):
        self.selected_student_id = None
        self.roll_var.set('')
        self.name_var.set('')
        self.class_var.set('')
        self.math_var.set('')
        self.science_var.set('')
        self.english_var.set('')
        for i in self.tree.selection():
            self.tree.selection_remove(i)

    def populate_tree(self):
        for r in self.tree.get_children():
            self.tree.delete(r)
        rows = db.fetch_all(order_by='id')
        for row in rows:
            self.tree.insert('', 'end', values=row)

    def perform_search(self):
        term = self.search_var.get().strip()
        for r in self.tree.get_children():
            self.tree.delete(r)
        if term == '':
            rows = db.fetch_all()
        else:
            rows = db.search(term)
        for row in rows:
            self.tree.insert('', 'end', values=row)

    def on_tree_select(self, event):
        sel = self.tree.selection()
        if not sel:
            return
        item = self.tree.item(sel[0])
        vals = item['values']
        if not vals:
            return
        self.selected_student_id = vals[0]
        self.roll_var.set(vals[1])
        self.name_var.set(vals[2])
        self.class_var.set(vals[3])
        self.math_var.set(vals[4])
        self.science_var.set(vals[5])
        self.english_var.set(vals[6])

    def export_csv(self):
        rows = db.fetch_all(order_by='id')
        if not rows:
            messagebox.showinfo('No Data', 'No student data to export')
            return
        ts = datetime.now().strftime('%Y%m%d_%H%M%S')
        default_name = f'export_students_{ts}.csv'
        filename = filedialog.asksaveasfilename(defaultextension='.csv', initialfile=default_name, filetypes=[('CSV','*.csv')])
        if not filename:
            return
        headers = ['id','roll','name','class','math','science','english','total','average','grade']
        try:
            with open(filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(headers)
                for row in rows:
                    writer.writerow(row)
            messagebox.showinfo('Exported', f'Exported {len(rows)} records to {os.path.basename(filename)}')
        except Exception as e:
            messagebox.showerror('Error', f'Could not export: {e}')
