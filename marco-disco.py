# marco-discord.py
# Uses discord.py to intermediate between discord's API and a marco object.

import discord
import asyncio
# from discord.ext import commands
import random
import datetime, threading
from marco import marco

client = discord.Client()

@client.event
async def on_ready():
    """Initialize the marco module."""
    client.markov = marco()
    client.idle = False
    client.blacklisted_channels = []
    print('Logged in as ' + client.user.display_name)

@client.event
async def on_message(message):
    """Process message, potentially running a command, parsing input, and/or
    creating output.
    """
    text = message.clean_content
    if message.author != client.user:
        print('<<< ' + text)
    if client.idle != client.markov.silent:
        # silent state changed, update status
        await client.change_status(idle = client.markov.silent)
    if message.author.bot or client.markov.silent:
        # ignore bots: we don't want to parse our own output, and we also don't
        # want to start feedback loops with other bots
        return
    if text.startswith('!'):
        words = text.split()
        command = words[0]
        command = command[1:]
        # discord-specific commands
        if command == 'blacklist' and not message.channel.is_private:
            channel_id = message.channel.id
            if channel_id not in client.blacklisted_channels:
                client.blacklisted_channels.append(channel_id)
                await output(message.channel, (
                    'Channel blacklisted.'
                    ))
            else:
                await output(message.channel, (
                    'This channel is already blacklisted.'
                    ))
            return
        elif command == 'whitelist' and not channel.is_private:
            channel_id = channel.id
            if channel_id in client.blacklisted_channels:
                client.blacklisted_channels.remove(channel_id)
                await output(message.channel, (
                    'Channel removed from blacklist.'
                    ))
            else:
                await output(message.channel, (
                    'This channel is not blacklisted.'
                    ))
            return
        args = ' '.join(words[1:])
        silent_temp = client.markov.silent
        result = client.markov.command(command, args)
        await output(message.channel, result)
        return
    if message.channel in client.blacklisted_channels:
        return
    # replace bot mentions with the $you control signal
    text = text.replace('@' + client.user.display_name, '$you')
    result = client.markov.input(text)
    if not result:
        # force output on mention
        if message.mentions:
            mentions = message.mentions
            for mention in mentions:
                if mention == client.user:
                    result = client.markov.output()
        # always respond to private messages
        elif message.channel.is_private:
            result = client.markov.output()
    if result:
        # replace $you control signals with the name of the respondee
        result = result.replace('$you', '@' + message.author.display_name)
        await output(message.channel, result)

async def output(channel, string):
    """Output the given message to the given channel.

    Keyword arguments:
    channel: The channel to output to.
    string: The output.
    """
    if not string:
        return
    await client.send_typing(channel)
    await asyncio.sleep(len(string) / 50)
    print('>>> ' + string)
    await client.send_message(channel, string)

# Run the client.
token = open('./discord_api_token.txt').read()
client.run(token)
