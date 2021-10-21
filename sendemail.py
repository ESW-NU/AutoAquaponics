# Send an HTML email with an embedded image and a plain text message for
# email clients that don't want to display the HTML.
import smtplib
import csv
#from main import user_settings
#from main import user_settings
from data import Reader
from datetime import datetime
import os
import matplotlib.pyplot as plt
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage


def sendEmail(user_settings):
    while True:
        #if not sunday - return
        weekday = datetime.today().weekday()
        time =  datetime.now()
        hour = time.hour
        minute = time.minute
        second = time.second
        
        if weekday == 6 and hour == 12 and minute == 0 and second == 0:
            pass
        else: 
            continue

        config_path, db_path, _ = user_settings()
        with open(config_path, 'r') as file:
            config_settings = list(csv.reader(file))
            strTos = config_settings[3]
            strTos = list(filter(('Email').__ne__, strTos))


        # Define these once; use them twice!
        strFrom = 'nu.urbanagriculture@gmail.com'

        ###########
        
        #we need to edit this so that it takes from GUI
        #we will DEFINITELY have to 'import GUI'

        ###########
        sec_per_week = 7 * 24 * 60 * 60
        tsamp = 1
        nsamp = 5
        information = Reader(db_path,'sensor_db.db').get_timeset(table="SensorData", num= sec_per_week / (tsamp * nsamp)) #num is the number of data points. We need to figure out what num is for a whole week
        #Daniel will apply SQL lite later
    
        def func1(x):
            return x[1:]
        
        information = list(map(func1,information))
        #print('information')
        #print(information)

        param_list = ['pH', 'TDS (ppm)', 'Rela. Humidity (%)', 'Air Temp (\N{DEGREE SIGN}C)', 'Water Temp (\N{DEGREE SIGN}C)', 'Water Level (cm)']
        plt.figure(figsize = (12,12))
        plt.suptitle('Weekly Stats', fontsize = 30)
        #allOfData = {}
        for i in range(len(param_list)):
            def func2(x):
                return x[i]
            
            partOfInfo = list(map(func2,information))
            #print('part of info')
            #print(partOfInfo)
            #allOfData[param_list[i]] = partOfInfo
            plt.subplot(2,3,1+i)
            plt.plot(partOfInfo)
            plt.title(param_list[i])
            ax = plt.gca()
            ax.axes.xaxis.set_visible(False)
        
        title = 'thisweek.png'

        plt.tight_layout()
        plt.savefig(title)


        for strTo in strTos:
            # Create the root message and fill in the from, to, and subject headers
            msgRoot = MIMEMultipart('related')
            msgRoot['Subject'] = 'NU-ESW Aquaponics Weekly Update'
            msgRoot['From'] = strFrom
            msgRoot['To'] = strTo
            msgRoot.preamble = 'This is a multi-part message in MIME format.'

            # Encapsulate the plain and HTML versions of the message body in an
            # 'alternative' part, so message agents can decide which they want to display.
            msgAlternative = MIMEMultipart('alternative')
            msgRoot.attach(msgAlternative)

            msgText = MIMEText('This is the alternative plain text message.')
            msgAlternative.attach(msgText)




            
            #num needs to be changed accordingly
            

            # We reference the image in the IMG SRC attribute by the ID we give it below
            #msgText = MIMEText('<b>Some <i>HTML</i> text</b> and an image.<br><img src="cid:image1"><br>Nifty!', 'html')
            msgText = MIMEText('<b>Here are the graphs for the weekly values.</b><br><img src="cid:image1"><br>', 'html')
            msgAlternative.attach(msgText)

            # This example assumes the image is in the current directory

            fp = open(title, 'rb')
            msgImage = MIMEImage(fp.read())
            fp.close()

            # Define the image's ID as referenced above
            msgImage.add_header('Content-ID', '<image1>')
            msgRoot.attach(msgImage)

            
            
            
            
            
            #otherwise it goes here
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            # Send the email (this example assumes SMTP authentication is required)
            
            email = strFrom
            smtp = 'smtp.gmail.com'
            port = 587
            password = 'Hydroponics1!1'
            server = smtplib.SMTP(smtp, port)

            server.starttls()

            server.login(email,password)
            server.sendmail(email, strTo, msgRoot.as_string())
            

        os.remove(title)
        #return
