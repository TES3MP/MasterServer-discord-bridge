import requests
from discord.ext import commands
from restClient import RestClient
import config
import json
from tableGen import TableGen, Column
from datetime import datetime

description = '''Masterserver admin bridge'''
bot = commands.Bot(command_prefix='?', description=description)

table_gen = TableGen([Column('Server addr', length=15), Column('Date', length=8), Column('Time', length=8),
                      Column('Reason', length=31, centred_content=False), Column('By', length=20)])


async def update_list(name, passw):
    rest = RestClient(name, passw)
    rest.banlist()
    result = rest.send()
    if result['code'] == 200:
        data = json.loads(result['response'])
    else:
        raise ValueError('You do not have permission to do this.')

    for entity in data:
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


@bot.event
async def on_message(message):  # Hack: check that channel is correct
    if message.channel.id == config.channel:
        await bot.process_commands(message)


@bot.command(pass_context=True)
async def ban(ctx, address: str, reason: str):
    tmp = await bot.say('Banning...')

    try:
        login = config.accounts[ctx.message.author.id]
        rest = RestClient(*login)
        rest.ban(address, reason)
        code = rest.send()['code']
        if code == 200:
            table_gen.clean()
            await bot.edit_message(tmp, '"{}" was banned.'.format(address))
        elif code == 403:
            await bot.edit_message(tmp, 'You do not have permission to do this.')
        elif code == 400:
            await bot.edit_message(tmp, 'Server not found')
    except KeyError:
        await bot.edit_message(tmp, 'You do not have permission to do this.')
    except requests.exceptions.RequestException:
        await bot.edit_message(tmp, 'Master server is down.')


@bot.command(pass_context=True)
async def unban(ctx, address: str):
    tmp = await bot.say('Unbanning...')

    try:
        login = config.accounts[ctx.message.author.id]
        rest = RestClient(*login)
        rest.unban(address)
        code = rest.send()['code']
        if code == 200:
            table_gen.clean()
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
        if table_gen.empty():
            login = config.accounts[ctx.message.author.id]
            await update_list(*login)
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
