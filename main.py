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
AFK_FILE = "afk_users.json"
PENDING_RANKS_FILE = "pending_ranks.json"
JJK_DATA_FILE = "jjk_data.json"
JJK_CLANS_FILE = "jjk_clans.json"
DEFAULT_PREFIX = "~"

DISBOARD_BOT_ID = 302050872383242240
ERROR_CHANNEL_ID = 1435009092782522449
STREAM_CHANNEL_ID = 1442613254546526298
BUMP_CHANNEL_ID = 1418819741471997982
BUMP_ROLE_ID = 1436421726727700542
LOG_CHANNEL_ID = 1435009184285589554  # Join/leave logs
ADMIN_ROLE_ID = 1410509859685662781   # Ping for new accounts

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
afk_users = {}
pending_ranks = {}

# Rank to Role mapping (loaded from DB)
rank_roles = {}

# JJK Economy Data
jjk_players = {}  # user_id -> player data
jjk_clans = {}    # clan_name -> clan data
jjk_cooldowns = {}  # user_id -> {action: timestamp}

# JJK Game Constants
JJK_SORCERERS = {
    "yuji": {"name": "Yuji Itadori", "cost": 0, "income": 10, "emoji": "👊", "grade": "1st Grade", "unlock": 0},
    "megumi": {"name": "Megumi Fushiguro", "cost": 5000, "income": 25, "emoji": "🐕", "grade": "1st Grade", "unlock": 5},
    "nobara": {"name": "Nobara Kugisaki", "cost": 5000, "income": 25, "emoji": "🔨", "grade": "3rd Grade", "unlock": 5},
    "maki": {"name": "Maki Zenin", "cost": 15000, "income": 50, "emoji": "🗡️", "grade": "Special Grade", "unlock": 10},
    "panda": {"name": "Panda", "cost": 15000, "income": 50, "emoji": "🐼", "grade": "2nd Grade", "unlock": 10},
    "inumaki": {"name": "Toge Inumaki", "cost": 25000, "income": 80, "emoji": "🍙", "grade": "Semi-1st Grade", "unlock": 15},
    "todo": {"name": "Aoi Todo", "cost": 40000, "income": 120, "emoji": "👏", "grade": "1st Grade", "unlock": 20},
    "yuta": {"name": "Yuta Okkotsu", "cost": 100000, "income": 300, "emoji": "💍", "grade": "Special Grade", "unlock": 30},
    "gojo": {"name": "Satoru Gojo", "cost": 500000, "income": 1000, "emoji": "👁️", "grade": "Special Grade", "unlock": 50},
}

JJK_TECHNIQUES = {
    "divergent_fist": {"name": "Divergent Fist", "cost": 2000, "multiplier": 1.1, "desc": "Delayed cursed energy impact"},
    "black_flash": {"name": "Black Flash", "cost": 10000, "multiplier": 1.25, "desc": "2.5x cursed energy distortion"},
    "ten_shadows": {"name": "Ten Shadows", "cost": 25000, "multiplier": 1.4, "desc": "Summon shikigami to fight"},
    "cursed_speech": {"name": "Cursed Speech", "cost": 35000, "multiplier": 1.5, "desc": "Command curses with words"},
    "boogie_woogie": {"name": "Boogie Woogie", "cost": 50000, "multiplier": 1.6, "desc": "Swap positions instantly"},
    "reverse_cursed": {"name": "Reverse Cursed Technique", "cost": 100000, "multiplier": 1.8, "desc": "Heal from any injury"},
    "domain_amplification": {"name": "Domain Amplification", "cost": 200000, "multiplier": 2.0, "desc": "Nullify cursed techniques"},
}

JJK_TOOLS = {
    "slaughter_demon": {"name": "Slaughter Demon", "cost": 3000, "bonus": 15, "desc": "Maki's cursed tool"},
    "playful_cloud": {"name": "Playful Cloud", "cost": 8000, "bonus": 40, "desc": "Three-section staff"},
    "inverted_spear": {"name": "Inverted Spear of Heaven", "cost": 20000, "bonus": 100, "desc": "Nullifies cursed techniques"},
    "split_soul_katana": {"name": "Split Soul Katana", "cost": 50000, "bonus": 250, "desc": "Cuts the soul directly"},
    "prison_realm": {"name": "Prison Realm", "cost": 150000, "bonus": 750, "desc": "Seal anything inside"},
}

JJK_DOMAINS = {
    0: {"name": "No Domain", "multiplier": 1.0, "cost": 0},
    1: {"name": "Incomplete Domain", "multiplier": 1.5, "cost": 50000},
    2: {"name": "Chimera Shadow Garden", "multiplier": 2.0, "cost": 150000},
    3: {"name": "Malevolent Shrine", "multiplier": 3.0, "cost": 500000},
    4: {"name": "Infinite Void", "multiplier": 5.0, "cost": 2000000},
}

JJK_CURSES = [
    {"name": "Finger Bearer", "min_yen": 50, "max_yen": 150, "xp": 5},
    {"name": "Cursed Spirit", "min_yen": 100, "max_yen": 300, "xp": 10},
    {"name": "Grade 4 Curse", "min_yen": 200, "max_yen": 500, "xp": 15},
    {"name": "Grade 3 Curse", "min_yen": 400, "max_yen": 800, "xp": 25},
    {"name": "Grade 2 Curse", "min_yen": 600, "max_yen": 1200, "xp": 40},
    {"name": "Grade 1 Curse", "min_yen": 1000, "max_yen": 2000, "xp": 60},
    {"name": "Special Grade Curse", "min_yen": 2000, "max_yen": 5000, "xp": 100},
]

JJK_MISSIONS = [
    {"name": "Clear Cursed Womb", "yen": 5000, "xp": 200, "cooldown": 3600},
    {"name": "Protect Civilians", "yen": 3000, "xp": 150, "cooldown": 1800},
    {"name": "Retrieve Cursed Object", "yen": 8000, "xp": 300, "cooldown": 7200},
    {"name": "Exorcise Domain", "yen": 15000, "xp": 500, "cooldown": 14400},
]

def get_jjk_grade(level):
    """Get sorcerer grade based on level"""
    if level < 5: return "Grade 4"
    if level < 10: return "Grade 3"
    if level < 20: return "Grade 2"
    if level < 35: return "Grade 1"
    if level < 50: return "Semi-1st Grade"
    return "Special Grade"

def calculate_jjk_income(player):
    """Calculate total hourly income for a player"""
    base = 50
    sorcerer_income = sum(JJK_SORCERERS.get(s, {}).get("income", 0) for s in player.get("sorcerers", []))
    tool_bonus = sum(JJK_TOOLS.get(t, {}).get("bonus", 0) for t in player.get("tools", []))
    tech_mult = 1.0
    for tech in player.get("techniques", []):
        tech_data = JJK_TECHNIQUES.get(tech, {})
        tech_mult *= tech_data.get("multiplier", 1.0)
    domain_mult = JJK_DOMAINS.get(player.get("domain", 0), JJK_DOMAINS[0])["multiplier"]
    return int((base + sorcerer_income + tool_bonus) * tech_mult * domain_mult)

def parse_iso_timestamp(ts_str):
    """Safely parse ISO timestamp string"""
    if not ts_str:
        return None
    try:
        dt = datetime.fromisoformat(ts_str)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
    except (ValueError, TypeError):
        return None

def xp_for_level(level):
    """XP needed for next level"""
    return 100 + (level * 50)

def get_rank_tier(rank_id):
    """Get the tier name from a rank ID"""
    if rank_id == 0: return None
    if rank_id <= 3: return 'bronze'
    if rank_id <= 6: return 'silver'
    if rank_id <= 9: return 'gold'
    if rank_id <= 12: return 'platinum'
    if rank_id <= 15: return 'diamond'
    if rank_id <= 18: return 'champion'
    if rank_id <= 21: return 'grand_champion'
    if rank_id == 22: return 'ssl'
    return None

# Twitch API tokens
twitch_access_token = None
twitch_token_expiry = None

# Rocket League Ranks
def normalize_rank_input(rank_input):
    """Convert number suffixes to roman numerals (e.g., Diamond 1 -> Diamond I)"""
    replacements = {'1': 'I', '2': 'II', '3': 'III'}
    result = rank_input
    for num, roman in replacements.items():
        result = re.sub(rf'\b{num}\b', roman, result)
    return result

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

def load_afk_users():
    global afk_users
    if db.is_db_available():
        afk_users = db.load_data('afk_users', {})
    elif os.path.exists(AFK_FILE):
        try:
            with open(AFK_FILE, 'r') as f:
                afk_users = json.load(f)
        except:
            afk_users = {}

def save_afk_users():
    try:
        if db.is_db_available():
            db.save_data('afk_users', afk_users)
        with open(AFK_FILE, 'w') as f:
            json.dump(afk_users, f, indent=2)
    except Exception as e:
        print(f"Error saving AFK users: {e}")

def load_pending_ranks():
    global pending_ranks
    if db.is_db_available():
        pending_ranks = db.load_data('pending_ranks', {})
    elif os.path.exists(PENDING_RANKS_FILE):
        try:
            with open(PENDING_RANKS_FILE, 'r') as f:
                pending_ranks = json.load(f)
        except:
            pending_ranks = {}

def save_pending_ranks():
    try:
        if db.is_db_available():
            db.save_data('pending_ranks', pending_ranks)
        with open(PENDING_RANKS_FILE, 'w') as f:
            json.dump(pending_ranks, f, indent=2)
    except Exception as e:
        print(f"Error saving pending ranks: {e}")

def load_rank_roles():
    global rank_roles
    if db.is_db_available():
        rank_roles = db.load_data('rank_roles', {})

def save_rank_roles():
    try:
        if db.is_db_available():
            db.save_data('rank_roles', rank_roles)
    except Exception as e:
        print(f"Error saving rank roles: {e}")

def load_jjk_data():
    global jjk_players, jjk_clans
    if db.is_db_available():
        jjk_players = db.load_data('jjk_players', {})
        jjk_clans = db.load_data('jjk_clans', {})
    else:
        if os.path.exists(JJK_DATA_FILE):
            try:
                with open(JJK_DATA_FILE, 'r') as f:
                    jjk_players = json.load(f)
            except:
                jjk_players = {}
        if os.path.exists(JJK_CLANS_FILE):
            try:
                with open(JJK_CLANS_FILE, 'r') as f:
                    jjk_clans = json.load(f)
            except:
                jjk_clans = {}

def save_jjk_data():
    try:
        if db.is_db_available():
            db.save_data('jjk_players', jjk_players)
            db.save_data('jjk_clans', jjk_clans)
        with open(JJK_DATA_FILE, 'w') as f:
            json.dump(jjk_players, f, indent=2)
        with open(JJK_CLANS_FILE, 'w') as f:
            json.dump(jjk_clans, f, indent=2)
    except Exception as e:
        print(f"Error saving JJK data: {e}")

def get_jjk_player(user_id):
    """Get or create a JJK player profile"""
    uid = str(user_id)
    if uid not in jjk_players:
        return None
    return jjk_players[uid]

def create_jjk_player(user_id):
    """Create a new JJK player"""
    uid = str(user_id)
    jjk_players[uid] = {
        "yen": 500,
        "xp": 0,
        "level": 1,
        "sorcerers": ["yuji"],
        "techniques": [],
        "tools": [],
        "domain": 0,
        "curses_exorcised": 0,
        "missions_completed": 0,
        "clan": None,
        "daily_streak": 0,
        "last_daily": None,
        "last_hunt": None,
        "last_train": None,
        "last_collect": None
    }
    save_jjk_data()
    return jjk_players[uid]

import random

async def assign_rank_role(member, rank_id):
    """Assign the appropriate rank role and remove old rank roles"""
    if not rank_roles:
        return
    
    tier = get_rank_tier(rank_id)
    if not tier:
        return
    
    new_role_id = rank_roles.get(tier)
    if not new_role_id:
        return
    
    # Get all configured rank role IDs
    all_rank_role_ids = set(v for v in rank_roles.values() if v)
    
    # Remove any existing rank roles
    roles_to_remove = [r for r in member.roles if r.id in all_rank_role_ids]
    for role in roles_to_remove:
        try:
            await member.remove_roles(role)
        except:
            pass
    
    # Add the new rank role
    new_role = member.guild.get_role(int(new_role_id))
    if new_role:
        try:
            await member.add_roles(new_role)
        except Exception as e:
            print(f"[ROLES] Error adding role: {e}")

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
    load_afk_users()
    load_pending_ranks()
    load_rank_roles()
    load_jjk_data()
    
    if not check_reminders.is_running():
        check_reminders.start()
        print("Started reminder checker task")
    
    if not check_streams.is_running():
        check_streams.start()
        print("Started stream checker task")
    
    print("Starting slash command sync...")
    try:
        await asyncio.sleep(2)
        
        # Clear any old guild-specific commands to prevent duplicates
        for guild in bot.guilds:
            try:
                bot.tree.clear_commands(guild=guild)
                await bot.tree.sync(guild=guild)
            except:
                pass
        
        # Sync global commands only
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} slash command(s) globally")
    except Exception as e:
        print(f"Error syncing commands: {e}")

@bot.event
async def on_message(message):
    # AFK system - clear AFK status when user sends a message
    if not message.author.bot:
        user_id = str(message.author.id)
        if user_id in afk_users:
            del afk_users[user_id]
            save_afk_users()
            await message.channel.send(f"👋 Welcome back {message.author.mention}! I removed your AFK status.", delete_after=5)
        
        # Notify when someone pings an AFK user
        for mention in message.mentions:
            mention_id = str(mention.id)
            if mention_id in afk_users:
                afk_data = afk_users[mention_id]
                since = datetime.fromisoformat(afk_data['since'])
                time_ago = datetime.now(timezone.utc) - since
                mins = int(time_ago.total_seconds() // 60)
                time_str = f"{mins} min ago" if mins < 60 else f"{mins // 60}h ago"
                await message.channel.send(f"💤 **{mention.display_name}** is AFK: {afk_data['reason']} ({time_str})", delete_after=10)
    
    # Process commands
    await bot.process_commands(message)
    
    # Bump detection (DISBOARD bot)
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

@bot.event
async def on_member_join(member):
    """Log when a member joins and check for new accounts"""
    channel = bot.get_channel(LOG_CHANNEL_ID)
    if not channel:
        return
    
    # Calculate account age
    account_age = datetime.now(timezone.utc) - member.created_at.replace(tzinfo=timezone.utc)
    days_old = account_age.days
    
    # Determine if account is new/suspicious
    is_new = days_old < 7
    is_semi_new = days_old < 30
    
    member_count = member.guild.member_count or 0
    
    embed = discord.Embed(
        title="📥 Member Joined",
        description=f"▸ Glad to have you here, {member.mention}\n▸ You've joined as **#{member_count}**",
        color=0xFF0000 if is_new else (0xFFA500 if is_semi_new else 0x00FF00)
    )
    embed.set_thumbnail(url=member.display_avatar.url)
    embed.add_field(name="Account Created", value=f"{member.created_at.strftime('%b %d, %Y')}", inline=True)
    embed.add_field(name="Account Age", value=f"{days_old} days", inline=True)
    embed.set_footer(text=f"ID: {member.id}")
    
    if is_new:
        embed.add_field(name="⚠️ Warning", value="**NEW ACCOUNT** - Please verify!", inline=False)
        await channel.send(f"<@&{ADMIN_ROLE_ID}>", embed=embed)
    elif is_semi_new:
        embed.add_field(name="⚠️ Notice", value="Semi-new account (< 30 days)", inline=False)
        await channel.send(embed=embed)
    else:
        await channel.send(embed=embed)

@bot.event
async def on_member_remove(member):
    """Log when a member leaves"""
    channel = bot.get_channel(LOG_CHANNEL_ID)
    if not channel:
        return
    
    # Calculate how long they were in the server
    if member.joined_at:
        time_in_server = datetime.now(timezone.utc) - member.joined_at.replace(tzinfo=timezone.utc)
        days_in = time_in_server.days
        time_text = f"{days_in} days"
    else:
        time_text = "Unknown"
    
    embed = discord.Embed(
        title="📤 Member Left",
        color=0x808080
    )
    embed.set_thumbnail(url=member.display_avatar.url)
    embed.add_field(name="User", value=f"{member} ({member.id})", inline=False)
    embed.add_field(name="Time in Server", value=time_text, inline=True)
    embed.set_footer(text=f"ID: {member.id}")
    
    await channel.send(embed=embed)

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

@bot.hybrid_command(name='resetranks')
@commands.has_permissions(administrator=True)
async def reset_ranks(ctx):
    """Reset all RL ranks for new season and ping users"""
    global rl_ranks
    
    if not rl_ranks:
        await ctx.send("❌ No ranks to reset.")
        return
    
    # Get list of users to ping
    user_ids = list(rl_ranks.keys())
    mentions = [f"<@{uid}>" for uid in user_ids]
    
    # Clear all ranks
    rl_ranks = {}
    save_rl_ranks()
    
    embed = discord.Embed(
        title="🚀 Season 21 Rank Reset!",
        description=f"All Rocket League ranks have been reset for the new season!\n\n"
                    f"**To update your rank:**\n"
                    f"1. Link your tracker: `~setrlprofile <platform> <username>`\n"
                    f"2. Set your rank: `~setrank <rank>`\n\n"
                    f"An admin will verify your rank using your tracker profile.",
        color=0xFF4500
    )
    embed.add_field(name="Players Reset", value=str(len(user_ids)), inline=True)
    
    # Send ping and embed
    await ctx.send(" ".join(mentions), embed=embed)

@bot.hybrid_command(name='adminsetprofile')
@commands.has_permissions(administrator=True)
async def admin_set_profile(ctx, user_input: str, rank_input: str, *, url: str):
    """(Admin) Set a user's rank and tracker URL - Usage: ~adminsetprofile <@user or ID> <rank> <url>"""
    # Parse user from mention or ID
    user_id = re.sub(r'[<@!>]', '', user_input)
    
    try:
        target = await bot.fetch_user(int(user_id))
    except:
        await ctx.send("❌ Invalid user mention or ID")
        return
    
    # Parse the tracker URL
    url_pattern = r'https?://rocketleague\.tracker\.(gg|network)/rocket-league/profile/([^/]+)/([^/\s]+)'
    url_match = re.search(url_pattern, url)
    
    if url_match:
        platform = url_match.group(2).lower()
        username = url_match.group(3).split('/')[0]
        tracker_url = f"https://rocketleague.tracker.gg/rocket-league/profile/{platform}/{quote(username)}"
    else:
        await ctx.send("❌ Invalid tracker URL. Use a rocketleague.tracker.gg URL")
        return
    
    # Parse rank (normalize 1/2/3 to I/II/III)
    rank_input_normalized = normalize_rank_input(rank_input).lower().strip()
    division = None
    div_match = re.search(r'\b(?:div(?:ision)?\.?\s*|d)([1-4])\b', rank_input_normalized)
    if div_match:
        division = int(div_match.group(1))
        rank_input_normalized = re.sub(r'\b(?:div(?:ision)?\.?\s*|d)[1-4]\b', '', rank_input_normalized).strip()
    
    matched_rank = None
    for rank_id, rank_data in RL_RANKS.items():
        if rank_data['name'].lower() == rank_input_normalized:
            matched_rank = rank_id
            break
    if matched_rank is None:
        for rank_id, rank_data in RL_RANKS.items():
            if rank_input_normalized in rank_data['name'].lower():
                matched_rank = rank_id
                break
    
    if matched_rank is None:
        rank_list = "\n".join([f"{data['emoji']} {data['name']}" for data in RL_RANKS.values()])
        await ctx.send(f"❌ Invalid rank.\n\nAvailable ranks:\n{rank_list}")
        return
    
    if matched_rank == 22:
        division = None
    elif division is None:
        division = 1
    
    # Save profile and rank
    rl_profiles[str(target.id)] = {'username': username, 'platform': platform, 'url': tracker_url}
    save_rl_profiles()
    
    rl_ranks[str(target.id)] = {'rank': matched_rank, 'division': division}
    save_rl_ranks()
    
    # Auto-assign rank role
    member = ctx.guild.get_member(int(target.id))
    if member:
        await assign_rank_role(member, matched_rank)
    
    rank_data = RL_RANKS[matched_rank]
    div_text = f" Div {division}" if division else ""
    
    embed = discord.Embed(
        title="✅ Profile Set by Admin",
        description=f"**User:** {target.mention}\n"
                    f"**Rank:** {rank_data['emoji']} {rank_data['name']}{div_text}\n"
                    f"**Tracker:** [Link]({tracker_url})",
        color=0x00FF00
    )
    await ctx.send(embed=embed)

@bot.hybrid_command(name='setrank', aliases=['rlrank'])
async def set_rl_rank(ctx, *, rank_input: str):
    """Set your Rocket League rank with division (e.g. Diamond 1 Div 3)"""
    user_id = str(ctx.author.id)
    
    # Check if user has linked their tracker
    if user_id not in rl_profiles:
        prefix = get_prefix_from_ctx(ctx)
        await ctx.send(f"❌ Please link your Rocket League tracker first!\n"
                       f"Use: `{prefix}setrlprofile <url>` or `{prefix}setrlprofile <platform> <username>`")
        return
    
    # Normalize 1/2/3 to I/II/III
    rank_input_normalized = normalize_rank_input(rank_input).lower().strip()
    
    # Parse division from input (div 1, div 2, div 3, div 4, d1, d2, d3, d4)
    division = None
    div_match = re.search(r'\b(?:div(?:ision)?\.?\s*|d)([1-4])\b', rank_input_normalized)
    if div_match:
        division = int(div_match.group(1))
        # Remove division from rank input for matching
        rank_input_normalized = re.sub(r'\b(?:div(?:ision)?\.?\s*|d)[1-4]\b', '', rank_input_normalized).strip()
    
    matched_rank = None
    for rank_id, rank_data in RL_RANKS.items():
        if rank_data['name'].lower() == rank_input_normalized:
            matched_rank = rank_id
            break
    
    if matched_rank is None:
        for rank_id, rank_data in RL_RANKS.items():
            if rank_input_normalized in rank_data['name'].lower():
                matched_rank = rank_id
                break
    
    if matched_rank is None:
        rank_list = "\n".join([f"{data['emoji']} {data['name']}" for data in RL_RANKS.values()])
        await ctx.send(f"❌ Invalid rank. Example: `~setrank Diamond 1 Div 3`\n\nAvailable ranks:\n{rank_list}")
        return
    
    # SSL doesn't have divisions
    if matched_rank == 22:
        division = None
    elif division is None:
        division = 1  # Default to Div 1 if not specified
    
    rank_data = RL_RANKS[matched_rank]
    profile = rl_profiles[user_id]
    tracker_url = profile.get('url') or f"https://rocketleague.tracker.gg/rocket-league/profile/{profile['platform']}/{quote(profile['username'])}"
    
    # Add to pending queue for admin verification
    pending_ranks[user_id] = {
        'rank': matched_rank,
        'division': division,
        'tracker_url': tracker_url,
        'submitted': datetime.now(timezone.utc).isoformat()
    }
    save_pending_ranks()
    
    div_text = f" Div {division}" if division else ""
    embed = discord.Embed(
        title="🚀 Rank Submitted for Verification!",
        description=f"{rank_data['emoji']} **{rank_data['name']}{div_text}**\n\n"
                    f"⏳ An admin will verify using your tracker:\n{tracker_url}",
        color=0xFFA500
    )
    embed.set_footer(text="You'll be notified when approved")
    await ctx.send(embed=embed)

@bot.hybrid_command(name='rllb', aliases=['rlleaderboard'])
async def rl_leaderboard(ctx):
    """Show Rocket League rank leaderboard"""
    if not rl_ranks:
        await ctx.send("No players have set their RL rank yet!")
        return
    
    def get_rank_sort_value(item):
        user_id, rank_info = item
        if isinstance(rank_info, dict):
            return (rank_info.get('rank', 0), rank_info.get('division', 0))
        return (rank_info, 0)  # Legacy format
    
    sorted_ranks = sorted(rl_ranks.items(), key=get_rank_sort_value, reverse=True)[:10]
    
    lines = []
    for i, (user_id, rank_info) in enumerate(sorted_ranks, 1):
        user = bot.get_user(int(user_id))
        name = user.display_name if user else f"User {user_id}"
        
        if isinstance(rank_info, dict):
            rank_val = rank_info.get('rank', 0)
            division = rank_info.get('division')
        else:
            rank_val = rank_info  # Legacy format
            division = None
        
        rank_data = RL_RANKS.get(rank_val, RL_RANKS[0])
        div_text = f" Div {division}" if division else ""
        lines.append(f"`{i}.` {rank_data['emoji']} **{name}** - {rank_data['name']}{div_text}")
    
    embed = discord.Embed(
        title="🏆 Rocket League Leaderboard",
        description="\n".join(lines),
        color=0x00BFFF
    )
    await ctx.send(embed=embed)

@bot.hybrid_command(name='setrlprofile', aliases=['linkrl'])
async def set_rl_profile(ctx, *, profile_input: str):
    """Link your Rocket League Tracker profile (URL or platform + username)"""
    profile_input = profile_input.strip()
    
    # Check if it's a URL
    url_pattern = r'https?://rocketleague\.tracker\.(gg|network)/rocket-league/profile/([^/]+)/([^/]+)'
    url_match = re.match(url_pattern, profile_input)
    
    if url_match:
        platform = url_match.group(2).lower()
        username = url_match.group(3).split('/')[0]  # Remove /overview if present
    else:
        # Try platform + username format
        parts = profile_input.split(maxsplit=1)
        if len(parts) < 2:
            await ctx.send("❌ **Usage:**\n"
                          "`~setrlprofile <url>` - Paste your tracker URL\n"
                          "`~setrlprofile <platform> <username>` - epic/steam/psn/xbl + username")
            return
        platform = parts[0].lower()
        username = parts[1]
    
    valid_platforms = ['epic', 'steam', 'psn', 'xbl', 'switch']
    if platform not in valid_platforms:
        await ctx.send(f"❌ Invalid platform. Use: {', '.join(valid_platforms)}")
        return
    
    tracker_url = f"https://rocketleague.tracker.gg/rocket-league/profile/{platform}/{quote(username)}"
    rl_profiles[str(ctx.author.id)] = {'username': username, 'platform': platform, 'url': tracker_url}
    save_rl_profiles()
    
    await ctx.send(f"✅ Linked **{username}** on **{platform.upper()}**\n{tracker_url}")

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
    user_id = str(target.id)
    
    embed = discord.Embed(
        title=f"{target.display_name}'s Profile",
        color=target.color if target.color != discord.Color.default() else 0x5865F2
    )
    embed.set_thumbnail(url=target.display_avatar.url)
    
    rank_info = rl_ranks.get(user_id, {'rank': 0, 'division': None})
    if isinstance(rank_info, dict):
        rank_val = rank_info.get('rank', 0)
        division = rank_info.get('division')
    else:
        rank_val = rank_info  # Legacy format
        division = None
    rank_data = RL_RANKS.get(rank_val, RL_RANKS[0])
    div_text = f" Div {division}" if division else ""
    embed.add_field(name="🚀 RL Rank", value=f"{rank_data['emoji']} {rank_data['name']}{div_text}", inline=True)
    
    # Platform info
    profile = rl_profiles.get(user_id)
    if profile:
        platform_icons = {
            'epic': '🎮 Epic Games',
            'steam': '🎮 Steam',
            'psn': '🎮 PlayStation',
            'xbl': '🎮 Xbox',
            'switch': '🎮 Nintendo Switch'
        }
        platform_display = platform_icons.get(profile['platform'], f"🎮 {profile['platform'].upper()}")
        embed.add_field(name="Platform", value=platform_display, inline=True)
        
        tracker_url = profile.get('url') or f"https://rocketleague.tracker.gg/rocket-league/profile/{profile['platform']}/{quote(profile['username'])}"
        embed.add_field(name="🔗 Tracker", value=f"[{profile['username']}]({tracker_url})", inline=True)
    else:
        embed.add_field(name="Platform", value="Not linked", inline=True)
    
    if target.joined_at:
        embed.add_field(name="📅 Joined", value=target.joined_at.strftime("%b %d, %Y"), inline=True)
    
    user_bumps = sum(1 for r in reminders if r.get('completed', False))
    embed.add_field(name="🔔 Server Bumps", value=str(user_bumps), inline=True)
    
    await ctx.send(embed=embed)

@bot.hybrid_command(name='botinfo', aliases=['info', 'about'])
async def bot_info(ctx):
    """Show bot information and stats"""
    # Calculate stats
    server_count = len(bot.guilds)
    member_count = sum(g.member_count or 0 for g in bot.guilds)
    command_count = len(bot.commands)
    
    # Get owner
    owner = await bot.fetch_user(OWNER_ID)
    owner_text = owner.mention if owner else f"<@{OWNER_ID}>"
    
    embed = discord.Embed(color=0x5865F2)
    embed.set_author(name="Bot Online", icon_url=bot.user.display_avatar.url if bot.user else None)
    embed.description = "Kursein v3.2 - Rebuilt from the ground up!"
    
    embed.add_field(name="Commands", value=str(command_count), inline=True)
    embed.add_field(name="Servers", value=str(server_count), inline=True)
    embed.add_field(name="Members", value=f"{member_count:,}", inline=True)
    embed.add_field(name="Owner", value=owner_text, inline=True)
    
    embed.set_footer(text="Tokyo Ghoul + Rocket League Theme")
    
    await ctx.send(embed=embed)

# =====================
# COMMANDS - AFK SYSTEM
# =====================

@bot.hybrid_command(name='afk')
async def set_afk(ctx, *, reason: str = "AFK"):
    """Set your AFK status"""
    user_id = str(ctx.author.id)
    afk_users[user_id] = {
        'reason': reason,
        'since': datetime.now(timezone.utc).isoformat()
    }
    save_afk_users()
    await ctx.send(f"💤 {ctx.author.display_name} is now AFK: **{reason}**")

# =====================
# COMMANDS - RANK VERIFICATION
# =====================

@bot.hybrid_command(name='pendingranks', aliases=['rankqueue'])
@commands.has_permissions(administrator=True)
async def pending_ranks_list(ctx):
    """View pending rank verifications"""
    if not pending_ranks:
        await ctx.send("✅ No pending rank verifications!")
        return
    
    lines = []
    for user_id, data in list(pending_ranks.items())[:10]:
        user = bot.get_user(int(user_id))
        name = user.display_name if user else f"User {user_id}"
        rank_data = RL_RANKS.get(data['rank'], RL_RANKS[0])
        div_text = f" Div {data.get('division', 1)}" if data.get('division') else ""
        tracker = data.get('tracker_url', 'No URL')
        lines.append(f"**{name}** - {rank_data['emoji']} {rank_data['name']}{div_text}\n└ [Tracker]({tracker})")
    
    embed = discord.Embed(
        title="⏳ Pending Rank Verifications",
        description="\n\n".join(lines),
        color=0xFFA500
    )
    embed.set_footer(text=f"Use ~approverank <@user> or ~denyrank <@user>")
    await ctx.send(embed=embed)

@bot.hybrid_command(name='approverank')
@commands.has_permissions(administrator=True)
async def approve_rank(ctx, user_input: str):
    """Approve a pending rank verification"""
    user_id = re.sub(r'[<@!>]', '', user_input)
    
    if user_id not in pending_ranks:
        await ctx.send("❌ No pending rank for this user")
        return
    
    data = pending_ranks[user_id]
    rl_ranks[user_id] = {'rank': data['rank'], 'division': data.get('division', 1)}
    save_rl_ranks()
    
    del pending_ranks[user_id]
    save_pending_ranks()
    
    rank_data = RL_RANKS.get(data['rank'], RL_RANKS[0])
    div_text = f" Div {data.get('division', 1)}" if data.get('division') else ""
    
    # Auto-assign rank role
    member = ctx.guild.get_member(int(user_id))
    if member:
        await assign_rank_role(member, data['rank'])
    
    try:
        user = await bot.fetch_user(int(user_id))
        await user.send(f"✅ Your rank **{rank_data['name']}{div_text}** has been approved!")
    except:
        pass
    
    await ctx.send(f"✅ Approved {rank_data['emoji']} **{rank_data['name']}{div_text}** for <@{user_id}>")

@bot.hybrid_command(name='setrankrole')
@commands.has_permissions(administrator=True)
async def set_rank_role(ctx, tier: str, role: discord.Role):
    """Set a role for a rank tier - Usage: ~setrankrole diamond @Diamond"""
    valid_tiers = ['bronze', 'silver', 'gold', 'platinum', 'diamond', 'champion', 'grand_champion', 'ssl']
    tier_lower = tier.lower().replace(' ', '_')
    
    if tier_lower not in valid_tiers:
        await ctx.send(f"❌ Invalid tier. Use: {', '.join(valid_tiers)}")
        return
    
    rank_roles[tier_lower] = role.id
    save_rank_roles()
    await ctx.send(f"✅ {tier.title()} ranks will now receive {role.mention}")

@bot.hybrid_command(name='rankroles')
@commands.has_permissions(administrator=True)
async def view_rank_roles(ctx):
    """View configured rank roles"""
    if not rank_roles:
        await ctx.send("❌ No rank roles configured. Use `~setrankrole <tier> @role`")
        return
    
    lines = []
    tiers = ['bronze', 'silver', 'gold', 'platinum', 'diamond', 'champion', 'grand_champion', 'ssl']
    for tier in tiers:
        role_id = rank_roles.get(tier)
        if role_id:
            role = ctx.guild.get_role(int(role_id))
            lines.append(f"**{tier.replace('_', ' ').title()}**: {role.mention if role else 'Role not found'}")
        else:
            lines.append(f"**{tier.replace('_', ' ').title()}**: Not set")
    
    embed = discord.Embed(
        title="🎮 Rank Role Configuration",
        description="\n".join(lines),
        color=0x5865F2
    )
    await ctx.send(embed=embed)

@bot.hybrid_command(name='denyrank')
@commands.has_permissions(administrator=True)
async def deny_rank(ctx, user_input: str, *, reason: str = "No reason provided"):
    """Deny a pending rank verification"""
    user_id = re.sub(r'[<@!>]', '', user_input)
    
    if user_id not in pending_ranks:
        await ctx.send("❌ No pending rank for this user")
        return
    
    data = pending_ranks[user_id]
    rank_data = RL_RANKS.get(data['rank'], RL_RANKS[0])
    
    del pending_ranks[user_id]
    save_pending_ranks()
    
    try:
        user = await bot.fetch_user(int(user_id))
        await user.send(f"❌ Your rank request for **{rank_data['name']}** was denied.\nReason: {reason}")
    except:
        pass
    
    await ctx.send(f"❌ Denied rank request from <@{user_id}>\nReason: {reason}")

# =====================
# COMMANDS - SERVER STATS
# =====================

@bot.hybrid_command(name='serverstats', aliases=['sstats'])
async def server_stats(ctx):
    """View server statistics"""
    guild = ctx.guild
    if not guild:
        await ctx.send("❌ This command only works in a server")
        return
    
    total_members = guild.member_count or 0
    bots = sum(1 for m in guild.members if m.bot)
    humans = total_members - bots
    online = sum(1 for m in guild.members if m.status != discord.Status.offline)
    
    text_channels = len(guild.text_channels)
    voice_channels = len(guild.voice_channels)
    roles = len(guild.roles)
    
    created = guild.created_at
    age_days = (datetime.now(timezone.utc) - created).days
    
    embed = discord.Embed(
        title=f"📊 {guild.name} Stats",
        color=0x5865F2
    )
    if guild.icon:
        embed.set_thumbnail(url=guild.icon.url)
    
    embed.add_field(name="👥 Members", value=f"{humans:,} humans\n{bots} bots", inline=True)
    embed.add_field(name="🟢 Online", value=f"{online:,}", inline=True)
    embed.add_field(name="📅 Created", value=f"{created.strftime('%b %d, %Y')}\n({age_days:,} days ago)", inline=True)
    embed.add_field(name="💬 Channels", value=f"{text_channels} text\n{voice_channels} voice", inline=True)
    embed.add_field(name="🎭 Roles", value=str(roles), inline=True)
    embed.add_field(name="👑 Owner", value=guild.owner.mention if guild.owner else "Unknown", inline=True)
    
    await ctx.send(embed=embed)

# =====================
# MOD LOGGING EVENTS
# =====================

@bot.event
async def on_member_ban(guild, user):
    """Log when a member is banned"""
    channel = bot.get_channel(LOG_CHANNEL_ID)
    if not channel:
        return
    
    embed = discord.Embed(
        title="🔨 Member Banned",
        description=f"**User:** {user} ({user.id})",
        color=0xFF0000
    )
    embed.set_thumbnail(url=user.display_avatar.url)
    embed.timestamp = datetime.now(timezone.utc)
    
    try:
        async for entry in guild.audit_logs(action=discord.AuditLogAction.ban, limit=1):
            if entry.target.id == user.id:
                embed.add_field(name="Banned by", value=entry.user.mention, inline=True)
                if entry.reason:
                    embed.add_field(name="Reason", value=entry.reason, inline=False)
                break
    except:
        pass
    
    await channel.send(embed=embed)

@bot.event
async def on_member_unban(guild, user):
    """Log when a member is unbanned"""
    channel = bot.get_channel(LOG_CHANNEL_ID)
    if not channel:
        return
    
    embed = discord.Embed(
        title="🔓 Member Unbanned",
        description=f"**User:** {user} ({user.id})",
        color=0x00FF00
    )
    embed.set_thumbnail(url=user.display_avatar.url)
    embed.timestamp = datetime.now(timezone.utc)
    await channel.send(embed=embed)

@bot.hybrid_command(name='warn')
@commands.has_permissions(kick_members=True)
async def warn_user(ctx, member: discord.Member, *, reason: str = "No reason provided"):
    """Warn a user and log it"""
    channel = bot.get_channel(LOG_CHANNEL_ID)
    
    embed = discord.Embed(
        title="⚠️ Member Warned",
        color=0xFFFF00
    )
    embed.add_field(name="User", value=f"{member.mention} ({member})", inline=True)
    embed.add_field(name="Warned by", value=ctx.author.mention, inline=True)
    embed.add_field(name="Reason", value=reason, inline=False)
    embed.set_thumbnail(url=member.display_avatar.url)
    embed.timestamp = datetime.now(timezone.utc)
    
    if channel:
        await channel.send(embed=embed)
    
    try:
        await member.send(f"⚠️ You were warned in **{ctx.guild.name}**\nReason: {reason}")
    except:
        pass
    
    await ctx.send(f"⚠️ Warned {member.mention}: {reason}")

# =====================
# JJK ECONOMY COMMANDS
# =====================

@bot.hybrid_command(name='jjkstart', aliases=['jstart'])
async def jjk_start(ctx):
    """Start your Jujutsu Sorcerer journey"""
    uid = str(ctx.author.id)
    if uid in jjk_players:
        await ctx.send("You already have a Jujutsu School! Use `~school` to view it.")
        return
    
    player = create_jjk_player(ctx.author.id)
    embed = discord.Embed(
        title="🔮 Welcome to Jujutsu High!",
        description=f"**{ctx.author.display_name}**, you've enrolled as a Jujutsu Sorcerer!\n\nYou start as a **Grade 4** sorcerer with **Yuji Itadori** on your team.",
        color=0x9B59B6
    )
    embed.add_field(name="💴 Starting Yen", value="500", inline=True)
    embed.add_field(name="📊 Level", value="1", inline=True)
    embed.add_field(name="⚔️ First Steps", value="`~hunt` - Exorcise curses for yen\n`~sorcerers` - View available sorcerers\n`~school` - View your stats", inline=False)
    embed.set_footer(text="Rise through the ranks and become a Special Grade!")
    await ctx.send(embed=embed)

@bot.hybrid_command(name='school', aliases=['jjk', 'jschool'])
async def jjk_school(ctx, member: Optional[discord.Member] = None):
    """View your Jujutsu School stats"""
    target = member or ctx.author
    player = get_jjk_player(target.id)
    if not player:
        if target == ctx.author:
            await ctx.send("You haven't started yet! Use `~jjkstart` to begin.")
        else:
            await ctx.send(f"{target.display_name} hasn't started their journey yet.")
        return
    
    grade = get_jjk_grade(player['level'])
    income = calculate_jjk_income(player)
    domain = JJK_DOMAINS[player.get('domain', 0)]
    xp_needed = xp_for_level(player['level'])
    
    embed = discord.Embed(
        title=f"🏫 {target.display_name}'s Jujutsu School",
        color=0x9B59B6
    )
    embed.set_thumbnail(url=target.display_avatar.url)
    
    embed.add_field(name="💴 Yen", value=f"{player['yen']:,}", inline=True)
    embed.add_field(name="📊 Level", value=f"{player['level']} ({grade})", inline=True)
    embed.add_field(name="✨ XP", value=f"{player['xp']}/{xp_needed}", inline=True)
    embed.add_field(name="💰 Income/hr", value=f"{income:,} yen", inline=True)
    embed.add_field(name="👻 Curses Exorcised", value=f"{player['curses_exorcised']:,}", inline=True)
    embed.add_field(name="📜 Missions", value=f"{player['missions_completed']}", inline=True)
    embed.add_field(name="🌀 Domain", value=domain['name'], inline=True)
    embed.add_field(name="👥 Sorcerers", value=str(len(player.get('sorcerers', []))), inline=True)
    
    if player.get('clan'):
        embed.add_field(name="🏯 Clan", value=player['clan'], inline=True)
    
    await ctx.send(embed=embed)

@bot.hybrid_command(name='balance', aliases=['bal', 'yen'])
async def jjk_balance(ctx, member: Optional[discord.Member] = None):
    """Check your yen balance"""
    target = member or ctx.author
    player = get_jjk_player(target.id)
    if not player:
        await ctx.send("No profile found. Use `~jjkstart` to begin!")
        return
    
    await ctx.send(f"💴 **{target.display_name}** has **{player['yen']:,}** yen")

@bot.hybrid_command(name='hunt', aliases=['exorcise'])
async def jjk_hunt(ctx):
    """Hunt and exorcise curses for yen and XP"""
    player = get_jjk_player(ctx.author.id)
    if not player:
        await ctx.send("Use `~jjkstart` to begin your journey!")
        return
    
    uid = str(ctx.author.id)
    now = datetime.now(timezone.utc)
    
    # Check cooldown (30 seconds)
    last_hunt = parse_iso_timestamp(player.get('last_hunt'))
    if last_hunt:
        elapsed = (now - last_hunt).total_seconds()
        if elapsed < 30:
            remaining = max(1, int(30 - elapsed))
            await ctx.send(f"⏳ You're still recovering! Wait **{remaining}s** before hunting again.")
            return
    
    # Select curse based on level
    max_curse_idx = min(player['level'] // 5, len(JJK_CURSES) - 1)
    curse = random.choice(JJK_CURSES[:max_curse_idx + 1])
    
    # Calculate rewards with multipliers
    base_yen = random.randint(curse['min_yen'], curse['max_yen'])
    tech_mult = 1.0
    for tech in player.get('techniques', []):
        tech_mult *= JJK_TECHNIQUES[tech]['multiplier']
    domain_mult = JJK_DOMAINS[player.get('domain', 0)]['multiplier']
    
    yen_earned = int(base_yen * tech_mult * domain_mult)
    xp_earned = curse['xp']
    
    player['yen'] += yen_earned
    player['xp'] += xp_earned
    player['curses_exorcised'] += 1
    player['last_hunt'] = now.isoformat()
    
    # Level up check
    leveled = False
    while player['xp'] >= xp_for_level(player['level']):
        player['xp'] -= xp_for_level(player['level'])
        player['level'] += 1
        leveled = True
    
    save_jjk_data()
    
    embed = discord.Embed(
        title=f"⚔️ Exorcised: {curse['name']}",
        description=f"You defeated the curse and earned rewards!",
        color=0x00FF00
    )
    embed.add_field(name="💴 Yen Earned", value=f"+{yen_earned:,}", inline=True)
    embed.add_field(name="✨ XP Earned", value=f"+{xp_earned}", inline=True)
    embed.add_field(name="💰 Total Yen", value=f"{player['yen']:,}", inline=True)
    
    if leveled:
        grade = get_jjk_grade(player['level'])
        embed.add_field(name="🎉 LEVEL UP!", value=f"You're now Level {player['level']} ({grade})!", inline=False)
    
    await ctx.send(embed=embed)

@bot.hybrid_command(name='train')
async def jjk_train(ctx):
    """Train to gain XP and level up"""
    player = get_jjk_player(ctx.author.id)
    if not player:
        await ctx.send("Use `~jjkstart` to begin your journey!")
        return
    
    now = datetime.now(timezone.utc)
    last_train = parse_iso_timestamp(player.get('last_train'))
    if last_train:
        elapsed = (now - last_train).total_seconds()
        if elapsed < 60:
            remaining = max(1, int(60 - elapsed))
            await ctx.send(f"⏳ Still training! Wait **{remaining}s** to train again.")
            return
    
    xp_earned = random.randint(20, 50) + (player['level'] * 2)
    player['xp'] += xp_earned
    player['last_train'] = now.isoformat()
    
    leveled = False
    while player['xp'] >= xp_for_level(player['level']):
        player['xp'] -= xp_for_level(player['level'])
        player['level'] += 1
        leveled = True
    
    save_jjk_data()
    
    messages = [
        "practiced Divergent Fist on training dummies",
        "sparred with Todo until exhaustion",
        "meditated to control cursed energy",
        "ran 100 laps around Jujutsu High",
        "practiced domain expansion visualization"
    ]
    
    embed = discord.Embed(
        title="🥋 Training Complete!",
        description=f"You {random.choice(messages)}.",
        color=0x3498DB
    )
    embed.add_field(name="✨ XP Gained", value=f"+{xp_earned}", inline=True)
    
    if leveled:
        grade = get_jjk_grade(player['level'])
        embed.add_field(name="🎉 LEVEL UP!", value=f"Level {player['level']} ({grade})!", inline=False)
    
    await ctx.send(embed=embed)

@bot.hybrid_command(name='daily')
async def jjk_daily(ctx):
    """Collect your daily yen reward"""
    player = get_jjk_player(ctx.author.id)
    if not player:
        await ctx.send("Use `~jjkstart` to begin your journey!")
        return
    
    now = datetime.now(timezone.utc)
    last_daily = parse_iso_timestamp(player.get('last_daily'))
    
    if last_daily:
        hours_passed = max(0, (now - last_daily).total_seconds() / 3600)
        if hours_passed < 24:
            remaining = 24 - hours_passed
            hours = int(remaining)
            mins = int((remaining - hours) * 60)
            await ctx.send(f"⏳ Daily already claimed! Come back in **{hours}h {mins}m**")
            return
        
        # Check streak
        if hours_passed < 48:
            player['daily_streak'] = player.get('daily_streak', 0) + 1
        else:
            player['daily_streak'] = 1
    else:
        player['daily_streak'] = 1
    
    streak = player['daily_streak']
    base_reward = 1000
    streak_bonus = min(streak * 100, 1000)
    total = base_reward + streak_bonus
    
    player['yen'] += total
    player['last_daily'] = now.isoformat()
    save_jjk_data()
    
    embed = discord.Embed(
        title="📅 Daily Reward Claimed!",
        color=0xFFD700
    )
    embed.add_field(name="💴 Base Reward", value=f"{base_reward:,} yen", inline=True)
    embed.add_field(name="🔥 Streak Bonus", value=f"+{streak_bonus:,} yen", inline=True)
    embed.add_field(name="💰 Total", value=f"**{total:,}** yen", inline=True)
    embed.add_field(name="📆 Streak", value=f"{streak} days", inline=True)
    embed.set_footer(text="Come back tomorrow to keep your streak!")
    
    await ctx.send(embed=embed)

@bot.hybrid_command(name='collect')
async def jjk_collect(ctx):
    """Collect your hourly income from sorcerers"""
    player = get_jjk_player(ctx.author.id)
    if not player:
        await ctx.send("Use `~jjkstart` to begin your journey!")
        return
    
    now = datetime.now(timezone.utc)
    last_collect = parse_iso_timestamp(player.get('last_collect'))
    
    if last_collect:
        hours_passed = max(0, (now - last_collect).total_seconds() / 3600)
        if hours_passed < 1:
            mins = max(1, int((1 - hours_passed) * 60))
            await ctx.send(f"⏳ Income not ready! Wait **{mins}m** to collect.")
            return
    else:
        hours_passed = 1
    
    hours_to_pay = max(1, min(int(hours_passed), 24))  # Cap at 24 hours, min 1
    income = calculate_jjk_income(player)
    total = income * hours_to_pay
    
    player['yen'] += total
    player['last_collect'] = now.isoformat()
    save_jjk_data()
    
    embed = discord.Embed(
        title="💰 Income Collected!",
        color=0x2ECC71
    )
    embed.add_field(name="⏰ Hours", value=str(hours_to_pay), inline=True)
    embed.add_field(name="💴 Per Hour", value=f"{income:,}", inline=True)
    embed.add_field(name="💵 Total", value=f"**{total:,}** yen", inline=True)
    
    await ctx.send(embed=embed)

@bot.hybrid_command(name='sorcerers')
async def jjk_sorcerers(ctx):
    """View available sorcerers to hire"""
    player = get_jjk_player(ctx.author.id)
    if not player:
        await ctx.send("Use `~jjkstart` to begin your journey!")
        return
    
    embed = discord.Embed(
        title="👥 Jujutsu Sorcerers",
        description="Hire sorcerers to increase your income!",
        color=0x9B59B6
    )
    
    for key, sorc in JJK_SORCERERS.items():
        owned = "✅" if key in player.get('sorcerers', []) else ""
        locked = player['level'] < sorc['unlock']
        status = "🔒" if locked else owned
        
        if locked:
            value = f"Unlocks at Level {sorc['unlock']}"
        else:
            value = f"Cost: {sorc['cost']:,} yen\nIncome: +{sorc['income']}/hr"
        
        embed.add_field(
            name=f"{sorc['emoji']} {sorc['name']} {status}",
            value=value,
            inline=True
        )
    
    embed.set_footer(text="Use ~hire <name> to hire a sorcerer")
    await ctx.send(embed=embed)

@bot.hybrid_command(name='hire')
async def jjk_hire(ctx, *, sorcerer_name: str):
    """Hire a sorcerer for your school"""
    player = get_jjk_player(ctx.author.id)
    if not player:
        await ctx.send("Use `~jjkstart` to begin your journey!")
        return
    
    sorc_key = sorcerer_name.lower().replace(" ", "")
    
    # Find matching sorcerer
    found = None
    for key, sorc in JJK_SORCERERS.items():
        if key == sorc_key or sorc['name'].lower().replace(" ", "") == sorc_key:
            found = (key, sorc)
            break
    
    if not found:
        await ctx.send(f"❌ Sorcerer not found. Use `~sorcerers` to see available options.")
        return
    
    key, sorc = found
    
    if key in player.get('sorcerers', []):
        await ctx.send(f"❌ **{sorc['name']}** is already on your team!")
        return
    
    if player['level'] < sorc['unlock']:
        await ctx.send(f"🔒 You need Level {sorc['unlock']} to hire **{sorc['name']}**!")
        return
    
    if player['yen'] < sorc['cost']:
        await ctx.send(f"❌ You need **{sorc['cost']:,}** yen to hire **{sorc['name']}**! (You have {player['yen']:,})")
        return
    
    player['yen'] -= sorc['cost']
    player['sorcerers'].append(key)
    save_jjk_data()
    
    embed = discord.Embed(
        title=f"{sorc['emoji']} Sorcerer Hired!",
        description=f"**{sorc['name']}** has joined your school!",
        color=0x2ECC71
    )
    embed.add_field(name="💴 Cost", value=f"-{sorc['cost']:,} yen", inline=True)
    embed.add_field(name="💰 Income Boost", value=f"+{sorc['income']}/hr", inline=True)
    
    await ctx.send(embed=embed)

@bot.hybrid_command(name='techniques', aliases=['techs'])
async def jjk_techniques(ctx):
    """View available cursed techniques"""
    player = get_jjk_player(ctx.author.id)
    if not player:
        await ctx.send("Use `~jjkstart` to begin your journey!")
        return
    
    embed = discord.Embed(
        title="🔮 Cursed Techniques",
        description="Learn techniques to multiply your earnings!",
        color=0xE74C3C
    )
    
    for key, tech in JJK_TECHNIQUES.items():
        owned = "✅" if key in player.get('techniques', []) else ""
        mult_pct = int((tech['multiplier'] - 1) * 100)
        embed.add_field(
            name=f"{tech['name']} {owned}",
            value=f"{tech['desc']}\nCost: {tech['cost']:,} yen | +{mult_pct}% earnings",
            inline=False
        )
    
    embed.set_footer(text="Use ~learntechnique <name> to learn")
    await ctx.send(embed=embed)

@bot.hybrid_command(name='learntechnique', aliases=['learntech'])
async def jjk_learn_tech(ctx, *, technique_name: str):
    """Learn a cursed technique"""
    player = get_jjk_player(ctx.author.id)
    if not player:
        await ctx.send("Use `~jjkstart` to begin your journey!")
        return
    
    tech_key = technique_name.lower().replace(" ", "_")
    
    found = None
    for key, tech in JJK_TECHNIQUES.items():
        if key == tech_key or tech['name'].lower().replace(" ", "_") == tech_key:
            found = (key, tech)
            break
    
    if not found:
        await ctx.send("❌ Technique not found. Use `~techniques` to see options.")
        return
    
    key, tech = found
    
    if key in player.get('techniques', []):
        await ctx.send(f"❌ You already know **{tech['name']}**!")
        return
    
    if player['yen'] < tech['cost']:
        await ctx.send(f"❌ You need **{tech['cost']:,}** yen! (You have {player['yen']:,})")
        return
    
    player['yen'] -= tech['cost']
    player['techniques'].append(key)
    save_jjk_data()
    
    await ctx.send(f"🔮 You learned **{tech['name']}**! {tech['desc']}")

@bot.hybrid_command(name='tools')
async def jjk_tools(ctx):
    """View available cursed tools"""
    player = get_jjk_player(ctx.author.id)
    if not player:
        await ctx.send("Use `~jjkstart` to begin your journey!")
        return
    
    embed = discord.Embed(
        title="🗡️ Cursed Tools",
        description="Equip tools to boost your income!",
        color=0x95A5A6
    )
    
    for key, tool in JJK_TOOLS.items():
        owned = "✅" if key in player.get('tools', []) else ""
        embed.add_field(
            name=f"{tool['name']} {owned}",
            value=f"{tool['desc']}\nCost: {tool['cost']:,} yen | +{tool['bonus']}/hr",
            inline=True
        )
    
    embed.set_footer(text="Use ~buytool <name> to purchase")
    await ctx.send(embed=embed)

@bot.hybrid_command(name='buytool')
async def jjk_buy_tool(ctx, *, tool_name: str):
    """Buy a cursed tool"""
    player = get_jjk_player(ctx.author.id)
    if not player:
        await ctx.send("Use `~jjkstart` to begin your journey!")
        return
    
    tool_key = tool_name.lower().replace(" ", "_")
    
    found = None
    for key, tool in JJK_TOOLS.items():
        if key == tool_key or tool['name'].lower().replace(" ", "_") == tool_key:
            found = (key, tool)
            break
    
    if not found:
        await ctx.send("❌ Tool not found. Use `~tools` to see options.")
        return
    
    key, tool = found
    
    if key in player.get('tools', []):
        await ctx.send(f"❌ You already own **{tool['name']}**!")
        return
    
    if player['yen'] < tool['cost']:
        await ctx.send(f"❌ You need **{tool['cost']:,}** yen! (You have {player['yen']:,})")
        return
    
    player['yen'] -= tool['cost']
    player['tools'].append(key)
    save_jjk_data()
    
    await ctx.send(f"🗡️ You acquired **{tool['name']}**! +{tool['bonus']}/hr income")

@bot.hybrid_command(name='domain', aliases=['domains'])
async def jjk_domain(ctx):
    """View and upgrade your Domain Expansion"""
    player = get_jjk_player(ctx.author.id)
    if not player:
        await ctx.send("Use `~jjkstart` to begin your journey!")
        return
    
    current = player.get('domain', 0)
    
    embed = discord.Embed(
        title="🌀 Domain Expansion",
        description="The pinnacle of Jujutsu - multiply all earnings!",
        color=0x8E44AD
    )
    
    for level, domain in JJK_DOMAINS.items():
        if level == 0:
            continue
        is_current = "⬅️ Current" if level == current else ""
        is_next = "📍 Next" if level == current + 1 else ""
        owned = "✅" if level <= current else ""
        
        mult_pct = int(domain['multiplier'] * 100)
        embed.add_field(
            name=f"{domain['name']} {owned} {is_current} {is_next}",
            value=f"Cost: {domain['cost']:,} yen\n{mult_pct}% earnings multiplier",
            inline=False
        )
    
    if current < 4:
        embed.set_footer(text="Use ~upgradedomain to unlock the next level")
    else:
        embed.set_footer(text="You've mastered the ultimate Domain!")
    
    await ctx.send(embed=embed)

@bot.hybrid_command(name='upgradedomain')
async def jjk_upgrade_domain(ctx):
    """Upgrade your Domain Expansion"""
    player = get_jjk_player(ctx.author.id)
    if not player:
        await ctx.send("Use `~jjkstart` to begin your journey!")
        return
    
    current = player.get('domain', 0)
    
    if current >= 4:
        await ctx.send("🌀 You've already mastered **Infinite Void** - the ultimate Domain!")
        return
    
    next_level = current + 1
    next_domain = JJK_DOMAINS[next_level]
    
    if player['yen'] < next_domain['cost']:
        await ctx.send(f"❌ You need **{next_domain['cost']:,}** yen for **{next_domain['name']}**! (You have {player['yen']:,})")
        return
    
    player['yen'] -= next_domain['cost']
    player['domain'] = next_level
    save_jjk_data()
    
    mult_pct = int(next_domain['multiplier'] * 100)
    embed = discord.Embed(
        title="🌀 Domain Expansion Unlocked!",
        description=f"**{next_domain['name']}**\n\nAll earnings now multiplied by **{mult_pct}%**!",
        color=0x8E44AD
    )
    
    await ctx.send(embed=embed)

@bot.hybrid_command(name='jjklb', aliases=['jjkleaderboard', 'jlb'])
async def jjk_leaderboard(ctx):
    """View the JJK leaderboard"""
    if not jjk_players:
        await ctx.send("No players yet! Be the first with `~jjkstart`")
        return
    
    sorted_players = sorted(jjk_players.items(), key=lambda x: x[1].get('yen', 0), reverse=True)[:10]
    
    embed = discord.Embed(
        title="🏆 Jujutsu Sorcerer Leaderboard",
        description="Top sorcerers by yen",
        color=0xFFD700
    )
    
    medals = ["🥇", "🥈", "🥉"]
    lines = []
    
    for i, (uid, data) in enumerate(sorted_players):
        user = bot.get_user(int(uid))
        name = user.display_name if user else f"User {uid}"
        medal = medals[i] if i < 3 else f"**{i+1}.**"
        grade = get_jjk_grade(data.get('level', 1))
        lines.append(f"{medal} {name}\n└ {data.get('yen', 0):,} yen | Lv.{data.get('level', 1)} ({grade})")
    
    embed.description = "\n".join(lines) if lines else "No players found"
    await ctx.send(embed=embed)

@bot.hybrid_command(name='clancreate', aliases=['createclan'])
async def jjk_clan_create(ctx, *, clan_name: str):
    """Create a clan (costs 50,000 yen)"""
    player = get_jjk_player(ctx.author.id)
    if not player:
        await ctx.send("Use `~jjkstart` first!")
        return
    
    if player.get('clan'):
        await ctx.send("❌ You're already in a clan! Leave it first with `~clanleave`")
        return
    
    if len(clan_name) > 30:
        await ctx.send("❌ Clan name too long (max 30 characters)")
        return
    
    clan_key = clan_name.lower()
    if clan_key in jjk_clans:
        await ctx.send("❌ A clan with that name already exists!")
        return
    
    cost = 50000
    if player['yen'] < cost:
        await ctx.send(f"❌ Creating a clan costs **{cost:,}** yen! (You have {player['yen']:,})")
        return
    
    player['yen'] -= cost
    player['clan'] = clan_name
    
    jjk_clans[clan_key] = {
        "name": clan_name,
        "leader": str(ctx.author.id),
        "members": [str(ctx.author.id)],
        "created": datetime.now(timezone.utc).isoformat(),
        "total_yen": player['yen']
    }
    
    save_jjk_data()
    
    await ctx.send(f"🏯 **{clan_name}** clan has been created! You are the leader.")

@bot.hybrid_command(name='clanjoin', aliases=['joinclan'])
async def jjk_clan_join(ctx, *, clan_name: str):
    """Join an existing clan"""
    player = get_jjk_player(ctx.author.id)
    if not player:
        await ctx.send("Use `~jjkstart` first!")
        return
    
    if player.get('clan'):
        await ctx.send("❌ You're already in a clan! Leave it first.")
        return
    
    clan_key = clan_name.lower()
    if clan_key not in jjk_clans:
        await ctx.send("❌ Clan not found!")
        return
    
    clan = jjk_clans[clan_key]
    clan['members'].append(str(ctx.author.id))
    player['clan'] = clan['name']
    save_jjk_data()
    
    await ctx.send(f"🏯 You joined **{clan['name']}**!")

@bot.hybrid_command(name='clanleave', aliases=['leaveclan'])
async def jjk_clan_leave(ctx):
    """Leave your current clan"""
    player = get_jjk_player(ctx.author.id)
    if not player:
        await ctx.send("Use `~jjkstart` first!")
        return
    
    if not player.get('clan'):
        await ctx.send("❌ You're not in a clan!")
        return
    
    clan_key = player['clan'].lower()
    if clan_key in jjk_clans:
        clan = jjk_clans[clan_key]
        uid = str(ctx.author.id)
        if uid in clan['members']:
            clan['members'].remove(uid)
        
        # Delete clan if empty
        if not clan['members']:
            del jjk_clans[clan_key]
    
    old_clan = player['clan']
    player['clan'] = None
    save_jjk_data()
    
    await ctx.send(f"👋 You left **{old_clan}**")

@bot.hybrid_command(name='claninfo', aliases=['clan'])
async def jjk_clan_info(ctx, *, clan_name: Optional[str] = None):
    """View clan information"""
    player = get_jjk_player(ctx.author.id)
    
    if clan_name:
        clan_key = clan_name.lower()
    elif player and player.get('clan'):
        clan_key = player['clan'].lower()
    else:
        await ctx.send("Specify a clan name or join one first!")
        return
    
    if clan_key not in jjk_clans:
        await ctx.send("❌ Clan not found!")
        return
    
    clan = jjk_clans[clan_key]
    
    # Calculate total clan wealth
    total_yen = 0
    total_level = 0
    for mid in clan['members']:
        mp = jjk_players.get(mid, {})
        total_yen += mp.get('yen', 0)
        total_level += mp.get('level', 1)
    
    leader = bot.get_user(int(clan['leader']))
    leader_name = leader.display_name if leader else "Unknown"
    
    embed = discord.Embed(
        title=f"🏯 {clan['name']}",
        color=0x9B59B6
    )
    embed.add_field(name="👑 Leader", value=leader_name, inline=True)
    embed.add_field(name="👥 Members", value=str(len(clan['members'])), inline=True)
    embed.add_field(name="💴 Total Wealth", value=f"{total_yen:,}", inline=True)
    embed.add_field(name="📊 Avg Level", value=f"{total_level // max(1, len(clan['members']))}", inline=True)
    
    await ctx.send(embed=embed)

@bot.hybrid_command(name='clanlb', aliases=['clanleaderboard'])
async def jjk_clan_lb(ctx):
    """View clan leaderboard"""
    if not jjk_clans:
        await ctx.send("No clans exist yet! Create one with `~clancreate <name>`")
        return
    
    # Calculate total wealth for each clan
    clan_wealth = []
    for key, clan in jjk_clans.items():
        total = sum(jjk_players.get(m, {}).get('yen', 0) for m in clan['members'])
        clan_wealth.append((clan['name'], len(clan['members']), total))
    
    clan_wealth.sort(key=lambda x: x[2], reverse=True)
    
    embed = discord.Embed(
        title="🏯 Clan Leaderboard",
        color=0xFFD700
    )
    
    lines = []
    medals = ["🥇", "🥈", "🥉"]
    for i, (name, members, wealth) in enumerate(clan_wealth[:10]):
        medal = medals[i] if i < 3 else f"**{i+1}.**"
        lines.append(f"{medal} **{name}**\n└ {wealth:,} yen | {members} members")
    
    embed.description = "\n".join(lines)
    await ctx.send(embed=embed)

@bot.hybrid_command(name='jjkguide', aliases=['jguide'])
async def jjk_guide(ctx):
    """View all JJK commands"""
    prefix = get_prefix_from_ctx(ctx)
    
    embed = discord.Embed(
        title="🔮 Jujutsu Kaisen Economy Guide",
        description="Become the strongest sorcerer!",
        color=0x9B59B6
    )
    
    embed.add_field(name="📝 Getting Started", value=f"""
`{prefix}jjkstart` - Begin your journey
`{prefix}school` - View your stats
`{prefix}balance` - Check yen
    """, inline=False)
    
    embed.add_field(name="⚔️ Earning Yen", value=f"""
`{prefix}hunt` - Exorcise curses (30s cd)
`{prefix}train` - Gain XP (60s cd)
`{prefix}daily` - Daily reward
`{prefix}collect` - Collect hourly income
    """, inline=False)
    
    embed.add_field(name="🛒 Upgrades", value=f"""
`{prefix}sorcerers` / `{prefix}hire <name>`
`{prefix}techniques` / `{prefix}learntechnique <name>`
`{prefix}tools` / `{prefix}buytool <name>`
`{prefix}domain` / `{prefix}upgradedomain`
    """, inline=False)
    
    embed.add_field(name="🏯 Clans", value=f"""
`{prefix}clancreate <name>` - Create (50k yen)
`{prefix}clanjoin <name>` - Join a clan
`{prefix}clanleave` - Leave clan
`{prefix}claninfo` - View clan
`{prefix}clanlb` - Clan leaderboard
    """, inline=False)
    
    embed.add_field(name="📊 Leaderboard", value=f"""
`{prefix}jjklb` - Top sorcerers
    """, inline=False)
    
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
`{prefix}setrlprofile <platform> <user>` - Link Tracker (required)
`{prefix}setrank <rank>` - Submit rank for verification
`{prefix}rllb` - Rank leaderboard
`{prefix}stats [@user]` - View RL stats
`{prefix}profile [@user]` - View profile
    """, inline=False)
    
    embed.add_field(name="🔧 RL Admin", value=f"""
`{prefix}pendingranks` - View pending verifications
`{prefix}approverank <@user>` - Approve rank
`{prefix}denyrank <@user> [reason]` - Deny rank
`{prefix}adminsetprofile <@user/ID> <rank> <url>` - Set rank directly
`{prefix}setrankrole <tier> @role` - Configure auto-role
`{prefix}rankroles` - View role config
`{prefix}resetranks` - Reset all ranks
    """, inline=False)
    
    embed.add_field(name="💤 AFK System", value=f"""
`{prefix}afk [reason]` - Set AFK status
    """, inline=False)
    
    embed.add_field(name="📊 Server", value=f"""
`{prefix}serverstats` - Server statistics
`{prefix}botinfo` - Bot stats & info
    """, inline=False)
    
    embed.add_field(name="🔨 Moderation", value=f"""
`{prefix}warn <@user> [reason]` - Warn a user
    """, inline=False)
    
    embed.add_field(name="🔔 Other", value=f"""
`{prefix}bumpinfo` - Bump reminder status
`{prefix}list` - View monitored streamers
    """, inline=False)
    
    embed.add_field(name="🔮 JJK Economy", value=f"""
`{prefix}jjkguide` - Full JJK command list
`{prefix}jjkstart` - Start your sorcerer journey
    """, inline=False)
    
    await ctx.send(embed=embed)

# Run the bot
if __name__ == "__main__":
    token = os.getenv('DISCORD_BOT_TOKEN')
    if token:
        bot.run(token)
    else:
        print("Error: DISCORD_BOT_TOKEN not found")
