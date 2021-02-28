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
    general = client.get_channel(347364869357436941)
    await general.send(f"{client.user} is online.")


@client.event
async def on_member_join(member):
    with open('users.json') as f:
        users = json.load(f)

    await add_user(users, member)
    
    with open('users.json', 'w') as f:
        json.dump(users, f, indent=2)


@client.event
async def on_message(message):
    if not message.author.bot:
        if isinstance(message.channel, discord.DMChannel) and not (message.author == client.user):
            dm_base = client.get_channel(815396624918118421)
            await dm_base.send(f'{message.author} ({message.author.id}):\n{message.content}')

        with open('users.json') as f:
            users = json.load(f)

        await add_user(users, message.author)
        await add_exp(users, message.author, int(len(message.content) / 1.5))
        await lvl_up(users, message.author, message.channel)

        with open('users.json', 'w') as f:
            json.dump(users, f, indent=2)

        await client.process_commands(message)


@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        embe=discord.Embed(title="<:redcross:781952086454960138>Error", description="**Insufficient permissions!**", color=0x7289da)
        await ctx.send(embed=embe)
    else:
        await ctx.send("Error: something went wrong.")


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
    lvl_end = int(exp ** (1/4))
    
    if int(lvl_start) < lvl_end or lvl_down == True:
        await channel.send('{} has leveled up to level {}'.format(member.mention, lvl_end))
        users[str(member.id)]['lvl'] = lvl_end


@client.event
async def on_member_remove(member):
    print('A member has left the server ', member)


@client.command()
async def servers(ctx):
  servers = list(client.guilds)
  await ctx.send(f"Connected on {str(len(servers))} servers:")
  await ctx.send('\n'.join(guild.name for guild in servers))


@client.command()
@commands.has_permissions(administrator=True)
async def dm(ctx, member : discord.Member, *, msg):
    await member.send(msg)
    

@client.command()
@commands.has_permissions(administrator=True)
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
@commands.has_permissions(administrator=True)
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
@commands.has_permissions(administrator=True)
async def set_level(ctx, lvl, *, member : discord.Member):
    with open('users.json') as f:
        users = json.load(f)
    
    users[str(member.id)]['lvl'] = lvl

    with open('users.json', 'w') as f:
        json.dump(users, f, indent=2)

    await rank(ctx, member)


@client.command()
async def ping(ctx):
    await ctx.send(f'ping {round(client.latency * 1000)}ms')


@client.command()
@commands.has_permissions(manage_messages=True)
async def clear(ctx, amount=100):
    amount += 1
    await ctx.channel.purge(limit=amount)


@client.command()
async def rank(ctx, member : discord.Member=None):
    if member == None or not member.bot:
        with open('users.json') as f:
            users = json.load(f)
        exp = users[str(ctx.author.id) if member == None else str(member.id)]['exp']
        await ctx.send(f"{ctx.author.mention if member == None else member.mention} is level: {users[str(ctx.author.id) if member == None else str(member.id)]['lvl']}\nExp: {exp}")
    else:
        await ctx.send(f"Bots don't have a rank.")


@client.command()
@commands.has_permissions(administrator=True)
async def all_ranks(ctx):
    with open('users.json') as f:
        users = json.load(f)
    for user_id in users:
        user = client.get_user(int(user_id))
        await ctx.send(f"{user}: Level: {users[str(user.id)]['lvl']}  -  Exp: {users[str(user.id)]['exp']}")


@client.command()
@commands.has_permissions(kick_members=True)
async def kick(ctx, member : discord.Member, *, reason=None):
    await member.kick(reason=reason)
    await ctx.send(f'{member} got kicked.')


@client.command()
@commands.has_permissions(ban_members=True)
async def ban(ctx, member : discord.Member, *, reason=None):
    await member.ban(reason=reason)
    await ctx.send(f'{member} is banned from this server.')


@client.command()
async def bans(ctx):
    banned_users = await ctx.guild.bans()
    if len(banned_users) > 0:
        for ban_usr in banned_users:
            await ctx.send(ban_usr)
    else:
        await ctx.send('There are nobody banned from this server.')


@client.command()
@commands.has_permissions(ban_members=True)
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
client.run(os.getenv('SUPER_SECRET_TOKEN_THAT_YOU_WONT_SEE'))
