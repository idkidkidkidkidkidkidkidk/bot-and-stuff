import sys
import asyncio
import aiohttp
import requests
from random import randint
from bs4 import BeautifulSoup
from discord import Game, Embed
from discord.utils import get
from discord.ext.commands import Bot
from arsenic import get_session, browsers, services, keys

TOKEN = "lol nope"
client = Bot(command_prefix="/")

GECKODRIVER = "./geckodriver.exe"
ADMINS = [123456789012345678, 123456789012345678]

@client.command(name="decide",
                aliases=["eightball", "eight_ball"],
                description="Answer a yes/no question like BillyWAR.",
                brief="Answer a yes/no question.",
                pass_context=False)
async def decide():
    possible_responses = [
        "Nope",
        "Nah",
        "Of course not",
        "Probably not",
        "Probably",
        "Maybe",
        "Of course",
        "Yeah",
        "Definitely",
        "Idk",
        "P much",
        "P much"

    ]
    await context.message.channel.send(possible_responses[randint(0, len(possible_responses) - 1)])


@client.command(name="flipcoin",
                aliases=["flipacoin", "flip", "coin", "justflipacoin"],
                pass_context=True)
async def justflipacoin(context):
    msg = await context.message.channel.send("Flipping coin...")
    if randint(0, 1) == 0:
        await msg.edit("HEADS")
    else:
        await msg.edit("TAILS")


@client.command(name="mashup",
                pass_context=True)
async def mashup(context):
    # msg = await client.say("Mashing...")
    url = "https://rave.dj/mix"
    service = services.Geckodriver(binary=GECKODRIVER)
    browser = browsers.Firefox()
    
    async with get_session(service, browser) as session:
        await session.get(url)
        search = await session.wait_for_element(10, "input[class=search-input]")
        songs = context.message.content[8:].split(",")
        for song in songs:
            if song[0] == ' ':
                await search.send_keys(song[1:])
            else:
                await search.send_keys(song)
            await search.send_keys(keys.ENTER)
            await search.send_keys(keys.ENTER)
            result = await session.wait_for_element(10, "div[style=order: 0;]")
            # wip
        await asyncio.sleep(10)


@client.command(name="ping",
                pass_context=False)
async def ping():
    if randint(0, 5) == 0:
        await context.message.channel("No u")
        await context.message.channel("/ping")
    else:
        await context.message.channel("Pong")
    
    


## ------------------------------------------- ##
##             "advanced" commands             ##
## ------------------------------------------- ##


@client.command(name="flirt",
                pass_context=True)
async def flirt(context):
    attempt = context.message.content[7:]
    attempt = attempt.replace("ä", "ae")
    attempt = attempt.replace("ö", "oe")
    attempt = attempt.replace("ü", "ue")
    attempt = attempt.replace("ß", "ss")
    attempt = attempt.lower()

    score = 0
    if attempt == "ich finde dich suess":
        score = 1
    elif attempt == "deine augen sind wie sterne":
        score = 2
    elif attempt == "du siehst aus wie meine naechste freundin":
        score = 3

    if score == 0:
        possible_responses = [
            "Ewww, no thanks",
            "Ewww, nein danke",
            "Ew, is that English?",
            "Ew, ist das Englisch?",
            "Ewww"
        ]
        await client.say(possible_responses[randint(0, len(possible_responses) - 1)])
        await client.say("*You might want to get some help on flirting with her.*")
        return

    flirter = context.message.author.id
    bfscore = open("bfscore.txt", "r+")
    content = bfscore.read()
    pos = content.find(flirter)
    if pos == -1:
        bfscore.write(" " + flirter + " 0")
        bfscore.seek(0, 0)
        content = bfscore.read()
        pos = content.find(flirter)

    bfscore.seek(pos, 0)
    current_score = int(bfscore.read(len(flirter) + 2)[-1])
    # print(current_score)
    bfscore.seek(pos, 0)

    if current_score == 0:
        if score == 1:
            await client.say("Nein du uwu")
            bfscore.write(flirter + " 1")
        else:
            await client.say("Do I know you?")
    elif current_score == 1:
        if score == 1:
            await client.say("But... You already said that...")
        elif score == 2:
            await client.say("Du bringst mich zum Erröten >///<")
            bfscore.write(flirter + " 2")
        elif score == 3:
            await client.say("We don't know each other well enough yet...")
    elif current_score == 2:
        if score == 1 or score == 2:
            await client.say("But... You already said that...")
        elif score == 3:
            await client.say("Aww >w<")
            await client.say("*BillyBOT resetted. Check your roles!*")
            boyfriend = context.message.author
            await client.add_roles(boyfriend, get(boyfriend.server.roles, name="BillyBOT's Boyfriend"))
            bfscore.write(flirter + " 0")
    bfscore.close()


@client.command(name="lhc",
                aliases=["hasthelargehadroncolliderdestroyedtheworldyet","superlongcommand"],
                pass_context=False)
async def lhc():
    url = "http://hasthelargehadroncolliderdestroyedtheworldyet.com/"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            raw_response = await resp.text()
            soup = BeautifulSoup(raw_response, "html.parser")
            await client.say(soup.find("noscript").string)


@client.command(name="peakefficiencyflip",
                aliases=["justflipacoinbutitsanactualwebsite"],
                pass_context=False)
async def peakefficiencyflip():
    msg = await client.say("Flipping coin...")
    url = "https://justflipacoin.com/"
    service = services.Geckodriver(binary=GECKODRIVER)
    browser = browsers.Firefox()
    
    async with get_session(service, browser) as session:
        await session.get(url)
        res = await session.wait_for_element(10, 'span[class=start]')
        await client.edit_message(msg, await res.get_text())



@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if str(message.channel.type) != "private":
        await client.process_commands(message)
        return

    if message.author.id in ADMINS and message.content[:3] == "/dm":
        # /dm [recipient id] [message]
        command = message.content.split(" ", 2)
        await client.get_user(int(command[1])).create_dm()
        recipient = await client.get_user(int(command[1])).dm_channel
        content = command[2]
        await recipient.send(content)

    elif message.author.id in ADMINS and message.content[:4] == "/log":
        # /log [subject id] [limit]
        command = message.content.split(" ", 2)
        await client.get_user(int(command[1])).create_dm()
        subject = client.get_user(int(command[1])).dm_channel
        async for msg in subject.history(limit=int(command[2]), oldest_first=True):
            await message.channel.send("**" + str(msg.author) + ":** "+ msg.content)
            try:
                print("attachments:" + msg.attachments[0]["url"])
            except:
                pass
            await asyncio.sleep(0.5)

    else:
        # send the dm to admins
        for admin in ADMINS:
            await client.get_user(admin).create_dm()
            recipient = client.get_user(admin).dm_channel
            sender = "**" + str(message.author) + "** (" + str(message.author.id) + ")"
            content = sender+ ": " + message.content
            await recipient.send(content)
            


@client.event
async def on_reaction_add(reaction, user):
    if str(reaction.emoji) == "⭐":
        if reaction.count >= 1:
            if str(reaction.message.id) in open("starcache.txt").read():
                return
            channel = client.get_channel(reaction.message.channel.id)
            await client.send_message(channel, "star: " + str(reaction.count))
            
            author = reaction.message.author.name
            content = reaction.message.content
            embed = Embed(title="Author", description=author, color=0x43b581)
            embed.add_field(name="Content", value=content, inline=True)

            starboard = client.get_channel(reaction.message.channel.id)
            starcache = open("starcache.txt", "a")
            starcache.write(str(reaction.message.id) + " ")
            await starboard.send_message(embed=embed)


@client.event
async def on_ready():
    await client.change_presence(activity=Game("Mixcraft 8"))
    print("Logged in as " + client.user.name)


client.remove_command("help")
client.run(TOKEN)
