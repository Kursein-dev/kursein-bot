# pyright: reportGeneralTypeIssues=false
# pyright: reportOptionalMemberAccess=false
# pyright: reportArgumentType=false
# type: ignore
import discord
from discord.ext import commands, tasks
import os
import re
from datetime import datetime, timedelta, timezone
import json
import asyncio
from typing import Optional, Union
from dotenv import load_dotenv
import aiohttp
from urllib.parse import quote
import db

load_dotenv()

# Bot Version: 3.1.0 - Streamlined (Tokyo Ghoul + Rocket League theme)

# File paths
REMINDERS_FILE = "reminders.json"
PREFIXES_FILE = "prefixes.json"
BUMP_CONFIG_FILE = "bump_config.json"
RL_RANKS_FILE = "rl_ranks.json"
RL_PROFILES_FILE = "rl_profiles.json"
STREAMS_CONFIG_FILE = "streams_config.json"
DEFAULT_PREFIX = "~"

DISBOARD_BOT_ID = 302050872383242240
ERROR_CHANNEL_ID = 1435009092782522449
STREAM_CHANNEL_ID = 1442613254546526298
BUMP_CHANNEL_ID = 1418819741471997982
BUMP_ROLE_ID = 1436421726727700542

HARDCODED_STREAMERS = [
    {'platform': 'twitch', 'username': 'kursein', 'live': False},
    {'platform': 'twitch', 'username': 'hikarai_', 'live': False},
    {'platform': 'twitch', 'username': 'warinspanish209', 'live': False},
    {'platform': 'twitch', 'username': 'loafylmaoo', 'live': False},
]

# Admin/Staff IDs
OWNER_ID = 343055455263916045
ADMIN_IDS = {697495071737511997, 187729483174903808, 343055455263916045, 525815097847840798, 760075655374176277}

# In-memory data
reminders = []
prefixes = {}
bump_config = {}
rl_ranks = {}
rl_profiles = {}
streams_config = {}

# Twitch API tokens
twitch_access_token = None
twitch_token_expiry = None

# Rocket League Ranks
RL_RANKS = {
    0: {"name": "Unranked", "emoji": "⚪", "color": 0x808080},
    1: {"name": "Bronze I", "emoji": "<:Bronze1:1438556246990127246>", "color": 0xCD7F32},
    2: {"name": "Bronze II", "emoji": "<:Bronze2:1438564385978323024>", "color": 0xCD7F32},
    3: {"name": "Bronze III", "emoji": "<:Bronze3:1438556325339594903>", "color": 0xCD7F32},
    4: {"name": "Silver I", "emoji": "<:Silver1:1438556374979186800>", "color": 0xC0C0C0},
    5: {"name": "Silver II", "emoji": "<:Silver2:1438564703876943914>", "color": 0xC0C0C0},
    6: {"name": "Silver III", "emoji": "<:Silver3:1438556422718623836>", "color": 0xC0C0C0},
    7: {"name": "Gold I", "emoji": "<:Gold1:1438556470001008641>", "color": 0xFFD700},
    8: {"name": "Gold II", "emoji": "<:Gold2:1438556611302916096>", "color": 0xFFD700},
    9: {"name": "Gold III", "emoji": "<:Gold3:1438556538133286972>", "color": 0xFFD700},
    10: {"name": "Platinum I", "emoji": "<:Platinum1:1438556692362039307>", "color": 0x00BFFF},
    11: {"name": "Platinum II", "emoji": "<:Platinum2:1438556763728248833>", "color": 0x00BFFF},
    12: {"name": "Platinum III", "emoji": "<:Platinum3:1438556855831105689>", "color": 0x00BFFF},
    13: {"name": "Diamond I", "emoji": "<:Diamond1:1438556935095062680>", "color": 0x6A5ACD},
    14: {"name": "Diamond II", "emoji": "<:Diamond2:1438556980506525776>", "color": 0x6A5ACD},
    15: {"name": "Diamond III", "emoji": "<:Diamond3:1438557028783100088>", "color": 0x6A5ACD},
    16: {"name": "Champion I", "emoji": "<:Champion1:1438557083451523102>", "color": 0x9B59B6},
    17: {"name": "Champion II", "emoji": "<:Champion2:1438557142276898876>", "color": 0x9B59B6},
    18: {"name": "Champion III", "emoji": "<:Champion3:1438557199545798686>", "color": 0x9B59B6},
    19: {"name": "Grand Champion I", "emoji": "<:GrandChampion1:1438557252507140117>", "color": 0xDC143C},
    20: {"name": "Grand Champion II", "emoji": "<:GrandChampion2:1438557312817041590>", "color": 0xDC143C},
    21: {"name": "Grand Champion III", "emoji": "<:GrandChampion3:1438557361483550821>", "color": 0xDC143C},
    22: {"name": "Supersonic Legend", "emoji": "<:SupersonicLegend:1438557403892416563>", "color": 0xFF1493}
}

# =====================
# DATA PERSISTENCE
# =====================

def load_reminders():
    global reminders
    if db.is_db_available():
        reminders = db.load_data('reminders', [])
    elif os.path.exists(REMINDERS_FILE):
        try:
            with open(REMINDERS_FILE, 'r') as f:
                reminders = json.load(f)
        except:
            reminders = []

def save_reminders():
    try:
        if db.is_db_available():
            db.save_data('reminders', reminders)
        with open(REMINDERS_FILE, 'w') as f:
            json.dump(reminders, f, indent=2)
    except Exception as e:
        print(f"Error saving reminders: {e}")

def load_prefixes():
    global prefixes
    if db.is_db_available():
        prefixes = db.load_data('prefixes', {})
    elif os.path.exists(PREFIXES_FILE):
        try:
            with open(PREFIXES_FILE, 'r') as f:
                prefixes = json.load(f)
        except:
            prefixes = {}

def save_prefixes():
    try:
        if db.is_db_available():
            db.save_data('prefixes', prefixes)
        with open(PREFIXES_FILE, 'w') as f:
            json.dump(prefixes, f, indent=2)
    except Exception as e:
        print(f"Error saving prefixes: {e}")

def load_bump_config():
    global bump_config
    if db.is_db_available():
        bump_config = db.load_data('bump_config', {})
    elif os.path.exists(BUMP_CONFIG_FILE):
        try:
            with open(BUMP_CONFIG_FILE, 'r') as f:
                bump_config = json.load(f)
        except:
            bump_config = {}

def save_bump_config():
    try:
        if db.is_db_available():
            db.save_data('bump_config', bump_config)
        with open(BUMP_CONFIG_FILE, 'w') as f:
            json.dump(bump_config, f, indent=2)
    except Exception as e:
        print(f"Error saving bump config: {e}")

def load_rl_ranks():
    global rl_ranks
    if db.is_db_available():
        rl_ranks = db.load_data('rl_ranks', {})
    elif os.path.exists(RL_RANKS_FILE):
        try:
            with open(RL_RANKS_FILE, 'r') as f:
                rl_ranks = json.load(f)
        except:
            rl_ranks = {}

def save_rl_ranks():
    try:
        if db.is_db_available():
            db.save_data('rl_ranks', rl_ranks)
        with open(RL_RANKS_FILE, 'w') as f:
            json.dump(rl_ranks, f, indent=2)
    except Exception as e:
        print(f"Error saving RL ranks: {e}")

def load_rl_profiles():
    global rl_profiles
    if db.is_db_available():
        rl_profiles = db.load_data('rl_profiles', {})
    elif os.path.exists(RL_PROFILES_FILE):
        try:
            with open(RL_PROFILES_FILE, 'r') as f:
                rl_profiles = json.load(f)
        except:
            rl_profiles = {}

def save_rl_profiles():
    try:
        if db.is_db_available():
            db.save_data('rl_profiles', rl_profiles)
        with open(RL_PROFILES_FILE, 'w') as f:
            json.dump(rl_profiles, f, indent=2)
    except Exception as e:
        print(f"Error saving RL profiles: {e}")

def load_streams_config():
    global streams_config
    if db.is_db_available():
        streams_config = db.load_data('streams_config', {})
        if streams_config:
            print(f"[STREAMS] Loaded config from database: {len(streams_config)} guilds")
    elif os.path.exists(STREAMS_CONFIG_FILE):
        try:
            with open(STREAMS_CONFIG_FILE, 'r') as f:
                streams_config = json.load(f)
        except:
            streams_config = {}

def save_streams_config():
    try:
        if db.is_db_available():
            db.save_data('streams_config', streams_config)
        with open(STREAMS_CONFIG_FILE, 'w') as f:
            json.dump(streams_config, f, indent=2)
    except Exception as e:
        print(f"Error saving streams config: {e}")

# =====================
# TWITCH API
# =====================

async def get_twitch_access_token():
    global twitch_access_token, twitch_token_expiry
    
    client_id = os.getenv('TWITCH_CLIENT_ID')
    client_secret = os.getenv('TWITCH_CLIENT_SECRET')
    
    if not client_id or not client_secret:
        print("[TWITCH] Missing TWITCH_CLIENT_ID or TWITCH_CLIENT_SECRET")
        return None
    
    try:
        async with aiohttp.ClientSession() as session:
            data = {
                'client_id': client_id,
                'client_secret': client_secret,
                'grant_type': 'client_credentials'
            }
            async with session.post('https://id.twitch.tv/oauth2/token', data=data, timeout=aiohttp.ClientTimeout(total=5)) as resp:
                if resp.status == 200:
                    result = await resp.json()
                    twitch_access_token = result.get('access_token')
                    twitch_token_expiry = datetime.now(timezone.utc) + timedelta(seconds=result.get('expires_in', 3600))
                    print(f"[TWITCH] Got new access token")
                    return twitch_access_token
                else:
                    print(f"[TWITCH] Failed to get token: {resp.status}")
                    return None
    except Exception as e:
        print(f"[TWITCH] Error getting access token: {e}")
        return None

async def get_twitch_stream_data(username: str):
    global twitch_access_token, twitch_token_expiry
    
    client_id = os.getenv('TWITCH_CLIENT_ID')
    
    if not twitch_access_token or (twitch_token_expiry and datetime.now(timezone.utc) >= twitch_token_expiry):
        twitch_access_token = await get_twitch_access_token()
    
    if not twitch_access_token or not client_id:
        return None
    
    try:
        async with aiohttp.ClientSession() as session:
            headers = {
                'Client-ID': client_id,
                'Authorization': f'Bearer {twitch_access_token}'
            }
            async with session.get(f'https://api.twitch.tv/helix/users?login={username}', headers=headers, timeout=aiohttp.ClientTimeout(total=5)) as resp:
                if resp.status != 200:
                    return None
                users = await resp.json()
                if not users.get('data'):
                    return None
                user_id = users['data'][0]['id']
            
            async with session.get(f'https://api.twitch.tv/helix/streams?user_id={user_id}', headers=headers, timeout=aiohttp.ClientTimeout(total=5)) as resp:
                if resp.status != 200:
                    return None
                streams = await resp.json()
                if streams.get('data'):
                    stream = streams['data'][0]
                    return {
                        'is_live': True,
                        'title': stream.get('title', 'No title'),
                        'game_name': stream.get('game_name', 'Unknown'),
                        'viewer_count': stream.get('viewer_count', 0),
                        'thumbnail_url': stream.get('thumbnail_url', '').replace('{width}', '1280').replace('{height}', '720')
                    }
                return {'is_live': False}
    except Exception as e:
        print(f"[TWITCH] Error getting stream data: {e}")
        return None

# =====================
# BOT SETUP
# =====================

def get_prefix(bot, message):
    if message is None or not hasattr(message, 'guild') or not message.guild:
        return DEFAULT_PREFIX
    return prefixes.get(str(message.guild.id), DEFAULT_PREFIX)

def get_prefix_from_ctx(ctx):
    if ctx.guild:
        return prefixes.get(str(ctx.guild.id), DEFAULT_PREFIX)
    return DEFAULT_PREFIX

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix=get_prefix, intents=intents, help_command=None)

@bot.event
async def on_ready():
    if bot.user:
        print(f'Logged in as {bot.user.name} (ID: {bot.user.id})')
    print('------')
    
    if db.is_db_available():
        try:
            db.init_database()
            print("[DB] Database connected and initialized")
        except Exception as e:
            print(f"[DB] Database initialization failed: {e}")
    
    load_reminders()
    load_prefixes()
    load_bump_config()
    load_rl_ranks()
    load_rl_profiles()
    load_streams_config()
    
    if not check_reminders.is_running():
        check_reminders.start()
        print("Started reminder checker task")
    
    if not check_streams.is_running():
        check_streams.start()
        print("Started stream checker task")
    
    print("Starting slash command sync...")
    try:
        await asyncio.sleep(2)
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} slash command(s) globally")
    except Exception as e:
        print(f"Error syncing commands: {e}")

@bot.event
async def on_message(message):
    await bot.process_commands(message)
    
    if message.author.id == DISBOARD_BOT_ID and message.embeds:
        embed = message.embeds[0]
        if embed.description and "Bump done" in embed.description:
            remind_at = datetime.now() + timedelta(hours=2)
            bump_reminder = {
                "type": "bump",
                "guild_id": message.guild.id,
                "channel_id": BUMP_CHANNEL_ID,
                "role_id": BUMP_ROLE_ID,
                "remind_at": remind_at.isoformat(),
                "completed": False
            }
            reminders.append(bump_reminder)
            save_reminders()
            print(f"Bump detected in {message.guild.name}. Reminder set for 2 hours.")

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        return
    
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ You don't have permission to use this command.")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"❌ Missing argument: `{error.param.name}`")
    else:
        await ctx.send("❌ An error occurred. Please try again.")

# =====================
# BACKGROUND TASKS
# =====================

@tasks.loop(minutes=1)
async def check_reminders():
    now = datetime.now()
    completed = []
    
    for reminder in reminders:
        if reminder.get('completed'):
            continue
        
        try:
            remind_at = datetime.fromisoformat(reminder['remind_at'])
            if now >= remind_at:
                if reminder.get('type') == 'bump':
                    channel = bot.get_channel(BUMP_CHANNEL_ID)
                    if channel:
                        mention = f"<@&{BUMP_ROLE_ID}>"
                        embed = discord.Embed(
                            title="🔔 Time to Bump!",
                            description=f"{mention}\n\nThe 2-hour cooldown is over! Use `/bump` to bump the server on DISBOARD.",
                            color=0x00FF00
                        )
                        await channel.send(mention, embed=embed)
                
                reminder['completed'] = True
                completed.append(reminder)
        except Exception as e:
            print(f"Error processing reminder: {e}")
    
    if completed:
        for r in completed:
            if r in reminders:
                reminders.remove(r)
        save_reminders()

@check_reminders.before_loop
async def before_check_reminders():
    await bot.wait_until_ready()

@tasks.loop(minutes=2)
async def check_streams():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'text/html,application/xhtml+xml',
    }
    
    channel = bot.get_channel(STREAM_CHANNEL_ID)
    if not channel:
        return
    
    for streamer in HARDCODED_STREAMERS:
        username = streamer['username']
        is_live = False
        stream_data = {}
        
        try:
            stream_data = await get_twitch_stream_data(username)
            if stream_data:
                is_live = stream_data.get('is_live', False)
            else:
                async with aiohttp.ClientSession() as session:
                    async with session.get(f'https://www.twitch.tv/{username}', headers=headers, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                        if resp.status == 200:
                            text = await resp.text()
                            is_live = '"isLiveBroadcast":true' in text or '"isLive":true' in text
        except Exception as e:
            print(f"[STREAMS] Error checking {username}: {e}")
            continue
        
        if is_live and not streamer.get('live'):
            try:
                title = stream_data.get('title', 'No title') if stream_data else 'No title'
                game = stream_data.get('game_name', 'Unknown') if stream_data else 'Unknown'
                viewers = stream_data.get('viewer_count', 0) if stream_data else 0
                
                message = f"""━━━━━━━━━━━━━━━━━━━━━━━━━━
[ LIVE ] TWITCH STREAM ALERT
━━━━━━━━━━━━━━━━━━━━━━━━━━

Streamer: **{username}**
Title   : {title}
Game    : **{game}**
Viewers : **{viewers:,}** watching

Watch Here:
https://twitch.tv/{username}

━━━━━━━━━━━━━━━━━━━━━━━━━━"""
                
                await channel.send(message)
            except Exception as e:
                print(f"[STREAMS] Error sending notification: {e}")
        
        streamer['live'] = is_live

@check_streams.before_loop
async def before_check_streams():
    await bot.wait_until_ready()

# =====================
# COMMANDS - BUMP REMINDERS
# =====================

@bot.hybrid_command(name='bumpinfo')
async def bump_info(ctx):
    """View bump reminder status"""
    channel = bot.get_channel(BUMP_CHANNEL_ID)
    pending_reminders = [r for r in reminders if not r.get('completed')]
    
    embed = discord.Embed(title="🔔 Bump Reminder Info", color=0x00FF00)
    embed.add_field(name="Channel", value=channel.mention if channel else f"<#{BUMP_CHANNEL_ID}>", inline=True)
    embed.add_field(name="Ping Role", value=f"<@&{BUMP_ROLE_ID}>", inline=True)
    embed.add_field(name="Pending Reminders", value=str(len(pending_reminders)), inline=True)
    
    if pending_reminders:
        next_reminder = min(pending_reminders, key=lambda r: r.get('remind_at', ''))
        try:
            remind_at = datetime.fromisoformat(next_reminder['remind_at'])
            remaining = remind_at - datetime.now()
            mins = int(remaining.total_seconds() // 60)
            embed.add_field(name="Next Reminder", value=f"In {mins} minutes", inline=False)
        except:
            pass
    
    await ctx.send(embed=embed)

# =====================
# COMMANDS - STREAM NOTIFICATIONS
# =====================

@bot.hybrid_command(name='list')
async def stream_list(ctx):
    """View monitored streamers"""
    lines = []
    for s in HARDCODED_STREAMERS:
        status = '🔴' if s.get('live') else '⚫'
        url = f"https://twitch.tv/{s['username']}"
        lines.append(f"{status} **[{s['username']}]({url})**")
    
    embed = discord.Embed(
        title="📺 Monitored Streamers",
        description="\n".join(lines),
        color=0x9146FF
    )
    embed.set_footer(text="Notifications go to #stream-notifications")
    await ctx.send(embed=embed)

# =====================
# COMMANDS - ROCKET LEAGUE
# =====================

@bot.hybrid_command(name='setrank', aliases=['rlrank'])
async def set_rl_rank(ctx, *, rank_input: str):
    """Set your Rocket League rank"""
    rank_input_lower = rank_input.lower().strip()
    
    matched_rank = None
    for rank_id, rank_data in RL_RANKS.items():
        if rank_data['name'].lower() == rank_input_lower:
            matched_rank = rank_id
            break
    
    if matched_rank is None:
        for rank_id, rank_data in RL_RANKS.items():
            if rank_input_lower in rank_data['name'].lower():
                matched_rank = rank_id
                break
    
    if matched_rank is None:
        rank_list = "\n".join([f"{data['emoji']} {data['name']}" for data in RL_RANKS.values()])
        await ctx.send(f"❌ Invalid rank. Available ranks:\n{rank_list}")
        return
    
    rl_ranks[str(ctx.author.id)] = matched_rank
    save_rl_ranks()
    
    rank_data = RL_RANKS[matched_rank]
    embed = discord.Embed(
        title="🚀 Rank Set!",
        description=f"{rank_data['emoji']} **{rank_data['name']}**",
        color=rank_data['color']
    )
    await ctx.send(embed=embed)

@bot.hybrid_command(name='rllb', aliases=['rlleaderboard'])
async def rl_leaderboard(ctx):
    """Show Rocket League rank leaderboard"""
    if not rl_ranks:
        await ctx.send("No players have set their RL rank yet!")
        return
    
    sorted_ranks = sorted(rl_ranks.items(), key=lambda x: x[1], reverse=True)[:10]
    
    lines = []
    for i, (user_id, rank_val) in enumerate(sorted_ranks, 1):
        user = bot.get_user(int(user_id))
        name = user.display_name if user else f"User {user_id}"
        rank_data = RL_RANKS.get(rank_val, RL_RANKS[0])
        lines.append(f"`{i}.` {rank_data['emoji']} **{name}** - {rank_data['name']}")
    
    embed = discord.Embed(
        title="🏆 Rocket League Leaderboard",
        description="\n".join(lines),
        color=0x00BFFF
    )
    await ctx.send(embed=embed)

@bot.hybrid_command(name='setrlprofile', aliases=['linkrl'])
async def set_rl_profile(ctx, platform: str, *, username: str):
    """Link your Rocket League Tracker profile"""
    valid_platforms = ['epic', 'steam', 'psn', 'xbl']
    platform = platform.lower()
    
    if platform not in valid_platforms:
        await ctx.send(f"❌ Invalid platform. Use: {', '.join(valid_platforms)}")
        return
    
    rl_profiles[str(ctx.author.id)] = {'username': username, 'platform': platform}
    save_rl_profiles()
    
    await ctx.send(f"✅ Linked **{username}** on **{platform.upper()}**")

@bot.hybrid_command(name='stats', aliases=['rlstats', 'rlprofile'])
async def rl_stats(ctx, member: Optional[discord.Member] = None):
    """View Rocket League stats from Tracker.gg"""
    target = member or ctx.author
    profile = rl_profiles.get(str(target.id))
    
    if not profile:
        await ctx.send(f"❌ No RL profile linked. Use `{get_prefix_from_ctx(ctx)}setrlprofile <platform> <username>`")
        return
    
    api_key = os.getenv('TRACKER_API_KEY')
    if not api_key:
        await ctx.send("❌ Tracker API not configured")
        return
    
    try:
        async with aiohttp.ClientSession() as session:
            url = f"https://api.tracker.gg/api/v2/rocket-league/standard/profile/{profile['platform']}/{quote(profile['username'])}"
            headers = {'TRN-Api-Key': api_key}
            
            async with session.get(url, headers=headers) as resp:
                if resp.status != 200:
                    await ctx.send("❌ Could not fetch stats")
                    return
                
                data = await resp.json()
                segments = data.get('data', {}).get('segments', [])
                
                embed = discord.Embed(
                    title=f"🚀 {profile['username']}'s RL Stats",
                    color=0x00BFFF
                )
                
                for segment in segments[:3]:
                    if segment.get('type') == 'playlist':
                        playlist = segment.get('metadata', {}).get('name', 'Unknown')
                        stats = segment.get('stats', {})
                        rank = stats.get('tier', {}).get('metadata', {}).get('name', 'Unranked')
                        mmr = stats.get('rating', {}).get('value', 0)
                        embed.add_field(name=playlist, value=f"{rank}\nMMR: {mmr}", inline=True)
                
                await ctx.send(embed=embed)
    except Exception as e:
        await ctx.send(f"❌ Error fetching stats: {e}")

# =====================
# COMMANDS - UTILITY
# =====================

@bot.hybrid_command(name='profile')
async def profile_command(ctx, member: Optional[discord.Member] = None):
    """View a user's profile"""
    target = member or ctx.author
    
    embed = discord.Embed(
        title=f"{target.display_name}'s Profile",
        color=target.color if target.color != discord.Color.default() else 0x5865F2
    )
    embed.set_thumbnail(url=target.display_avatar.url)
    
    rank_val = rl_ranks.get(str(target.id), 0)
    rank_data = RL_RANKS.get(rank_val, RL_RANKS[0])
    embed.add_field(name="🚀 RL Rank", value=f"{rank_data['emoji']} {rank_data['name']}", inline=True)
    
    if target.joined_at:
        embed.add_field(name="📅 Joined", value=target.joined_at.strftime("%b %d, %Y"), inline=True)
    
    user_bumps = sum(1 for r in reminders if r.get('completed', False))
    embed.add_field(name="🔔 Server Bumps", value=str(user_bumps), inline=True)
    
    await ctx.send(embed=embed)

@bot.hybrid_command(name='guide')
async def guide_command(ctx):
    """Show all available commands"""
    prefix = get_prefix_from_ctx(ctx)
    
    embed = discord.Embed(
        title="📚 Kursein Bot Guide",
        description="Tokyo Ghoul + Rocket League themed bot",
        color=0x5865F2
    )
    
    embed.add_field(name="🚀 Rocket League", value=f"""
`{prefix}setrank <rank>` - Set your RL rank
`{prefix}rllb` - Rank leaderboard
`{prefix}setrlprofile <platform> <user>` - Link Tracker
`{prefix}stats [@user]` - View RL stats
`{prefix}profile [@user]` - View profile
    """, inline=False)
    
    embed.add_field(name="🔔 Bump Reminders", value=f"""
`{prefix}bumpinfo` - View bump reminder status
    """, inline=False)
    
    embed.add_field(name="📺 Stream Notifications", value=f"""
`{prefix}list` - View monitored streamers
    """, inline=False)
    
    await ctx.send(embed=embed)

# Run the bot
if __name__ == "__main__":
    token = os.getenv('DISCORD_BOT_TOKEN')
    if token:
        bot.run(token)
    else:
        print("Error: DISCORD_BOT_TOKEN not found")
