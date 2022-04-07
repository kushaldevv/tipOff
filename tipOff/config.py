from datetime import datetime
from pytz import timezone
import discord

DATE = datetime.now(timezone('EST')).strftime("%Y%m%d")
client = discord.Client()
curr = {}
currDate = DATE
currPbp = 0
RECENT_EVENT = 0
pbpStop = False