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
        if str(message.guild.id) in data:
          if str(message.author.id) in data[str(message.guild.id)]:
            xp = data[str(message.guild.id)][str(message.author.id)]['xp']
            lvl = data[str(message.guild.id)][str(message.author.id)]['level']
  
            #increase the xp by the number which has 100 as its multiple
            increased_xp = xp+25
            new_level = int(increased_xp/100)
  
            data[str(message.guild.id)][str(message.author.id)]['xp']=increased_xp
  
            with open("levels.json", "w") as f:
              json.dump(data, f)
  
            if new_level > lvl:
              await message.channel.send(f"{message.author.mention} Just Leveled Up to Level {new_level}!!!")
  
              data[str(message.guild.id)][str(message.author.id)]['level']=new_level
              data[str(message.guild.id)][str(message.author.id)]['xp']=0
  
              with open("levels.json", "w") as f:
                json.dump(data, f)
              
              for i in range(len(level)):
                if new_level == level_num[i]:
                  await message.author.add_roles(discord.utils.get(message.author.guild.roles, name=level[i]))
  
                  mbed = discord.Embed(title=f"{message.author} You Have Gotten role **{level[i]}**!", color = message.author.colour)
                  mbed.set_thumbnail(url=message.author.avatar_url)
                  await message.channel.send(embed=mbed)
            return
  
        if str(message.guild.id) in data:
          data[str(message.guild.id)][str(message.author.id)] = {}
          data[str(message.guild.id)][str(message.author.id)]['xp'] = 0
          data[str(message.guild.id)][str(message.author.id)]['level'] = 1
        else:
          data[str(message.guild.id)] = {}
          data[str(message.guild.id)][str(message.author.id)] = {}
          data[str(message.guild.id)][str(message.author.id)]['xp'] = 0
          data[str(message.guild.id)][str(message.author.id)]['level'] = 1
  
        with open("levels.json", "w") as f:
          json.dump(data, f)
  
        with open("userdata.json", "r") as f:
          user_data = json.load(f)
  
        if str(message.author.id) in user_data:
          pass
        else:
          #these are the default value for user rank card
          user_data[str(message.author.id)] = {}
          user_data[str(message.author.id)]['card'] = 5
          user_data[str(message.author.id)]['text_color'] = "#ff9933"
          user_data[str(message.author.id)]['bar_color'] = "#ff9933"
          user_data[str(message.author.id)]['blend'] = 1
  
        with open("userdata.json", "w") as f:
          json.dump(user_data, f)

  @commands.command(name="rank")
  async def rank(self, ctx: commands.Context, user: Optional[discord.Member]):
    userr = user or ctx.author

    with open("levels.json", "r") as f:
      data = json.load(f)

    with open("userdata.json", "r") as f:
      user_data = json.load(f)

    xp = data[str(ctx.guild.id)][str(userr.id)]["xp"]
    lvl = data[str(ctx.guild.id)][str(userr.id)]["level"]

    next_level_xp = (lvl+1) * 100
    xp_need = next_level_xp
    xp_have = data[str(ctx.guild.id)][str(userr.id)]["xp"]

    card_num = str(user_data[str(userr.id)]['card'])
    text_color = str(user_data[str(userr.id)]['text_color'])
    bar_color = str(user_data[str(userr.id)]['bar_color'])
    blend = int(user_data[str(userr.id)]['blend'])

    percentage = int(((xp_have * 100)/ xp_need))

    if percentage < 1:
      percentage = 0
    
    ## Rank card
    background = Editor(f"{card_num}.png")
    profile = await load_image_async(str(userr.avatar_url))

    profile = Editor(profile).resize((150, 150)).circle_image()
    
    poppins = Font.poppins(size=40)
    poppins_small = Font.poppins(size=30)

    #you can skip this part, I'm adding this because the text is difficult to read in my selected image
    if blend == 1:
      ima = Editor("zBLACK.png")
      background.blend(image=ima, alpha=.5, on_top=False)

    background.paste(profile.image, (30, 30))

    background.rectangle((30, 220), width=650, height=40, fill="#fff", radius=20)
    background.bar(
        (30, 220),
        max_width=650,
        height=40,
        percentage=percentage,
        fill=bar_color,
        radius=20,
    )
    background.text((200, 40), str(userr.name), font=poppins, color=text_color)

    background.rectangle((200, 100), width=350, height=2, fill=bar_color)
    background.text(
        (200, 130),
        f"Level : {lvl}   "
        + f" XP : {xp} / {(lvl+1) * 100}",
        font=poppins_small,
        color=text_color,
    )

    card = File(fp=background.image_bytes, filename="zCARD.png")
    await ctx.send(file=card)

  @commands.command(name="leaderboard")
  async def leaderboard(self, ctx, range_num=5):
    with open("levels.json", "r") as f:
      data = json.load(f)

    l = {}
    total_xp = []

    for userid in data[str(ctx.guild.id)]:
      xp = int(data[str(ctx.guild.id)][str(userid)]['xp']+(int(data[str(ctx.guild.id)][str(userid)]['level'])*100))

      l[xp] = f"{userid};{data[str(ctx.guild.id)][str(userid)]['level']};{data[str(ctx.guild.id)][str(userid)]['xp']}"
      total_xp.append(xp)

    total_xp = sorted(total_xp, reverse=True)
    index=1

    mbed = discord.Embed(
      title="Leaderboard Command Results"
    )

    for amt in total_xp:
      id_ = int(str(l[amt]).split(";")[0])
      level = int(str(l[amt]).split(";")[1])
      xp = int(str(l[amt]).split(";")[2])

      member = await self.bot.fetch_user(id_)

      if member is not None:
        name = member.name
        mbed.add_field(name=f"{index}. {name}",
        value=f"**Level: {level} | XP: {xp}**", 
        inline=False)

        if index == range_num:
          break
        else:
          index += 1

    await ctx.send(embed = mbed)

  @commands.command("rank_reset")
  async def rank_reset(self, ctx, user: Optional[discord.Member]):
    member = user or ctx.author

    #this if statement will check that user who's using this command is trying to remove his data or any other user data
    #if she is trying to remove any other user's data then we are going to check that he has a specific role or not (in my case its 'Bot-Mod') so that only admins can remov any users data and not other people can remove other
    if not member == ctx.author:
      role = discord.utils.get(ctx.author.guild.roles, name="Bot-Mod")

      if not role in member.roles:
        await ctx.send(f"You can only reset your data, to reset other data you must have {role.mention} role")
        return 
    
    with open("levels.json", "r") as f:
      data = json.load(f)

    del data[str(ctx.guild.id)][str(member.id)]

    with open("levels.json", "w") as f:
      json.dump(data, f)

    await ctx.send(f"{member.mention}'s Data Got reset")
  
  @commands.command(name="increase_level")
  @commands.has_role("Bot-Mod")
  async def increase_level(self, ctx, increase_by: int, user: Optional[discord.Member]):
    member = user or ctx.author

    with open("levels.json", "r") as f:
      data = json.load(f)
    
    data[str(ctx.guild.id)][str(member.id)]['level'] += increase_by

    with open("levels.json", "w") as f:
      json.dump(data, f)
    
    await ctx.send(f"{member.mention}, Your level was increased by {increase_by}")

  @commands.command(name="increase_xp")
  @commands.has_role("Bot-Mod")
  async def increase_xp(self, ctx, increase_by: int, user: Optional[discord.Member]):
    member = user or ctx.author

    with open("levels.json", "r") as f:
      data = json.load(f)

    data[str(ctx.guild.id)][str(member.id)]['xp'] += increase_by

    with open("levels.json", "w") as f:
      json.dump(data, f)

    await ctx.send(f"{member.mention}, Your Xp was increased by {increase_by}")

def setup(client):
  client.add_cog(Levelsys(client))