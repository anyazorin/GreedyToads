from flask import Flask, render_template, request
import sqlite3

app = Flask(__name__)    #create Flask object

db = sqlite3.connect("story.db") #open db if file exists, otherwise create db
c = db.cursor()               #facilitate db ops -- you will use cursor to trigger db events

@app.route("/create") # , methods=['GET', 'POST'])
def create_story() -> None: #Adding page data from created webpage to data_subtopics table in subtopics.db
    args_to_get = ['story_id', 'story_contrib'] #Arguments to look for from create form
    data = {args : request.args[args] for args in args_to_get}
    try: c.execute("CREATE TABLE %s(id INTEGER PRIMARY KEY, user_id INTEGER, story_contrib TEXT)" % data['story_id'])
    except: return "This story already exists. Sorry, please choose another name!"
    c.commit()
    story_add_helper(story_id, story_contrib)

@app.route("/add")
def story_add() -> None:
    args_to_get = ['story_id', 'story_contrib'] #Arguments to look for from create form
    data = {args : request.args[args] for args in args_to_get}
    story_add_helper(story_id, story_contrib)

def story_add_helper(story_id: str, story_contrib: str) -> str:
    user_id = str(getActiveUserID())
    c.execute("INSERT INTO %s(user_id, story_contrib) VALUES(%s, %s);" % (story_id, user_id, '"'+story_contrib+'"')) #Insert the values into the table
    c.execute("UPDATE user_table SET story_ids = story_ids || %s WHERE user_id = %s;" % ('",'+story_id+'"', user_id))
    c.commit()
    render_story(form_call=False, story_title=story_id) #Taking function input, not html form input
    return "Successfully contributed to story and rendered it"

@app.route("/render")
def render_story(form_call=True,story_title="",create=True,add=True) -> str:
    if form_call:
        args_to_get = ['create', 'add'] #Arguments to look for from create form
        create,add = [request.args[args] for args in args_to_get]
        if create: story_title = request.args['story_title']
    if not create: render_template("create.html")
    elif not add:
        c.execute("SELECT * FROM %s ORDER BY column DESC LIMIT 1;" % story_title)
        story_contrib = c.fetchall()[2] #Might need to do like c.fetchall()[0][2] here
        render_template("add.html", story_contrib = story_contrib)
    else:
        c.execute("SELECT * from " + story_title)
        story_bits = [row[2] for row in c.fetchall()]
        render_template("story.html", story = story_bits)
