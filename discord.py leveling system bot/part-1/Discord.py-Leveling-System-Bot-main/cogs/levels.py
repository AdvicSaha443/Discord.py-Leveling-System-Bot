import discord
import json

from discord import File
from discord.ext import commands
from typing import Optional
from easy_pil import Editor, load_image_async, Font

#if you want to give role to the user at any specific level upgrade then you can do like this
#enter the name of the role in a list
level = ["Level-5+", "Level-10+", "Level-15+"]

#add the level number at which you want to give the role
level_num = [5, 10, 15]

class Levelsys(commands.Cog):
  def __init__(self, bot):
    self.bot = bot

  @commands.Cog.listener()
  async def on_ready(self):
    print("Leveling Cog Ready!")

  #this will increase the user's xp everytime they message
  @commands.Cog.listener()
  async def on_message(self, message):

    #the bot's prefix is ? that's why we are adding this statement so user's xp doesn't increase when they use any commands
    if not message.content.startswith("?"):

      #checking if the bot has not sent the message
      if not message.author.bot:
        with open("levels.json", "r") as f:
          data = json.load(f)
        
        #checking if the user's data is already there in the file or not
        if str(message.author.id) in data:
          xp = data[str(message.author.id)]['xp']
          lvl = data[str(message.author.id)]['level']

          #increase the xp by the number which has 100 as its multiple
          increased_xp = xp+25
          new_level = int(increased_xp/100)

          data[str(message.author.id)]['xp']=increased_xp

          with open("levels.json", "w") as f:
            json.dump(data, f)

          if new_level > lvl:
            await message.channel.send(f"{message.author.mention} Just Leveled Up to Level {new_level}!!!")

            data[str(message.author.id)]['level']=new_level
            data[str(message.author.id)]['xp']=0

            with open("levels.json", "w") as f:
              json.dump(data, f)
            
            for i in range(len(level)):
              if new_level == level_num[i]:
                await message.author.add_roles(discord.utils.get(message.author.guild.roles, name=level[i]))

                mbed = discord.Embed(title=f"{message.author} You Have Gotten role **{level[i]}**!", color = message.author.colour)
                mbed.set_thumbnail(url=message.author.avatar_url)
                await message.channel.send(embed=mbed)
        else:
          data[str(message.author.id)] = {}
          data[str(message.author.id)]['xp'] = 0
          data[str(message.author.id)]['level'] = 1

          with open("levels.json", "w") as f:
            json.dump(data, f)

  @commands.command(name="rank")
  async def rank(self, ctx: commands.Context, user: Optional[discord.Member]):
    userr = user or ctx.author

    with open("levels.json", "r") as f:
      data = json.load(f)

    xp = data[str(userr.id)]["xp"]
    lvl = data[str(userr.id)]["level"]

    next_level_xp = (lvl+1) * 100
    xp_need = next_level_xp
    xp_have = data[str(userr.id)]["xp"]

    percentage = int(((xp_have * 100)/ xp_need))

    if percentage < 1:
      percentage = 0
    
    ## Rank card
    background = Editor(f"zIMAGE.png")
    profile = await load_image_async(str(userr.avatar_url))

    profile = Editor(profile).resize((150, 150)).circle_image()
    
    poppins = Font.poppins(size=40)
    poppins_small = Font.poppins(size=30)

    #you can skip this part, I'm adding this because the text is difficult to read in my selected image
    ima = Editor("zBLACK.png")
    background.blend(image=ima, alpha=.5, on_top=False)

    background.paste(profile.image, (30, 30))

    background.rectangle((30, 220), width=650, height=40, fill="#fff", radius=20)
    background.bar(
        (30, 220),
        max_width=650,
        height=40,
        percentage=percentage,
        fill="#ff9933",
        radius=20,
    )
    background.text((200, 40), str(userr.name), font=poppins, color="#ff9933")

    background.rectangle((200, 100), width=350, height=2, fill="#ff9933")
    background.text(
        (200, 130),
        f"Level : {lvl}   "
        + f" XP : {xp} / {(lvl+1) * 100}",
        font=poppins_small,
        color="#ff9933",
    )

    card = File(fp=background.image_bytes, filename="zCARD.png")
    await ctx.send(file=card)

def setup(client):
  client.add_cog(Levelsys(client))