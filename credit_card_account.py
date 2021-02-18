# This program helps to create and log in through a credit card and PIN
import random
import sqlite3  # Imports the module sqlite for the creation and management of databases
import sys

conn = sqlite3.connect('card.s3db')  # Makes a connection with the database named 'card.s3db'
cur = conn.cursor()  # Creates a cursor object in order to execute SQL queries
# Creates the table 'card' in the database 'card.s3db'
# cur.execute('DROP TABLE card')
cur.execute("CREATE TABLE IF NOT EXISTS card ("
            "id INTEGER PRIMARY KEY, "
            "number TEXT, "
            "pin TEXT, "
            "balance INTEGER DEFAULT 0)""")
conn.commit()  # Commits once the query was executed


def luhn_checker(credit_input):
    """This function checks that the card number is valid according to the luhn algorithm."""
    luhn_list_original = list(str(credit_input))
    luhn_list_original = [int(i) for i in luhn_list_original]
    check_number = luhn_list_original.pop()  # the last number is removed and allocated in check_number
    luhn_list = [i * 2 if index % 2 == 0 else i for index, i in enumerate(reversed(luhn_list_original))]
    luhn_list = [i - 9 if i > 9 else i for i in luhn_list]
    if (sum(luhn_list) + check_number) % 10 != 0:
        return False
    else:
        return True


def luhn_generate_card(generated_card):
    """This function checks the first 15 generated digits in order to create a valid card number with luhn algorithm."""
    luhn_list_original = list(str(generated_card))
    luhn_list_original = [int(i) for i in luhn_list_original]
    luhn_list = [i * 2 if index % 2 == 0 else i for index, i in enumerate(reversed(luhn_list_original))]
    luhn_list = [i - 9 if i > 9 else i for i in luhn_list]
    if sum(luhn_list) % 10 != 0:
        luhn_list_original.append(10 - sum(luhn_list) % 10)
    else:
        luhn_list_original.append(0)
    luhn_list_string = [str(i) for i in luhn_list_original]
    single_string = "".join(luhn_list_string)
    return int(single_string)


def check_credit_card(credit_input):
    cur.execute("SELECT number FROM card WHERE number = ?", (credit_input,))
    conn.commit()
    row_card = cur.fetchone()
    if row_card is not None:
        if credit_input in row_card:
            return True
        else:
            return False
    else:
        return False


def check_pin(pin_input, credit_input):
    cur.execute("SELECT number, pin FROM card WHERE number = ? AND pin = ?", (credit_input, pin_input))
    conn.commit()
    #  row_pin is the pin number returned from the database
    row_pin = cur.fetchone()
    if row_pin is not None:
        if pin_input == row_pin[1]:
            return True
        else:
            return False
    else:
        return False


def update_balance(money_added, account_card):
    cur.execute("SELECT balance FROM card WHERE number = ?", (str(account_card),))
    conn.commit()
    bal = cur.fetchone()
    total_balance = bal[0] + money_added
    cur.execute("UPDATE card SET balance = ? WHERE number = ?", (total_balance, str(account_card)), )
    conn.commit()


def loggin_in(credit_login):
    print("You have successfully logged in!")
    second_menu_condition = True
    while second_menu_condition:
        print("1. Balance")
        print("2. Add income")
        print("3. Do transfer")
        print("4. Close account")
        print("5. Log out")
        print("0. Exit")
        try:
            action = int(input())
        except:
            print("Please, enter a number from the menu")
            continue
        if action == 1:
            cur.execute("SELECT balance FROM card WHERE number = ?", (str(credit_login),))
            conn.commit()
            bal = cur.fetchone()
            print("Balance: {}".format(bal[0]))
        elif action == 2:
            print("Enter income:")
            try:
                added_income = int(input())  # User enters the income to add to the balance
            except:
                print("Enter a value greater than zero.")
                continue
            update_balance(added_income, credit_login)
            print("Income was added!")
        elif action == 3:
            print("Enter card number")
            try:
                add_card_number = int(input())  # User enters the transfer's destination
            except:
                print("Enter a valid card number.")
                continue
            if add_card_number == credit_login:  # Checks that transfer's destination is not the same as the origin
                print("You can't transfer money to the same account!")
            elif not luhn_checker(add_card_number):
                print("Probably you made a mistake in the card number. Please try again!")
            elif not check_credit_card(str(add_card_number)):
                print("Such a card does not exist.")
            else:
                try:
                    print("Enter how much money you want to transfer:")
                except:
                    print("Please enter a valid number")
                    continue
                transfer_money = int(input())
                cur.execute("SELECT balance FROM card WHERE number = ?", (str(credit_login),))
                conn.commit()
                bal = cur.fetchone()
                if transfer_money > bal[0]:
                    print("Not enough money!")
                else:
                    update_balance(transfer_money, add_card_number)  # updates the receiver's account
                    update_balance(-transfer_money, credit_login)  # updates the sender's account
                    print("Success!")
        elif action == 4:
            cur.execute("DELETE FROM card WHERE number = ?", (str(credit_login),))
            conn.commit()
            print("The account has been closed!")
            second_menu_condition = False
        elif action == 5:
            print("You have logged out!")
            second_menu_condition = False
        elif action == 0:
            print("Bye!")
            sys.exit()  # Exits both menus (the logging and the principal menu)
        else:
            print("Select a valid number from the option list.")


def menu():
    initial_condition = True
    while initial_condition:
        print("1. Create an account")
        print("2. Log into account")
        print("0. Exit")
        try:
            option = int(input())
        except:
            print("Please, select a valid option")
            continue
        if option == 1:
            new_client = CreditCard()
            new_client.create_account()
            # Inserts the card number and pin into the database
            cur.execute('INSERT INTO card (number, pin) VALUES (?, ?)', (new_client.cardnumber, new_client.pin))
            conn.commit()
        elif option == 2:
            cur.execute('SELECT * FROM card')
            conn.commit()
            row = cur.fetchone()
            if row is None:
                print("You need first to create an account.")
                continue
            try:
                credit_login = int(input("Please, enter your card number: "))
                pin_login = int(input("Please, enter your PIN: "))
            except:
                print("Insert a valid card number or PIN")
                continue
            if check_credit_card(str(credit_login)) and check_pin(str(pin_login), str(credit_login)):
                loggin_in(credit_login)
            else:
                check_pin(pin_login, credit_login)
                print("Wrong card number or PIN!")
        elif option == 0:
            initial_condition = False
            print("Bye!")
        else:
            print("Select a valid number from the option list.")


class CreditCard:
    def __init__(self):
        self.cardnumber = None
        self.pin = None
        self.balance = 0

    def create_account(self):
        generated_card_number = 400000000000000 + random.randint(100000000, 999999999)
        self.cardnumber = luhn_generate_card(generated_card_number)
        print("Your card number:")
        print(self.cardnumber)
        self.pin = random.randint(1000, 9999)
        print("Your card PIN:")
        print(self.pin)


menu()
