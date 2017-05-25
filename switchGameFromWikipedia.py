import wikipedia
from datetime import datetime
from bs4 import BeautifulSoup
from urllib.request import urlopen
import re
import logging

REGIONS_COLUMN = {"Europe" : 7,
           "America" : 6,
           "Japan" : 5,
           }

WIKIPEDIA_PAGE_NAME = 'List_of_Nintendo_Switch_games'
CONSOLE_NAME = 'Switch'
DATE_IN_COLUMN_PATTERN = '00000000\d\d\d\d.\d\d.\d\d.0000(.*)'
DATE_PATTERN = '(\w+ \d+, \d+)'

def getSwitchGamesAndReleaseDate(region):
    switchPage = wikipedia.page(WIKIPEDIA_PAGE_NAME)
    header = {'User-Agent': 'Mozilla/5.0'} #Needed to prevent 403 error on Wikipedia
    page = urlopen(switchPage.url)
     
    html = page.read()
    soup = BeautifulSoup(html, "html.parser")
    
    tables = soup.findAll("table", { "class" : "wikitable" })
    
    for tn in range(len(tables)):
        table=tables[tn]
    
        # preinit list of lists
        rows=table.findAll("tr")
        row_lengths=[len(r.findAll(['th','td'])) for r in rows]
        ncols=max(row_lengths)
        nrows=len(rows)
        data=[]
        for i in range(nrows):
            rowD=[]
            for j in range(ncols):
                rowD.append('')
            data.append(rowD)
        
        # process html
        for i in range(len(rows)):
            row=rows[i]
            rowD=[]
            cells = row.findAll(["td","th"])
            for j in range(len(cells)):
                cell=cells[j]
                
                #lots of cells span cols and rows so lets deal with that
                cspan=int(cell.get('colspan',1))
                rspan=int(cell.get('rowspan',1))
                for k in range(rspan):
                    for l in range(cspan):
                        data[i+k][j+l]+=cell.text
        
            data.append(rowD)
        
        # Create the map ConsoleCalendar[GameName (ConsoleName)]=ReleaseDate
        game={}    
        for i in range(nrows):
            releaseDate = re.match(DATE_IN_COLUMN_PATTERN,data[i][REGIONS_COLUMN[region]])
            if(releaseDate):
                formatedReleaseDate = re.match(DATE_PATTERN,releaseDate.group(1))
                if(formatedReleaseDate):
                    datetime_object = datetime.strptime(formatedReleaseDate.group(1), '%B %d, %Y')
                    logging.info(data[i][0] + " is coming out on " + str(datetime_object))
                    gameName = data[i][0] + " (" + CONSOLE_NAME + ")"
                    game[gameName]=datetime_object
        return game