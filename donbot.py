# donbot.py
import os
import random

from discord.ext import commands
from discord import FFmpegPCMAudio
from discord.utils import get
from dotenv import load_dotenv

load_dotenv()
token = os.getenv('DISCORD_TOKEN')

sounds = ['m_auw', 'm_hehe', 'm_wow', 'surprise', 'diablo', 'callate', 'idiota', 'freezer', 'goshi', 'ninos', 'shi', 'la_puta', 'el_peluca', 'goku_estupido', 'simio', 'dias']

bot = commands.Bot(command_prefix='*')
@bot.command(name='play')
async def soundBoard(ctx, arg):
    #await ctx.send(str(arg))
    #if len(arg) == 0 or len(arg) > 1:
    #    await ctx.send("Specify a sound:" + str(sounds))
    #    return
    if str(arg) in sounds:
        await playSound(ctx, str(arg) + ".mp3")
    else:
        await ctx.send("Specify a sound:" + str(sounds))
    return

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
    source = FFmpegPCMAudio(soundName)
    player = voice.play(source)

bot.run(token)
