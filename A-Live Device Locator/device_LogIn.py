import tkinter as tk
from tkinter import messagebox
import csv
from datetime import datetime


# Function to save input to CSV file
def save_to_csv(initials, device_id, destination):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    data = [initials, device_id, destination, timestamp]

    # Open the CSV file and write the data
    with open('returns.csv', mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(data)


# Function to handle form submission
def submit_entry():
    initials = entry_initials.get()
    device_id = entry_device_id.get()
    destination = entry_destination.get()

    # Check if all fields are filled
    if not initials or not device_id or not destination:
        messagebox.showerror("Input Error", "All fields are required!")
        return

    # Save the entry to the CSV
    save_to_csv(initials, device_id, destination)

    # Clear the entries
    entry_initials.delete(0, tk.END)
    entry_device_id.delete(0, tk.END)
    entry_destination.delete(0, tk.END)

    # Inform the user that the entry was saved
    messagebox.showinfo("Success", "Entry saved successfully!")


# Setting up the Tkinter window
root = tk.Tk()
root.title("User Entry Form")

# Create labels and entry widgets
label_initials = tk.Label(root, text="Enter Initials:")
label_initials.grid(row=0, column=0, padx=10, pady=10)
entry_initials = tk.Entry(root)
entry_initials.grid(row=0, column=1, padx=10, pady=10)

label_device_id = tk.Label(root, text="Enter Device ID:")
label_device_id.grid(row=1, column=0, padx=10, pady=10)
entry_device_id = tk.Entry(root)
entry_device_id.grid(row=1, column=1, padx=10, pady=10)

label_destination = tk.Label(root, text="Location Returned From:")
label_destination.grid(row=2, column=0, padx=10, pady=10)
entry_destination = tk.Entry(root)
entry_destination.grid(row=2, column=1, padx=10, pady=10)

# Submit button
submit_button = tk.Button(root, text="Submit", command=submit_entry)
submit_button.grid(row=3, column=0, columnspan=2, pady=20)

# Run the Tkinter event loop
root.mainloop()
