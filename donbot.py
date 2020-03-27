# donbot.py
import os
import random

from discord.ext import commands
from discord import FFmpegPCMAudio
from discord.utils import get
from dotenv import load_dotenv

import pickle
import os.path
import io
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.http import MediaIoBaseDownload

from os import listdir
from os.path import isfile, join

from gtts import gTTS 

import time
from timeloop import Timeloop
from datetime import timedelta

INITIAL_PICKLES = 20
STEP_PICKLES = 2
SOUND_PRICE_PICKLES = 1

#-----------------------------------------
class PickleUser:
    def __init__(self, id, name):
        self.id = id
        self.name = name
        self.pickles = INITIAL_PICKLES
    
    def __str__(self):
        return f"{str(self.name)}<{str(self.id)}>: {str(self.pickles)}\t pickles."
#--------------------------------------------

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/drive.metadata.readonly', 'https://www.googleapis.com/auth/drive.apps.readonly', 'https://www.googleapis.com/auth/drive.readonly']
sounds = []
my_players = {}
bot = commands.Bot(command_prefix='*')
soundsPath = "/usr/src/app/sounds/"
timeloop = Timeloop()

def main():
    global sounds
    timeloop.start(block=False)
    sounds = initSounds()
    load_dotenv()
    token = os.getenv('DISCORD_TOKEN')
    bot.run(token)

@timeloop.job(interval=timedelta(minutes=1))
def sample_job_every_5s():
    print(f"Giving {STEP_PICKLES} pickles to everyone")
    global my_players
    if my_players:
        for playerKey in my_players.keys():
            my_players[playerKey].pickles += STEP_PICKLES
    

@bot.command(name='say')
async def say_discord(ctx, arg):
    if not canUseSound(ctx.author.id):
        await ctx.send("You cannot use this command because you are poor")
        return

    ctx.author.id
    text = arg
    language = 'es'
    speech = gTTS(text = text, lang = language, slow = False)
    speech.save(f'{soundsPath}text.mp3')
    await playSound(ctx, "text.mp3")

def canUseSound(userId):
    if userId == "204363336329068545":
        return True

    global my_players
    newBalance = my_players[userId].pickles - SOUND_PRICE_PICKLES
    if newBalance < 0:
        return False

    my_players[userId].pickles = newBalance
    return True

@bot.command(name='initSounds')
async def initSounds_discord(ctx):
    global sounds
    await ctx.send("Please wait, initializing sounds")
    sounds = initSounds()
    await ctx.send(f"Sounds have been initialized, list of sounds:{str(sounds)}")

@bot.command(name='initList')
async def initList_discord(ctx):
    global my_players
    await ctx.send("Initializing list of pickle members")
    for member in ctx.message.guild.members:
        if not member.id in my_players.keys():
            my_players[member.id] = PickleUser(member.id, member.name)
    await ctx.send("Pickle list ready")

@bot.command(name='showList')
async def showList_discord(ctx):
    global my_players
    completeList = ""
    for player in my_players.values():
        completeList += str(player) + "\n"
    await ctx.send(completeList)

@bot.command(name='p')
async def soundBoard(ctx, arg):
    if not canUseSound(ctx.author.id):
        await ctx.send("You cannot use this command because you are poor")
        return

    if str(arg) in sounds:
        await playSound(ctx, str(arg) + ".mp3")
    else:
        await ctx.send("Specify a sound:" + str(sounds))
    return

@bot.command(name='balance')
async def balance_discord(ctx):
    await ctx.send(f"Your pickle balance is {getBalance(ctx.author.id)}")

def getBalance(userId):
    global my_players
    return my_players[userId].pickles

async def playSound(ctx, soundName):
    channel = ctx.message.author.voice.channel
    if not channel:
        await ctx.send("You are not connected to a voice channel")
        return
    voice = get(bot.voice_clients, guild=ctx.guild)
    if voice and voice.is_connected():
        await voice.move_to(channel)
    else:
        voice = await channel.connect()
    source = FFmpegPCMAudio(f"{soundsPath}{soundName}")
    player = voice.play(source)

def connectToDrive():
    """Shows basic usage of the Drive v3 API.
    Prints the names and ids of the first 10 files the user has access to.
    """
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            authorization_url, state = flow.authorization_url(access_type='offline', login_hint='mhernaro@gmail.com', include_granted_scopes='true')
            creds = flow.run_local_server(port=31000)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('drive', 'v3', credentials=creds)
    return service

def initSounds():
    service = connectToDrive()
    results = service.files().list(
        q="mimeType='application/vnd.google-apps.folder' and name = 'sounds'",
        pageSize=10, fields="nextPageToken, files(id, name)").execute()
    items = results.get('files', [])

    if not items:
        print('Sounds folder not found')
    else:
        filesIndex = [f for f in listdir(soundsPath) if isfile(join(soundsPath, f))]
        folder=items[0]
        print(u'{0} ({1})'.format(folder['name'], folder['id']))
        folderId = folder['id']
        results = service.files().list(
            q=f"'{folderId}' in parents",
            pageSize=100, fields="nextPageToken, files(id, name)").execute()
        items = results.get('files', [])

        if not items:
            print('No audio files found')
        else:
            print('Files:')
            for item in items:
                print(u'{0} ({1})'.format(item['name'], item['id']))
                if not item['name'] in filesIndex:
                    downloadFile(item, service)
            return list(o['name'].replace('.mp3', '') for o in items)
                
def downloadFile(item, drive_service):
    request = drive_service.files().get_media(fileId=item['id'])
    fh = io.BytesIO()
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while done is False:
        status, done = downloader.next_chunk()
        print(f"Download {str(int(status.progress() * 100))}%.")
    path = f"{soundsPath}{item['name']}"
    print(f"Path: {path}")
    f = open(path, 'wb')
    f.write(fh.getbuffer())
    f.close()

if __name__ == '__main__':
    main()
