from flask import Flask, render_template, request
import sqlite3

app = Flask(__name__)    #create Flask object

@app.route("/create") # , methods=['GET', 'POST'])
def create_story() -> None: #Adding page data from created webpage to data_subtopics table in subtopics.db
    args_to_get = ['story_id', 'story_contrib'] #Arguments to look for from create form
    data = {args : request.args[args] for args in args_to_get}
    db = sqlite3.connect("story.db") #open db if file exists, otherwise create db
    c = db.cursor()               #facilitate db ops -- you will use cursor to trigger db events
    try: c.execute("CREATE TABLE %s(id INTEGER PRIMARY KEY, user_id INTEGER, story_contrib TEXT)" % data['story_id'])
    except: return "This story already exists. Sorry, please choose another name!"
    story_add_helper(story_id, story_contrib)

@app.route("/add")
def story_add() -> None:
    args_to_get = ['story_id', 'story_contrib'] #Arguments to look for from create form
    data = {args : request.args[args] for args in args_to_get}
    story_add_helper(story_id, story_contrib)

def story_add_helper(story_id: str, story_contrib: str) -> str:
    user_id = str(getActiveUserID())
    db = sqlite3.connect("story.db") #open db if file exists, otherwise create db
    c = db.cursor()               #facilitate db ops -- you will use cursor to trigger db events
    c.execute("INSERT INTO %s(user_id, story_contrib) VALUES(%s, %s);" % (story_id, user_id, '"'+story_contrib+'"')) #Insert the values into the table
    c.execute("UPDATE user_table SET story_ids = story_ids || %s WHERE user_id = %s;" % ('",'+story_id+'"', user_id))
    render_story(add=True)
    return "Successfully contributed to story and rendered it"
#Create a render_story function that will accept boolean inputs of create and add  to @app.route("/render").
#If create=False, just render_template create.html that’ll output to the create_story function.
#If create=True and add=False, also search for a string input of story_title from form, grab story_contrib from the last row of the corresponding table and send it as input to render_template add.html which will output to the story_add function.
#If create=True and add=True, also search for a string input of story_title from form, grab story_contrib from all rows of the corresponding table and send it as a list as input to render_template story.html
@app.route("/render")
def render_story(create=True,add=True) -> str:
    pass
