import random, string, sqlite3 

#generates the random string to use as the receiving email on remembert-side
def random_string(N):
    return ''.join(random.choice(string.letters  + string.digits) for x in range(N))

#used to setup the table... 
#adds a tester account cuz I didn't wanna think about ID gen
#requires remembert.db to exist already
def setup_users_table():
    conn = sqlite3.connect('remembert.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE users(
        "id" INTEGER PRIMARY KEY AUTOINCREMENT,
        "username" varchar(200) NOT NULL UNIQUE,
        "user_email" varchar(200) NOT NULL UNIQUE,
        "creation_date" timestamp with time zone NOT NULL,
        "email" varchar(200) NOT NULL UNIQUE,
        "deleted");''')
    conn.commit()
    c.execute('''INSERT INTO 
        users("username", "user_email", "creation_date", "email", "deleted")
        VALUES('tester', 'tester@test.com', datetime('now'), ?, ?)''',
        (random_string(20), False))
    conn.commit()
    conn.close()

#adds a new user nearly everything must be unique.
def add_user(username, user_email):
    conn = sqlite3.connect('remembert.db')
    c = conn.cursor()
    internal_email = random_string(20)
    while internal_email in c.fetchall():
        internal_email = random_string(20)
    try:
        c.execute('''INSERT INTO 
            users("username", "user_email", "creation_date", "email", "deleted")
            VALUES(?, ?, datetime('now'), ?, ?)''',
            (username, user_email, internal_email, False))
        conn.commit()
        conn.close()
    except sqlite3.IntegrityError as problem:
        print 'ERROR ', problem

#creates the table that holds all the list data
def create_list_table():
    conn = sqlite3.connect('remembert.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE list_entries(
        "id" INTEGER PRIMARY KEY AUTOINCREMENT,
        "user_id" NOT NULL,
        "content" varchar(200) NOT NULL,
        "creation_date" timestamp with time zone NOT NULL,
        "deleted",
        FOREIGN KEY(user_id) REFERENCES users(id));''')
    conn.commit()
    c.execute('''INSERT INTO list_entries ("user_id", "content", "creation_date",
        "deleted") 
        VALUES(0, 'testing', datetime('now'), 0)''')
    conn.commit()
    conn.close()

#adds an element to the list data
def add_list(u_id, content):
    conn = sqlite3.connect('remembert.db')
    c = conn.cursor()
    #c.execute('SELECT "id" FROM users WHERE "username"=?', (u_name,))
    #u_id = c.fetchone()[0]
    c.execute('''INSERT INTO list_entries ("user_id", "content", "creation_date",
        "deleted")
        VALUES(?, ?, datetime('now'), 0)''',(u_id, content))
    conn.commit()
    conn.close()

#grabs all the active data for a particular user
def get_list(u_id):
    conn = sqlite3.connect('remembert.db')
    c = conn.cursor()
    c.execute('''SELECT content, creation_date, id FROM list_entries WHERE user_id=?
        AND deleted=0''', (u_id,))
    list = c.fetchall()
    conn.close()
    return list

def get_user_email(u_id):
    conn = sqlite3.connect('remembert.db')
    c = conn.cursor()
    c.execute('''SELECT user_email, email FROM users WHERE id=? AND deleted=0''', 
        (u_id,))
    email = c.fetchall()
    conn.close()
    return email

#marks an entry for deletion based on the unique id
def del_list_item(item_id):
    conn = sqlite3.connect('remembert.db')
    c = conn.cursor()
    c.execute("UPDATE list_entries SET deleted = 1 WHERE id=?", (item_id,))
    conn.commit()
    conn.close()

#looks up the userid based off of email address
def get_uid(email):
    conn = sqlite3.connect('remembert.db')
    c = conn.cursor()
    c.execute('''SELECT id FROM users WHERE user_email = ? AND deleted=0''',
        (email,))
    user_id = c.fetchall()
    conn.close()
    return user_id 

#setup_users_table()
#create_list_table()
