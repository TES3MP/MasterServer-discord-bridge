import discord
import requests
from discord.ext import commands
from restClient import RestClient
import config
import json
from tableGen import TableGen, Column
from datetime import datetime
from utils import is_valid_address

description = '''Masterserver admin bridge'''
bot = commands.Bot(command_prefix='?', description=description)

table_gen = TableGen([Column('Server addr', length=15), Column('Date', length=8), Column('Time', length=8),
                      Column('Reason', length=31, centred_content=False), Column('By', length=20)])

bans_cache_updated = True
bans_cache = []


def loadBans(name, passw):
    global bans_cache_updated
    global bans_cache
    rest = RestClient(name, passw)
    rest.banlist()
    result = rest.send()
    if result['code'] == 200:
        bans_cache = json.loads(result['response'])
    else:
        raise ValueError('You do not have permission to do this.')

    bans_cache_updated = False


async def update_list():
    print('we are here')
    table_gen.clean()
    for entity in bans_cache:
        timestamp = datetime.fromtimestamp(entity['date'])
        table_gen.add(entity['address'], str(timestamp.strftime("%d-%m-%y")), str(timestamp.time()), entity['reason'],
                      entity['by'])
    return


@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')
    await bot.change_presence(game=discord.Game(name=config.game_status))


@bot.event
async def on_command_error(exception, ctx):
    channel = discord.Object(id=config.channel)
    if ctx.command is None:
        await bot.send_message(channel, 'Exception "{}": {}'
                               .format(type(exception).__name__, exception))
    else:
        await bot.send_message(channel, 'Exception "{}" in command "{}": {}'
                               .format(type(exception).__name__, ctx.command, exception))


@bot.event
async def on_message(message):  # Hack: check that channel is correct
    if message.channel.id == config.channel:
        await bot.process_commands(message)


@bot.command(pass_context=True, description='Ban server.')
async def ban(ctx, address: str, reason: str):
    global bans_cache_updated
    tmp = await bot.say('Banning...')
    if not is_valid_address(address):
        await bot.edit_message(tmp, 'address "{}" is not correct'.format(address))
        return
    try:
        login = config.accounts[ctx.message.author.id]
        rest = RestClient(*login)
        rest.ban(address, reason)
        code = rest.send()['code']
        if code == 200:
            bans_cache_updated = True
            await bot.edit_message(tmp, '"{}" was banned.'.format(address))
        elif code == 403:
            await bot.edit_message(tmp, 'You do not have permission to do this.')
        elif code == 400:
            await bot.edit_message(tmp, 'Server not found')
    except KeyError:
        await bot.edit_message(tmp, 'You do not have permission to do this.')
    except requests.exceptions.RequestException:
        await bot.edit_message(tmp, 'Master server is down.')


@bot.command(pass_context=True, description='Unban server.')
async def unban(ctx, address: str):
    global bans_cache_updated
    tmp = await bot.say('Unbanning...')

    try:
        login = config.accounts[ctx.message.author.id]
        rest = RestClient(*login)
        rest.unban(address)
        code = rest.send()['code']
        if code == 200:
            bans_cache_updated = True
            await bot.edit_message(tmp, '"{}" was unbanned.'.format(address))
        elif code == 403:
            await bot.edit_message(tmp, 'You do not have permission to do this.')
        elif code == 400:
            await bot.edit_message(tmp, 'Server not found')

    except KeyError:
        await bot.edit_message(tmp, 'You do not have permission to do this.')
    except requests.exceptions.RequestException:
        await bot.edit_message(tmp, 'Master server is down.')


@bot.command(pass_context=True)
async def savebans(ctx):
    tmp = await bot.say('Saving...')
    try:
        login = config.accounts[ctx.message.author.id]
        rest = RestClient(*login)
        rest.savebans()
        code = rest.send()['code']
        if code == 200:
            await bot.edit_message(tmp, 'Banlist are saved')
        elif code == 403:
            await bot.edit_message(tmp, 'You do not have permission to do this.')
    except KeyError:
        await bot.edit_message(tmp, 'You do not have permission to do this.')
    except requests.exceptions.RequestException:
        await bot.edit_message(tmp, 'Master server is down.')


@bot.command(pass_context=True)
async def banlist(ctx):
    tmp = await bot.say('Loading list...')
    try:
        if bans_cache_updated:
            loadBans(*config.accounts[ctx.message.author.id])
            await update_list()
        for chunk in table_gen.chunks:
            msg = '```'
            for row in chunk:
                msg += row
            if len(msg) <= 2000:
                if tmp is not None:
                    await bot.edit_message(tmp, msg + '```')
                    tmp = None
                else:
                    await bot.say(msg + '```')
    except KeyError:
        await bot.edit_message(tmp, 'You do not have permission to do this.')
    except requests.exceptions.RequestException:
        await bot.edit_message(tmp, 'Master server is down.')
    except ValueError as err:
        await bot.edit_message(tmp, err)


@bot.command()
async def ping():
    await bot.say('pong!')


bot.run(config.token)
