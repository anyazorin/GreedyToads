from flask import Flask, render_template, request
import sqlite3

app = Flask(__name__)    #create Flask object

db = sqlite3.connect("story.db") #open db if file exists, otherwise create db
c = db.cursor()               #facilitate db ops -- you will use cursor to trigger db events

@app.route("/home")
def render_home():
    c.execute("SELECT * FROM users;")
    
    user = c.fetchone()                 #user stores first line of user table
    while request.args['username'] != user[0]:      #while form username != table username
        user = c.fetchone()                         #move on to the next line of user table
    
    story_ids_str = user[2]                 #user's story_ids as a string (i.e. directly from users table)
    story_ids = story_ids_str.split(',')    #list of user's story_ids
    
    my_stories = []             #list of stories user has entries in
    
    for story_id in story_ids:
        c.execute("SELECT * FROM %s ORDER BY id ASC;" % story_id)
        
        story = ""
        for entry in c.fetchall():
            story += entry[2]
            
        my_stories.append(story)
    
    render_template("home.html", stories = my_stories)
