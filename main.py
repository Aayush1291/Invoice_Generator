import tkinter
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from datetime import date, datetime
import random
import jinja2
import pdfkit
import mysql.connector

# Database connection configuration
def connect_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="YOUR_PASSWORD",
        database="invoices_db"  # Make sure this database exists
    )

# Create necessary tables if they don't exist
def create_tables():
    conn = connect_db()
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS invoices (
            invoice_id INT PRIMARY KEY,
            date VARCHAR(10),
            customer_name VARCHAR(100),
            customer_phone VARCHAR(20),
            subtotal DECIMAL(10,2),
            tax_amount DECIMAL(10,2),
            total_amount DECIMAL(10,2)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS invoice_items (
            id INT AUTO_INCREMENT PRIMARY KEY,
            invoice_id INT,
            quantity INT,
            description VARCHAR(200),
            price DECIMAL(10,2),
            line_total DECIMAL(10,2),
            FOREIGN KEY (invoice_id) REFERENCES invoices(invoice_id)
        )
    ''')
    
    conn.commit()
    cursor.close()
    conn.close()

invoice_num = random.randint(1, 999999)
current_date = date.today().strftime("%d/%m/%Y")
print("Hello")

def clear_item():
    qty_entry.delete(0, tkinter.END)
    qty_entry.insert(0, "1")
    description_entry.delete(0, tkinter.END)
    Product_Price_entry.delete(0, tkinter.END)
    Product_Price_entry.insert(0, "0.0")

invoice_list = []

def add_item():
    qty = int(qty_entry.get())
    desc = description_entry.get()
    price = float(Product_Price_entry.get())
    line_total = qty * price
    invoice_item = [qty, desc, price, line_total]
    tree.insert('', 0, values=invoice_item)
    clear_item()
    invoice_list.append(invoice_item)

def new_invoice():
    first_name_entry.delete(0, tkinter.END)
    last_name_entry.delete(0, tkinter.END)
    customer_phone_entry.delete(0, tkinter.END)
    clear_item()
    tree.delete(*tree.get_children())
    invoice_list.clear()
    global invoice_num
    invoice_num = random.randint(1, 999999)
    invoice_number_entry.delete(0, tkinter.END)
    invoice_number_entry.insert(0, invoice_num)

def save_to_database():
    conn = connect_db()
    cursor = conn.cursor()
    
    name = first_name_entry.get() + " " + last_name_entry.get()
    phone = customer_phone_entry.get()
    subtotal = sum(item[3] for item in invoice_list)
    salestax_rate = 0.12
    salestax = subtotal * salestax_rate
    total = subtotal + salestax
    
    # Insert invoice data
    cursor.execute('''
        INSERT INTO invoices (invoice_id, date, customer_name, customer_phone, subtotal, tax_amount, total_amount)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    ''', (invoice_num, current_date, name, phone, subtotal, salestax, total))
    
    # Insert invoice items
    for item in invoice_list:
        cursor.execute('''
            INSERT INTO invoice_items (invoice_id, quantity, description, price, line_total)
            VALUES (%s, %s, %s, %s, %s)
        ''', (invoice_num, item[0], item[1], item[2], item[3]))
    
    conn.commit()
    cursor.close()
    conn.close()

def generate_invoice():
    template_loader = jinja2.FileSystemLoader('./')
    template_env = jinja2.Environment(loader=template_loader)
    template = template_env.get_template("invoice_template.html")

    name = first_name_entry.get() + " " + last_name_entry.get()
    pdf_username = first_name_entry.get() + last_name_entry.get()
    phone = customer_phone_entry.get()
    subtotal = sum(item[3] for item in invoice_list)
    salestax_rate = 0.12
    salestax = subtotal * salestax_rate
    total = subtotal + salestax

    output_text = template.render({
        "INVOICE_NUMBER": invoice_num,
        "INVOICE_DATE": current_date,
        "CUSTOMER_NAME": name,
        "CUSTOMER_PHONE": phone,
        "invoice_list": invoice_list,
        "SUBTOTAL": subtotal,
        "GST_RATE": salestax_rate * 100,
        "GST_AMOUNT": salestax,
        "TOTAL_AMOUNT": total
    })

    pdf_name = "new_invoice" + pdf_username + datetime.now().strftime("%Y-%m-%d-%H%M%S") + ".pdf"
    config = pdfkit.configuration(wkhtmltopdf="C:/Program Files/wkhtmltopdf/bin/wkhtmltopdf.exe")
    pdfkit.from_string(output_text, pdf_name, configuration=config, css="pdf-styles.css")
    
    # Save to database before clearing
    save_to_database()
    
    messagebox.showinfo("Invoice Complete", "Invoice Complete")
    new_invoice()

# Initialize window and database
window = tkinter.Tk()
window.title("Invoice Generator Form")
create_tables()  # Create tables when program starts

frame = tkinter.Frame(window)
frame.pack(padx=20, pady=10)

# Rest of your UI code remains the same...
invoice_number_label = tk.Label(frame, text="Invoice Number:")
invoice_number_label.grid(row=0, column=0,padx=5, pady=5)
invoice_number_entry = tk.Entry(frame)
invoice_number_entry.grid(row=1, column=0,padx=5, pady=5)
invoice_number_entry.insert(0, invoice_num)

invoice_date_label = tk.Label(frame, text="Invoice Date:")
invoice_date_label.grid(row=0, column=2, padx=5, pady=5)
invoice_date_entry = tk.Entry(frame)
invoice_date_entry.grid(row=1, column=2, padx=5, pady=5)
invoice_date_entry.insert(0, current_date)

first_name_label = tk.Label(frame,text="First Name:")
first_name_label.grid(row=3, column=0,padx=5, pady=5)
first_name_entry = tk.Entry(frame)
first_name_entry.grid(row=4, column=0,padx=5, pady=5)

last_name_label = tk.Label(frame,text="Last Name:")
last_name_label.grid(row=3, column=1,padx=5, pady=5)
last_name_entry = tk.Entry(frame)
last_name_entry.grid(row=4, column=1,padx=5, pady=5)

customer_phone_label = tk.Label(frame, text="Customer Phone:")
customer_phone_label.grid(row=3, column=2, padx=5, pady=5)
customer_phone_entry = tk.Entry(frame)
customer_phone_entry.grid(row=4, column=2, padx=5, pady=5)

qty_label = tk.Label(frame, text="Qty:")
qty_label.grid(row=5, column=0, padx=5, pady=5)
qty_entry = tk.Spinbox(frame, from_=1, to=1000)
qty_entry.grid(row=6, column=0, padx=5, pady=5)

description_label = tk.Label(frame, text="Description:")
description_label.grid(row=5, column=1, padx=5, pady=5)
description_entry = tk.Entry(frame)
description_entry.grid(row=6, column=1, padx=5, pady=5)

Product_Price_label = tk.Label(frame, text="Price:")
Product_Price_label.grid(row=5, column=2, padx=5, pady=5)
Product_Price_entry = tk.Spinbox(frame, from_=0.0, to=10000,increment=0.5)
Product_Price_entry.grid(row=6, column=2, padx=5, pady=5)

add_item_button = tkinter.Button(frame, text="Add item",command=add_item)
add_item_button.grid(row=7, column=2)

columns = ('Qty','desc','price','total')
tree=ttk.Treeview(frame, columns=columns, show="headings")
tree.heading('Qty', text='Qty')
tree.heading('desc', text='Description')
tree.heading('price', text='Unit Price')
tree.heading('total', text="Total")
tree.grid(row=8, column=0, columnspan=3, padx=20, pady=10)

Generate_Invoice_button = tkinter.Button(frame, text="Generate Invoice", command=generate_invoice)
Generate_Invoice_button.grid(row=9, column=0, columnspan=3, sticky="news",padx=20, pady=10)
New_Invoice_button = tkinter.Button(frame, text="New Invoice", command=new_invoice)
New_Invoice_button.grid(row=10, column=0, columnspan=3, sticky="news",padx=20, pady=10)

window.mainloop()
