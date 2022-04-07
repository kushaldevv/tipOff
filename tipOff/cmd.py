import json, config, datetime
from urllib.request import urlopen
from matplotlib.font_manager import json_dump
from urllib.error import URLError

def getTeam(id):
    f = open ('teams.json', "r")
    data = json.loads(f.read())
    for i in data:
        if i['teamId'] == int(id):
            return (i['teamName'])
    f.close()
    return "team name"

def isTeam(str):
    f = open ('teams.json', "r")
    data = json.loads(f.read())
    for i in data: 
        if str in i['simpleName'].lower():
            return i['teamId']
    f.close()
    return "No team"

def gameWinner(gameID, teamID, date):
    URL = "http://data.nba.net/10s/prod/v1/" + date + "/scoreboard.json"
    data = json.loads(urlopen(URL).read())
    for i in data['games']:
        if i['gameId'] == gameID and 'endTimeUTC' in i:
            winner = i['hTeam']['teamId'] if int(i['hTeam']['score']) > int(i['vTeam']['score']) else i['vTeam']['teamId']
            loser = i['hTeam']['teamId'] if int(i['hTeam']['score']) < int(i['vTeam']['score']) else i['vTeam']['teamId']
            if winner == teamID:
                return [True, True, getTeam(winner), getTeam(loser)]
            else:
                return [True, False, getTeam(winner), getTeam(loser)]
        elif i['gameId'] == gameID:
            otherTeam = getTeam(i['hTeam']['teamId']) if teamID != i['hTeam']['teamId'] else getTeam(i['vTeam']['teamId'])
            return [False, False, otherTeam]

def gameStatus(gameID, date):
    URL = "http://data.nba.net/10s/prod/v1/" + date + "/scoreboard.json"
    data = json.loads(urlopen(URL).read())
    for i in data['games']:
        if i['gameId'] == gameID and 'endTimeUTC' in i:
            return "finished"
        elif i['gameId'] == gameID and not i['isGameActivated']:
            return "not started"
        elif i['gameId'] == gameID:
            return "game in progresss"
 

def correctTeam(gameID, teamID):
    URL = "http://data.nba.net/10s/prod/v1/" + config.currDate + "/scoreboard.json"
    data = json.loads(urlopen(URL).read())
    for i in data['games']:
        if i['gameId'] == gameID:
            if i['vTeam']['teamId'] == teamID or i['hTeam']['teamId'] == teamID:
                return True
    return False

def printScores(date):  
    URL = "http://data.nba.net/10s/prod/v1/" + date + "/scoreboard.json"
    try:
        response = urlopen(URL)
    except URLError:
         return ("Invalid date")
    data = json.loads(response.read())
    if data['numGames'] == 0:
        return "No games"
    output = ""
    count = 1
    config.currDate = date
    config.curr.clear()
    for i in data['games']:
        config.curr[count] = i['gameId']
        home = getTeam(i['hTeam']['teamId'])
        away = getTeam(i['vTeam']['teamId'])
        if len(i['hTeam']['score']) > 0 and int(i['hTeam']['score']) > int(i['vTeam']['score']):
            home = "**" + home + "**"
        elif len(i['hTeam']['score']) > 0 and int(i['hTeam']['score']) < int(i['vTeam']['score']):
            away = "**" + away + "**"            
        if(i['isGameActivated']):
            output += (str(count) + ") " + home + " " + i['hTeam']['score'] + " vs " + away + " " + i['vTeam']['score'] + " Live\n")
        elif('endTimeUTC' in i):

            output += (str(count) + ") " + home + " " + i['hTeam']['score'] + " vs " + away + " " + i['vTeam']['score'] + " Final\n")
        else:
            output += (str(count) + ") " + home + " vs " + away + " @ " + i['startTimeEastern'] + "\n")
        count += 1
    return output

def livePlayByPlay(date, gameId):
    URL = "http://data.nba.net/json/cms/noseason/game/" + date+ "/" + gameId +"/pbp_last.json"
    try:
        response = urlopen(URL)
    except URLError:
         return ("Game not started")
    data = json.loads(response.read())
    if 'sports_content' not in data:
        return
    return (data['sports_content']['play']['description'])

def getEventId(date, gameId):
    URL = "http://data.nba.net/json/cms/noseason/game/" + date+ "/" + str(gameId) +"/pbp_last.json"
    try:
        response = urlopen(URL)
    except URLError:
         return
    data = json.loads(response.read())
    if 'sports_content' not in data:
        return
    return int(data['sports_content']['play']['event'])

def printBoxScore(date, gameId):
    URL = "http://data.nba.net/prod/v1/" + date + "/" + gameId + "_boxscore.json"
    try:
        response = urlopen(URL)
    except URLError:
         return 
    data = json.loads(response.read())
    if 'stats' not in data:
        return (["Game not started"])
    homeId = data['basicGameData']['hTeam']['teamId']
    homeName = (data['basicGameData']['hTeam']['triCode'])
    vName = (data['basicGameData']['vTeam']['triCode'])
    h = {}
    v = {}
    for i in data['stats']['activePlayers']:
        if(i['min'] != '0:00' and i['min'] != '0' and i['min'] != ""):
            name = (i['firstName'] + " " + i['lastName'])
            pts = i['points']
            ast = i['assists']
            reb = i['totReb']
            stl = i['steals']
            blk = i['blocks']
            to = i['turnovers']
            minutes = i['min'].partition(":")[0]
            if i['teamId'] == homeId:
                h[("|" + name + " |"+ minutes + " min|" +  pts + " pts|"+ ast + " ast|" + reb + " reb|" + stl + " stl|" + blk+ " blk|" + to + " tov|")] = -int(pts)
            else:
                v[("|" + name + " |"+ minutes + " min|" +  pts + " pts|"+ ast + " ast|" + reb + " reb|" + stl + " stl|" + blk+ " blk|" + to + " tov|")] = -int(pts)
  
    sortedH = dict(sorted(h.items(), key=lambda item: item[1]))
    sortedV =  dict(sorted(v.items(), key=lambda item: item[1]))
    hOut = ("`"+ homeName + ":\n")
    vOut = ("`"+ vName + ":\n")
    for key, v in sortedH.items(): 
        hOut += key + "\n\n"
    for key, v in sortedV.items(): 
        vOut += key + "\n\n"
    return([hOut + "`", vOut + "`"])

def printStandings():
    URL = "http://data.nba.net/10s/prod/v1/current/standings_conference.json"
    response = urlopen(URL)
    data = json.loads(response.read())
    eastOut = "`Eastern       |wins|loss|last10|strk|\n-------------------------------------\n"
    westOut = "`Western       |wins|loss|last10|strk|\n-------------------------------------\n"
    for i in data['league']['standard']['conference']['east']:
        teamName = getTeam(i['teamId']).split()[-1]
        if i['isWinStreak']:
            streak = (" " + i['streak']).ljust(3)
        else:
            streak = ("-" + i['streak']).ljust(3)
        eastOut += (teamName.ljust(12) + "  | " + i['win'].ljust(2) + " | " + i['loss'].ljust(2) + " |  " 
        + (i['lastTenWin'] + "-" + i['lastTenLoss']).ljust(4) + "| " +  streak + "|\n" +
        "-------------------------------------\n")
    for i in data['league']['standard']['conference']['west']:
        teamName = getTeam(i['teamId']).split()[-1]
        if i['isWinStreak']:
            streak = (" " + i['streak']).ljust(3)
        else:
            streak = ("-" + i['streak']).ljust(3)
        westOut += (teamName.ljust(12) + "  | " + i['win'].ljust(2) + " | " + i['loss'].ljust(2) + " |  " 
        + (i['lastTenWin'] + "-" + i['lastTenLoss']).ljust(4) + "| " +  streak + "|\n\n" +
        "-------------------------------------\n")
    return ([eastOut + "`", westOut + "`"])

def userFunds(userID, amount):
    with open("bank.json") as file: 
        data = json.load(file)
        if userID not in data:
            data[userID] = {'amount': 10420}
            data[userID]['bets'] = {}
        else:
            getAmount = data[userID]['amount']
            bets = data[userID]['bets']
            data[userID]['amount'] = getAmount + amount
            data[userID]['bets'] = bets
        json_dump(data, 'bank.json')

def addBet(userID, amount, gameID, betTeam, date):
    with open("bank.json") as file:
        data = json.load(file)
        userFunds(userID, 0)
        if  date not in data[userID]['bets'] and amount < 0:
            return
        if  date not in data[userID]['bets']:
            data[userID]['bets'][date] = {}
        if gameID not in data[userID]['bets'][date]:
            data[userID]['bets'][date][gameID] = {}
        if betTeam not in data[userID]['bets'][date][gameID]:
            data[userID]['bets'][date][gameID][betTeam] = {'amount': 0, 'betComplete' : 0}
        prevAmount = data[userID]['bets'][date][gameID][betTeam]['amount']
        data[userID]['bets'][date][gameID][betTeam]['amount'] = amount + prevAmount
        json_dump(data, 'bank.json')

def printBets(userId):
    today = datetime.date.today()
    start_day = today - datetime.timedelta(today.weekday() + 5)
    listDates = [(start_day + datetime.timedelta(x)).strftime("%Y%m%d") for x in range(14)]
    f = open ('bank.json', "r")
    data = json.loads(f.read())
    ret = ""
    for bd in data[userId]['bets']:
      if bd in listDates:
        for games in data[userId]['bets'][bd]:
          for teams in data[userId]['bets'][bd][games]:
            try:
                gameStatus = gameWinner(games, teams, bd)
                gameStatus[3]
                if gameStatus[0] and gameStatus[1]:
                  ret += "-won $" + str(data[userId]['bets'][bd][games][teams]['amount']) + " from " + gameStatus[2] + " vs " + gameStatus[3] + "\n"
                elif gameStatus[0] and not gameStatus[1]:
                  ret += "-lost $" + str(data[userId]['bets'][bd][games][teams]['amount']) + " from " + gameStatus[2] + " vs " + gameStatus[3] + "\n"
            except:
                  ret += "-Betting $" +  str(data[userId]['bets'][bd][games][teams]['amount']) + " on ***" + getTeam(teams) + "*** vs "+ gameStatus[2] + "\n"
    if len(ret) == 0:
      return "No Bets"
    return ret
      
def checkBets():
    with open("bank.json") as file:
        data = json.load(file)
        for users in data:
            for dates in data[users]['bets']:
                for games in data[users]['bets'][dates]:
                    for teams in data[users]['bets'][dates][games]:
                        ret = gameWinner(games, teams, dates)
                        if ret[0] and ret[1] and  data[users]['bets'][dates][games][teams]['betComplete'] == 0:
                            userFunds(users, 2*(data[users]['bets'][dates][games][teams]['amount']))
                        elif ret[0]:
                          data[users]['bets'][dates][games][teams]['betComplete'] = 1
        json_dump(data, 'bank.json')

def getAmount(userID):
    f = open ('bank.json', "r")
    data = json.loads(f.read())
    f.close()
    return data[userID]['amount']

def giveAmount(givee, recievee, amount):
    if amount < 0:
        return "you thought bozo"
    if getAmount(givee) - amount < 0:
        return "not enough funds bozo"
    userFunds(givee, -amount)
    userFunds(recievee, amount)
    return "successfully transfered $" + str(amount)