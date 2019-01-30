"""
This script has been built to run on Python27
*Workflow*
    Get's access to the feature service (config.json)
    Dynamically creates time.json files for all the datacollectors
    Checks the timestamp on the timejsons against the LastEdited field for each user
    Sends an email the the respective managers
    Updates the Last-Checked time stamp on the timeJsons

Edit the config.json to include the following:
    featureServiceUrl
    portal url + Credentials
    Enumertors usernames + their respective managers' emails

Developed by: Esri Eastern Africa Professional Services Team
"""
import os
import json
import urllib
import urllib2
import datetime
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
"""
Getting the ReQuired JSON Files: 
    info.json
"""
jsonConfig = "config.json"
jsonResponse = urllib.urlopen(jsonConfig)
jsonData = json.loads(jsonResponse.read())

i = len(jsonData['enumerators'])
dataCollectorsIndex = i-1

"""
Defining Variables Used by the script
"""

FeatureServiceUrl = jsonData["featureServiceUrl"]
FeatureServiceQuery = "/0/query"

username = jsonData["portal"]["username"]
password = jsonData["portal"]["password"]
referer = jsonData["portal"]["url"]
emailSmtp = jsonData["emailConfig"]["smtp"]
emailPort = jsonData["emailConfig"]["smtpPort"]
URL = FeatureServiceUrl + FeatureServiceQuery
uniqueID = 'globalid'
dateField = 'CreationDate'
editorField = 'Editor'


"""
Getting Access to ArcGIS Online/Portal for ArcGIS
"""
token = ''
# noinspection PyBroadException
try:
    print('Generating Token')
    tokenURL = referer + '/sharing/rest/generateToken'
    params = {'f': 'pjson', 'username': username, 'password': password, 'referer': referer}
    req = urllib2.Request(tokenURL, urllib.urlencode(params))
    response = urllib2.urlopen(req)
    data = json.load(response)
    token = data['token']
    print token
except:
    print "Something went horribly wrong"

"""
Querying Hosted Feature Service 
"""

params = {
            'f': 'pjson',
            'where': "1=1",
            'outfields': 'EditDate,Editor',
            'returnGeometry': 'false',
            'token': token
        }

req = urllib2.Request(URL, urllib.urlencode(params))
response = urllib2.urlopen(req)

fsDetails = FeatureServiceUrl+'/0?&token='+token+'&f=pjson'
openFsDetails = urllib2.urlopen(fsDetails)
loadFsDetails = json.load(openFsDetails)

# Feature Service Query Results.
data = json.load(response)
# Get the total number of features collected in the service.
numFeatures = len(data['features'])
featureIndex = numFeatures - 1

# Last Edited Date

lastEdit = loadFsDetails['editingInfo']['lastEditDate']
last = datetime.datetime.fromtimestamp(lastEdit/1000.0)
print lastEdit
timeJson = ''
for ii in range(dataCollectorsIndex):
    dataCollectors = jsonData['enumerators']['user'+str(ii)]['username']
    manager = jsonData['enumerators']['user' + str(ii)]['managersEmail']
    timeJson = str('time' + str(dataCollectors) + '.json')
    if os.path.exists(timeJson):
        print timeJson + ".....  "+u'\u2713'
    else:
        # Create the Missing Time.Json FIle
        fh = open(timeJson, "w")

        # Add the Current 'Last Edited Date' on the New Json
        def writeToTimeJson(path, filename, timestamp):
            filePath = './' + path + '/' + filename
            with open(filePath, 'w') as fp:
                json.dump(timestamp, fp)


        # Example
        timestamp = {}
        timestamp['LastEditedDate'] = lastEdit

        writeToTimeJson('./', timeJson, timestamp)

    # Print timeJson

    # Load the time JSON files for comparison

    timeJsonLoad = timeJson
    timeResponse = urllib.urlopen(timeJsonLoad)
    timejsonData = json.loads(timeResponse.read())
    for x in range(numFeatures):
        featureEdits = data['features'][x]['attributes']['EditDate']
        featureEditsCalender = datetime.datetime.fromtimestamp(featureEdits / 1000.0)
        featureEditors = data['features'][x]['attributes']['Editor']
        editedTime = timejsonData["LastEditedDate"]

        if featureEdits > editedTime and featureEditors == dataCollectors:
            print " Sending an email "+manager+ " mananger for feature added on " + str(featureEditsCalender)

            msg = MIMEMultipart()
            message = "Dear Manager, \n\n You are receiving this email because a" \
                      " new feature update has been made on the data collection tool by "+featureEditors+"\n\n" \
                      "This is an automated email. Please do not reply.\n\nRegards,\nICT"

            # setup the parameters of the message
            password = str(jsonData["emailConfig"]["password"])
            msg['From'] = str(jsonData["emailConfig"]["noReply"])
            msg['To'] = manager
            msg['Subject'] = "No Reply: New Data Submitted by " + dataCollectors

            # add in the message body
            msg.attach(MIMEText(message, 'plain'))

            # create server
            server = smtplib.SMTP(emailSmtp + ':' + emailPort)

            server.starttls()

            # Login Credentials for sending the mail
            server.login(msg['From'], password)

            # send the message via the server.
            server.sendmail(msg['From'], msg['To'], msg.as_string())

            server.quit()
            finalUpdateJsonTime = timeJson
            finalJsonTimeResponse = urllib.urlopen(finalUpdateJsonTime)
            finalJsonTimeData = json.loads(finalJsonTimeResponse.read())
            updateTimeJson = {"LastEditedDate": lastEdit}

            with open(finalUpdateJsonTime, 'w') as outfile:
                json.dump(updateTimeJson, outfile)
print "End!"