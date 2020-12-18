from flask import Flask, render_template, request
from create import add_page_data

app = Flask(__name__)    #create Flask object

@app.route("/create") # , methods=['GET', 'POST'])
def create_page() -> None: #Adding page data from created webpage to data_subtopics table in subtopics.db
    args_to_get = ['entry_title', 'entry', 'contributor_name'] #Arguments to look for from create form
    data = {args : request.args[args] for args in args_to_get}
    console_message = add_page_data(data)
    print(console_message) #Error or Success Message
