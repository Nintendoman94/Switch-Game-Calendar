from __future__ import print_function
import httplib2

from switchGameFromWikipedia import getSwitchGamesAndReleaseDate
from googleCalendarUtilities import get_credentials
from googleCalendarUtilities import getCalendarId
from googleCalendarUtilities import createEventInCalendar

from apiclient import discovery

import logging
import datetime

APPLICATION_NAME = 'Switch games release calendar'
REGION_NAME = 'Europe'
CALENDAR_NAME = 'Video Games'

# Main function
def main():
    
    # First connect onto the google calendar
    credentials = get_credentials(APPLICATION_NAME)
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('calendar', 'v3', http=http)
    
    # Retrieve map of game and release date for the Nintendo Switch
    switchGameList = getSwitchGamesAndReleaseDate(REGION_NAME)
    
    # Retrieve the calendar 'Video Games' and all its events
    videoGameCalendarId = getCalendarId(service, CALENDAR_NAME)
    videoGameEventsList = service.events().list(calendarId=videoGameCalendarId).execute()
    videoGameEvents = videoGameEventsList.get('items', [])
    
    # For each switch games with a release date, find if it's exist into the calendar
    for switchGames, releaseDate in switchGameList.items():
        
        foundGame = 0
        for event in videoGameEvents:
            currentGameNameEvent = event['summary'].lower()
            
            # The game exists in the calendar
            if(currentGameNameEvent == switchGames.lower()):
                foundGame = 1
                
                currentStartDate = event['start']
                currentDate = currentStartDate['date']
                
                # The date has changed
                if(str(currentDate) != str(releaseDate.date())):
                    logging.info(switchGames + " is schedueled for " + str(currentDate) + " in your calendar")
                    logging.info(switchGames + " will be updated to " + str(releaseDate.date()))
                    currentEventId = event['id']
                    event['start']['date']=str(releaseDate.date())
                    event['end']['date']=str(releaseDate.date())
                    service.events().update(calendarId=videoGameCalendarId, eventId=currentEventId, body=event).execute()
                break
                
        if(foundGame == 0):
            logging.info(switchGames + " will be created to " + str(releaseDate.date()))
            createEventInCalendar(service, switchGames, releaseDate, videoGameCalendarId )
            
# MAIN
if __name__ == '__main__':
    logging.basicConfig(filename=APPLICATION_NAME+'_'+str(datetime.datetime.now())+'.log',level=logging.DEBUG)
    main()