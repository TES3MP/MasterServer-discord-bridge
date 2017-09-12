import discord
import requests
from discord.ext import commands
import random


import config
from restClient import RestClient

description = '''Masterserver admin bridge'''
bot = commands.Bot(command_prefix='?', description=description)

@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')

@bot.event
async def on_message(message): # Hack: check that channel is correct
    if message.channel.id == config.channel:
        await bot.process_commands(message)

@bot.command(pass_context=True)
async def ban(ctx, address : str, reason : str):
    tmp = await bot.say('Banning...')

    try:
        login = config.accounts[ctx.message.author.id]
        rest = RestClient(*login)
        rest.ban(address, reason)
        status_code = rest.send()
        await bot.edit_message(tmp, '"{}" was banned.'.format(address))
    except KeyError:
        await bot.edit_message(tmp, 'You do not have permission to do this.')
    except requests.exceptions.RequestException:
        await bot.edit_message(tmp, 'Master server is down.')

@bot.command(pass_context=True)
async def unban(ctx, address : str):
    tmp = await bot.say('Unbanning...')

    try:
        login = config.accounts[ctx.message.author.id]
        rest = RestClient(*login)
        rest.unban(address)
        status_code = rest.send()
        await bot.edit_message(tmp, '"{}" was unbanned.'.format(address))
    except KeyError:
        await bot.edit_message(tmp, 'You do not have permission to do this.')
    except requests.exceptions.RequestException:
        await bot.edit_message(tmp, 'Master server is down.')

@bot.command()
async def banlist():
    await bot.say('todo: banlist()')

@bot.command()
async def ping():
    await bot.say('pong!')


bot.run(config.token)
