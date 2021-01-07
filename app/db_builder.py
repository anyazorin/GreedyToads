#makes users table
import sqlite3
db = sqlite3.connect("story.db") #open db if file exists, otherwise create db
c = db.cursor()  
c.execute("CREATE TABLE users(username TEXT, password TEXT, story_ids TEXT)")
db.commit()
db.close()