import sys
import asyncio
import requests
from random import choice, randint
from discord import Game, Embed, File, FFmpegPCMAudio, VoiceClient
from discord.ext.commands import Bot

TOKEN = "lol nope"
client = Bot(command_prefix="dj!")


# list of channel IDs
mashup_posting = 123456789012345678
voice_channel =  123456789012345678
hall_of_mashup = 123456789012345678

original = dict()
recently_played = list()
now_playing = ""
voice_client = VoiceClient


async def getmashup():
    """
    Download every .mp3 from the latest 70 messages in mashup_posting, 
    then save them under./music with filename [song name]#by[artist].mp3

    Update original: a list of links to the original messages with the mashup 
    """

    posting = client.get_channel(mashup_posting)
    async for message in posting.history(limit=70):
        try:
            filename = message.attachments[0].filename
            url = message.attachments[0].url
            if filename[-4:] == ".mp3":
                # music/[song name]#by[artist].mp3
                filename = filename[:-4] + "#by" + message.author.name + ".mp3"
                req = requests.get(url, allow_redirects=True)
                with open("music/" + filename, "wb") as file:
                    file.write(req.content)
                music[filename] = message.jump_url
        except:
            # message doesn't contain an mp3, move on to the next message
            pass


async def playmashup():
    """
    Randomly choose a song to play from the music downloaded.
    Will avoid playing a song if it has been played less than
    15 songs ago.
    """
    await asyncio.sleep(10)
    global now_playing
    global voice_client
    if not voice_client.is_playing():
        now_playing = choice(list(music.keys()))
        while now_playing in recently_played:
            now_playing = choice(list(music.keys()))
        song = "music/" + now_playing
        audio_source = FFmpegPCMAudio(song)
        player = voice_client.play(audio_source)
        recently_played.append(now_playing)
     
        if len(recently_played) >= 10:
            recently_played.pop(0)


async def dj():
    """
    Async task for looping.
    """
    await client.wait_until_ready()
    await getmashup()
    while True:
        await playmashup()


@client.command(name="np",
                aliases=["nowplaying", "now_playing"],
                pass_context=True)
async def np(context):
    """
    Reply with a message listing the song name and the artist, and use
    embed to link to the original message.
    """
    global now_playing
    if now_playing == "":
        await context.channel.send("No song playing right now, please try again later")
    else:
        song = now_playing.split("#by")[0]
        artist = now_playing.split("#by")[1][:-4]
        content = "[" + song.replace("_", " ") + "](" + original[now_playing] + ") by " + artist

        embed = Embed(color=0x43b581)
        embed.add_field(name="🎵 Now Playing", value=content, inline=True)
        await context.channel.send(embed=embed)


@client.event
async def on_ready():
    global voice_client
    channel = client.get_channel(voice_channel)
    voice_client = await channel.connect()
    await client.change_presence(activity=Game("mashups"))
    print("Logged in as " + client.user.name)


@client.event
async def on_message(message):
    """
    A copy of the nowplaying command, triggered when the bot is mentioned.
    """
    if client.user.id in message.raw_mentions:
        global now_playing
        if now_playing == "":
            await message.channel.send("No song playing right now, please try again later")
        else:
            song = now_playing.split("#by")[0]
            artist = now_playing.split("#by")[1][:-4]
            content = "[" + song.replace("_", " ") + "](" + original[now_playing] + ") by " + artist

            embed = Embed(color=0x43b581)
            embed.add_field(name="🎵 Now Playing", value=content, inline=True)
            await message.channel.send(embed=embed)
    else:
        await client.process_commands(message)
        return


@client.event
async def on_raw_reaction_add(payload):
    """
    Let the user react to music they like with :approved: emote.
    If a song gets at least 5 approval, add it to the hall_of_mashup.
    """

    if payload.channel_id != mashup_posting:
        return

    if payload.emoji.name == "approved":
        posting = client.get_channel(mashup_posting)
        message = await posting.fetch_message(payload.message_id)
        print(message.reactions)
        reaction = next((c for c in message.reactions if str(c.emoji) == "<:approved:622815525407555594>"), None)
        
        if reaction.count >= 5:
            try:
                if str(message.id) in open("mashupcache.txt").read():
                    return

                filename = message.attachments[0].filename
                url = message.attachments[0].url
                if filename[-4:] == ".mp3":
                    song = filename
                    filename = filename[:-4] + "#by" + message.author.name + ".mp3"
                    req = requests.get(url, allow_redirects=True)
                    with open("music/" + filename, "wb") as file:
                        file.write(req.content)

                    embed = Embed(color=0x1e8d4b, title="🌟 Hall of Mashup")
                    song_link = "[" + song[:-4].replace("_", " ") + "](" + message.jump_url + ")"
                    embed.add_field(name="Song", value=song_link)
                    embed.add_field(name="Artist", value=message.author.name)

                    file = File(fp=open("music/" + filename, "rb"), filename=song)
                    hall = client.get_channel(hall_of_mashup)
                    await hall.send(embed=embed, file=file)

                    mashupcache = open("mashupcache.txt", "a")
                    mashupcache.write(str(message.id) + " ")
            except Exception as e:
                print(e)
        


client.loop.create_task(dj())
client.remove_command("help")
client.run(TOKEN)

