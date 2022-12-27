import sys
import xbmc
import xbmcaddon
import xbmcgui
from datetime import datetime
import json
import time


ADDON = xbmcaddon.Addon()
ADDONID = ADDON.getAddonInfo('id')
ADDONNAME = ADDON.getAddonInfo('name')
LANGUAGE = ADDON.getLocalizedString
DIALOG = xbmcgui.Dialog()

def getSettings():
    build_all = xbmc.getInfoLabel('System.BuildVersionShort')
    build_split = build_all.split('-')
    build = float(build_split[0])
    if float(build) >= 20.0:
        # read settings for v20
        SETTINGS = xbmcaddon.Addon().getSettings()
        getSettings.enable_static_hours = SETTINGS.getBool('enable_static_hours')
        getSettings.static_hours = SETTINGS.getInt('static_hours')
    else:
        # read settings for v19
        getSettings.enable_static_hours = ADDON.getSettingBool('enable_static_hours')
        getSettings.static_hours = ADDON.getSettingInt('static_hours')

def calcTimes(endDate, endTime):

    # get, format and truncate current time
    now = datetime.now()
    formattedNow = now.strftime("%d/%m/%Y %H:%M")
    try:
        dateTimeTruncated = datetime.strptime(formattedNow, '%d/%m/%Y %H:%M')
    except TypeError:
        dateTimeTruncated = datetime(*(time.strptime(formattedNow, '%d/%m/%Y %H:%M')[0:6]))

    # get and format given time
    dateTimeString = str(endDate) + " " + str(endTime)
    xbmc.log("Ends before: given date-time: " + dateTimeString, level=xbmc.LOGDEBUG)
    try:
        timeString = datetime.strptime(dateTimeString, '%d/%m/%Y %H:%M')
    except TypeError:
        timeString = datetime(*(time.strptime(dateTimeString, '%d/%m/%Y %H:%M')[0:6]))
    diff = timeString - dateTimeTruncated
    diffInSeconds = int(diff.total_seconds())
    xbmc.log("Ends before: calculated diff in seconds: " + str(diffInSeconds), level=xbmc.LOGDEBUG)
    xbmc.log("Ends before: dateTimeTruncated: " + str(dateTimeTruncated), level=xbmc.LOGDEBUG)
    return diffInSeconds

def getMoviesJSON():
    allMovies = xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "VideoLibrary.GetMovies", "params": { "properties" : ["runtime"]}, "id": "libMovies"}')
    allMoviesJSON = json.loads(allMovies)
    return allMoviesJSON
    #DIALOG.ok(ADDONNAME, str(allMoviesJSON['result']['movies']))

def playMovie(libraryID):
    xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "Player.Open", "params": { "item" : {"movieid": %d } } }' %libraryID)


def main():
    getSettings()
    xbmc.log("Ends before: static hours enabled: " + str(getSettings.enable_static_hours), level=xbmc.LOGDEBUG)
    xbmc.log("Ends before: static hours set: " + str(getSettings.static_hours), level=xbmc.LOGDEBUG)

    if not getSettings.enable_static_hours:
        endDate = DIALOG.input(LANGUAGE(32001), type=xbmcgui.INPUT_DATE)
        endTime = DIALOG.input(LANGUAGE(32002), type=xbmcgui.INPUT_TIME)
        maxDuration = str(calcTimes(endDate, endTime))
        if int(maxDuration) < 0:
            DIALOG.ok(ADDONNAME, LANGUAGE(32005))
            sys.exit(0)
    else:
        maxDuration = int(getSettings.static_hours) * 3600


    movies = getMoviesJSON()
    #DIALOG.ok(ADDONNAME, str(movies['result']['movies']))
    listMovies = []
    listMovieID= []
    for movie in movies['result']['movies']:
        if int(movie['runtime']) < int(maxDuration) and int(movie['runtime'] != 0 ):
            listMovies.append(movie['label'])
            listMovieID.append(movie['movieid'])
    
    xbmc.log("Ends before: movie count: " + str(len(listMovies)), level=xbmc.LOGDEBUG)
    if len(listMovies) != 0:
        selected = DIALOG.select(ADDONNAME, listMovies)
        if selected == -1:
            DIALOG.ok(ADDONNAME, LANGUAGE(32004))
        else:
            xbmc.log("Ends before: movieID: " + str(listMovieID[selected]), level=xbmc.LOGDEBUG)
            xbmc.log("Ends before: movie: " + str(listMovies[selected]), level=xbmc.LOGDEBUG)
            playMovie(listMovieID[selected])
    else:
        DIALOG.ok(ADDONNAME, LANGUAGE(32003))

    
