
Uses Python 2.7
edit config.json file to include:
  1. Portal for ArcGIS / AGOL Details
  2. Feature Service Rest End Point
  3. Enumerator/Field Worker usernames (should be the accounts the use on portal/agol)
  4. Person to be notified's email
  5. Senders email (noreply@yourdomain.com) + smptp email
  
 The script will generate time stamp json for each enumerator which stores the time in which they last updated the service
 Add the script to task scheduler
