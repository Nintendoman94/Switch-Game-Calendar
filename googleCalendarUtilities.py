# -*- coding: utf-8 -*-
"""
Created on Sun Feb 19 12:15:21 2017

@author: JPE2
"""
from __future__ import print_function
import httplib2
import os

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

import datetime
import logging

def createEventInCalendar(service, eventName, eventDate, eventCalendarId):
    event = {
      'summary': eventName,
      'start': {
        'date': str(eventDate.date()),
      },
      'end': {
        'date': str(eventDate.date()),
      },
      'reminders': {
        'useDefault': True,
      },
    }
    
    event = service.events().insert(calendarId=eventCalendarId, body=event).execute()
    logging.debug('Event created: %s' % (event.get('htmlLink')))
    
    
def getCalendarId(service, calendarName):
    page_token = None
    while True:
      calendar_list = service.calendarList().list(pageToken=page_token).execute()
      for calendar_list_entry in calendar_list['items']:
        if(calendar_list_entry['summary'] == calendarName):
          videoGameCalendarId = calendar_list_entry['id']
          logging.debug("Calendar <<"+calendarName+">> id is "+videoGameCalendarId)
          return videoGameCalendarId
      page_token = calendar_list.get('nextPageToken')
      if not page_token:
          logging.error("Calendar <<"+calendarName+">> not found !")
          break
    
# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/calendar-python-quickstart.json
SCOPES = 'https://www.googleapis.com/auth/calendar'
CLIENT_SECRET_FILE = 'client_secret.json'

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

def get_credentials(APPLICATION_NAME):
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'calendar-python-switchVideoGames.json')

    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        logging.debug('Storing credentials to ' + credential_path)
    return credentials
