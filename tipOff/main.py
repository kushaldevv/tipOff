import json, re, discord
from discord.ext import tasks
import config, cmd, os

from uptime import keep_alive

@config.client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(config.client))
    @tasks.loop(minutes=10)
    async def betCheck():
        cmd.checkBets()  

    @tasks.loop(hours=24)
    async def dailyAmount():
        f = open ('bank.json', "r")
        data = json.loads(f.read())
        for users in data:
          cmd.userFunds(users, 1000)
        f.close()
    await config.client.change_presence(activity=discord.Game(name="!tipoff for commands"))
    betCheck.start()
    dailyAmount.start()

@config.client.event
async def on_message(message):
    if message.author == config.client.user:
        return
    msg = message.content
    ret = message.channel
    scoresRe = (re.search(r'^!scores \d{2}\/\d{2}\/\d{4}$', msg))
    bsRe = (re.search(r'^!boxscore \d{1,2}$', msg))
    pbpreg = re.search(r'^!pbp \d{1,2}$', msg)
    betRe = re.search(r'^!bet (\d+) ([\w|\s|\d]+) (\d+)$', msg.lower())
    bankRe = re.search(r'^!bank ([.|\S]+)$', msg)
    betCheckRe = re.search(r'^!bet check ([.|\S]+)$', msg)
  
    if msg == '!scores':
        config.pbpStop = True
        await ret.send(cmd.printScores(config.DATE))
    elif msg == "!pbp stop":
        config.pbpStop = True
    elif msg.startswith('!standings'):
        standingsReturn = cmd.printStandings()
        await ret.send(standingsReturn[0])
        await ret.send(standingsReturn[1])
    elif msg == "!tipoff help" or msg == "!tipoff" or msg == "!tipoff commands":
        await ret.send("https://tipoff-8f836.web.app/commands.html")
    elif msg == "!bank":
        mentionID = '<@' + str(message.author.id) + '>'
        await ret.send(mentionID + ": $" + str(cmd.getAmount(str(message.author.id))))
    elif msg == "!bet check":
        await ret.send(cmd.printBets(str(message.author.id)))
    elif scoresRe:
        config.pbpStop = True
        await ret.send(cmd.printScores(scoresRe.group(0)[14:18] + scoresRe.group(0)[8:10] + scoresRe.group(0)[11:13]))
    elif bsRe:
        gameInt = int(bsRe.group(0).ljust(12)[10:12])
        if gameInt > len(config.curr): 
            return
        retBoxScore = cmd.printBoxScore(config.currDate, config.curr[gameInt])
        (await ret.send(retBoxScore[0]) and await ret.send(retBoxScore[1])) if len(retBoxScore) == 2 else await ret.send(retBoxScore[0])
    elif pbpreg:
        config.pbpStop = False
        config.currPbp = int(pbpreg.group(0).ljust(6)[5:7])
        config.RECENT_EVENT = cmd.getEventId(config.currDate, config.currPbp)
        if config.currPbp > len(config.curr):
            return
        if cmd.livePlayByPlay(config.currDate, config.curr[config.currPbp]) == "Game not started":
            await ret.send(cmd.livePlayByPlay(config.currDate, config.curr[config.currPbp]))
        @tasks.loop(seconds=5)
        async def pbpLive():
            eventCount = cmd.getEventId(config.currDate, config.curr[config.currPbp])
            if not config.pbpStop and eventCount != config.RECENT_EVENT:
                await ret.send(cmd.livePlayByPlay(config.currDate, config.curr[config.currPbp]))
            elif not config.pb:
                config.RECENT_EVENT = eventCount
            pbpLive.start()
    elif bankRe:
        mentionID = bankRe.group(1)
        x = mentionID[2:len(mentionID) - 1]
        try:
            await ret.send(mentionID + ": $" + str(cmd.getAmount(x)))
        except:
            await ret.send("Bank robbed")
    elif betCheckRe:
        mentionID = betCheckRe.group(1)
        x = mentionID[2:len(mentionID) - 1]
        try:
            await ret.send(cmd.printBets(x))
        except:
            None
    elif betRe:
        f = open ('bank.json', "r")
        data = json.loads(f.read())
        if str(message.author.id) not in data:
            cmd.userFunds(message.author.id, 1000)
        f.close()
        gameNum = int(betRe.group(1))
        bettingTeam = str(cmd.isTeam(betRe.group(2)))
        if (gameNum <= len(config.curr) and bettingTeam != "No team" and cmd.correctTeam(config.curr[gameNum], bettingTeam) 
        and cmd.gameStatus(config.curr[gameNum],config.currDate) == "not started"):
            if cmd.getAmount(str(message.author.id)) < int(betRe.group(3)):
                await ret.send("Not enough funds bozo")
            else:
                cmd.giveAmount(str(message.author.id), "958759669139112038", int(betRe.group(3)))
                cmd.addBet(str(message.author.id),int(betRe.group(3)), config.curr[gameNum], bettingTeam, config.currDate)
                mentionID = '<@' + str(message.author.id) + '>'
                await ret.send(mentionID + " Succesfully betted $" + betRe.group(3) + " on the " + cmd.getTeam(bettingTeam))
        else:
            await ret.send("Invalid bet")
  
keep_alive()
config.client.run(os.environ['TOKEN'])
