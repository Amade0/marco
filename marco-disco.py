# marco-discord.py
# Uses discord.py to intermediate between discord's API and a marco object.

import discord
import asyncio
import random
import datetime, threading
import os.path
from marco import marco

client = discord.Client()

@client.event
async def on_ready():
    """Initialize the marco module."""
    client.markov = marco()
    client.idle = False
    if os.path.isfile('./discord_blacklist.psv'):
        client.blacklisted_channels = open('./discord_blacklist.psv').read()
    else:
        client.blacklisted_channels = ''
    print('Logged in as ' + client.user.display_name)

@client.event
async def on_message(message):
    """Process message, potentially running a command, parsing input, and/or
    creating output.
    """
    text = message.clean_content
    channel = message.channel
    channel_id = '(' + str(channel.id) + ')'
    # if message.author != client.user:
        # print('<<< ' + text)
    if client.idle != client.markov.silent:
        # silent state changed, update status
        client.idle = client.markov.silent
        await client.change_status(client.idle)
    if message.author.bot:
        # ignore bots: we don't want to parse our own output, and we also don't
        # want to start feedback loops with other bots
        return
    if text.startswith('!'):
        words = text.split()
        command = words[0]
        command = command[1:]
        # discord-specific commands
        if command == 'blacklist' and not channel.is_private:
            if channel_id not in client.blacklisted_channels:
                client.blacklisted_channels = (
                        client.blacklisted_channels + channel_id
                        )
                await output(message.channel, (
                    'Channel blacklisted.'
                    ))
                save_blacklist()
            else:
                await output(message.channel, (
                    'This channel is already blacklisted.'
                    ))
            return
        elif command == 'whitelist' and not channel.is_private:
            if channel_id in client.blacklisted_channels:
                client.blacklisted_channels = (
                    client.blacklisted_channels.replace(channel_id, '')
                    )
                await output(message.channel, (
                    'Channel removed from blacklist.'
                    ))
                save_blacklist()
            else:
                await output(message.channel, (
                    'This channel is not blacklisted.'
                    ))
            return
        args = ' '.join(words[1:])
        result = client.markov.command(command, args)
        await output(message.channel, result)
        return
    if channel.id in client.blacklisted_channels or client.markov.silent:
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
        elif channel.is_private:
            result = client.markov.output()
    if result:
        # replace $you control signals with the name of the respondee
        result = result.replace('$you', '@' + message.author.display_name)
        await output(channel, result)

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
    # print('>>> ' + string)
    await client.send_message(channel, string)

def save_blacklist():
    """Save the blacklist to discord_blacklist.psv."""
    blacklist = client.blacklisted_channels
    blacklist_file = open('./discord_blacklist.psv', 'w')
    blacklist_file.write(blacklist)
    blacklist_file.close()

# Run the client.
token = open('./discord_api_token.txt').read()
client.run(token)

