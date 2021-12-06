"""
File:           gui.py
Author:         Dibyaranjan Sathua
Created on:     02/12/21, 6:50 pm

Search for "Update on client side" and do the necessary changes
"""
import csv
from pathlib import Path
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

from src.dbhandler import DBHandler


DB_CONFIG_FILE = Path(__file__).absolute().parents[1] / "config" / "db_config.json"


class EmailUpdateGUI:
    """ Class to load the GUI to update email """

    def __init__(self):
        self.dbhandler = DBHandler.from_config_file(DB_CONFIG_FILE)
        self.row_data = None
        self.db_divisions = []
        # Key will be division and value will be list of depts
        self.db_departments = dict()
        # Key will department and value will be list of categories
        self.db_categories = dict()
        self.check_value = None
        self.check = None
        self.division_name = None
        self.dept_name = None
        self.category_name = None
        self.update_btn = None
        self.sm_name = None
        self.sm_email = None
        self.asm_name = None
        self.asm_email = None
        self.csv_file = None
        self.selected_division = ""
        self.selected_department = ""
        self.selected_categories = []
        self.category_id_name_to_id = dict()

    def init_db_data(self):
        """ Initialize with database data """
        # Update on client side: CHANGE TABLE NAME
        query = "SELECT * FROM div_contact_list_audit;"
        # self.row_data = self.dbhandler.create_pandas_table(query)
        # for index, row in self.row_data.iterrows():
        self.row_data = self.dbhandler.fetch_all(query)
        for row in self.row_data:
            # Update on client side: CHANGE COLUMN NAME FOR DIVISION, DEPARTMENT AND CATEGORY
            division = row["division_nm"]
            department = row["dept_nm"]
            category = row["category_nm"]
            category_id = row["category_id"]
            cat_id_name = f"{category_id} {category}"
            if division not in self.db_divisions:
                self.db_divisions.append(division)
            if division not in self.db_departments:
                self.db_departments[division] = []
            if division not in self.db_categories:
                self.db_categories[division] = dict()
            if department not in self.db_departments[division]:
                self.db_departments[division].append(department)
            if department not in self.db_categories[division]:
                self.db_categories[division][department] = []
            if cat_id_name not in self.db_categories[division][department]:
                self.db_categories[division][department].append(cat_id_name)
                self.category_id_name_to_id[cat_id_name] = category_id

    def load_gui(self):
        """ Load the main GUI """
        self.init_db_data()
        window = tk.Tk()
        window.title("Email Update GUI")
        window.columnconfigure(0, weight=1, minsize=75)
        window.rowconfigure(0, weight=1, minsize=50)

        frame = ttk.Frame(master=window, padding=10)
        frame.grid(sticky="nsew")
        # frame.columnconfigure(0, weight=1, minsize=75)
        # frame.rowconfigure(0, weight=1, minsize=50)
        row = 0
        self.check_value = tk.BooleanVar()
        self.check_value.set(False)
        self.check = ttk.Checkbutton(
            frame,
            text="Update using CSV",
            variable=self.check_value,
            command=self.csv_update_checkbox_callback,
        )
        self.check.grid(column=0, row=row, columnspan=2, sticky="w")
        row += 1

        # Division input
        division_name_label = ttk.Label(frame, text="Division Name")
        division_name_label.grid(column=0, row=row, sticky="w")
        division_name_choices = tk.StringVar()
        self.division_name = ttk.Combobox(
            frame, textvariable=division_name_choices, state="readonly", width=50
        )
        self.division_name["values"] = self.db_divisions
        self.division_name.current()
        self.division_name.grid(column=1, row=row)
        # Add callback to division combo box which will populate the choices for department combobox
        self.division_name.bind("<<ComboboxSelected>>", self.division_callback)
        row += 1

        # Department input
        dept_label = ttk.Label(frame, text="Department Name")
        dept_label.grid(column=0, row=row, sticky="w")
        # dept_label.rowconfigure(0, weight=1)
        # dept_label.columnconfigure(0, weight=1)
        dept_name_choices = tk.StringVar()
        self.dept_name = ttk.Combobox(
            frame, textvariable=dept_name_choices, state="readonly", width=50
        )
        self.dept_name.grid(column=1, row=row)
        # Add callback to dept combo box which will populate the choices for category Listbox
        self.dept_name.bind("<<ComboboxSelected>>", self.department_callback)
        row += 1

        # Category input
        category_name_label = ttk.Label(frame, text="Category Name")
        category_name_label.grid(column=0, row=row, sticky="w")
        category_items = tk.StringVar()
        self.category_name = tk.Listbox(
            frame, width=50, height=10, selectmode="extended", listvariable=category_items
        )
        self.category_name.grid(column=1, row=row)
        scrollbar = ttk.Scrollbar(
            frame, orient='vertical', command=self.category_name.yview
        )
        scrollbar.grid(column=2, row=row, sticky='ns')
        self.category_name['yscrollcommand'] = scrollbar.set
        row += 1

        # SM details
        sm_name_label = ttk.Label(frame, text="SM Name")
        sm_name_label.grid(column=0, row=row, sticky="w")
        self.sm_name = ttk.Entry(frame, width=50)
        self.sm_name.grid(column=1, row=row)
        row += 1
        sm_email_label = ttk.Label(frame, text="SM Email")
        sm_email_label.grid(column=0, row=row, sticky="w")
        self.sm_email = ttk.Entry(frame, width=50)
        self.sm_email.grid(column=1, row=row)
        row += 1

        # ASM details
        asm_name_label = ttk.Label(frame, text="ASM Name")
        asm_name_label.grid(column=0, row=row, sticky="w")
        self.asm_name = ttk.Entry(frame, width=50)
        self.asm_name.grid(column=1, row=row)
        row += 1
        asm_email_label = ttk.Label(frame, text="ASM Email")
        asm_email_label.grid(column=0, row=row, sticky="w")
        self.asm_email = ttk.Entry(frame, width=50)
        self.asm_email.grid(column=1, row=row)
        row += 1

        # CSV File
        csv_file_label = ttk.Label(frame, text="CSV File path")
        csv_file_label.grid(column=0, row=row, sticky="w")
        self.csv_file = ttk.Entry(frame, width=50)
        self.csv_file.grid(column=1, row=row)
        row += 1

        # Add a button to update
        self.update_btn = ttk.Button(frame, text="Update")
        self.update_btn.grid(column=0, row=row, columnspan=2, pady=10, sticky="e")
        self.update_btn.bind("<Button-1>", self.update_btn_callback)
        row += 1

        # Initial callback for checkbox
        self.csv_update_checkbox_callback()
        window.mainloop()

    def division_callback(self, event):
        """ Callback for division combo box """
        self.selected_division = event.widget.get()
        # Set the choices of for department
        self.dept_name["values"] = self.db_departments[self.selected_division]
        self.dept_name.current()

    def department_callback(self, event):
        """ Callback for department combo box """
        self.selected_department = event.widget.get()
        db_categories = self.db_categories[self.selected_division][self.selected_department]
        # Set the items for Listbox
        for index, category in enumerate(db_categories):
            self.category_name.insert(index, category)

    def update_email_from_gui_input(self):
        """ Update email from gui input """
        print(self.check_value.get())
        selected_indices = self.category_name.curselection()
        # Get the category id for the selected categories
        self.selected_categories = [
            self.category_id_name_to_id[self.category_name.get(x)]
            for x in selected_indices
        ]
        sm_name = self.sm_name.get()
        sm_email = self.sm_email.get()
        asm_name = self.asm_name.get()
        asm_email = self.asm_email.get()
        if not (sm_name or sm_email or asm_name or asm_email):
            messagebox.showerror(
                "Error",
                "All fields sm_name, sm_email, asm_name or asm_email can not be empty"
            )
        input_emails = []
        # Update on client side: CHANGE TABLE NAME
        query = "UPDATE div_contact_list_audit SET"
        if sm_name:
            query += f" sm_name = %s,"      # Update on client side: CHANGE COLUMN NAME
            input_emails.append(sm_name)
        if sm_email:
            query += f" sm_email = %s,"     # Update on client side: CHANGE COLUMN NAME
            input_emails.append(sm_email)
        if asm_name:
            query += f" asm_name = %s,"     # Update on client side: CHANGE COLUMN NAME
            input_emails.append(asm_name)
        if asm_email:
            query += f" asm_email = %s,"    # Update on client side: CHANGE COLUMN NAME
            input_emails.append(asm_email)
        # Remove the last comma
        query = query.strip(",")
        # Update on client side: CHANGE COLUMN NAME
        query += " WHERE division_nm = %s AND dept_nm = %s AND category_id = %s;"
        records = [
            input_emails + [self.selected_division, self.selected_department, x]
            for x in self.selected_categories
        ]
        print(query)
        # print(records)
        return query, records

    def update_using_csv(self):
        """ Update email using CSV """
        csv_file_path = Path(self.csv_file.get())
        if not csv_file_path.is_file():
            messagebox.showerror(
                "Error",
                f"CSV file {csv_file_path} does not exist"
            )
        records = []
        # Update on client side: CHANGE TABLE NAME
        query = "UPDATE div_contact_list_audit SET"
        with open(csv_file_path, mode="r") as fp:
            reader = csv.DictReader(fp)
            for row in reader:
                data = []
                if "SM_NAME" in row:                # Update on client side: CHANGE CSV HEADER NAME
                    data.append(row["SM_NAME"])
                if "SM_EMAIL" in row:
                    data.append(row["SM_EMAIL"])    # Update on client side: CHANGE CSV HEADER NAME
                if "ASM_NAME" in row:
                    data.append(row["ASM_NAME"])    # Update on client side: CHANGE CSV HEADER NAME
                if "ASM_EMAIL" in row:
                    data.append(row["ASM_EMAIL"])   # Update on client side: CHANGE CSV HEADER NAME
                # Update on client side: CHANGE CSV HEADER NAME
                data += [row["DIVISION_NM"], row["DEPT_NM"], row["CATEGORY_ID"]]
                records.append(data)

        if "SM_NAME" in row:                # Update on client side: CHANGE CSV HEADER NAME
            query += f" sm_name = %s,"      # Update on client side: CHANGE COLUMN NAME
        if "SM_EMAIL" in row:               # Update on client side: CHANGE CSV HEADER NAME
            query += f" sm_email = %s,"     # Update on client side: CHANGE COLUMN NAME
        if "ASM_NAME" in row:               # Update on client side: CHANGE CSV HEADER NAME
            query += f" asm_name = %s,"     # Update on client side: CHANGE COLUMN NAME
        if "ASM_EMAIL" in row:              # Update on client side: CHANGE CSV HEADER NAME
            query += f" asm_email = %s,"    # Update on client side: CHANGE COLUMN NAME
        # Remove the last comma
        query = query.strip(",")
        # Update on client side: CHANGE COLUMN NAME
        query += " WHERE division_nm = %s AND dept_nm = %s AND category_id = %s;"
        print(query)
        # print(records)
        return query, records

    def update_btn_callback(self, event):
        """ Callback for update button """
        if self.check_value.get():
            # Update using CSV
            query, records = self.update_using_csv()
        else:
            # Update using GUI inputs
            query, records = self.update_email_from_gui_input()
        row_count = self.dbhandler.bulk_update(query, records)
        messagebox.showinfo("Information", f"{row_count} rows updated successfully")

    def csv_update_checkbox_callback(self):
        """ Callback for checkbox """
        if self.check_value.get():
            self.division_name["state"] = tk.DISABLED
            self.dept_name["state"] = tk.DISABLED
            self.category_name["state"] = tk.DISABLED
            self.sm_name["state"] = tk.DISABLED
            self.sm_email["state"] = tk.DISABLED
            self.asm_name["state"] = tk.DISABLED
            self.asm_email["state"] = tk.DISABLED
            self.csv_file["state"] = tk.NORMAL
        else:
            self.division_name["state"] = tk.NORMAL
            self.dept_name["state"] = tk.NORMAL
            self.category_name["state"] = tk.NORMAL
            self.sm_name["state"] = tk.NORMAL
            self.sm_email["state"] = tk.NORMAL
            self.asm_name["state"] = tk.NORMAL
            self.asm_email["state"] = tk.NORMAL
            self.csv_file["state"] = tk.DISABLED


if __name__ == "__main__":
    EmailUpdateGUI().load_gui()
