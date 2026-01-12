# pyright: reportGeneralTypeIssues=false
# pyright: reportOptionalMemberAccess=false
# pyright: reportArgumentType=false
# type: ignore
import discord
from discord import app_commands
from discord.ext import commands, tasks
import os
import re
import time
from datetime import datetime, timedelta, timezone
import json
import asyncio
import random
from typing import Optional, Union
from dotenv import load_dotenv
import aiohttp
from urllib.parse import quote
import db
from google import genai
from google.genai import types

load_dotenv()

# Bot Version: 3.0.0 - Rebuilt from ground up (Tokyo Ghoul + Rocket League theme)

# File paths
REMINDERS_FILE = "reminders.json"
PREFIXES_FILE = "prefixes.json"
BUMP_CONFIG_FILE = "bump_config.json"
VERIFIED_USERS_FILE = "verified_users.json"
RL_RANKS_FILE = "rl_ranks.json"
RL_PROFILES_FILE = "rl_profiles.json"
STREAMS_CONFIG_FILE = "streams_config.json"
STAFF_FILE = "staff.json"
KARUTA_WISHLISTS_FILE = "karuta_wishlists.json"
KARUTA_COOLDOWNS_FILE = "karuta_cooldowns.json"
KARUTA_SETTINGS_FILE = "karuta_settings.json"
PROFILE_BANNERS_FILE = "profile_banners.json"
DEFAULT_PREFIX = "~"

DISBOARD_BOT_ID = 302050872383242240
KARUTA_BOT_ID = 646937666251915264
ERROR_CHANNEL_ID = 1435009092782522449

# Admin/Staff IDs
OWNER_ID = 343055455263916045  # kursein
ADMIN_IDS = {697495071737511997, 187729483174903808, 343055455263916045, 525815097847840798, 760075655374176277}
MOD_IDS = {504812129560428554}
JRMOD_IDS = {878870610158178335, 1131474199286907000}
STAFF_IDS = ADMIN_IDS | MOD_IDS | JRMOD_IDS | {OWNER_ID}

# In-memory data
reminders = []
prefixes = {}
bump_config = {}
staff_data = {}
verified_users = set()
rl_ranks = {}
rl_profiles = {}
streams_config = {}
karuta_wishlists = {}
karuta_cooldowns = {}
karuta_settings = {}
profile_banners = {}

# Twitch API tokens
twitch_access_token = None
twitch_token_expiry = None

# Karuta cooldown durations (in seconds)
KARUTA_COOLDOWNS = {
    'drop': 30 * 60,
    'daily': 24 * 60 * 60,
    'vote': 12 * 60 * 60,
    'grab': 10 * 60,
    'work': 12 * 60 * 60,
    'visit': 2 * 60 * 60,
}

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

def load_verified_users():
    global verified_users
    if db.is_db_available():
        data = db.load_data('verified_users', [])
        verified_users = set(data) if isinstance(data, list) else set()
    elif os.path.exists(VERIFIED_USERS_FILE):
        try:
            with open(VERIFIED_USERS_FILE, 'r') as f:
                verified_users = set(json.load(f))
        except:
            verified_users = set()

def save_verified_users():
    try:
        if db.is_db_available():
            db.save_data('verified_users', list(verified_users))
        with open(VERIFIED_USERS_FILE, 'w') as f:
            json.dump(list(verified_users), f, indent=2)
    except Exception as e:
        print(f"Error saving verified users: {e}")

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

def load_staff_data():
    global staff_data
    if db.is_db_available():
        staff_data = db.load_data('staff_data', {})
    elif os.path.exists(STAFF_FILE):
        try:
            with open(STAFF_FILE, 'r') as f:
                staff_data = json.load(f)
        except:
            staff_data = {}

def save_staff_data():
    try:
        if db.is_db_available():
            db.save_data('staff_data', staff_data)
        with open(STAFF_FILE, 'w') as f:
            json.dump(staff_data, f, indent=2)
    except Exception as e:
        print(f"Error saving staff data: {e}")

def load_karuta_wishlists():
    global karuta_wishlists
    if db.is_db_available():
        karuta_wishlists = db.load_data('karuta_wishlists', {})
    elif os.path.exists(KARUTA_WISHLISTS_FILE):
        try:
            with open(KARUTA_WISHLISTS_FILE, 'r') as f:
                karuta_wishlists = json.load(f)
        except:
            karuta_wishlists = {}

def save_karuta_wishlists():
    try:
        if db.is_db_available():
            db.save_data('karuta_wishlists', karuta_wishlists)
        with open(KARUTA_WISHLISTS_FILE, 'w') as f:
            json.dump(karuta_wishlists, f, indent=2)
    except Exception as e:
        print(f"Error saving Karuta wishlists: {e}")

def load_karuta_cooldowns():
    global karuta_cooldowns
    if db.is_db_available():
        karuta_cooldowns = db.load_data('karuta_cooldowns', {})
    elif os.path.exists(KARUTA_COOLDOWNS_FILE):
        try:
            with open(KARUTA_COOLDOWNS_FILE, 'r') as f:
                karuta_cooldowns = json.load(f)
        except:
            karuta_cooldowns = {}

def save_karuta_cooldowns():
    try:
        if db.is_db_available():
            db.save_data('karuta_cooldowns', karuta_cooldowns)
        with open(KARUTA_COOLDOWNS_FILE, 'w') as f:
            json.dump(karuta_cooldowns, f, indent=2)
    except Exception as e:
        print(f"Error saving Karuta cooldowns: {e}")

def load_karuta_settings():
    global karuta_settings
    if db.is_db_available():
        karuta_settings = db.load_data('karuta_settings', {})
    elif os.path.exists(KARUTA_SETTINGS_FILE):
        try:
            with open(KARUTA_SETTINGS_FILE, 'r') as f:
                karuta_settings = json.load(f)
        except:
            karuta_settings = {}

def save_karuta_settings():
    try:
        if db.is_db_available():
            db.save_data('karuta_settings', karuta_settings)
        with open(KARUTA_SETTINGS_FILE, 'w') as f:
            json.dump(karuta_settings, f, indent=2)
    except Exception as e:
        print(f"Error saving Karuta settings: {e}")

def load_profile_banners():
    global profile_banners
    if db.is_db_available():
        profile_banners = db.load_data('profile_banners', {})
    elif os.path.exists(PROFILE_BANNERS_FILE):
        try:
            with open(PROFILE_BANNERS_FILE, 'r') as f:
                profile_banners = json.load(f)
        except:
            profile_banners = {}

def save_profile_banners():
    try:
        if db.is_db_available():
            db.save_data('profile_banners', profile_banners)
        with open(PROFILE_BANNERS_FILE, 'w') as f:
            json.dump(profile_banners, f, indent=2)
    except Exception as e:
        print(f"Error saving profile banners: {e}")

# =====================
# TWITCH API
# =====================

async def get_twitch_access_token():
    """Get Twitch OAuth access token using Client Credentials"""
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
    """Get live stream data from Twitch API"""
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
    
    # Initialize database
    if db.is_db_available():
        try:
            db.init_database()
            print("[DB] Database connected and initialized")
        except Exception as e:
            print(f"[DB] Database initialization failed: {e}")
    
    # Load all data
    load_reminders()
    load_prefixes()
    load_bump_config()
    load_verified_users()
    load_rl_ranks()
    load_rl_profiles()
    load_streams_config()
    load_staff_data()
    load_karuta_wishlists()
    load_karuta_cooldowns()
    load_karuta_settings()
    load_profile_banners()
    
    # Start background tasks
    if not check_reminders.is_running():
        check_reminders.start()
        print("Started reminder checker task")
    
    if not check_streams.is_running():
        check_streams.start()
        print("Started stream checker task")
    
    if not check_karuta_cooldowns_task.is_running():
        check_karuta_cooldowns_task.start()
        print("Started Karuta cooldown checker task")
    
    # Sync slash commands
    print("Starting slash command sync...")
    try:
        await asyncio.sleep(2)
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} slash command(s) globally")
        
        for guild in bot.guilds:
            try:
                await bot.tree.sync(guild=guild)
            except:
                pass
        
        # Send startup notification
        update_channel = bot.get_channel(1435009184285589554)
        if update_channel:
            startup_embed = discord.Embed(
                title="🟢 Bot Online",
                description="Kursein v3.0 - Rebuilt from the ground up!",
                color=0x2ecc71,
                timestamp=datetime.now()
            )
            startup_embed.add_field(name="Commands", value=f"{len(synced)} synced", inline=True)
            startup_embed.add_field(name="Servers", value=f"{len(bot.guilds)}", inline=True)
            startup_embed.add_field(name="Members", value=f"{sum(g.member_count or 0 for g in bot.guilds):,}", inline=True)
            startup_embed.set_footer(text="Tokyo Ghoul + Rocket League Theme")
            await update_channel.send(embed=startup_embed)
    except Exception as e:
        print(f"Error syncing commands: {e}")

@bot.event
async def on_message(message):
    await bot.process_commands(message)
    
    # Handle Karuta bot messages
    if message.author.id == KARUTA_BOT_ID:
        await handle_karuta_message(message)
        return
    
    # Track Karuta commands for cooldowns
    if not message.author.bot:
        content = message.content.lower()
        if content.startswith(('k!drop', 'k!d ', 'kd')):
            await track_karuta_cooldown(message.author.id, 'drop')
        elif content.startswith(('k!daily', 'k!da')):
            await track_karuta_cooldown(message.author.id, 'daily')
        elif content.startswith('k!vote'):
            await track_karuta_cooldown(message.author.id, 'vote')
        elif content.startswith(('k!work', 'k!w ')):
            await track_karuta_cooldown(message.author.id, 'work')
        elif content.startswith(('k!visit', 'k!vi')):
            await track_karuta_cooldown(message.author.id, 'visit')
    
    # Check for DISBOARD bump
    if message.author.id == DISBOARD_BOT_ID and message.embeds:
        embed = message.embeds[0]
        if embed.description and "Bump done" in embed.description:
            guild_id = str(message.guild.id)
            if guild_id in bump_config:
                config = bump_config[guild_id]
                remind_at = datetime.now() + timedelta(hours=2)
                bump_reminder = {
                    "type": "bump",
                    "guild_id": message.guild.id,
                    "channel_id": config.get("channel_id"),
                    "ping_target": config.get("ping_target"),
                    "ping_type": config.get("ping_type", "user"),
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
    
    try:
        error_channel = bot.get_channel(ERROR_CHANNEL_ID)
        if error_channel:
            embed = discord.Embed(
                title="⚠️ Command Error",
                description=f"```{str(error)[:1000]}```",
                color=0xFF0000,
                timestamp=datetime.now()
            )
            embed.add_field(name="Command", value=ctx.message.content[:100] if ctx.message else "Unknown", inline=False)
            embed.add_field(name="User", value=f"{ctx.author} ({ctx.author.id})", inline=True)
            embed.add_field(name="Server", value=ctx.guild.name if ctx.guild else "DM", inline=True)
            await error_channel.send(embed=embed)
    except:
        pass
    
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
    """Check and send due reminders"""
    now = datetime.now()
    completed = []
    
    for reminder in reminders:
        if reminder.get('completed'):
            continue
        
        try:
            remind_at = datetime.fromisoformat(reminder['remind_at'])
            if now >= remind_at:
                if reminder.get('type') == 'bump':
                    channel = bot.get_channel(reminder['channel_id'])
                    if channel:
                        ping_type = reminder.get('ping_type', 'user')
                        ping_target = reminder['ping_target']
                        
                        if ping_type == 'role':
                            mention = f"<@&{ping_target}>"
                        else:
                            mention = f"<@{ping_target}>"
                        
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
    """Check if streamers are live"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'text/html,application/xhtml+xml',
    }
    
    for guild_id, config in streams_config.items():
        try:
            guild = bot.get_guild(int(guild_id))
            if not guild or not config.get('channel_id') or not config.get('role_id'):
                continue
            
            channel = bot.get_channel(config['channel_id'])
            role = guild.get_role(config['role_id'])
            if not channel or not role:
                continue
            
            for streamer in config.get('streamers', []):
                platform = streamer.get('platform', '').lower()
                username = streamer.get('username', '')
                
                if not username or platform not in ['twitch', 'youtube']:
                    continue
                
                is_live = False
                stream_data = {}
                
                try:
                    if platform == 'twitch':
                        stream_data = await get_twitch_stream_data(username)
                        if stream_data:
                            is_live = stream_data.get('is_live', False)
                        else:
                            # Fallback to page scraping
                            async with aiohttp.ClientSession() as session:
                                async with session.get(f'https://www.twitch.tv/{username}', headers=headers, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                                    if resp.status == 200:
                                        text = await resp.text()
                                        is_live = '"isLiveBroadcast":true' in text or '"isLive":true' in text
                    
                    elif platform == 'youtube':
                        async with aiohttp.ClientSession() as session:
                            async with session.get(f'https://www.youtube.com/@{username}/live', headers=headers, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                                if resp.status == 200:
                                    text = await resp.text()
                                    is_live = '"isLive":true' in text.lower() or 'watching now' in text.lower()
                except Exception as e:
                    print(f"[STREAMS] Error checking {username}: {e}")
                    continue
                
                # Send notification if just went live
                if is_live and not streamer.get('live'):
                    try:
                        if platform == 'twitch':
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
                        else:
                            message = f"""━━━━━━━━━━━━━━━━━━━━━━━━━━
[ LIVE ] YOUTUBE STREAM ALERT
━━━━━━━━━━━━━━━━━━━━━━━━━━

Channel: **{username}**

Watch Here:
https://youtube.com/@{username}/live

━━━━━━━━━━━━━━━━━━━━━━━━━━"""
                        
                        await channel.send(f"{role.mention}\n{message}")
                    except Exception as e:
                        print(f"[STREAMS] Error sending notification: {e}")
                
                streamer['live'] = is_live
            
            save_streams_config()
        except Exception as e:
            print(f"[STREAMS] Error for guild {guild_id}: {e}")

@check_streams.before_loop
async def before_check_streams():
    await bot.wait_until_ready()

@tasks.loop(minutes=1)
async def check_karuta_cooldowns_task():
    """Check Karuta cooldowns and send DM reminders"""
    now = datetime.now()
    
    for user_id_str, cooldowns in karuta_cooldowns.items():
        for cooldown_type, data in list(cooldowns.items()):
            if data.get('reminded', False):
                continue
            
            try:
                remind_at = datetime.fromisoformat(data['remind_at'])
                if now >= remind_at:
                    try:
                        user = await bot.fetch_user(int(user_id_str))
                        if user:
                            cooldown_names = {
                                'drop': 'Drop (k!drop)',
                                'daily': 'Daily (k!daily)',
                                'vote': 'Vote (k!vote)',
                                'grab': 'Grab',
                                'work': 'Work (k!work)',
                                'visit': 'Visit (k!visit)'
                            }
                            
                            embed = discord.Embed(
                                title="🎴 Karuta Cooldown Ready!",
                                description=f"Your **{cooldown_names.get(cooldown_type, cooldown_type)}** cooldown is ready!",
                                color=0x00FF00
                            )
                            await user.send(embed=embed)
                    except discord.Forbidden:
                        pass
                    except Exception as e:
                        print(f"[KARUTA] Error sending reminder: {e}")
                    
                    data['reminded'] = True
            except:
                pass
    
    save_karuta_cooldowns()

@check_karuta_cooldowns_task.before_loop
async def before_karuta_check():
    await bot.wait_until_ready()

# =====================
# KARUTA FUNCTIONS
# =====================

async def handle_karuta_message(message):
    """Handle Karuta bot messages for drop detection"""
    content = message.content.lower() if message.content else ""
    
    if "is dropping" in content and "card" in content:
        characters = await extract_characters_from_drop(message)
        if characters and characters[0]:
            await process_karuta_drop(message.channel, characters, message)

async def extract_characters_from_drop(message):
    """Extract characters from Karuta drop using Gemini Vision"""
    start_time = time.time()
    cards = []
    
    image_url = None
    if message.attachments:
        for attachment in message.attachments:
            if attachment.content_type and attachment.content_type.startswith('image/'):
                image_url = attachment.url
                break
    
    if not image_url:
        return cards, time.time() - start_time
    
    try:
        gemini_key = os.getenv('GEMINI_API_KEY')
        if not gemini_key:
            return cards, time.time() - start_time
        
        async with aiohttp.ClientSession() as session:
            async with session.get(image_url) as resp:
                if resp.status != 200:
                    return cards, time.time() - start_time
                image_bytes = await resp.read()
                content_type = resp.headers.get('Content-Type', 'image/webp')
        
        client = genai.Client(api_key=gemini_key)
        prompt = 'This is a Karuta card drop image. For each card, extract the character name (top) and series name (bottom). Return ONLY a JSON array: [{"character": "Name", "series": "Series"}]. No other text.'
        
        def call_gemini():
            for _ in range(3):
                try:
                    response = client.models.generate_content(
                        model="gemini-2.0-flash-001",
                        contents=[types.Part.from_bytes(data=image_bytes, mime_type=content_type), prompt]
                    )
                    return response.text if response.text else ""
                except Exception as e:
                    if "503" in str(e) or "429" in str(e):
                        time.sleep(8)
                        continue
                    raise
            return ""
        
        result = await asyncio.get_event_loop().run_in_executor(None, call_gemini)
        result = result.strip()
        
        if result.startswith('```'):
            result = re.sub(r'^```(?:json)?\n?', '', result)
            result = re.sub(r'\n?```$', '', result)
        
        cards = json.loads(result)
    except Exception as e:
        print(f"[KARUTA] Vision error: {e}")
    
    return cards[:4], time.time() - start_time

async def process_karuta_drop(channel, characters_data, message):
    """Process dropped characters and check wishlists"""
    if not message.guild:
        return
    
    cards, elapsed_time = characters_data
    if not cards:
        return
    
    # Count wishlist matches
    wishlist_counts = {}
    for i, card in enumerate(cards):
        char_name = card['character'].lower()
        count = sum(1 for wishlist in karuta_wishlists.values() 
                   for wish in wishlist if wish.lower() in char_name or char_name in wish.lower())
        wishlist_counts[i] = count
    
    # Build analysis
    drop_lines = []
    for i, card in enumerate(cards):
        wl_count = wishlist_counts.get(i, 0)
        heart = "♡" if wl_count == 0 else "❤️"
        series = card.get('series', '')
        if series:
            drop_lines.append(f"`{i+1}` {heart}{wl_count} · **{card['character']}** · {series}")
        else:
            drop_lines.append(f"`{i+1}` {heart}{wl_count} · **{card['character']}**")
    
    reply_text = f"Analyzed in {elapsed_time:.2f}s\n\n" + "\n".join(drop_lines)
    
    try:
        await message.reply(reply_text, mention_author=False)
    except:
        try:
            await channel.send(reply_text)
        except:
            pass
    
    # Ping users with wishlist matches
    for user_id, wishlist in karuta_wishlists.items():
        if not wishlist:
            continue
        
        for card in cards:
            char_lower = card['character'].lower()
            for wish in wishlist:
                if wish.lower() in char_lower or char_lower in wish.lower():
                    try:
                        user = bot.get_user(int(user_id))
                        if user:
                            settings = karuta_settings.get(user_id, {})
                            ping_channel = bot.get_channel(settings.get('ping_channel_id')) or channel
                            
                            embed = discord.Embed(
                                title="🎴 Wishlist Character Dropped!",
                                description=f"**{card['character']}** just dropped!",
                                color=0xFF69B4
                            )
                            if card.get('series'):
                                embed.add_field(name="Series", value=card['series'], inline=True)
                            embed.add_field(name="Channel", value=channel.mention, inline=True)
                            
                            await ping_channel.send(f"{user.mention}", embed=embed)
                    except:
                        pass
                    break

async def track_karuta_cooldown(user_id: int, cooldown_type: str):
    """Track when a user uses a Karuta command"""
    user_id_str = str(user_id)
    
    if user_id_str not in karuta_cooldowns:
        karuta_cooldowns[user_id_str] = {}
    
    settings = karuta_settings.get(user_id_str, {})
    if not settings.get('dm_reminders', True):
        return
    
    duration = KARUTA_COOLDOWNS.get(cooldown_type, 30 * 60)
    remind_at = datetime.now() + timedelta(seconds=duration)
    
    karuta_cooldowns[user_id_str][cooldown_type] = {
        'remind_at': remind_at.isoformat(),
        'reminded': False
    }
    save_karuta_cooldowns()

# =====================
# COMMANDS - UTILITY
# =====================

@bot.hybrid_command(name='ping')
async def ping_command(ctx):
    """Check the bot's response time"""
    start = time.time()
    message = await ctx.send("🏓 Pinging...")
    end = time.time()
    
    ws_latency = bot.latency * 1000
    message_latency = (end - start) * 1000
    
    if ws_latency < 100:
        quality, color = "🟢 Excellent", 0x00FF00
    elif ws_latency < 200:
        quality, color = "🟡 Good", 0xFFFF00
    else:
        quality, color = "🔴 Poor", 0xFF0000
    
    embed = discord.Embed(
        title="🏓 Pong!",
        description=f"**Bot Latency:** {ws_latency:.0f}ms\n**Message Latency:** {message_latency:.0f}ms\n**Status:** {quality}",
        color=color
    )
    await message.edit(content=None, embed=embed)

@bot.hybrid_command(name='id')
async def emoji_id_command(ctx, *, emoji_input: Optional[str] = None):
    """Get the ID of a custom emoji"""
    if not emoji_input:
        await ctx.send(f"❌ Usage: `{get_prefix_from_ctx(ctx)}id <emoji>`")
        return
    
    pattern = r'<(a)?:(\w+):(\d+)>'
    match = re.match(pattern, emoji_input.strip())
    
    if match:
        animated = match.group(1) == 'a'
        name, emoji_id = match.group(2), match.group(3)
        code_format = f"<{'a' if animated else ''}:{name}:{emoji_id}>"
        
        embed = discord.Embed(title="🔍 Emoji Info", color=0x5865F2)
        embed.add_field(name="Name", value=f"`{name}`", inline=True)
        embed.add_field(name="ID", value=f"`{emoji_id}`", inline=True)
        embed.add_field(name="Format", value=f"`{code_format}`", inline=False)
        await ctx.send(embed=embed)
    else:
        await ctx.send("❌ Could not find emoji. Use the actual emoji in your message.")

@bot.hybrid_command(name='roll')
async def roll_command(ctx, dice: str = "1d6"):
    """Roll dice (e.g., 1d6, 2d20)"""
    try:
        if 'd' not in dice.lower():
            await ctx.send("❌ Use format like `1d6`, `2d20`")
            return
        
        parts = dice.lower().split('d')
        count = int(parts[0]) if parts[0] else 1
        sides = int(parts[1])
        
        if count < 1 or count > 10 or sides < 2 or sides > 100:
            await ctx.send("❌ 1-10 dice with 2-100 sides")
            return
        
        rolls = [random.randint(1, sides) for _ in range(count)]
        total = sum(rolls)
        
        embed = discord.Embed(title="🎲 Dice Roll", color=0x5865F2)
        embed.add_field(name="Roll", value=dice, inline=True)
        embed.add_field(name="Result", value=f"{', '.join(map(str, rolls))} = **{total}**", inline=True)
        await ctx.send(embed=embed)
    except:
        await ctx.send("❌ Invalid dice format")

@bot.hybrid_command(name='8ball')
async def eightball_command(ctx, *, question: Optional[str] = None):
    """Ask the magic 8-ball"""
    if not question:
        await ctx.send("❌ Ask a question!")
        return
    
    responses = [
        "It is certain.", "Without a doubt.", "Yes.", "Most likely.",
        "Ask again later.", "Cannot predict now.", "Reply hazy.",
        "Don't count on it.", "My sources say no.", "Very doubtful."
    ]
    
    embed = discord.Embed(title="🎱 Magic 8-Ball", color=0x5865F2)
    embed.add_field(name="Question", value=question, inline=False)
    embed.add_field(name="Answer", value=random.choice(responses), inline=False)
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

@bot.hybrid_command(name='rlstats', aliases=['rlprofile'])
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
# COMMANDS - BUMP REMINDERS
# =====================

@bot.hybrid_command(name='bumpreminder')
@commands.has_permissions(administrator=True)
async def setup_bump_reminder(ctx, ping_type: str, target: Union[discord.Member, discord.Role]):
    """Setup DISBOARD bump reminders (Admin)"""
    guild_id = str(ctx.guild.id)
    
    if ping_type.lower() == 'user' and isinstance(target, discord.Member):
        bump_config[guild_id] = {
            'channel_id': ctx.channel.id,
            'ping_target': target.id,
            'ping_type': 'user'
        }
    elif ping_type.lower() == 'role' and isinstance(target, discord.Role):
        bump_config[guild_id] = {
            'channel_id': ctx.channel.id,
            'ping_target': target.id,
            'ping_type': 'role'
        }
    else:
        await ctx.send("❌ Usage: `~bumpreminder user @User` or `~bumpreminder role @Role`")
        return
    
    save_bump_config()
    await ctx.send(f"✅ Bump reminders set! Will ping {target.mention} in {ctx.channel.mention}")

@bot.hybrid_command(name='bumpdisable')
@commands.has_permissions(administrator=True)
async def disable_bump(ctx):
    """Disable bump reminders (Admin)"""
    guild_id = str(ctx.guild.id)
    if guild_id in bump_config:
        del bump_config[guild_id]
        save_bump_config()
        await ctx.send("✅ Bump reminders disabled")
    else:
        await ctx.send("❌ Bump reminders not enabled")

# =====================
# COMMANDS - STREAM NOTIFICATIONS
# =====================

@bot.hybrid_command(name='streamnotify')
@commands.has_permissions(administrator=True)
async def stream_notify(ctx, action: str, *, args: Optional[str] = None):
    """Manage stream notifications (Admin)"""
    guild_id = str(ctx.guild.id)
    prefix = get_prefix_from_ctx(ctx)
    
    if action.lower() == 'setup':
        if not args:
            await ctx.send(f"❌ Usage: `{prefix}streamnotify setup #channel @role`")
            return
        
        channel_match = re.search(r'<#(\d+)>', args)
        role_match = re.search(r'<@&(\d+)>', args)
        
        if not channel_match or not role_match:
            await ctx.send(f"❌ Usage: `{prefix}streamnotify setup #channel @role`")
            return
        
        streams_config[guild_id] = {
            'channel_id': int(channel_match.group(1)),
            'role_id': int(role_match.group(1)),
            'streamers': []
        }
        save_streams_config()
        await ctx.send("✅ Stream notifications configured!")
    
    elif action.lower() == 'add':
        if guild_id not in streams_config:
            await ctx.send(f"❌ Run `{prefix}streamnotify setup` first")
            return
        
        if not args:
            await ctx.send(f"❌ Usage: `{prefix}streamnotify add twitch/youtube <username>`")
            return
        
        parts = args.split()
        if len(parts) < 2:
            await ctx.send(f"❌ Usage: `{prefix}streamnotify add twitch/youtube <username>`")
            return
        
        platform, username = parts[0].lower(), parts[1]
        if platform not in ['twitch', 'youtube']:
            await ctx.send("❌ Platform must be `twitch` or `youtube`")
            return
        
        streams_config[guild_id]['streamers'].append({
            'platform': platform,
            'username': username,
            'live': False
        })
        save_streams_config()
        await ctx.send(f"✅ Added **{username}** ({platform})")
    
    elif action.lower() == 'remove':
        if guild_id not in streams_config:
            await ctx.send("❌ No stream config found")
            return
        
        if not args:
            await ctx.send(f"❌ Usage: `{prefix}streamnotify remove <username>`")
            return
        
        username = args.strip().lower()
        streamers = streams_config[guild_id].get('streamers', [])
        original_len = len(streamers)
        streamers[:] = [s for s in streamers if s['username'].lower() != username]
        
        if len(streamers) < original_len:
            save_streams_config()
            await ctx.send(f"✅ Removed **{args.strip()}**")
        else:
            await ctx.send("❌ Streamer not found")
    
    elif action.lower() == 'list':
        if guild_id not in streams_config:
            await ctx.send("❌ No stream notifications configured")
            return
        
        config = streams_config[guild_id]
        streamers = config.get('streamers', [])
        
        if not streamers:
            await ctx.send("No streamers added yet")
            return
        
        lines = [f"{'🔴' if s.get('live') else '⚫'} **{s['username']}** ({s['platform']})" for s in streamers]
        embed = discord.Embed(
            title="📺 Monitored Streamers",
            description="\n".join(lines),
            color=0x9146FF
        )
        await ctx.send(embed=embed)
    
    else:
        await ctx.send(f"❌ Actions: `setup`, `add`, `remove`, `list`")

# =====================
# COMMANDS - KARUTA
# =====================

@bot.hybrid_command(name='kwish', aliases=['kw'])
async def karuta_wish(ctx, action: Optional[str] = None, *, args: Optional[str] = None):
    """Manage your Karuta wishlist"""
    user_id = str(ctx.author.id)
    prefix = get_prefix_from_ctx(ctx)
    
    if user_id not in karuta_wishlists:
        karuta_wishlists[user_id] = []
    
    if not action:
        embed = discord.Embed(title="🎴 Karuta Wishlist", color=0xFF69B4)
        embed.add_field(name="Commands", value=f"""
`{prefix}kwish add <character>` - Add to wishlist
`{prefix}kwish remove <character>` - Remove from wishlist
`{prefix}kwish list` - View your wishlist
`{prefix}kwish clear` - Clear wishlist
`{prefix}kwish channel #channel` - Set ping channel
`{prefix}kwish reminders on/off` - Toggle DM reminders
        """, inline=False)
        await ctx.send(embed=embed)
        return
    
    action = action.lower()
    
    if action == 'add':
        if not args:
            await ctx.send("❌ Specify a character name")
            return
        
        if len(karuta_wishlists[user_id]) >= 50:
            await ctx.send("❌ Wishlist full (50 max)")
            return
        
        if args.lower() in [c.lower() for c in karuta_wishlists[user_id]]:
            await ctx.send("❌ Already in wishlist")
            return
        
        karuta_wishlists[user_id].append(args)
        save_karuta_wishlists()
        await ctx.send(f"✅ Added **{args}** to wishlist ({len(karuta_wishlists[user_id])}/50)")
    
    elif action == 'remove':
        if not args:
            await ctx.send("❌ Specify a character name")
            return
        
        for char in karuta_wishlists[user_id]:
            if char.lower() == args.lower():
                karuta_wishlists[user_id].remove(char)
                save_karuta_wishlists()
                await ctx.send(f"✅ Removed **{char}** from wishlist")
                return
        
        await ctx.send("❌ Character not found")
    
    elif action == 'list':
        wishlist = karuta_wishlists[user_id]
        if not wishlist:
            await ctx.send("Your wishlist is empty!")
            return
        
        embed = discord.Embed(
            title=f"🎴 {ctx.author.display_name}'s Wishlist",
            description="\n".join([f"`{i+1}.` {c}" for i, c in enumerate(wishlist)]),
            color=0xFF69B4
        )
        embed.set_footer(text=f"{len(wishlist)}/50 characters")
        await ctx.send(embed=embed)
    
    elif action == 'clear':
        karuta_wishlists[user_id] = []
        save_karuta_wishlists()
        await ctx.send("✅ Wishlist cleared")
    
    elif action == 'channel':
        if not args:
            await ctx.send("❌ Mention a channel")
            return
        
        match = re.search(r'<#(\d+)>', args)
        if not match:
            await ctx.send("❌ Invalid channel")
            return
        
        if user_id not in karuta_settings:
            karuta_settings[user_id] = {}
        
        karuta_settings[user_id]['ping_channel_id'] = int(match.group(1))
        save_karuta_settings()
        await ctx.send(f"✅ Pings will go to <#{match.group(1)}>")
    
    elif action == 'reminders':
        if not args or args.lower() not in ['on', 'off']:
            await ctx.send("❌ Use `on` or `off`")
            return
        
        if user_id not in karuta_settings:
            karuta_settings[user_id] = {}
        
        karuta_settings[user_id]['dm_reminders'] = args.lower() == 'on'
        save_karuta_settings()
        await ctx.send(f"✅ DM reminders {'enabled' if args.lower() == 'on' else 'disabled'}")

@bot.hybrid_command(name='kcooldowns', aliases=['kcd'])
async def karuta_cooldowns_cmd(ctx):
    """View your Karuta cooldowns"""
    user_id = str(ctx.author.id)
    cooldowns = karuta_cooldowns.get(user_id, {})
    
    if not cooldowns:
        await ctx.send("No cooldowns tracked yet. Use Karuta commands to start tracking!")
        return
    
    now = datetime.now()
    lines = []
    
    cooldown_names = {
        'drop': '🎴 Drop',
        'daily': '📅 Daily',
        'vote': '🗳️ Vote',
        'work': '💼 Work',
        'visit': '🏠 Visit',
        'grab': '✋ Grab'
    }
    
    for cd_type, data in cooldowns.items():
        try:
            remind_at = datetime.fromisoformat(data['remind_at'])
            if now >= remind_at:
                status = "✅ Ready!"
            else:
                remaining = remind_at - now
                mins = int(remaining.total_seconds() // 60)
                status = f"⏳ {mins}m"
            
            lines.append(f"{cooldown_names.get(cd_type, cd_type)}: {status}")
        except:
            pass
    
    embed = discord.Embed(
        title="🎴 Karuta Cooldowns",
        description="\n".join(lines) if lines else "No active cooldowns",
        color=0xFF69B4
    )
    await ctx.send(embed=embed)

# =====================
# COMMANDS - STAFF & PROFILE
# =====================

@bot.hybrid_command(name='staff')
async def staff_command(ctx):
    """View staff directory"""
    if not staff_data:
        await ctx.send("No staff profiles configured yet!")
        return
    
    embed = discord.Embed(title="👥 Staff Directory", color=0x5865F2)
    
    for user_id, data in staff_data.items():
        user = bot.get_user(int(user_id))
        name = data.get('name', user.display_name if user else f"User {user_id}")
        position = data.get('position', 'Staff')
        embed.add_field(name=f"{name} - {position}", value=data.get('description', 'No description'), inline=False)
    
    await ctx.send(embed=embed)

@bot.hybrid_command(name='staffedit')
async def staff_edit(ctx, field: str, *, value: str):
    """Edit your staff profile"""
    if ctx.author.id not in STAFF_IDS:
        await ctx.send("❌ Staff only")
        return
    
    user_id = str(ctx.author.id)
    if user_id not in staff_data:
        staff_data[user_id] = {}
    
    if field.lower() in ['name', 'position', 'description']:
        staff_data[user_id][field.lower()] = value
        save_staff_data()
        await ctx.send(f"✅ Updated {field}")
    else:
        await ctx.send("❌ Fields: `name`, `position`, `description`")

@bot.hybrid_command(name='profile')
async def profile_command(ctx, member: Optional[discord.Member] = None):
    """View a user's profile"""
    target = member or ctx.author
    
    embed = discord.Embed(
        title=f"{target.display_name}'s Profile",
        color=target.color if target.color != discord.Color.default() else 0x5865F2
    )
    embed.set_thumbnail(url=target.display_avatar.url)
    
    # RL Rank
    rank_val = rl_ranks.get(str(target.id), 0)
    rank_data = RL_RANKS.get(rank_val, RL_RANKS[0])
    embed.add_field(name="🚀 RL Rank", value=f"{rank_data['emoji']} {rank_data['name']}", inline=True)
    
    # Joined
    if target.joined_at:
        embed.add_field(name="📅 Joined", value=target.joined_at.strftime("%b %d, %Y"), inline=True)
    
    # Banner
    banner_url = profile_banners.get(str(target.id))
    if banner_url:
        embed.set_image(url=banner_url)
    
    await ctx.send(embed=embed)

@bot.hybrid_command(name='setbanner')
async def set_banner(ctx, *, url: Optional[str] = None):
    """Set your profile banner"""
    if not url and ctx.message.attachments:
        url = ctx.message.attachments[0].url
    
    if not url:
        await ctx.send("❌ Provide an image URL or attach an image")
        return
    
    profile_banners[str(ctx.author.id)] = url
    save_profile_banners()
    await ctx.send("✅ Banner set!")

@bot.hybrid_command(name='removebanner')
async def remove_banner(ctx):
    """Remove your profile banner"""
    if str(ctx.author.id) in profile_banners:
        del profile_banners[str(ctx.author.id)]
        save_profile_banners()
        await ctx.send("✅ Banner removed")
    else:
        await ctx.send("❌ No banner to remove")

# =====================
# COMMANDS - ADMIN
# =====================

@bot.hybrid_command(name='setprefix')
@commands.has_permissions(administrator=True)
async def set_prefix(ctx, new_prefix: str):
    """Change the bot prefix (Admin)"""
    if len(new_prefix) > 5:
        await ctx.send("❌ Prefix must be 5 characters or less")
        return
    
    prefixes[str(ctx.guild.id)] = new_prefix
    save_prefixes()
    await ctx.send(f"✅ Prefix set to `{new_prefix}`")

@bot.hybrid_command(name='verify')
async def verify_command(ctx):
    """Verify yourself"""
    if ctx.author.id in verified_users:
        await ctx.send("✅ You're already verified!")
        return
    
    verified_users.add(ctx.author.id)
    save_verified_users()
    await ctx.send("✅ You are now verified!")

@bot.hybrid_command(name='update')
async def update_command(ctx, *, message: str):
    """Post an update (Owner only)"""
    if ctx.author.id != OWNER_ID:
        await ctx.send("❌ Owner only")
        return
    
    update_channel = bot.get_channel(1435009184285589554)
    if update_channel:
        embed = discord.Embed(
            title="📢 Bot Update",
            description=message,
            color=0x5865F2,
            timestamp=datetime.now()
        )
        embed.set_footer(text=f"Posted by {ctx.author}")
        await update_channel.send(embed=embed)
        await ctx.send("✅ Update posted!")
    else:
        await ctx.send("❌ Update channel not found")

@bot.hybrid_command(name='guide')
async def guide_command(ctx):
    """Show all available commands"""
    prefix = get_prefix_from_ctx(ctx)
    
    embed = discord.Embed(
        title="📚 Kursein Bot Guide",
        description="Tokyo Ghoul + Rocket League themed bot",
        color=0x5865F2
    )
    
    embed.add_field(name="🎮 Utility", value=f"""
`{prefix}ping` - Check latency
`{prefix}id <emoji>` - Get emoji info
`{prefix}roll <dice>` - Roll dice (1d6, 2d20)
`{prefix}8ball <question>` - Magic 8-ball
`{prefix}profile [@user]` - View profile
    """, inline=False)
    
    embed.add_field(name="🚀 Rocket League", value=f"""
`{prefix}setrank <rank>` - Set your RL rank
`{prefix}rllb` - Rank leaderboard
`{prefix}setrlprofile <platform> <user>` - Link Tracker
`{prefix}rlstats [@user]` - View RL stats
    """, inline=False)
    
    embed.add_field(name="🎴 Karuta", value=f"""
`{prefix}kwish` - Manage wishlist
`{prefix}kcd` - View cooldowns
    """, inline=False)
    
    embed.add_field(name="⚙️ Admin", value=f"""
`{prefix}bumpreminder` - Setup bump reminders
`{prefix}streamnotify` - Manage stream alerts
`{prefix}setprefix <prefix>` - Change prefix
    """, inline=False)
    
    await ctx.send(embed=embed)

# Run the bot
if __name__ == "__main__":
    token = os.getenv('DISCORD_BOT_TOKEN')
    if token:
        bot.run(token)
    else:
        print("Error: DISCORD_BOT_TOKEN not found")
