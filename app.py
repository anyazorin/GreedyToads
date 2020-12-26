from flask import Flask, render_template, request, session
import sqlite3, random, os

app = Flask(__name__)    #create Flask object

db = sqlite3.connect("story.db") #open db if file exists, otherwise create db
c = db.cursor()               #facilitate db ops -- you will use cursor to trigger db events
app.secret_key= os.urandom(32) #Generates a random 32-byte key for the session

@app.route("/") #, methods=['GET', 'POST'])
def disp_loginpage():
    #If the username is in session go to welcome page
    if 'username' in session:
        return render_template('home.html', username=session['username'])
    return render_template('login.html', err='')

@app.route("/login")
def login():
    #Retreive the username and password from the form
    user= request.args['username']
    password= request.args['password']
    #run a query which returns a true/false if there exists a user/password combo that matches the given one
    c.execute("""SELECT username, password FROM users WHERE username=? AND password=?""", (user, password))
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
    #check if the user already exists
    c.execute("""SELECT username FROM users WHERE username=?""", (user))
    result = c.fetchone()
    #send error message asking for new username
    if not result:
        render_template('signup.html', err="Username already exists, please try another")
    #insert the user into the table
    c.execute('''INSERT INTO users(username, password, story_ids) VALUES(?,?,?)''', (user, password, ''))
    c.commit()
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


