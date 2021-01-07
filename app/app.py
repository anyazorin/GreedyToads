
from flask import Flask, render_template, request, session
import sqlite3, random, os


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
    c.execute("SELECT username, password FROM users WHERE username=? AND password=?", (user, password))
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
def encrypt_id(id): return id.replace(" ","10S01").replace(",","10C01") #Encrypt for DB
def decrypt_id(id): return id.replace("10S01"," ").replace("10C01",",") #Decrypt for other purposes

@app.route("/create")
def create_story() -> None:
    story_id= request.args["story_id"] #Gets Story Title
    story_contrib=request.args["story_contrib"] #Gets the Story Contribution
    try: c.execute("CREATE TABLE %s(id INTEGER PRIMARY KEY, user_id TEXT, story_contrib TEXT)" % encrypt_id(story_id))
    except: return render_template("storyCreate.html", err="Title already exists, choose another title")
    db.commit()
    return story_add_helper(story_id, story_contrib)

@app.route("/add")
def story_add() -> None:
    story_id= request.args["story_id"]
    story_contrib=request.args["story_contrib"]
    return story_add_helper(story_id, story_contrib)

def story_add_helper(story_id: str, story_contrib: str) -> str:
    user_id = str(getActiveUser())
    story_id = encrypt_id(story_id)
    c.execute("INSERT INTO %s(user_id, story_contrib) VALUES(%s, %s);" % (story_id, '"'+user_id+'"', '"'+story_contrib+'"')) #Insert the values into the table
    c.execute("UPDATE users SET story_ids = story_ids || %s WHERE username = %s;" % ('"'+story_id+',"', '"'+user_id+'"'))
    db.commit()
    c.execute("SELECT * from " + story_id+";")
    story_bits = [row[2] for row in c.fetchall()]
    return render_template("storyView.html", story=story_bits, title=decrypt_id(story_id)) #Taking function input, not html form input

@app.route("/renderCreate")
def renderCreateHTML():
    return render_template("storyCreate.html")

@app.route("/renderAdd")
def renderStoryAdd():
    story_id=request.args['story_id']
    c.execute("SELECT * FROM %s ORDER BY id DESC LIMIT 1;" % encrypt_id(story_id))
    story_contrib = c.fetchone()[2]
    return render_template("storyAdd.html", title= story_id, old_story_contrib = story_contrib)

@app.route("/renderView")
def renderFullStory():
    return render_template("storyView.html", story=renderStory(request.args['story_id']))

def renderStory(story_id):
    c.execute("SELECT * from " + encrypt_id(story_id)+";")
    story_bits = [row[2] for row in c.fetchall()]
    return render_template("storyView.html")

@app.route("/home")
def render_home():
    db = sqlite3.connect("story.db", check_same_thread=False) #open db if file exists, otherwise create db
    c = db.cursor()
    c.execute("SELECT * FROM users;")
    username= getActiveUser()
    print(username)
    c.execute('SELECT name from sqlite_master where type= "table"')
    stories=list(set(item[0] for item in c.fetchall()) - {"users"})
    db.commit()
    db.close()
    db = sqlite3.connect("story.db", check_same_thread=False)
    c = db.cursor()
    print(stories)
    story_titles=[]
    for title in stories:
        try:
            print("SELECT user_id FROM "+title+ " WHERE user_id='"+username+"'")
            c.execute("SELECT user_id FROM "+title+ " WHERE user_id='"+username+"'")
            #c.execute("SELECT EXISTS(SELECT 1 FROM ? WHERE user_id=?);", (title, username))
            print(title)
            story_titles+=[title]
        except: print("oops")
    print(story_titles)
    return render_template("home.html", story_titles=story_titles)




    # print(username)
    # user = c.fetchone()                #user stores first line of user table
    # while username!= user[0]:      #while form username != table username
    #     user = c.fetchone()                         #move on to the next line of user table

    # story_ids_str = user[2]                 #user's story_ids as a string (i.e. directly from users table)
    # story_ids = story_ids_str.split(',')    #list of user's story_ids

    # my_stories = []             #list of stories user has entries in

    # for story_id in story_ids:
    #     c.execute("SELECT * FROM %s ORDER BY id ASC;" %story_id)

    #     story = ""
    #     for entry in c.fetchall():
    #         story += entry[2]

    #     my_stories.append(story)

    # render_template("home.html", story_titles = my_stories, title=story_id)

#shows list of story titles on explore page
@app.route("/explore")
def explore():
    username= getActiveUser()
    c.execute('SELECT name from sqlite_master where type= "table"')
    all_stories=set(decrypt_id(item[0]) for item in c.fetchall()) - {"users"}
    c.execute('SELECT * FROM users;')
    user_stories = set()
    for row in c.fetchall():
        if row[0] == username:
            user_stories = set(row[2].split(","))
    story_titles = list(all_stories - user_stories)
    return render_template("explore.html", story_titles=story_titles)

if __name__ == "__main__":
    app.debug = True
    app.run()
