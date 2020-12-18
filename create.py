import sqlite3

def _is_valid(data:dict) -> bool: #Error Handling, print error info here
    DB_FILE="subtopics.db"
    db = sqlite3.connect(DB_FILE) #open if file exists, otherwise create
    c = db.cursor()               #facilitate db ops -- you will use cursor to trigger db events
    c.execute("SELECT * from data_subtopics")
    for row in c.fetchall():
        if row[2] == data['entry_title']:
            return False,"Sorry, that subtopic title already exists in this wiki."
    return True,"No errors here, your subtopic has been implemented. Thanks %s!" % data['contributor_name']

def add_page_data(data:dict) -> None:
    db = sqlite3.connect("subtopics.db") #open db if file exists, otherwise create db
    c = db.cursor()               #facilitate db ops -- you will use cursor to trigger db events
    subtopics = ['entry_title', 'entry', 'contributor_name'] #Columns for Subtopics
    try: c.execute("CREATE TABLE data_subtopics(id INTEGER PRIMARY KEY, Timestamp DATETIME DEFAULT CURRENT_TIMESTAMP, entry_title, entry, contributor_name)") #Creating table for subtopics data
    except: print("Table already exists or an unexpected error has occured")
    db.commit() #save changes
    valid,console_message = _is_valid(data)
    if not valid: return console_message #If entry already exists, return error
    VALUES = ", ".join(value if value.isnumeric() else '"'+value+'"' for value in [*data.values()]) #If the value is supposed to be numeric, make it represented as such otherwise its a string
    c.execute("INSERT INTO data_subtopics (%s) VALUES(%s);" % (",".join(subtopics),VALUES)) #Insert the values into the table
    db.commit() #save changes
    db.close()  #close database
    return console_message
