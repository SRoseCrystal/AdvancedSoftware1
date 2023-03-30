import tkinter as tk
import json
import os
import base64
import uuid
from tkinter import messagebox
import tkinter.simpledialog as simpledialog 

def encrypt(data):
    """
    Encrypts the given string using base64 encoding.

    Args:
    - data (str): the string to be encrypted.

    Returns:
    - str: the encrypted string.
    """
    encoded = base64.b64encode(data.encode())
    return encoded.decode()

def decrypt(data):
    """
    Decrypts the given base64-encoded string.

    Args:
    - data (str): the base64-encoded string to be decrypted.

    Returns:
    - str: the decrypted string.
    """
    decoded = base64.b64decode(data.encode()).decode()
    return decoded

class Account:
    def __init__(self, id, name):
        """
        Constructor for the Account class.

        Args:
        - id (int): the account ID
        - name (str): the account holder's name
        """
        self.id = id
        self.name = name
        self.balance = 0

    def __str__(self):
        """
        Returns a string representation of the account.

        Returns:
        - str: a string containing the account ID, name, balance, and type
        """
        return f"ID: {self.id}, Name: {self.name}, Balance: {self.balance}, Type: {self.type}"

    def to_dict(self):
        """
        Returns a dictionary representation of the account.

        Returns:
        - dict: a dictionary containing the account's name and balance
        """
        return {
            "name": self.name,
            "balance": self.balance,
        }

class Bank:
    def __init__(self):
        # Initialize the class with an empty dictionary to store accounts
        # and a filename for saving and loading data
        self.accounts = {}
        self.filename = "accounts.json"
         # If the file exists, load the data from the file
        if os.path.exists(self.filename):
            # Read the encrypted data from the file
            encrypted_data = open(self.filename, "r").read()
            decrypted_data = decrypt(encrypted_data)
            # Parse the JSON data into a dictionary
            data = json.loads(decrypted_data)
            # Loop through the data and create account objects for each account

            for id, account_data in data.items():
                account = self._create_account(id, account_data)
                self.accounts[id] = account
                

    def _create_account(self, id, data):
         # Helper function to create an account object based on the account type
        type = data["type"]
        if type == "checking":
            account = CheckingAccount.from_dict(id, data)
        else:
            account = SavingsAccount.from_dict(id, data)

        return account

    def create_account(self, name, account_type):
        while True:
            # Generate a unique account ID using UUID library
            account_id = str(uuid.uuid4().int)[:8]
            if account_id not in self.accounts:
                break
         # Create a new account object based on the account type
        if account_type.lower() == "checking":
            account = CheckingAccount(account_id, name)
        else:
            account = SavingsAccount(account_id, name)

        self.accounts[account_id] = account
        self._save()

        return account_id

    def view_account(self, id):
         # Return the account object for a given account ID
        return self.accounts[id]

    def withdraw_cash(self, id, amount):
        account = self.accounts[id]
        account.balance -= amount
        self._save()

    def deposit(self, id, amount):
        account = self.accounts[id]
        account.balance += amount
        self._save()

    def transfer(self, from_id, to_id, amount):
        from_account = self.accounts[from_id]
        to_account = self.accounts[to_id]

        from_account.balance -= amount
        to_account.balance += amount

        self._save()

    def display_all_accounts(self):
        for account in self.accounts.values():
            print(account)

    def _save(self):
        # Helper function to save the account data to the file
        data = {}
        for id, account in self.accounts.items():
            data[id] = {
                "name": account.name,
                "type": account.type,
                "balance": account.balance,
                }
             # Convert the data to JSON format and encrypt it using a custom function
        data = json.dumps(data)
        encrypted_data = encrypt(data)

        open(self.filename, "w").write(encrypted_data)

class CheckingAccount(Account):
    def __init__(self, id, name):
        super().__init__(id, name)  # Initialize the parent class (Account) with id and name
        self.type = "checking"     # Add a new attribute to the object

    @classmethod
    def from_dict(cls, id, data):
        name = data["name"]        # Get the name from the data dictionary
        account = cls(id, name)    # Create a new instance of the CheckingAccount class with the given id and name
        account.balance = data["balance"]  # Set the balance of the account from the data dictionary
        return account             # Return the new account object

class SavingsAccount(Account):
    def __init__(self, id, name):
        super().__init__(id, name)
        self.type = "savings"

    @classmethod
    def from_dict(cls, id, data):
        name = data["name"]
        account = cls(id, name)
        account.balance = data["balance"]
        return account

class GUI(tk.Tk):
    def __init__(self, bank):
        super().__init__()
        self.bank = bank
        self._create_widgets()

    def _create_widgets(self):
        self.title("Banking App")

        frame = tk.Frame(self)
        frame.pack(side="top", fill="both", expand=True)


        btn_create = tk.Button(frame, text="Create Account", command=self._create_account)
        btn_create.pack(side="left", padx=10, pady=10)

        btn_view = tk.Button(frame, text="View Account", command=self._view_account)
        btn_view.pack(side="left", padx=10, pady=10)

        btn_withdraw = tk.Button(frame, text="Withdraw", command=self._withdraw)
        btn_withdraw.pack(side="left", padx=10, pady=10)

        btn_deposit = tk.Button(frame, text="Deposit", command=self._deposit)
        btn_deposit.pack(side="left", padx=10, pady=10)

        btn_transfer = tk.Button(frame, text="Transfer", command=self._transfer)
        btn_transfer.pack(side="left", padx=10, pady=10)

        btn_display_all = tk.Button(frame, text="Display All Accounts", command=self._display_all_accounts)
        btn_display_all.pack(side="left", padx=10, pady=10)


    def _create_account(self):
        name = self._get_input("Enter name:")
        type = self._get_input("Enter type (checking/savings):")
        id = self.bank.create_account(name, type)
        self._show_message(f"Account created with ID: {id}")

    def _view_account(self):
        id = self._get_input("Enter account ID:")
        account = self.get_account(id)
        if not account:
            self._show_message("Account not found.")
            return

        message = (
            f"ID: {account.id}\n"
            f"Name: {account.name}\n"
            f"Type: {account.type}\n"
            f"Balance: {account.balance}\n"
        )
        self._show_message(message)

    def _withdraw(self):
        id = self._get_input("Enter account ID:")
        amount = self._get_input("Enter amount:")

        result = self.bank.withdraw(id, amount)
        if not result:
            self._show_message("Operation failed.")
            return

        self._show_message("Withdraw successful.")

    def _deposit(self):
        id = self._get_input("Enter account ID:")
        amount = self._get_input("Enter amount:")

        result = self.bank.deposit(id, amount)
        if not result:
            self._show_message("Operation failed.")
            return

        self._show_message("Deposit successful.")

    def _transfer(self):
        id1 = self._get_input("Enter source account ID:")
        id2 = self._get_input("Enter destination account ID:")
        amount = self._get_input("Enter amount:")

        result = self.bank.transfer(id1, id2, amount)
        if not result:
            self._show_message("Operation failed.")
            return

        self._show_message("Transfer successful.")

    def _display_all_accounts(self):
        accounts = self.bank.display_all_accounts()
        if not accounts:
            self._show_message("No accounts found.")
            return

        message = ""
        for account in accounts:
            message += (
                f"ID: {account.id}\n"
                f"Name: {account.name}\n"
                f"Type: {account.type}\n"
                f"Balance: {account.balance}\n\n"
            )
        self._show_message(message)


    def _get_input(self, prompt):
        return simpledialog.askstring("Input", prompt, parent=self)

    def _show_message(self, message):
        messagebox.showinfo("Message", message, parent=self)

if __name__ == "__main__":
    bank = Bank()
    bank_gui = GUI(bank)
    bank_gui.mainloop()

