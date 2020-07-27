
import smtplib 
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

email = "nu.urbanagriculture@gmail.com"
pas = "Hydroponics1!1"

sms_gateway = '12029266579@tmomail.net' #change this to .. you know, not Mady's number

# SMS Gateways for each Carrier
# AT&T: [number]@txt.att.net
# Sprint: [number]@messaging.sprintpcs.com or [number]@pm .sprint.com
# T-Mobile: [number]@tmomail.net
# Verizon: [number]@vtext.com
# Boost Mobile: [number]@myboostmobile.com
# Cricket: [number]@sms.mycricket.com
# Metro PCS: [number]@mymetropcs.com
# Tracfone: [number]@mmst5.tracfone.com
# U.S. Cellular: [number]@email.uscc.net
# Virgin Mobile: [number]@vmobl.com


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

# Now we use the MIME module to structure our message.
msg = MIMEMultipart()
msg['From'] = email
msg['To'] = sms_gateway
# Make sure you add a new line in the subject
msg['Subject'] = "Aquaponics Update\n"
# Make sure you also add new lines to your body
body = "your plants are on fire\n"
# and then attach that body furthermore you can also send html content.
msg.attach(MIMEText(body)) #, 'plain'))

sms = msg.as_string()

server.sendmail(email,sms_gateway,sms)
