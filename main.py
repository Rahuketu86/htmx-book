# AUTOGENERATED! DO NOT EDIT! File to edit: 01_main.ipynb.

# %% auto 0
__all__ = ['app', 'index', 'contacts', 'view', 'edit', 'delete', 'delete_htmx', 'contact_new_get', 'contact_new',
           'contact_email_get']

# %% 01_main.ipynb 2
import pandas as pd
from flask import Flask, redirect, request, render_template, flash
from datamodel import Contact, Contacts, ContactErrors
import re

# %% 01_main.ipynb 4
app = Flask(__name__)
app.secret_key = "superdupersecret"


# %% 01_main.ipynb 5
@app.get("/")
def index():
    return redirect("/contacts")

# %% 01_main.ipynb 6
@app.get("/contacts")
def contacts():
    search = request.args.get("q")
    contact_set = None
    if search is not None: contact_set = Contacts().search(search)
    else: contact_set = Contacts().all()
    return render_template("index.html", contact_set=contact_set)

# %% 01_main.ipynb 8
@app.get("/contacts/<int:id>")
def view(id:int):
    return render_template("view.html", contact=Contacts().get(id))

# %% 01_main.ipynb 11
@app.route("/contacts/<int:id>/edit", methods=['GET', 'POST'])
def edit(id):
    if request.method == 'GET':
        c_dict = Contacts().get(id)
        c = Contact()
        c.from_contacts_dict(c_dict)
        c.check_valid(duplicate_ok=True)
        return render_template('edit.html', contact=c)
    else:
        c_dict = Contacts().get(id)
        c = Contact()
        c.from_contacts_dict(c_dict)
        c.firstname = request.form['firstname']
        c.lastname = request.form['lastname']
        c.phone=request.form['phone']
        c.email=request.form['email']
        c.check_valid(duplicate_ok=False)
        if c.commit(duplicate_ok=False):
            flash("Updated Contract")
            return redirect("/contacts/"+str(id))
        else: return render_template('edit.html', contact=c)

# %% 01_main.ipynb 12
@app.route("/contacts/<int:id>/delete", methods=['POST'])
def delete(id):
    Contacts().delete(id)
    flash("Contract Deleted")
    return redirect("/contacts")

# %% 01_main.ipynb 13
@app.route("/contacts/<int:id>", methods=['DELETE'])
def delete_htmx(id):
    Contacts().delete(id)
    flash("Contract Deleted")
    return redirect("/contacts", 303)

# %% 01_main.ipynb 15
@app.route("/contacts/new", methods=['GET'])
def contact_new_get():
    return render_template('new.html', contact=Contact(firstname=None, lastname=None, phone=None, email=None))

# %% 01_main.ipynb 16
@app.route("/contacts/new", methods=['POST'])
def contact_new():
    c = Contact(firstname=request.form['firstname'], 
                lastname=request.form['lastname'],
                phone=request.form['phone'],
                email=request.form['email'])
    c.check_valid(duplicate_ok=False)
    if c.commit(duplicate_ok=False):
        flash("New contract created")
        return redirect("/contacts")
    else: 
        print(c)
        return render_template('new.html', contact=c)

# %% 01_main.ipynb 17
@app.get("/contacts/<int:id>/email")
def contact_email_get(id:int=0):
    c_dict = Contacts().get(id)
    c = Contact()
    c.from_contacts_dict(c_dict, validate=False)
    c.email = request.arg.get('email')
    c.validate_contact_email(duplicate_ok=False)
    return c.errors.email
