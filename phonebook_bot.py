"""
    Assistant bot for contact management and birthday tracking with data persistence.

    This bot facilitates easy contact and birthday management with various commands, providing colored outputs for user feedback, and it saves contact data for future sessions.

    Main functionalities:
    - 'add <name> <phone>': adds a new contact with the specified name and phone number, or updates an existing contact by adding a new phone number.
    - 'change <name> <old phone> <new phone>': changes the specified phone number of an existing contact.
    - 'phone <name>': displays all phone numbers associated with the specified contact.
    - 'all': lists all contacts in the address book with their details.
    - 'add-birthday <name> <birthday>': adds a birthday to a contact (format: 'DD.MM.YYYY').
    - 'show-birthday <name>': shows the birthday for a specific contact.
    - 'birthdays': displays contacts with upcoming birthdays within the next week.
    - 'hello': responds with a greeting message.
    - 'info': shows a list of available commands and their descriptions.
    - 'close' or 'exit': exits the bot, saving all contact data.

    Data persistence:
    - the bot saves data automatically upon exit to ensure all changes are retained for the next session.
    - contacts and birthdays are stored in a file ('addressbook.pkl') in binary format using the `pickle` library, and they are loaded upon starting the bot to maintain continuity.

    Error handling:
    - common errors such as missing arguments, invalid inputs, and non-existent contacts are handled with the `input_error` decorator.
    - managed errors include KeyError, ValueError, and IndexError, preventing application crashes and providing user-friendly messages.
    - unexpected errors are intercepted and reported with a general message, ensuring continuous bot operation.

    Returns:
    None: the bot outputs results directly to the console, including feedback on command execution and error messages.

    Additional Notes:
    - the bot uses the `colorama` library to apply color-coded output for clearer user interactions, differentiating success messages, errors, and informational feedback.
    - the bot operates in a loop, processing user commands until the user inputs 'close' or 'exit'.
"""



from collections import UserDict
from datetime import datetime
import re
from datetime import datetime, timedelta
from colorama import Fore
import pickle


class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)
    

class Name(Field):
		pass


class Phone(Field):
    def __init__(self, value):
        if re.match(r'^\d{10}$', value):
            super().__init__(value)
        else:
            raise ValueError("Invalid phone number. The number must consist of 10 digits.")


class Birthday(Field):
    def __init__(self, value):

        if re.match(r'^\d{2}\.\d{2}\.\d{4}$', value):
            try:
                birthday = datetime.strptime(value, '%d.%m.%Y').date()
            except:
                raise ValueError("Invalid date format. Ensure it exist.")
            
            super().__init__(birthday)

        else:
            raise ValueError("Invalid date format. Use the 'DD.MM.YYYY' format.")
        

class Record:
    def __init__(self, name):
        self.name = name
        self.phones = []
        self.birthday = None

    def __str__(self):
        phones = '; '.join(str(p) for p in self.phones)
        birthday_str = f", birthday: {self.birthday}" if self.birthday else ""
        return f"Contact name: {self.name}, phones: {phones}{birthday_str}"

    def add_phone(self, phone: Phone):
            self.phones.append(phone)
            return (f"Phone {phone} added to contact {self.name}")
        
    def remove_phone(self, phone):
        self.phones = [p for p in self.phones if p == phone]
        return (f"Phone {phone} deleted")
    
    def edit_phone(self, old_phone, new_phone):
        for index, phone in enumerate(self.phones):
            if phone.value == old_phone:
                self.phones[index] = Phone(new_phone)
                return f"Phone {old_phone} changed to {new_phone}"
        return f"Phone {old_phone} not found"

    def find_phone(self, phone):
        for p in self.phones:
            if p == phone:
                return p
            elif p not in self.phones:
                return (f"Phone {phone} not found")

    def add_birthday(self, birthday: Birthday):
        self.birthday = birthday
        return (f"{self.name}'s birthday on {birthday} added")
       

class AddressBook(UserDict):
    def add_record(self, record):
        self.data[str(record.name)] = record
        return (f"Contact {record.name} added to address book")

    def find(self, name):
        return self.data.get(name, None)


    def delete(self, name):
        if name in self.data:
            del self.data[name]
            return (f"Contact {name} deleted")
        else:
            return (f"Contact {name} not found")
    
    def get_upcoming_birthdays(self):
        congrats_list = []
        today = datetime.now().date()

        for contact in self.data.values():
            if contact.birthday:
                birthday = datetime.strptime(contact.birthday, "%d.%m.%Y").date()
                birthday_this_year = birthday.replace(year=today.year)

                if birthday_this_year < today:
                    birthday_this_year = birthday.replace(year=today.year + 1)
            
                days_until_birthday = (birthday_this_year - today).days

                if 0 <= days_until_birthday <= 7:

                    if birthday_this_year.weekday() == 5:
                        birthday_this_year += timedelta(days=2)
                    elif birthday_this_year.weekday() == 6:
                        birthday_this_year += timedelta(days=1)

                    congrats_list.append({ contact.name: birthday_this_year.strftime("%d.%m.%Y") })
            

        if len(congrats_list) > 0:
            return congrats_list
        else:
            return None

        





def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except KeyError as e:
            return e
        except ValueError as e:
            return e
        except IndexError as e:
            return e
        except Exception as e:
            return f'An unexpected error occurred: {e}. Please try again.'
    return inner

def parse_input(user_input):
    if not user_input.strip():
        return None, []
    
    cmd, *args = user_input.split()
    cmd = cmd.strip().lower()
    return cmd, *args


def colored_output(phrase):
    return Fore.GREEN + phrase + Fore.RESET

def colored_error(phrase):
    return Fore.RED + phrase + Fore.RESET

def colored_info(phrase):
    return Fore.YELLOW + phrase + Fore.RESET





@input_error
def add_contact(args, book: AddressBook):
    name, phone = args
    record = book.find(name)
    
    if record is None:
        record = Record(name)
        book.add_record(record)
        message = colored_output(f"Contact {record.name} added to address book.")
    else:
        message = colored_output(f"Contact {record.name} updated.")

    if phone:
        record.add_phone(Phone(phone))

    return message

@input_error
def change_contact(args, book: AddressBook):
    name, old_phone, new_phone = args
    record = book.find(name)

    if record is None:
        raise IndexError(colored_error(f"Contact '{name}' not found. Use 'add' to create it."))
    
    result = record.edit_phone(old_phone, new_phone)

    return colored_output(result)

@input_error
def show_phone(args, book: AddressBook):
    if not args:
        raise ValueError(colored_error("No contact name provided."))
    
    name = args[0]
    record = book.find(name)
    if record:
        phones = '; '.join(str(phone) for phone in record.phones)
        return colored_output(f"Contact '{name}' phones: {phones}")
    else:
        raise IndexError(colored_error(f"Contact '{name}' not found."))
    
@input_error
def show_all(book: AddressBook):
    if not book.data:
        raise ValueError(colored_error("No contacts available."))
    
    result = [f"{record}" for _, record in book.data.items()]
    return colored_output('\n'.join(result))

@input_error
def add_birthday(args, book: AddressBook):
    name, birthday = args
    record = book.find(name)
    if not record:
        raise IndexError(colored_error(f"Contact '{name}' not found. Use 'add' to create it."))
    
    result = record.add_birthday(birthday)
    return colored_output(result)

@input_error
def show_birthday(args, book: AddressBook):
    name, *_ = args
    record = book.find(name)
    if not record:
        raise IndexError(colored_error(f"Contact '{name}' not found. Use 'add' to create it."))
    
    result = f"{record.name} has Birthday on {record.birthday}"
    return colored_output(result)
    
@input_error
def show_all_birthdays(book: AddressBook):
    if not book.data:
        raise ValueError(colored_error("No contacts available."))
    
    result = book.get_upcoming_birthdays()

    if not result:
        return colored_output("No birthdays soon.")
    
    formatted_result = [f'{name}: {date}' for birthday_dict in result for name, date in birthday_dict.items()]
    return colored_output('\n'.join(formatted_result))
    
    

def show_info():
    result = [
        colored_output('add <name> <phone>') + ': adds a new contact with the name and phone number, or adds a phone number to an existing contact (e.g., add John 123456789)',
        colored_output('change <name> <old phone> <new phone>') + ': changes the phone number of an existing contact (e.g., change John 123456789 987654321)',
        colored_output('phone <name>') + ': shows the phone number(s) of the specified contact (e.g., phone John)',
        colored_output('all') + ': shows all contacts in your address book',
        colored_output('add-birthday <name> <birthday>') + ': adds a birthday for the specified contact (e.g., add-birthday John 01.01.1990)',
        colored_output('show-birthday <name>') + ': shows the birthday of the specified contact (e.g., show-birthday John)',
        colored_output('birthdays') + ': shows upcoming birthdays within the next week',
        colored_output('hello') + ': receive a greeting from the bot',
        colored_output('info') + ': displays the list of available commands',
        colored_output('close or exit') + ': exits the application'
    ]
    return colored_info("Available commands:\n" + '\n'.join(result))




def save_data(book, filename="addressbook.pkl"):
    with open(filename, 'wb') as f:
        pickle.dump(book, f)

def load_data(filename="addressbook.pkl"):
    try:
        with open(filename, 'rb') as f:
            return pickle.load(f)
    except FileNotFoundError:
        return AddressBook()




def main():
    book = load_data()
    print(("Welcome to the assistant bot!"))
    while True:
        user_input = input("Enter a command: ")
        command, *args = parse_input(user_input)

        if command in ["close", "exit"]:
            save_data(book)
            print(colored_info("Good bye!" + Fore.RESET))
            break

        elif command == "hello":
            print(colored_info("How can I help you?" + Fore.RESET)) 

        elif command == "info":
            print(show_info()) 

        elif command == "add":
            print(add_contact(args, book)) 

        elif command == "change":
            print(change_contact(args, book)) 

        elif command == "phone":
            print(show_phone(args, book)) 

        elif command == "all":
            print(show_all(book)) 

        elif command == "add-birthday":
            print(add_birthday(args, book))

        elif command == "show-birthday":
            print(show_birthday(args, book)) 

        elif command == "birthdays":
            print(show_all_birthdays(book))

        else:
            print(colored_error("Invalid command."))

if __name__ == "__main__":
    main()