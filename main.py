# AUTOGENERATED! DO NOT EDIT! File to edit: 01_main.ipynb.

# %% auto 0
__all__ = ['email_regex', 'phone_regex', 'app', 'ContactErrors', 'validate_email', 'validate_phone_number', 'Contact', 'Contacts',
           'index', 'contacts', 'view', 'edit', 'delete', 'delete_htmx', 'contact_new_get', 'contact_new']

# %% 01_main.ipynb 2
import pandas as pd
from flask import Flask, redirect, request, render_template, flash
from dataclasses import dataclass
import re

# %% 01_main.ipynb 8
class ContactErrors:
    firstname:str = "Error in Firstname"
    lastname:str = "Error in Lastname"
    phone:str = "Error in Phone"
    email:str = "Error in Email"

# %% 01_main.ipynb 10
# Regular expression pattern for validating email
email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
phone_regex =  r'^(?:\d{7,}|\d{1,}-\d{1,}-?\d{5,}|\d+-\d{7,}|\d{3}-\d{4})$'

# %% 01_main.ipynb 11
# Function to validate email
def validate_email(email):
    if re.match(email_regex, email): return True
    else: return False

# %% 01_main.ipynb 12
# Function to validate phone number
def validate_phone_number(phone_number):
    if re.match(phone_regex, phone_number): return True
    else: return False

# %% 01_main.ipynb 15
@dataclass
class Contact:
    firstname:str=None
    lastname:str=None
    phone:str=None
    email:str=None
    id: int =None
    errors:ContactErrors = ContactErrors()

    def from_contacts_dict(self, c):
        self.firstname = c['firstname']
        self.lastname = c['lastname']
        self.phone = c['phone']
        self.email = c['email']
        self.id = c['id']

    def save(self):
        if not self.validate(): return False
        else: 
            db = Contacts()
            db.add(firstname = self.firstname, 
                   lastname = self.lastname, 
                   phone=self.phone, 
                   email=self.email)
            return True
        
    def edit(self):
        if not self.validate(): return False
        else:
            db = Contacts()
            db.edit(id=self.id,
                    firstname = self.firstname, 
                    lastname = self.lastname, 
                    phone=self.phone, 
                    email=self.email)
            return True


    def validate(self):
        if not self._check_nones([self.firstname, self.lastname, self.phone, self.email]): return False
        elif not validate_email(self.email): return False
        elif not validate_phone_number(self.phone): return False
        else:
            # print("Validated") 
            return True

    def _check_nones(self, ls):
        for e in ls: 
            # print(e)
            if e is None or e == "": 
                # print(e, "Noness or empty")
                return False
        return True
        

# %% 01_main.ipynb 17
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
        # print(contact)
        return contact.to_dict('records')[0]
    
    def add(self, firstname, lastname, phone, email):
        a={'firstname': firstname,
           'lastname': lastname,
           'phone':phone,
           'email': email}
        a['id'] = self.db['id'].max()+1
        self.db.loc[len(self.db), a.keys()] = a.values()
        self.db.to_json(self.file_path, orient='records')
        self.refresh()

    def delete(self, id):
        id_idx = self.db[self.db['id']==id].index
        self.db.drop(index=id_idx, inplace=True, errors='raise')
        self.db.to_json(self.file_path, orient='records')
        self.refresh()

    def edit(self, id, firstname, lastname, phone, email):
        a={'firstname': firstname,
           'lastname': lastname,
           'phone':phone,
           'email': email,
           'id': id}
        id_idx = self.db[self.db['id']==id].index
        self.db.loc[id_idx, a.keys()] = a.values()
        self.db.to_json(self.file_path, orient='records')
        self.refresh()


# %% 01_main.ipynb 21
app = Flask(__name__)
app.secret_key = "superdupersecret"


# %% 01_main.ipynb 22
@app.get("/")
def index():
    return redirect("/contacts")

# %% 01_main.ipynb 23
@app.get("/contacts")
def contacts():
    search = request.args.get("q")
    contact_set = None
    if search is not None: contact_set = Contacts().search(search)
    else: contact_set = Contacts().all()
    # print(contact_set)
    return render_template("index.html", contact_set=contact_set)

# %% 01_main.ipynb 25
@app.get("/contacts/<int:id>")
def view(id:int):
    return render_template("view.html", contact=Contacts().get(id))

# %% 01_main.ipynb 28
@app.route("/contacts/<int:id>/edit", methods=['GET', 'POST'])
def edit(id):
    if request.method == 'GET':
        c_dict = Contacts().get(id)
        return render_template('edit.html', contact=c_dict)
    else:
        c_dict = Contacts().get(id)
        c = Contact()
        c.from_contacts_dict(c_dict)
        c.firstname = request.form['firstname']
        c.lastname = request.form['lastname']
        c.phone=request.form['phone']
        c.email=request.form['email']
        if c.edit():
            flash("Updated Contract")
            return redirect("/contacts/"+str(id))
        else: return render_template('edit.html', contact=c_dict)

# %% 01_main.ipynb 29
@app.route("/contacts/<int:id>/delete", methods=['POST'])
def delete(id):
    Contacts().delete(id)
    flash("Contract Deleted")
    return redirect("/contacts")

# %% 01_main.ipynb 30
@app.route("/contacts/<int:id>", methods=['DELETE'])
def delete_htmx(id):
    Contacts().delete(id)
    flash("Contract Deleted")
    return redirect("/contacts", 303)

# %% 01_main.ipynb 32
@app.route("/contacts/new", methods=['GET'])
def contact_new_get():
    return render_template('new.html', contact=Contact(firstname=None, lastname=None, phone=None, email=None))

# %% 01_main.ipynb 33
@app.route("/contacts/new", methods=['POST'])
def contact_new():
    c = Contact(firstname=request.form['firstname'], 
                lastname=request.form['lastname'],
                phone=request.form['phone'],
                email=request.form['email'])
    if c.save():
        flash("New contract created")
        return redirect("/contacts")
    else: return render_template('new.html', contact=c)
