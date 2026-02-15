import tkinter as tk
from tkinter import messagebox, ttk
from tkcalendar import Calendar
import csv
from datetime import datetime

# Function to read CSV file and search for entries
def search_entries():
    # Get the search inputs (user input or selected date)
    initials = entry_initials.get().lower()  # Convert to lowercase to make it case-insensitive
    device_id = entry_device_id.get().lower()
    destination = entry_destination.get().lower()
#    date_str = cal.get_date()
#    print(date_str)    
    # Convert date to the same format as saved in the CSV (e.g., 'YYYY-MM-DD')
#    try:
#        date_obj = datetime.strptime(date_str, "%Y/%m/%d").date()
#    except ValueError:
#        messagebox.showerror("Date Error", "Invalid date format!")
#        return
#    print(date_obj)
    # Open CSV file and search for matching entries
    results = []
    with open('entries.csv', mode='r', newline='') as file:
        reader = csv.reader(file)
        for row in reader:
            if row:
                saved_initials = row[0].lower()
                saved_device_id = row[1].lower()
                saved_destination = row[2].lower()
                saved_timestamp = row[3]
#                saved_date = datetime.strptime(saved_timestamp, "%Y-m%-%d %H:%M:%S").date()

                # Match the search criteria
                if (initials in saved_initials or
                        device_id in saved_device_id or
                        destination in saved_destination):
#                        saved_date == date_obj):
                    results.append(row)

    # Display results
    if results:
        display_results(results)
    else:
        messagebox.showinfo("No Results", "No matching entries found!")


# Function to display results in the GUI
def display_results(results):
    # Clear the previous results
    for row in results_treeview.get_children():
        results_treeview.delete(row)
    
    # Insert the results into the treeview
    for row in results:
        results_treeview.insert("", tk.END, values=row)


def clear_results():
    # Clear the search input fields
    entry_initials.delete(0, tk.END)
    entry_device_id.delete(0, tk.END)
    entry_destination.delete(0, tk.END)
    
    # Clear the date picker (optional)
#    cal.get_date(datetime.today().strftime("%d/%m/%y"))
        
    # Clear the previous results in the treeview
    for row in results_treeview.get_children():
        results_treeview.delete(row)


# Setting up the Tkinter window
root = tk.Tk()
root.title("Search Entries")

# Create labels and entry widgets
label_initials = tk.Label(root, text="Enter Initials:")
label_initials.grid(row=0, column=0, padx=10, pady=10)
entry_initials = tk.Entry(root)
entry_initials.grid(row=0, column=1, padx=10, pady=10)

label_device_id = tk.Label(root, text="Enter Device ID:")
label_device_id.grid(row=1, column=0, padx=10, pady=10)
entry_device_id = tk.Entry(root)
entry_device_id.grid(row=1, column=1, padx=10, pady=10)

label_destination = tk.Label(root, text="Enter Destination:")
label_destination.grid(row=2, column=0, padx=10, pady=10)
entry_destination = tk.Entry(root)
entry_destination.grid(row=2, column=1, padx=10, pady=10)

# Date picker (using tkcalendar)
label_date = tk.Label(root, text="Select Date:")
label_date.grid(row=3, column=0, padx=10, pady=10)
cal = Calendar(root, selectmode="day", date_pattern="dd/mm/yy")
cal.grid(row=3, column=1, padx=10, pady=10)

# Search button
search_button = tk.Button(root, text="Search", command=search_entries)
search_button.grid(row=4, column=0, columnspan=2, pady=20)

# Clear results button
clear_button = tk.Button(root, text="Clear Results", command=clear_results)
clear_button.grid(row=4, column=1, padx=10, pady=20)

# Treeview to display search results
columns = ["Initials", "Device ID", "Destination", "Timestamp"]
results_treeview = ttk.Treeview(root, columns=columns, show="headings")
results_treeview.grid(row=5, column=0, columnspan=2, padx=10, pady=10)

# Define the columns of the treeview
for col in columns:
    results_treeview.heading(col, text=col)
    results_treeview.column(col, width=150)

# Run the Tkinter event loop
root.mainloop()
