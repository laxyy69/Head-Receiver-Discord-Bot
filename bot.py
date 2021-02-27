import discord
import json
import os
from keep_alive import keep_alive
from discord.ext import commands

intents = discord.Intents.default()
intents.members = True 

client = commands.Bot(command_prefix='.', intents=intents)

@client.event
async def on_ready():
    print(f"{client.user} is online.")


@client.event
async def on_member_join(member):
    with open('users.json') as f:
        users = json.load(f)

    await add_user(users, member)
    
    with open('users.json', 'w') as f:
        json.dump(users, f, indent=2)


@client.event
async def on_message(message):
    with open('users.json') as f:
        users = json.load(f)

    await add_user(users, message.author)
    await add_exp(users, message.author, int(len(message.content) / 1.5))
    await lvl_up(users, message.author, message.channel)

    with open('users.json', 'w') as f:
        json.dump(users, f, indent=2)

    await client.process_commands(message)


async def add_user(users, member):
    if not str(member.id) in users:
        users[member.id] = {}
        users[member.id]['exp'] = 0
        users[member.id]['lvl'] = 1
        with open('users.json', 'w') as f:
            json.dump(users, f, indent=2)


async def add_exp(users, member, exp):
    users[str(member.id)]['exp'] += exp


async def lvl_up(users, member, channel, lvl_down=False):
    exp = users[str(member.id)]['exp']
    lvl_start = users[str(member.id)]['lvl']
    lvl_end = int(exp ** (1/4))\

    #if lvl_down:
        #await channel.send('{} has leveled up to level {}'.format(member.mention, lvl_end))
        #users[str(member.id)]['lvl'] = lvl_end
    
    if lvl_start < lvl_end or lvl_down == True:
        await channel.send('{} has leveled up to level {}'.format(member.mention, lvl_end))
        users[str(member.id)]['lvl'] = lvl_end


@client.event
async def on_member_remove(member):
    print('A member has left the server ', member)
    

@client.command()
async def add(ctx, amount=None, *, member : discord.Member): # ADD !!!
    if not amount == None:
        with open('users.json') as f:
            users = json.load(f)
        old_exp = users[str(member.id)]['exp']
        users[str(member.id)]['exp'] += int(amount)
        await ctx.send(f"{member.mention} exp: {old_exp} + {amount} = {users[str(member.id)]['exp']}")
        await lvl_up(users, member, ctx.channel, True)
        with open('users.json', 'w') as f:
            json.dump(users, f, indent=2)


@client.command()
async def remove(ctx, amount=None, *, member : discord.Member): # REMOVE !!!
    if not amount == None:
        with open('users.json') as f:
            users = json.load(f)
        old_exp = users[str(member.id)]['exp']
        users[str(member.id)]['exp'] -= int(amount)
        await ctx.send(f"{member.mention} exp: {old_exp} - {amount} = {users[str(member.id)]['exp']}")
        await lvl_up(users, member, ctx.channel, True)
        with open('users.json', 'w') as f:
            json.dump(users, f, indent=2)


@client.command()
async def ping(ctx):
    await ctx.send(f'ping {round(client.latency * 1000)}ms')


@client.command()
async def clear(ctx, amount=100):
    amount += 1
    await ctx.channel.purge(limit=amount)


@client.command()
async def rank(ctx, member : discord.Member=None):
    with open('users.json') as f:
        users = json.load(f)
    exp = users[str(ctx.author.id) if member == None else str(member.id)]['exp']
    await ctx.send(f"{ctx.author.mention if member == None else member.mention} is level: {users[str(ctx.author.id) if member == None else str(member.id)]['lvl']}\nExp: {exp}")


@client.command()
async def kick(ctx, member : discord.Member, *, reason=None):
    await member.kick(reason=reason)
    await ctx.send(f'{member} got kicked.')


@client.command()
async def ban(ctx, member : discord.Member, *, reason=None):
    await member.ban(reason=reason)
    await ctx.send(f'{member} is banned from this server.')


@client.command()
async def bans(ctx):
    banned_users = await ctx.guild.bans()
    for ban_usr in banned_users:
        await ctx.send(ban_usr)


@client.command()
async def unban(ctx, *, member):
    banned_users = await ctx.guild.bans()
    member_name, member_discriminator = member.split('#')

    for ban_entry in banned_users:
        user = ban_entry.user
        if (user.name, user.discriminator) == (member_name, member_discriminator):
            await ctx.guild.unban(user)
            await ctx.send(f'{user.name}#{user.id} is now unbanned.')
            return

keep_alive()
client.run(os.getenv('TOKEN'))
