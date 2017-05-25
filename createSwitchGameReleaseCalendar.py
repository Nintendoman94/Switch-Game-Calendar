from __future__ import print_function
import httplib2

from switchGameFromWikipedia import getSwitchGamesAndReleaseDate
from googleCalendarUtilities import get_credentials
from googleCalendarUtilities import getCalendarId
from googleCalendarUtilities import createEventInCalendar

from apiclient import discovery
import time
import logging
import datetime

APPLICATION_NAME = 'Switch games release calendar'
REGION_NAME = 'Europe'
CALENDAR_NAME = 'Video Games'
CONSOLE_NAME = 'Switch'
RESET_GAME = True

# Main function
def main():
    
    # First connect onto the google calendar
    credentials = get_credentials(APPLICATION_NAME)
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('calendar', 'v3', http=http)
    
    # Retrieve map of game and release date for the Nintendo Switch
    gameList = getSwitchGamesAndReleaseDate(REGION_NAME)
        
    # There have to be at least one game in the list. Otherwise the previous function has failed
    if(len(gameList) != 0):
        # Retrieve the calendar 'Video Games' and all its events
        
        calendarPageToken = None
        videoGameCalendarId = getCalendarId(service, CALENDAR_NAME)
        while True:
            
            videoGameEventsList = service.events().list(calendarId=videoGameCalendarId, pageToken=calendarPageToken).execute()
            videoGameEvents = videoGameEventsList.get('items', [])
                        
            # For each event from the calendar check if the game is in the list
            # If it's not in the list, it means the game has been cancelled or delayed to an unknown date
            for event in videoGameEvents:
                time.sleep(0.05)
                currentGameNameEvent = event['summary'].lower()
                currentEventId = event['id']
                # check if the game is related to this console
                if(currentGameNameEvent.find('('+CONSOLE_NAME.lower()+')') != -1):
                    logging.debug("The game " + str(currentGameNameEvent) + " is released on " + CONSOLE_NAME)
                    foundGame=False;
                    # if RESET_GAME is true, then delete game of this console and replace them
                    if(not RESET_GAME):
                        for games, releaseDate in gameList.items():                        
                            if(currentGameNameEvent == games.lower()):
                                foundGame=True
                                break
                    # The game is not in the updated list
                    if(not foundGame):
                        logging.info(str(currentGameNameEvent) + " will be deleted from your calendar" )
                        service.events().delete(calendarId=videoGameCalendarId, eventId=currentEventId).execute()                        
            calendarPageToken = videoGameEventsList.get('nextPageToken')
            if not calendarPageToken:
                break
            time.sleep(0.05)
            
        # For each switch games with a release date, find if it's exist into the calendar
        for games, releaseDate in gameList.items():
            
            foundGame = False
            if(not RESET_GAME):
                for event in videoGameEvents:
                    currentGameNameEvent = event['summary'].lower()
                    # print(games.lower() + " compare to " + currentGameNameEvent)
                    # The game exists in the calendar
                    if(currentGameNameEvent == games.lower()):
                        foundGame = True
                        
                        currentStartDate = event['start']
                        currentDate = currentStartDate['date']
                        
                        # The date has changed
                        if(str(currentDate) != str(releaseDate.date())):
                            logging.info(games + " is schedueled for " + str(currentDate) + " in your calendar")
                            logging.info(games + " will be updated to " + str(releaseDate.date()))
                            currentEventId = event['id']
                            event['start']['date']=str(releaseDate.date())
                            event['end']['date']=str(releaseDate.date())
                            service.events().update(calendarId=videoGameCalendarId, eventId=currentEventId, body=event).execute()
                            time.sleep(0.05)
                        break  
                time.sleep(0.05)
            
            if(not foundGame):
                #logging.info(games + " will be created to " + str(releaseDate.date()))
                createEventInCalendar(service, games, releaseDate, videoGameCalendarId )
                time.sleep(0.05)
#            else:
#                print("FOUNDED !")
    else:
        logging.error("No game found in wikipedia")
            
# MAIN
if __name__ == '__main__':
    logFilename = str(APPLICATION_NAME+'_'+str(datetime.datetime.now())+'.log').replace(':','.')
    logging.basicConfig(filename=APPLICATION_NAME+'.log',level=logging.DEBUG)
    main()