import tkinter as tk
from tkinter import messagebox
import bank_backend as bb

def create_account():
    try:
        acc = bb.Account()
        acc.accNo = int(entry_acc_no.get())
        acc.name = entry_name.get()
        acc.type = acc_type_var.get()
        acc.deposit = int(entry_amount.get())

        if acc.type == 'S' and acc.deposit < 500:
            raise ValueError("Minimum deposit for Saving is 500")
        if acc.type == 'C' and acc.deposit < 1000:
            raise ValueError("Minimum deposit for Current is 1000")

        bb.writeAccountsFile(acc)
        messagebox.showinfo("Success", "Account created successfully!")
    except Exception as e:
        messagebox.showerror("Error", str(e))

def display_accounts():
    output_text.delete(1.0, tk.END)
    try:
        file = bb.pathlib.Path("accounts.data")
        if file.exists():
            with open('accounts.data', 'rb') as f:
                accounts = bb.pickle.load(f)
                for acc in accounts:
                    output_text.insert(tk.END, f"Acc No: {acc.accNo}, Name: {acc.name}, Type: {acc.type}, Balance: {acc.deposit}\n")
        else:
            output_text.insert(tk.END, "No accounts found.")
    except Exception as e:
        output_text.insert(tk.END, str(e))

# GUI Setup
root = tk.Tk()
root.title("Bank Management System")

# Entry Widgets
tk.Label(root, text="Account No").grid(row=0, column=0)
entry_acc_no = tk.Entry(root)
entry_acc_no.grid(row=0, column=1)

tk.Label(root, text="Name").grid(row=1, column=0)
entry_name = tk.Entry(root)
entry_name.grid(row=1, column=1)

tk.Label(root, text="Account Type").grid(row=2, column=0)
acc_type_var = tk.StringVar()
tk.Radiobutton(root, text="Saving", variable=acc_type_var, value='S').grid(row=2, column=1, sticky="w")
tk.Radiobutton(root, text="Current", variable=acc_type_var, value='C').grid(row=2, column=2, sticky="w")
acc_type_var.set("S")

tk.Label(root, text="Initial Amount").grid(row=3, column=0)
entry_amount = tk.Entry(root)
entry_amount.grid(row=3, column=1)

# Buttons
tk.Button(root, text="Create Account", command=create_account).grid(row=4, column=0, pady=10)
tk.Button(root, text="Show All Accounts", command=display_accounts).grid(row=4, column=1, pady=10)

# Output Box
output_text = tk.Text(root, height=10, width=70)
output_text.grid(row=5, column=0, columnspan=3)

root.mainloop()
