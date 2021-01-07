from flask import Flask, render_template, request, session, Markup
import sqlite3, os

app = Flask(__name__)    #create Flask object

db = sqlite3.connect("story.db", check_same_thread=False) #open db if file exists, otherwise create db
c = db.cursor()

app.secret_key= os.urandom(32) #Generates a random 32-byte key for the session

@app.route("/") #, methods=['GET', 'POST'])
def disp_loginpage():
    #If the username is in session go to welcome page
    if 'username' in session:
        return render_template('home.html', username=session['username'])
    return render_template('login.html', err='')

@app.route("/makeAcct")
def disp_signup():
    return render_template('makeAcct.html')

@app.route("/login")
def login():
    #Retreive the username and password from the form
    user= request.args['username']
    password= request.args['password']
    #run a query which returns a true/false if there exists a user/password combo that matches the given one
    try: c.execute("SELECT username, password FROM users WHERE username=? AND password=?", (user, password))
    except: return render_template('login.html', err="Did you run db_builder.py")
    #fetches result from the query
    result = c.fetchone()
    #If the login info is correct, start session and go to home
    if result:
        session['username']=user
        return render_template('home.html')
    #if info incorrect, show error message on login page
    else:
        return render_template('login.html', err="Username or Password Incorrect")

@app.route("/signup")
def signup():
    #retreive the inputted user and password
    user= request.args['username']
    password= request.args['password']
    try: c.execute("SELECT username FROM users WHERE username=?", (user))
    except: render_template('makeAcct.html', err="Username already exists, please try another")
    #insert the user into the table
    c.execute("INSERT INTO users (username, password, story_ids) VALUES(?,?,?)", (user, password, ''))
    db.commit()
    session['username']=user
    return render_template('home.html')

#logout (end session) and return to login page
@app.route("/logout")
def logout():
    session.pop('username', None)
    return render_template('login.html', err='')

#helper function that returns the active username
def getActiveUser():
    if 'username' in session:
        return session['username']
    return

#Encrypts and decrypts story_id so it doesn't run into errors later
def encrypt(id): return id.replace(" ","S10S01").replace(",","C10C01") #Encrypt for DB
def decrypt(id): return id.replace("S10S01"," ").replace("C10C01",",") #Decrypt for other purposes

@app.route("/create")
def create_story(): #Creates story table in database
    story_id= request.args["story_id"] #Gets Story Title
    story_contrib=request.args["story_contrib"] #Gets the Story Contribution
    try: c.execute("CREATE TABLE %s(id INTEGER PRIMARY KEY, user_id TEXT, story_contrib TEXT)" % encrypt(story_id))
    except: return render_template("storyCreate.html", err="Title already exists, choose another title")
    db.commit()
    return story_add_helper(story_id, story_contrib)

@app.route("/add")
def story_add(): #Calls story_add_helper()
    story_id= request.args["story_id"]
    story_contrib=request.args["story_contrib"]
    return story_add_helper(story_id, story_contrib)

def story_add_helper(story_id: str, story_contrib: str) -> str: #Adds story entry to corresponding table
    user_id = str(getActiveUser())
    story_id = encrypt(story_id)
    c.execute("INSERT INTO %s(user_id, story_contrib) VALUES(%s, %s);" % (story_id, '"'+user_id+'"', '"'+story_contrib+'"')) #Insert the values into the table
    c.execute("UPDATE users SET story_ids = story_ids || %s WHERE username = %s;" % ('"'+story_id+',"', '"'+user_id+'"'))
    db.commit()
    c.execute("SELECT * from " + story_id+";")
    story_bits = [row[2] for row in c.fetchall()]
    return render_template("storyView.html", story=story_bits, title=decrypt(story_id)) #Taking function input, not html form input

@app.route("/renderCreate")
def renderCreateHTML(): #Renders storyCreate.html
    return render_template("storyCreate.html")

@app.route("/renderAdd")
def renderStoryAdd(): #Renders storyAdd.html with necessary information
    story_id=request.args['story_id']
    c.execute("SELECT * FROM %s ORDER BY id DESC LIMIT 1;" % encrypt(story_id))
    story_contrib = c.fetchone()[2]
    button = Markup('<input type="hidden"  name="story_id" value = "'+story_id+'">')
    return render_template("storyAdd.html", title= story_id, old_story_contrib = story_contrib, button=button)

@app.route("/renderView")
def renderFullStory(): #Renders a story given its story_id
    story_id=request.args['story_id']
    c.execute("SELECT * from " + encrypt(story_id)+";")
    story_bits = [row[2] for row in c.fetchall()]
    return render_template("storyView.html", title=story_id, story=story_bits)

def create_button(title): #Creates a button for HTML
    return '<button type="submit"  name="story_id" value = "'+title+'"> '+title+' </button><br>'

def getUserStories(): #Gets all the stories the current user is a part of
    username= getActiveUser()
    c.execute('SELECT * FROM users;')
    user_stories = set()
    for row in c.fetchall():
        if row[0] == username:
            user_stories = set(decrypt(item) for item in row[2].split(","))
    return user_stories-{''}

@app.route("/home")
def render_home(): #renders home.html
    buttons = Markup("".join([create_button(title) for title in getUserStories()]))
    return render_template("home.html",buttons=buttons)

#shows list of story titles on explore page
@app.route("/explore")
def explore(): #Renders explore.html
    c.execute('SELECT name from sqlite_master where type= "table"')
    all_stories=set(decrypt(item[0]) for item in c.fetchall()) - {"users"}
    story_titles = list(all_stories - getUserStories())
    buttons = Markup("".join([create_button(title) for title in story_titles]))
    return render_template("explore.html", buttons=buttons)

if __name__ == "__main__":
    app.debug = True
    app.run()
