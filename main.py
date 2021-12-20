import discord
import json
import os

from discord.ext import commands

bot = commands.Bot(command_prefix='?')

#to load the cogs from ./cogs folder
for filename in os.listdir('./cogs'):
  if filename.endswith('.py'):
    bot.load_extension(f'cogs.{filename[:-3]}')

@bot.event
async def on_ready():
  print("Bot now online")

bot.run(YOUR TOKEN)