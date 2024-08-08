# AUTOGENERATED! DO NOT EDIT! File to edit: 01_main.ipynb.

# %% auto 0
__all__ = ['app', 'Contact', 'index', 'contacts']

# %% 01_main.ipynb 2
import pandas as pd
from flask import Flask, redirect, request
from flask import render_template
import json

# %% 01_main.ipynb 6
class Contact(object):
    def __init__(self) -> None:
        self.db = pd.read_json('contactdb.json')

    def search(self, q):
        predicate_firstname = self.db['firstname'].str.lower().str.contains(q.lower())
        predicate_lastname = self.db['lastname'].str.lower().str.contains(q.lower())
        predicate_phone = self.db['phone'].str.lower().str.contains(q.lower())
        predicate_email= self.db['email'].str.lower().str.contains(q.lower())
        filter_df = self.db[predicate_firstname|predicate_lastname|predicate_phone|predicate_email]
        return filter_df.to_dict('records')

    def all(self):
        return self.db.to_dict('records')

# %% 01_main.ipynb 7
app = Flask(__name__)

# %% 01_main.ipynb 8
@app.get("/")
def index():
    return redirect("/contacts")

# %% 01_main.ipynb 9
@app.get("/contacts")
def contacts():
    search = request.args.get("q")
    contact_set = None
    if search is not None: contact_set = Contact().search(search)
    else: contact_set = Contact().all()
    # print(contact_set)
    return render_template("index.html", contact_set=contact_set)
