import poplib, smtplib, re, time
from sql_handler import add_list, add_user, get_uid, get_user_email, get_list
from email import parser
from bs4 import BeautifulSoup, SoupStrainer

from datetime import date

def send_email( TO, FROM, message ):
    email_uname = "USERNAME"
    email_pwd = "PASSWORD"

    try:
	server = smtplib.SMTP("smtp.gmail.com", 587)
	server.ehlo()
	server.starttls()
	server.login(email_uname, email_pwd)
	server.sendmail(FROM, TO, message)
	#server.quit()
	server.close()
	print 'email sent'
    except:
	print 'something happen'

def send_daily_list(u_id):
    user_emails = get_user_email(u_id)
    user_mail = user_emails[0][0]
    user_string = user_emails[0][1]

    today = date.today()
    today_date = today.strftime("%A %m/%d/%y")
    to_do = get_list(u_id) 
    
    body = "Myan! How're you?\nAre you ready to get things done today?\n"
    TEXT = body
    for entry in to_do:
        TEXT = "\n".join((TEXT, "- %s (added:%s) id %d" % entry))
    TEXT = "\n".join((TEXT, "\nYou can add/remove items to your todo list by replying to this email.\nGanbatte!\n\n<3CatBeard"))
    
    FROM = 'catbeardface@gmail.com'
    REPLY_TO = 'catbeardface+%s@gmail.com' % user_string
    TO = [user_mail]
    SUBJECT = "To Do: %s" % today_date
    #TEXT = " ".join((body, "\n".join(to_do)))
    message = """\From: %s\nTo: %s\nReply-To: %s\nSubject: %s\n\n%s""" % (FROM, ",".join(TO), REPLY_TO, SUBJECT, TEXT)
    send_email(TO, FROM, message)

def get_email():
    pop_conn = poplib.POP3_SSL('pop.gmail.com')
    pop_conn.user('catbeardface@gmail.com')
    pop_conn.pass_('WMHso6V2u4HG')

    print pop_conn.list()

    raw_list = [pop_conn.retr(i) for i in range(1, len(pop_conn.list()[1]) + 1)]
    raw_list = ["\n".join(mssg[1]) for mssg in raw_list] 
    raw_list = [parser.Parser().parsestr(mssg) for mssg in raw_list]

    only_ltr = SoupStrainer(dir="ltr")
    for message in raw_list:
	for part in message.walk():
            if part.get_content_type():
                body = part.get_payload(decode=True)#.decode(part.get_content_charset())
        html_bod = BeautifulSoup(body,"html.parser", parse_only=only_ltr)
        raw_bod = "\n".join( [text for text in html_bod.stripped_strings])
        body = re.sub('<\n|[a-zA-Z0-9_\-.]{1,}@(\w){1,}\.(\w)+\n|>\n.+', "", raw_bod)
        from_email = (re.search("[a-zA-Z0-9_\-.]{1,}@(\w){1,}\.(\w)+", message['from'])).group(0)
        to_email = (re.search("[a-zA-Z0-9_\-.]{1,}@(\w){1,}\.(\w)+", message['to'])).group(0)
        #lookup email based off of random string thing...
        to_email = ((re.search("\+.+@", to_email)).group(0))[1:20] 
        if not from_email: #in the case where the email isn't in the db for some reason???
            add_user(str_email, str_email) #maybe should add a field to the db stating these match and should bechanged
            from_email =get_uid(str_email)
        user_id = from_email[0][0]
        derp = body.splitlines()
        for line in derp:
            if len(line)>0 && re.match('**DELETE**', line):
                delete_list_item(u_id,line[10:])
            elif len(line) > 0 && not re.match('**DELETE**', line):
                add_list(user_id, line)
            elif len(line) == 0:
                #do nothing cuz a pirate is free? No seriously, the line is empty.
            else:
                #this should error... i should learn to error

get_email()
