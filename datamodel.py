# AUTOGENERATED! DO NOT EDIT! File to edit: 00_datamodel.ipynb.

# %% auto 0
__all__ = ['email_regex', 'phone_regex', 'ContactErrors', 'validate_email', 'check_duplicates', 'validate_phone_number',
           'Contacts', 'Contact']

# %% 00_datamodel.ipynb 2
import pandas as pd
from dataclasses import dataclass, field
import re

# %% 00_datamodel.ipynb 8
@dataclass
class ContactErrors:
    firstname:str = None
    lastname:str = None
    phone:str = None
    email:str = None


# %% 00_datamodel.ipynb 10
# Regular expression pattern for validating email
email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
phone_regex =  r'^(?:\d{7,}|\d{1,}-\d{1,}-?\d{5,}|\d+-\d{7,}|\d{3}-\d{4})$'

# %% 00_datamodel.ipynb 11
# Function to validate email
def validate_email(email):
    if re.match(email_regex, email): return True
    else: return False

# %% 00_datamodel.ipynb 12
def check_duplicates(elem, ls):
   return elem in ls

# %% 00_datamodel.ipynb 13
# Function to validate phone number
def validate_phone_number(phone_number):
    if re.match(phone_regex, phone_number): return True
    else: return False

# %% 00_datamodel.ipynb 16
class Contacts(object):
    def __init__(self) -> None:
        self.refresh()

    def search(self, q):
        predicate_firstname = self.db['firstname'].str.lower().str.contains(q.lower())
        predicate_lastname = self.db['lastname'].str.lower().str.contains(q.lower())
        predicate_phone = self.db['phone'].str.lower().str.contains(q.lower())
        predicate_email= self.db['email'].str.lower().str.contains(q.lower())
        filter_df = self.db[predicate_firstname|predicate_lastname|predicate_phone|predicate_email]
        return filter_df.to_dict('records')
    
    def refresh(self):
        self.file_path = 'contactdb.json'
        self.db = pd.read_json(self.file_path)

    def all(self):
        return self.db.to_dict('records')
    
    def get(self, id):
        contact = self.db[self.db['id']==id]
        return contact.to_dict('records')[0]
    

    def add_or_edit(self, id, firstname, lastname, phone, email):
        a={'firstname': firstname,
           'lastname': lastname,
           'phone':phone,
           'email': email,
           'id': id}
        id_idx = None
        # print("id is None" if id is None else "id is ok")
        if id is None: id_idx = self.db['id'].max()+1; a['id'] = id_idx
        else: id_idx = self.db[self.db['id']==id].index
        # print(id_idx)
        self.db.loc[id_idx, a.keys()] = a.values()
        # print(self.db.tail(1))
        self.db.to_json(self.file_path, orient='records')
        self.refresh()

    def delete(self, id):
        id_idx = self.db[self.db['id']==id].index
        self.db.drop(index=id_idx, inplace=True, errors='raise')
        self.db.to_json(self.file_path, orient='records')
        self.refresh()

    def get_emails(self):
        return self.db['email'].tolist()

# %% 00_datamodel.ipynb 17
@dataclass
class Contact:
    firstname:str=None
    lastname:str=None
    phone:str=None
    email:str=None
    id: int =None
    errors:ContactErrors = field(default_factory=lambda: ContactErrors())
    is_valid:bool=True

    def validate_contact_email(self, duplicate_ok):
        if self.email is None or self.email == "":
            self.is_valid = False
            self.errors.email= "Email is empty"
        elif not validate_email(self.email):
            self.is_valid = False
            self.errors.email= "Format email not correct"
        elif not duplicate_ok:
            if check_duplicates(self.email, Contacts().get_emails()):
                self.is_valid = False
                self.errors.email= "Duplicated email"
        else: pass


    def from_contacts_dict(self, c, validate=True, duplicate_ok=True):
        self.firstname = c['firstname']
        self.lastname = c['lastname']
        self.phone = c['phone']
        self.email = c['email']
        self.id = c['id']
        if validate:
            self.check_valid(duplicate_ok=duplicate_ok)

    def check_valid(self, duplicate_ok=False):
        self.is_valid = True
        if self.firstname is None or self.firstname == "":
            self.is_valid = False
            self.errors.firstname = "Firstname is empty"
        
        if self.lastname is None or self.lastname == "":
            self.is_valid = False
            self.errors.lastname = "Lastname is empty"
        
        if self.phone is None or self.phone == "":
            self.is_valid = False
            self.errors.phone= "Phone is empty"
        elif not validate_phone_number(self.phone):
            self.is_valid = False
            self.errors.phone= "Format phone not correct"
        else: pass

        self.validate_contact_email(duplicate_ok=duplicate_ok)

    def commit(self, duplicate_ok=True):
        self.check_valid(duplicate_ok=duplicate_ok)
        if not self.is_valid: return False
        else:
            db = Contacts()
            print("None" if self.id is None else "ok")
            db.add_or_edit(id=self.id,
                    firstname = self.firstname, 
                    lastname = self.lastname, 
                    phone=self.phone, 
                    email=self.email)
            return True

    def __repr__(self) -> str:
        a= [[self.firstname, self.errors.firstname],
            [self.lastname, self.errors.lastname],
            [self.phone, self.errors.phone],
            [self.email, self.errors.email],
            [self.is_valid, ""]]
        return f"Contact{str(a)}"
        
