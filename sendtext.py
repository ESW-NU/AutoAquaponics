

## this code sends a message to a keyworded dictionary of phone numbers, where the phone number is the key 
    ## and the carrier is the value. Carriers are case sensitive. Numbers must be in XXXYYYZZZZ format, 
    ## with no 1 at the beginning and no - in between sections

import smtplib 
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# call this function by typing the lines below (replace things in numbers with your actual number/carrier)
# the "numbers" list can have any number of key-value pairs in there
#   numbers = {'2029266579' : "T-Mobile", "2243459408" : "AT&T"}
#   sendtext("your text message", **numbers) 
numbers = {}

def sendtext(message, **numbers):
    
    numberlist =[]
    for number, carrier in numbers.items(): 
        if carrier == "AT&T":
            numemail = number+"@txt.att.net"
            #numemail1 = "1"+number+"@txt.att.net"
        elif carrier == "Sprint":
            numemail = number+'@messaging.sprintpcs.com'
            #numemail1 = "1"+number+'@messaging.sprintpcs.com'   
        elif carrier == "T-Mobile":
            numemail = number+'@tmomail.net'
            #numemail1 = "1"+number+'@tmomail.net'
        elif carrier == "Verizon":
            numemail = number+'@vtext.com'
            #numemail1 = "1"+number+'@vtext.com'
        elif carrier == "Boost Mobile":
            numemail = number+'@myboostmobile.com'
            #numemail1 = "1"+number+'@myboostmobile.com'
        elif carrier == "Cricket":
            numemail = number+'@sms.mycricket.com'
            #numemail1 = "1"+number+'@sms.mycricket.com'
        elif carrier == "Metro PCS":
            numemail = number+'@mymetropcs.com'
            #numemail1 = "1"+number+'@mymetropcs.com'
        elif carrier == "Tracfone":
            numemail = number+'@mmst5.tracfone.com'
            #numemail1 = "1"+number+'@mmst5.tracfone.com'
        elif carrier == "U.S. Cellular":
            numemail = number+'@email.uscc.net'
            #numemail1 = "1"+number+'@email.uscc.net'
        elif carrier == "Virgin Mobile":
            numemail = number+'@vmobl.com'
            #numemail1 = "1"+number+'@vmobl.com'
        numberlist.append(numemail)
        #numberlist.append(numemail1)
    print(numberlist)

    email = "nu.urbanagriculture@gmail.com"
    pas = "Hydroponics1!1"

    # The server we use to send emails in our case it will be gmail but every email provider has a different smtp 
    # and port is also provided by the email provider.
    smtp = "smtp.gmail.com" 
    port = 587
    # This will start our email server
    server = smtplib.SMTP(smtp,port)
    # Starting the server
    server.starttls()
    # Now we need to login
    server.login(email,pas)

    for entry in numberlist:
        msg = MIMEMultipart()
        sms_gateway = entry
        msg['From'] = email
        msg['To'] = sms_gateway
        body = message
        msg['Subject'] = "Aquaponics Update\n"
        msg.attach(MIMEText(body)) #, 'plain'))
        sms = msg.as_string()
        
        server.sendmail(email,sms_gateway,sms)

