"""
Python V 2.7
Demonstrates how to use python to list all feature services:
"""
import urllib, urllib2, json, ssl

#Generate Authentication token for the script;
username = "yourUsername"
password = "yoUrP@55Word"
portalUrl ="https://<yourSudomain/webadaptor>/" #or your AGOL account
tokenURL = portalUrl + 'sharing/rest/generateToken/'
params = {
    'f': 'pjson',
    'username': username,
    'password': password,
    'referer': 'https://<your Subdomain Name>' # or AGOL account
    }
req = urllib2.Request(tokenURL, urllib.urlencode(params))
try:
    response = urllib2.urlopen(req)
except:
    gcontext = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
    response = urllib2.urlopen(req, context=gcontext)
data = json.load(response)
token = data['token']

#Getting The authenticated user's data

userData = 'https://<yourSudomain/webadaptor>/sharing/rest/content/users/'+username+'?&token='+token+'&f=pjson'
getUserData= urllib.urlopen(userData)
data = json.loads(getUserData.read())
numItems = len(data['items'])

#looping through user items and filter out the ones that are hosted feature services

for i in range(numItems):
    #print 'Name: ' + data['items'][i]['title'] + '  ' + ' ID: ' + data['items'][i]['id']
    #print data['items'][i]['id']
    #print "Getting User Content .....Wait!"
    userItems ='https://<yourSudomain/webadaptor>/sharing/rest/content/users/'+username+'?&token='+token+'/items/'+data['items'][i]['id']+'&f=pjson'
    userContent =urllib.urlopen(userItems)
    userContentRead = json.loads(userContent.read())
    if userContentRead["items"][i]["type"] == 'Feature Service':
        print userContentRead["items"][i]["title"]
   
    
        
