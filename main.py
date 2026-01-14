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

# =====================
# MISSION BOARD SYSTEM
# =====================
MISSION_BOARD_TEMPLATES = {
    "easy": [
        {"name": "Patrol the School", "desc": "Check for curse activity around Jujutsu High", "duration": 60, "yen": 300, "xp": 30, "risk": 0.0, "min_level": 1},
        {"name": "Exorcise Weak Spirit", "desc": "A minor curse is causing disturbances", "duration": 90, "yen": 500, "xp": 50, "risk": 0.05, "min_level": 1},
        {"name": "Escort Mission", "desc": "Protect a civilian from curse activity", "duration": 120, "yen": 600, "xp": 60, "risk": 0.05, "min_level": 1},
        {"name": "Training Exercise", "desc": "Practice with fellow sorcerers", "duration": 60, "yen": 200, "xp": 80, "risk": 0.0, "min_level": 1},
    ],
    "medium": [
        {"name": "Cursed Womb Investigation", "desc": "Investigate a potential cursed womb", "duration": 180, "yen": 1200, "xp": 120, "risk": 0.15, "min_level": 5},
        {"name": "Retrieve Cursed Object", "desc": "Secure a dangerous artifact", "duration": 240, "yen": 1800, "xp": 150, "risk": 0.20, "min_level": 5},
        {"name": "Grade 3 Curse Hunt", "desc": "A confirmed Grade 3 curse needs exorcising", "duration": 150, "yen": 1500, "xp": 130, "risk": 0.15, "min_level": 5},
        {"name": "Protect VIP", "desc": "Guard someone with high curse attraction", "duration": 300, "yen": 2000, "xp": 180, "risk": 0.10, "min_level": 8},
    ],
    "hard": [
        {"name": "Grade 2 Curse Elimination", "desc": "A dangerous curse threatens civilians", "duration": 360, "yen": 4000, "xp": 300, "risk": 0.35, "min_level": 15},
        {"name": "Cursed Womb: Death Painting", "desc": "Confront a Death Painting Womb", "duration": 480, "yen": 6000, "xp": 400, "risk": 0.40, "min_level": 15},
        {"name": "Domain Expansion Training", "desc": "Master your incomplete domain", "duration": 600, "yen": 3000, "xp": 500, "risk": 0.25, "min_level": 20},
        {"name": "Rescue Operation", "desc": "Extract sorcerers from a hostile zone", "duration": 420, "yen": 5000, "xp": 350, "risk": 0.30, "min_level": 15},
    ],
    "extreme": [
        {"name": "Grade 1 Curse Suppression", "desc": "An extremely dangerous curse emerged", "duration": 720, "yen": 12000, "xp": 800, "risk": 0.55, "min_level": 25},
        {"name": "Special Grade Investigation", "desc": "Scout a Special Grade curse location", "duration": 900, "yen": 15000, "xp": 1000, "risk": 0.60, "min_level": 30},
        {"name": "Shibuya Incident Cleanup", "desc": "Clear remaining curses from Shibuya", "duration": 1200, "yen": 20000, "xp": 1500, "risk": 0.50, "min_level": 35},
        {"name": "Confront Disaster Curse", "desc": "Face one of the Disaster Curses", "duration": 1800, "yen": 50000, "xp": 3000, "risk": 0.70, "min_level": 40},
    ]
}

# =====================
# DISPATCH MISSIONS (Idle/Long-form)
# =====================
DISPATCH_MISSIONS = [
    {"id": "patrol_city", "name": "City Patrol", "desc": "Scout for curse activity", "duration_min": 30, "duration_max": 60, "base_yen": 800, "base_xp": 80, "risk": 0.05, "min_level": 1, "rare_loot_chance": 0.02},
    {"id": "clear_building", "name": "Building Cleanse", "desc": "Clear a cursed building", "duration_min": 60, "duration_max": 120, "base_yen": 2000, "base_xp": 150, "risk": 0.15, "min_level": 5, "rare_loot_chance": 0.05},
    {"id": "artifact_hunt", "name": "Artifact Hunt", "desc": "Search for cursed tools", "duration_min": 120, "duration_max": 240, "base_yen": 4000, "base_xp": 300, "risk": 0.20, "min_level": 10, "rare_loot_chance": 0.10},
    {"id": "curse_nest", "name": "Curse Nest Raid", "desc": "Clear a curse breeding ground", "duration_min": 180, "duration_max": 360, "base_yen": 8000, "base_xp": 500, "risk": 0.35, "min_level": 15, "rare_loot_chance": 0.15},
    {"id": "domain_scout", "name": "Domain Scouting", "desc": "Investigate domain expansion", "duration_min": 240, "duration_max": 480, "base_yen": 15000, "base_xp": 800, "risk": 0.45, "min_level": 25, "rare_loot_chance": 0.20},
    {"id": "special_grade", "name": "Special Grade Hunt", "desc": "Track a Special Grade curse", "duration_min": 360, "duration_max": 720, "base_yen": 30000, "base_xp": 1500, "risk": 0.60, "min_level": 35, "rare_loot_chance": 0.30},
]

# =====================
# INJURY SYSTEM
# =====================
INJURIES = {
    "minor_bruise": {"name": "Minor Bruise", "severity": 1, "duration_hours": 1, "hunt_penalty": 0.1, "train_penalty": 0.1, "blocks_hunt": False, "blocks_train": False},
    "cursed_wound": {"name": "Cursed Wound", "severity": 2, "duration_hours": 3, "hunt_penalty": 0.25, "train_penalty": 0.25, "blocks_hunt": False, "blocks_train": False},
    "broken_arm": {"name": "Broken Arm", "severity": 3, "duration_hours": 6, "hunt_penalty": 0.5, "train_penalty": 0.5, "blocks_hunt": True, "blocks_train": False},
    "cursed_poison": {"name": "Cursed Poison", "severity": 4, "duration_hours": 12, "hunt_penalty": 0.75, "train_penalty": 0.5, "blocks_hunt": True, "blocks_train": True},
    "domain_backlash": {"name": "Domain Backlash", "severity": 5, "duration_hours": 24, "hunt_penalty": 1.0, "train_penalty": 1.0, "blocks_hunt": True, "blocks_train": True},
}

# Injury chances by risk level
def get_injury_from_risk(risk_level):
    import random
    if risk_level < 0.1:
        return None
    if random.random() > risk_level:
        return None
    if risk_level < 0.2:
        return "minor_bruise"
    elif risk_level < 0.35:
        return random.choice(["minor_bruise", "cursed_wound"])
    elif risk_level < 0.5:
        return random.choice(["cursed_wound", "broken_arm"])
    elif risk_level < 0.65:
        return random.choice(["broken_arm", "cursed_poison"])
    else:
        return random.choice(["cursed_poison", "domain_backlash"])

# =====================
# ITEMS & INVENTORY
# =====================
JJK_ITEMS = {
    "bandage": {"name": "Medical Bandage", "cost": 500, "desc": "Reduces injury duration by 1 hour", "emoji": "🩹", "type": "healing", "effect": {"reduce_injury_hours": 1}},
    "cursed_salve": {"name": "Cursed Salve", "cost": 2000, "desc": "Reduces injury duration by 3 hours", "emoji": "💊", "type": "healing", "effect": {"reduce_injury_hours": 3}},
    "reverse_technique": {"name": "Reverse Technique Scroll", "cost": 10000, "desc": "Instantly clears all injuries", "emoji": "📜", "type": "healing", "effect": {"clear_injuries": True}},
    "xp_charm": {"name": "XP Charm", "cost": 3000, "desc": "+50% XP for next 3 hunts/trains", "emoji": "✨", "type": "boost", "effect": {"xp_mult": 1.5, "uses": 3}},
    "luck_talisman": {"name": "Luck Talisman", "cost": 5000, "desc": "+20% success chance for next 3 missions", "emoji": "🍀", "type": "boost", "effect": {"success_boost": 0.2, "uses": 3}},
    "protection_ward": {"name": "Protection Ward", "cost": 4000, "desc": "Blocks next injury", "emoji": "🛡️", "type": "protection", "effect": {"blocks_injury": 1}},
    "energy_drink": {"name": "Cursed Energy Drink", "cost": 1500, "desc": "Reduces hunt cooldown by 15 seconds", "emoji": "🥤", "type": "cooldown", "effect": {"reduce_hunt_cd": 15}},
    "onigiri": {"name": "Salmon Onigiri", "cost": 800, "desc": "Heals minor injuries and gives small XP", "emoji": "🍙", "type": "food", "effect": {"heal_minor": True, "xp": 25}},
}

# =====================
# RARE LOOT & COLLECTIONS
# =====================
RARE_LOOT = {
    "sukuna_finger": {"name": "Sukuna's Finger", "rarity": "legendary", "emoji": "☝️", "collection": "sukuna_parts"},
    "cursed_painting": {"name": "Death Painting Fragment", "rarity": "rare", "emoji": "🖼️", "collection": "death_paintings"},
    "gojo_blindfold": {"name": "Infinity Cloth", "rarity": "epic", "emoji": "🎭", "collection": "gojo_artifacts"},
    "todo_photo": {"name": "Todo's Idol Photo", "rarity": "uncommon", "emoji": "📸", "collection": "mementos"},
    "inumaki_throat": {"name": "Cursed Speech Seal", "rarity": "rare", "emoji": "🔇", "collection": "technique_scrolls"},
    "megumi_contract": {"name": "Shikigami Contract", "rarity": "epic", "emoji": "📋", "collection": "technique_scrolls"},
    "maki_glasses": {"name": "Heavenly Restriction Glasses", "rarity": "rare", "emoji": "👓", "collection": "zenin_relics"},
    "yuta_ring": {"name": "Rika's Ring", "rarity": "legendary", "emoji": "💍", "collection": "cursed_bonds"},
    "mahito_soul": {"name": "Idle Transfiguration Core", "rarity": "legendary", "emoji": "👤", "collection": "disaster_essence"},
    "jogo_ember": {"name": "Jogo's Ember", "rarity": "epic", "emoji": "🔥", "collection": "disaster_essence"},
    "hanami_seed": {"name": "Hanami's Seed", "rarity": "epic", "emoji": "🌱", "collection": "disaster_essence"},
    "dagon_shell": {"name": "Dagon's Shell", "rarity": "epic", "emoji": "🐚", "collection": "disaster_essence"},
}

COLLECTIONS = {
    "sukuna_parts": {"name": "King of Curses", "items_needed": 5, "bonus_type": "yen_mult", "bonus_value": 1.25, "title": "Vessel of Sukuna"},
    "death_paintings": {"name": "Death Paintings", "items_needed": 3, "bonus_type": "xp_mult", "bonus_value": 1.15, "title": "Painting Collector"},
    "gojo_artifacts": {"name": "Limitless Legacy", "items_needed": 3, "bonus_type": "success_boost", "bonus_value": 0.10, "title": "Six Eyes Heir"},
    "mementos": {"name": "Jujutsu Memories", "items_needed": 5, "bonus_type": "income_mult", "bonus_value": 1.10, "title": "Memory Keeper"},
    "technique_scrolls": {"name": "Technique Archive", "items_needed": 4, "bonus_type": "xp_mult", "bonus_value": 1.20, "title": "Technique Scholar"},
    "zenin_relics": {"name": "Zenin Legacy", "items_needed": 3, "bonus_type": "hunt_bonus", "bonus_value": 100, "title": "Zenin Heir"},
    "cursed_bonds": {"name": "Bonds of Curses", "items_needed": 2, "bonus_type": "yen_mult", "bonus_value": 1.30, "title": "Bound by Curse"},
    "disaster_essence": {"name": "Disaster Curses", "items_needed": 4, "bonus_type": "all_mult", "bonus_value": 1.15, "title": "Disaster Tamer"},
}

import random as _random

def roll_rare_loot(chance_multiplier=1.0):
    """Roll for rare loot based on chance"""
    base_chance = 0.05 * chance_multiplier
    if _random.random() > base_chance:
        return None
    rarities = {"uncommon": 0.50, "rare": 0.30, "epic": 0.15, "legendary": 0.05}
    roll = _random.random()
    cumulative = 0
    selected_rarity = "uncommon"
    for rarity, weight in rarities.items():
        cumulative += weight
        if roll <= cumulative:
            selected_rarity = rarity
            break
    matching = [k for k, v in RARE_LOOT.items() if v["rarity"] == selected_rarity]
    return _random.choice(matching) if matching else None

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
    return ensure_player_fields(jjk_players[uid])

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
        "last_collect": None,
        "inventory": {},
        "injuries": {},
        "active_mission": None,
        "mission_offers": [],
        "mission_offers_time": None,
        "dispatch_slots": [],
        "collections": {},
        "boosts": {},
        "last_eat": None,
        "last_rest": None,
        "protection_wards": 0
    }
    save_jjk_data()
    return jjk_players[uid]

def ensure_player_fields(player):
    """Ensure all new fields exist on a player (for migration)"""
    defaults = {
        "inventory": {},
        "injuries": {},
        "active_mission": None,
        "mission_offers": [],
        "mission_offers_time": None,
        "dispatch_slots": [],
        "collections": {},
        "boosts": {},
        "last_eat": None,
        "last_rest": None,
        "protection_wards": 0
    }
    for key, val in defaults.items():
        if key not in player:
            player[key] = val
    return player

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
    
    embed.add_field(name="📋 Mission Board", value=f"""
`{prefix}missions` - View available missions
`{prefix}accept <#>` - Accept a mission
`{prefix}missionclaim` - Claim completed mission
    """, inline=False)
    
    embed.add_field(name="📤 Dispatch (Idle)", value=f"""
`{prefix}dispatchlist` - View dispatch missions
`{prefix}dispatch <sorcerer> <id>` - Send sorcerer
`{prefix}dispatchstatus` - Check progress
`{prefix}dispatchclaim` - Claim rewards
    """, inline=False)
    
    embed.add_field(name="⚔️ Quick Actions", value=f"""
`{prefix}hunt` - Exorcise curses (30s cd)
`{prefix}train` - Gain XP (60s cd)
`{prefix}daily` - Daily reward
`{prefix}collect` - Collect hourly income
    """, inline=False)
    
    embed.add_field(name="🎒 Inventory & Items", value=f"""
`{prefix}inventory` - View items
`{prefix}shopitems` - Browse item shop
`{prefix}buyitem <name>` - Buy item
`{prefix}use <name>` - Use item
    """, inline=False)
    
    embed.add_field(name="😴 Recovery", value=f"""
`{prefix}eat` - Eat for XP (6h cd)
`{prefix}rest` - Heal injuries (12h cd)
    """, inline=False)
    
    embed.add_field(name="🏆 Collections", value=f"""
`{prefix}collections` - View rare loot
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
`{prefix}claninfo` - View clan | `{prefix}clanlb` - Leaderboard
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

# =====================
# MISSION BOARD COMMANDS
# =====================

def generate_mission_offers(player_level):
    """Generate 4 mission offers based on player level"""
    offers = []
    difficulties = ["easy", "medium", "hard", "extreme"]
    
    for i, diff in enumerate(difficulties):
        templates = MISSION_BOARD_TEMPLATES.get(diff, [])
        eligible = [t for t in templates if t["min_level"] <= player_level]
        if eligible:
            mission = random.choice(eligible).copy()
            mission["id"] = i + 1
            mission["difficulty"] = diff
            yen_var = random.uniform(0.8, 1.2)
            xp_var = random.uniform(0.9, 1.1)
            mission["yen"] = int(mission["yen"] * yen_var)
            mission["xp"] = int(mission["xp"] * xp_var)
            offers.append(mission)
    
    return offers

def check_player_injuries(player):
    """Check and clean up expired injuries, return active ones"""
    now = datetime.now(timezone.utc)
    injuries = player.get("injuries", {})
    active = {}
    for injury_key, data in injuries.items():
        expires = parse_iso_timestamp(data.get("expires"))
        if expires and expires > now:
            active[injury_key] = data
    player["injuries"] = active
    return active

def get_injury_status_text(player):
    """Get a text summary of player injuries"""
    injuries = check_player_injuries(player)
    if not injuries:
        return None
    now = datetime.now(timezone.utc)
    lines = []
    for injury_key, data in injuries.items():
        injury_info = INJURIES.get(injury_key, {})
        expires = parse_iso_timestamp(data.get("expires"))
        if expires:
            remaining = (expires - now).total_seconds()
            hours = int(remaining // 3600)
            mins = int((remaining % 3600) // 60)
            lines.append(f"• {injury_info.get('name', injury_key)}: {hours}h {mins}m remaining")
    return "\n".join(lines) if lines else None

def apply_injury(player, injury_key):
    """Apply an injury to a player"""
    if player.get("protection_wards", 0) > 0:
        player["protection_wards"] -= 1
        return None
    injury_info = INJURIES.get(injury_key)
    if not injury_info:
        return None
    now = datetime.now(timezone.utc)
    expires = now + timedelta(hours=injury_info["duration_hours"])
    player["injuries"][injury_key] = {"expires": expires.isoformat()}
    return injury_info

def can_hunt(player):
    """Check if player can hunt (not blocked by injuries)"""
    injuries = check_player_injuries(player)
    for injury_key in injuries:
        if INJURIES.get(injury_key, {}).get("blocks_hunt", False):
            return False, INJURIES[injury_key]["name"]
    return True, None

def can_train(player):
    """Check if player can train (not blocked by injuries)"""
    injuries = check_player_injuries(player)
    for injury_key in injuries:
        if INJURIES.get(injury_key, {}).get("blocks_train", False):
            return False, INJURIES[injury_key]["name"]
    return True, None

@bot.hybrid_command(name='missions', aliases=['mboard', 'missionboard'])
async def mission_board(ctx):
    """View available missions"""
    player = get_jjk_player(ctx.author.id)
    if not player:
        await ctx.send("Use `~jjkstart` to begin your journey!")
        return
    
    if player.get("active_mission"):
        mission = player["active_mission"]
        end_time = parse_iso_timestamp(mission.get("end_time"))
        now = datetime.now(timezone.utc)
        if end_time and end_time > now:
            remaining = int((end_time - now).total_seconds())
            mins = remaining // 60
            secs = remaining % 60
            await ctx.send(f"⚔️ You're on a mission: **{mission['name']}**\nTime remaining: **{mins}m {secs}s**\nUse `~missionclaim` when it's done!")
            return
    
    now = datetime.now(timezone.utc)
    offers_time = parse_iso_timestamp(player.get("mission_offers_time"))
    
    if not player.get("mission_offers") or not offers_time or (now - offers_time).total_seconds() > 1800:
        player["mission_offers"] = generate_mission_offers(player["level"])
        player["mission_offers_time"] = now.isoformat()
        save_jjk_data()
    
    offers = player["mission_offers"]
    
    embed = discord.Embed(
        title="📋 Mission Board",
        description="Choose a mission with `~accept <number>`\nMissions refresh every 30 minutes",
        color=0x9B59B6
    )
    
    diff_colors = {"easy": "🟢", "medium": "🟡", "hard": "🟠", "extreme": "🔴"}
    
    for mission in offers:
        diff_emoji = diff_colors.get(mission["difficulty"], "⚪")
        duration_mins = mission["duration"] // 60
        risk_pct = int(mission["risk"] * 100)
        
        field_value = f"{mission['desc']}\n"
        field_value += f"⏱️ {duration_mins}m | 💰 {mission['yen']:,} | ✨ {mission['xp']} XP\n"
        field_value += f"⚠️ Risk: {risk_pct}%"
        if mission["min_level"] > player["level"]:
            field_value += f"\n❌ Requires Level {mission['min_level']}"
        
        embed.add_field(
            name=f"{diff_emoji} [{mission['id']}] {mission['name']} ({mission['difficulty'].upper()})",
            value=field_value,
            inline=False
        )
    
    injury_text = get_injury_status_text(player)
    if injury_text:
        embed.add_field(name="🩹 Current Injuries", value=injury_text, inline=False)
    
    await ctx.send(embed=embed)

@bot.hybrid_command(name='accept', aliases=['startmission'])
async def accept_mission(ctx, mission_id: int):
    """Accept a mission from the board"""
    player = get_jjk_player(ctx.author.id)
    if not player:
        await ctx.send("Use `~jjkstart` to begin your journey!")
        return
    
    if player.get("active_mission"):
        await ctx.send("❌ You already have an active mission! Complete or claim it first.")
        return
    
    can, injury_name = can_hunt(player)
    if not can:
        await ctx.send(f"❌ You can't take missions while injured with **{injury_name}**! Rest or use healing items.")
        return
    
    offers = player.get("mission_offers", [])
    mission = None
    for m in offers:
        if m["id"] == mission_id:
            mission = m
            break
    
    if not mission:
        await ctx.send(f"❌ Mission #{mission_id} not found. Use `~missions` to see available missions.")
        return
    
    if mission["min_level"] > player["level"]:
        await ctx.send(f"❌ You need to be Level {mission['min_level']} for this mission!")
        return
    
    now = datetime.now(timezone.utc)
    end_time = now + timedelta(seconds=mission["duration"])
    
    player["active_mission"] = {
        "name": mission["name"],
        "difficulty": mission["difficulty"],
        "yen": mission["yen"],
        "xp": mission["xp"],
        "risk": mission["risk"],
        "end_time": end_time.isoformat(),
        "start_time": now.isoformat()
    }
    player["mission_offers"] = []
    save_jjk_data()
    
    duration_mins = mission["duration"] // 60
    await ctx.send(f"⚔️ **Mission Accepted: {mission['name']}**\nDuration: **{duration_mins} minutes**\nUse `~missionclaim` when the time is up!")

@bot.hybrid_command(name='missionclaim', aliases=['mclaim', 'claimission'])
async def claim_mission(ctx):
    """Claim rewards from completed mission"""
    player = get_jjk_player(ctx.author.id)
    if not player:
        await ctx.send("Use `~jjkstart` to begin your journey!")
        return
    
    mission = player.get("active_mission")
    if not mission:
        await ctx.send("❌ You don't have an active mission! Use `~missions` to find one.")
        return
    
    end_time = parse_iso_timestamp(mission.get("end_time"))
    now = datetime.now(timezone.utc)
    
    if end_time and end_time > now:
        remaining = int((end_time - now).total_seconds())
        mins = remaining // 60
        secs = remaining % 60
        await ctx.send(f"⏳ Mission not complete yet! **{mins}m {secs}s** remaining.")
        return
    
    yen_reward = mission["yen"]
    xp_reward = mission["xp"]
    risk = mission.get("risk", 0)
    
    xp_boost = player.get("boosts", {}).get("xp_mult", {})
    if xp_boost.get("uses", 0) > 0:
        xp_reward = int(xp_reward * xp_boost.get("value", 1.0))
        xp_boost["uses"] -= 1
        if xp_boost["uses"] <= 0:
            del player["boosts"]["xp_mult"]
    
    injury_result = None
    if risk > 0:
        injury_key = get_injury_from_risk(risk)
        if injury_key:
            injury_result = apply_injury(player, injury_key)
    
    loot_item = None
    if random.random() < 0.05 + (0.02 * (["easy", "medium", "hard", "extreme"].index(mission.get("difficulty", "easy")))):
        loot_item = roll_rare_loot(1.0)
        if loot_item:
            player["collections"][loot_item] = player.get("collections", {}).get(loot_item, 0) + 1
    
    player["yen"] += yen_reward
    player["xp"] += xp_reward
    player["missions_completed"] = player.get("missions_completed", 0) + 1
    player["active_mission"] = None
    
    while player["xp"] >= xp_for_level(player["level"]):
        player["xp"] -= xp_for_level(player["level"])
        player["level"] += 1
    
    save_jjk_data()
    
    embed = discord.Embed(
        title=f"✅ Mission Complete: {mission['name']}",
        color=0x00FF00
    )
    embed.add_field(name="Rewards", value=f"💰 {yen_reward:,} yen\n✨ {xp_reward} XP", inline=True)
    
    if injury_result:
        embed.add_field(name="🩹 Injury!", value=f"You sustained a **{injury_result['name']}**!\nDuration: {injury_result['duration_hours']}h", inline=True)
    
    if loot_item:
        loot_info = RARE_LOOT.get(loot_item, {})
        embed.add_field(name="🎁 Rare Loot!", value=f"{loot_info.get('emoji', '📦')} **{loot_info.get('name', loot_item)}**", inline=True)
    
    await ctx.send(embed=embed)

# =====================
# DISPATCH COMMANDS
# =====================

@bot.hybrid_command(name='dispatchlist', aliases=['dispatches', 'dlist'])
async def dispatch_list(ctx):
    """View available dispatch missions"""
    player = get_jjk_player(ctx.author.id)
    if not player:
        await ctx.send("Use `~jjkstart` to begin your journey!")
        return
    
    embed = discord.Embed(
        title="📤 Dispatch Missions",
        description="Send a sorcerer on a long mission\nUse `~dispatch <sorcerer> <mission_id>`",
        color=0x3498DB
    )
    
    for dm in DISPATCH_MISSIONS:
        if dm["min_level"] <= player["level"]:
            duration_text = f"{dm['duration_min']}-{dm['duration_max']}m"
            risk_pct = int(dm["risk"] * 100)
            loot_pct = int(dm["rare_loot_chance"] * 100)
            
            embed.add_field(
                name=f"[{dm['id']}] {dm['name']}",
                value=f"{dm['desc']}\n⏱️ {duration_text} | 💰 {dm['base_yen']:,} | ✨ {dm['base_xp']} XP\n⚠️ Risk: {risk_pct}% | 🎁 Loot: {loot_pct}%",
                inline=False
            )
    
    available_sorcerers = [s for s in player.get("sorcerers", []) if not any(d.get("sorcerer") == s for d in player.get("dispatch_slots", []))]
    if available_sorcerers:
        sorcerer_names = ", ".join([JJK_SORCERERS.get(s, {}).get("name", s) for s in available_sorcerers])
        embed.add_field(name="Available Sorcerers", value=sorcerer_names, inline=False)
    
    await ctx.send(embed=embed)

@bot.hybrid_command(name='dispatch', aliases=['send'])
async def dispatch_sorcerer(ctx, sorcerer: str, mission_id: str):
    """Send a sorcerer on a dispatch mission"""
    player = get_jjk_player(ctx.author.id)
    if not player:
        await ctx.send("Use `~jjkstart` to begin your journey!")
        return
    
    sorcerer_key = sorcerer.lower()
    if sorcerer_key not in player.get("sorcerers", []):
        await ctx.send(f"❌ You don't have **{sorcerer}**! Use `~sorcerers` to see who you have.")
        return
    
    if any(d.get("sorcerer") == sorcerer_key for d in player.get("dispatch_slots", [])):
        await ctx.send(f"❌ **{JJK_SORCERERS.get(sorcerer_key, {}).get('name', sorcerer)}** is already on a mission!")
        return
    
    mission = None
    for dm in DISPATCH_MISSIONS:
        if dm["id"] == mission_id:
            mission = dm
            break
    
    if not mission:
        await ctx.send(f"❌ Mission `{mission_id}` not found. Use `~dispatchlist` to see available missions.")
        return
    
    if mission["min_level"] > player["level"]:
        await ctx.send(f"❌ You need Level {mission['min_level']} for this mission!")
        return
    
    now = datetime.now(timezone.utc)
    duration = random.randint(mission["duration_min"], mission["duration_max"]) * 60
    end_time = now + timedelta(seconds=duration)
    
    dispatch_data = {
        "sorcerer": sorcerer_key,
        "mission_id": mission_id,
        "mission_name": mission["name"],
        "end_time": end_time.isoformat(),
        "base_yen": mission["base_yen"],
        "base_xp": mission["base_xp"],
        "risk": mission["risk"],
        "rare_loot_chance": mission["rare_loot_chance"]
    }
    
    player["dispatch_slots"].append(dispatch_data)
    save_jjk_data()
    
    sorcerer_name = JJK_SORCERERS.get(sorcerer_key, {}).get("name", sorcerer)
    duration_mins = duration // 60
    await ctx.send(f"📤 **{sorcerer_name}** dispatched on **{mission['name']}**!\nExpected return: **{duration_mins} minutes**\nCheck status with `~dispatchstatus`")

@bot.hybrid_command(name='dispatchstatus', aliases=['dstatus', 'mystatus'])
async def dispatch_status(ctx):
    """Check status of dispatched sorcerers"""
    player = get_jjk_player(ctx.author.id)
    if not player:
        await ctx.send("Use `~jjkstart` to begin your journey!")
        return
    
    dispatches = player.get("dispatch_slots", [])
    if not dispatches:
        await ctx.send("📭 No sorcerers on dispatch. Use `~dispatchlist` to send someone!")
        return
    
    now = datetime.now(timezone.utc)
    embed = discord.Embed(title="📤 Dispatch Status", color=0x3498DB)
    
    ready_count = 0
    for d in dispatches:
        sorcerer_name = JJK_SORCERERS.get(d["sorcerer"], {}).get("name", d["sorcerer"])
        end_time = parse_iso_timestamp(d.get("end_time"))
        
        if end_time and end_time <= now:
            status = "✅ **READY TO CLAIM**"
            ready_count += 1
        elif end_time:
            remaining = int((end_time - now).total_seconds())
            mins = remaining // 60
            secs = remaining % 60
            status = f"⏳ {mins}m {secs}s remaining"
        else:
            status = "❓ Unknown"
        
        embed.add_field(
            name=f"{JJK_SORCERERS.get(d['sorcerer'], {}).get('emoji', '👤')} {sorcerer_name}",
            value=f"Mission: {d['mission_name']}\n{status}",
            inline=True
        )
    
    if ready_count > 0:
        embed.set_footer(text=f"Use ~dispatchclaim to claim {ready_count} completed mission(s)")
    
    await ctx.send(embed=embed)

@bot.hybrid_command(name='dispatchclaim', aliases=['dclaim'])
async def dispatch_claim(ctx):
    """Claim all completed dispatch missions"""
    player = get_jjk_player(ctx.author.id)
    if not player:
        await ctx.send("Use `~jjkstart` to begin your journey!")
        return
    
    dispatches = player.get("dispatch_slots", [])
    if not dispatches:
        await ctx.send("📭 No sorcerers on dispatch!")
        return
    
    now = datetime.now(timezone.utc)
    completed = []
    still_active = []
    
    for d in dispatches:
        end_time = parse_iso_timestamp(d.get("end_time"))
        if end_time and end_time <= now:
            completed.append(d)
        else:
            still_active.append(d)
    
    if not completed:
        await ctx.send("⏳ No dispatches are ready yet! Check `~dispatchstatus`")
        return
    
    total_yen = 0
    total_xp = 0
    injuries = []
    loot = []
    
    for d in completed:
        yen_var = random.uniform(0.8, 1.3)
        xp_var = random.uniform(0.9, 1.2)
        yen = int(d["base_yen"] * yen_var)
        xp = int(d["base_xp"] * xp_var)
        
        success_boost = player.get("boosts", {}).get("success_boost", {})
        effective_risk = d["risk"]
        if success_boost.get("uses", 0) > 0:
            effective_risk = max(0, effective_risk - success_boost.get("value", 0))
            success_boost["uses"] -= 1
            if success_boost["uses"] <= 0:
                del player["boosts"]["success_boost"]
        
        if random.random() < effective_risk:
            injury_key = get_injury_from_risk(effective_risk)
            if injury_key:
                injury_result = apply_injury(player, injury_key)
                if injury_result:
                    injuries.append(f"{JJK_SORCERERS.get(d['sorcerer'], {}).get('name', d['sorcerer'])}: {injury_result['name']}")
        
        if random.random() < d["rare_loot_chance"]:
            loot_item = roll_rare_loot(1.5)
            if loot_item:
                player["collections"][loot_item] = player.get("collections", {}).get(loot_item, 0) + 1
                loot.append(RARE_LOOT.get(loot_item, {}).get("name", loot_item))
        
        total_yen += yen
        total_xp += xp
    
    player["dispatch_slots"] = still_active
    player["yen"] += total_yen
    player["xp"] += total_xp
    
    while player["xp"] >= xp_for_level(player["level"]):
        player["xp"] -= xp_for_level(player["level"])
        player["level"] += 1
    
    save_jjk_data()
    
    embed = discord.Embed(
        title=f"📥 Dispatch Complete ({len(completed)} missions)",
        color=0x00FF00
    )
    embed.add_field(name="Rewards", value=f"💰 {total_yen:,} yen\n✨ {total_xp} XP", inline=True)
    
    if injuries:
        embed.add_field(name="🩹 Injuries", value="\n".join(injuries), inline=True)
    
    if loot:
        embed.add_field(name="🎁 Rare Loot", value="\n".join(loot), inline=True)
    
    await ctx.send(embed=embed)

# =====================
# INVENTORY COMMANDS
# =====================

@bot.hybrid_command(name='inventory', aliases=['inv', 'items'])
async def inventory_cmd(ctx):
    """View your inventory"""
    player = get_jjk_player(ctx.author.id)
    if not player:
        await ctx.send("Use `~jjkstart` to begin your journey!")
        return
    
    inventory = player.get("inventory", {})
    
    embed = discord.Embed(title="🎒 Your Inventory", color=0xE67E22)
    
    if not inventory:
        embed.description = "Your inventory is empty!\nUse `~shopitems` to see what you can buy."
    else:
        for item_key, count in inventory.items():
            item_info = JJK_ITEMS.get(item_key, {})
            embed.add_field(
                name=f"{item_info.get('emoji', '📦')} {item_info.get('name', item_key)} x{count}",
                value=item_info.get("desc", "Unknown item"),
                inline=True
            )
    
    injury_text = get_injury_status_text(player)
    if injury_text:
        embed.add_field(name="🩹 Injuries", value=injury_text, inline=False)
    
    boosts = player.get("boosts", {})
    if boosts:
        boost_lines = []
        for boost_key, boost_data in boosts.items():
            uses = boost_data.get("uses", 0)
            if uses > 0:
                boost_lines.append(f"• {boost_key}: {uses} uses left")
        if boost_lines:
            embed.add_field(name="✨ Active Boosts", value="\n".join(boost_lines), inline=False)
    
    embed.add_field(name="🛡️ Protection Wards", value=str(player.get("protection_wards", 0)), inline=True)
    
    await ctx.send(embed=embed)

@bot.hybrid_command(name='shopitems', aliases=['itemshop', 'ishop'])
async def shop_items(ctx):
    """View items available for purchase"""
    player = get_jjk_player(ctx.author.id)
    if not player:
        await ctx.send("Use `~jjkstart` to begin your journey!")
        return
    
    embed = discord.Embed(
        title="🏪 Item Shop",
        description=f"Your balance: **{player['yen']:,} yen**\nBuy with `~buyitem <name>`",
        color=0xE67E22
    )
    
    for item_key, item in JJK_ITEMS.items():
        embed.add_field(
            name=f"{item['emoji']} {item['name']} - {item['cost']:,} yen",
            value=f"{item['desc']}\n`~buyitem {item_key}`",
            inline=True
        )
    
    await ctx.send(embed=embed)

@bot.hybrid_command(name='buyitem', aliases=['ibuy'])
async def buy_item(ctx, item_name: str):
    """Buy an item from the shop"""
    player = get_jjk_player(ctx.author.id)
    if not player:
        await ctx.send("Use `~jjkstart` to begin your journey!")
        return
    
    item_key = item_name.lower().replace(" ", "_")
    if item_key not in JJK_ITEMS:
        await ctx.send(f"❌ Item `{item_name}` not found. Use `~shopitems` to see available items.")
        return
    
    item = JJK_ITEMS[item_key]
    if player["yen"] < item["cost"]:
        await ctx.send(f"❌ Not enough yen! You need **{item['cost']:,}** but have **{player['yen']:,}**")
        return
    
    player["yen"] -= item["cost"]
    player["inventory"][item_key] = player.get("inventory", {}).get(item_key, 0) + 1
    save_jjk_data()
    
    await ctx.send(f"✅ Bought **{item['name']}** for **{item['cost']:,} yen**!")

@bot.hybrid_command(name='use', aliases=['useitem'])
async def use_item(ctx, item_name: str):
    """Use an item from your inventory"""
    player = get_jjk_player(ctx.author.id)
    if not player:
        await ctx.send("Use `~jjkstart` to begin your journey!")
        return
    
    item_key = item_name.lower().replace(" ", "_")
    if item_key not in player.get("inventory", {}) or player["inventory"][item_key] <= 0:
        await ctx.send(f"❌ You don't have **{item_name}**! Check `~inventory`")
        return
    
    item = JJK_ITEMS.get(item_key)
    if not item:
        await ctx.send("❌ Unknown item!")
        return
    
    effect = item.get("effect", {})
    result_text = []
    
    if effect.get("clear_injuries"):
        player["injuries"] = {}
        result_text.append("All injuries cleared!")
    
    if effect.get("reduce_injury_hours"):
        hours = effect["reduce_injury_hours"]
        injuries = player.get("injuries", {})
        now = datetime.now(timezone.utc)
        updated_injuries = {}
        for injury_key, data in injuries.items():
            expires = parse_iso_timestamp(data.get("expires"))
            if expires:
                new_expires = expires - timedelta(hours=hours)
                if new_expires > now:
                    data["expires"] = new_expires.isoformat()
                    updated_injuries[injury_key] = data
        player["injuries"] = updated_injuries
        result_text.append(f"Reduced injury duration by {hours} hour(s)")
    
    if effect.get("heal_minor"):
        if "minor_bruise" in player.get("injuries", {}):
            del player["injuries"]["minor_bruise"]
            result_text.append("Healed minor bruise")
    
    if effect.get("xp"):
        player["xp"] += effect["xp"]
        result_text.append(f"+{effect['xp']} XP")
    
    if effect.get("xp_mult"):
        player["boosts"]["xp_mult"] = {"value": effect["xp_mult"], "uses": effect.get("uses", 3)}
        result_text.append(f"XP boost active for {effect.get('uses', 3)} actions")
    
    if effect.get("success_boost"):
        player["boosts"]["success_boost"] = {"value": effect["success_boost"], "uses": effect.get("uses", 3)}
        result_text.append(f"Success boost active for {effect.get('uses', 3)} missions")
    
    if effect.get("blocks_injury"):
        player["protection_wards"] = player.get("protection_wards", 0) + effect["blocks_injury"]
        result_text.append(f"+{effect['blocks_injury']} protection ward(s)")
    
    if effect.get("reduce_hunt_cd"):
        result_text.append(f"Hunt cooldown reduced by {effect['reduce_hunt_cd']}s (applies next hunt)")
    
    player["inventory"][item_key] -= 1
    if player["inventory"][item_key] <= 0:
        del player["inventory"][item_key]
    
    save_jjk_data()
    
    await ctx.send(f"✅ Used **{item['name']}**!\n" + "\n".join(result_text))

# =====================
# IDLE ACTIONS
# =====================

@bot.hybrid_command(name='eat', aliases=['snack'])
async def eat_cmd(ctx):
    """Eat to recover (6h cooldown)"""
    player = get_jjk_player(ctx.author.id)
    if not player:
        await ctx.send("Use `~jjkstart` to begin your journey!")
        return
    
    now = datetime.now(timezone.utc)
    last_eat = parse_iso_timestamp(player.get("last_eat"))
    
    if last_eat:
        hours_passed = max(0, (now - last_eat).total_seconds() / 3600)
        if hours_passed < 6:
            remaining = 6 - hours_passed
            hours = int(remaining)
            mins = int((remaining - hours) * 60)
            await ctx.send(f"🍜 You're still full! Wait **{hours}h {mins}m** to eat again.")
            return
    
    xp_gain = random.randint(30, 60) + player["level"]
    heal_minor = random.random() < 0.3
    
    player["xp"] += xp_gain
    player["last_eat"] = now.isoformat()
    
    result = f"🍜 You enjoyed a meal!\n✨ +{xp_gain} XP"
    
    if heal_minor and "minor_bruise" in player.get("injuries", {}):
        del player["injuries"]["minor_bruise"]
        result += "\n🩹 Your minor bruise healed!"
    
    while player["xp"] >= xp_for_level(player["level"]):
        player["xp"] -= xp_for_level(player["level"])
        player["level"] += 1
    
    save_jjk_data()
    await ctx.send(result)

@bot.hybrid_command(name='rest', aliases=['sleep'])
async def rest_cmd(ctx):
    """Rest to recover from injuries (12h cooldown)"""
    player = get_jjk_player(ctx.author.id)
    if not player:
        await ctx.send("Use `~jjkstart` to begin your journey!")
        return
    
    now = datetime.now(timezone.utc)
    last_rest = parse_iso_timestamp(player.get("last_rest"))
    
    if last_rest:
        hours_passed = max(0, (now - last_rest).total_seconds() / 3600)
        if hours_passed < 12:
            remaining = 12 - hours_passed
            hours = int(remaining)
            mins = int((remaining - hours) * 60)
            await ctx.send(f"😴 You're not tired! Wait **{hours}h {mins}m** to rest again.")
            return
    
    injuries = player.get("injuries", {})
    healed = []
    reduced = []
    
    for injury_key, data in list(injuries.items()):
        injury_info = INJURIES.get(injury_key, {})
        if injury_info.get("severity", 0) <= 2:
            healed.append(injury_info.get("name", injury_key))
            del injuries[injury_key]
        else:
            expires = parse_iso_timestamp(data.get("expires"))
            if expires:
                new_expires = expires - timedelta(hours=3)
                if new_expires <= now:
                    healed.append(injury_info.get("name", injury_key))
                    del injuries[injury_key]
                else:
                    data["expires"] = new_expires.isoformat()
                    reduced.append(injury_info.get("name", injury_key))
    
    player["injuries"] = injuries
    player["last_rest"] = now.isoformat()
    save_jjk_data()
    
    result = "😴 You had a good rest!"
    if healed:
        result += f"\n✅ Healed: {', '.join(healed)}"
    if reduced:
        result += f"\n⏱️ Reduced duration: {', '.join(reduced)} (-3h each)"
    if not healed and not reduced:
        result += "\nNo injuries to heal, but you feel refreshed!"
    
    await ctx.send(result)

# =====================
# COLLECTIONS
# =====================

@bot.hybrid_command(name='collections', aliases=['collection', 'loot'])
async def collections_cmd(ctx):
    """View your rare loot collections"""
    player = get_jjk_player(ctx.author.id)
    if not player:
        await ctx.send("Use `~jjkstart` to begin your journey!")
        return
    
    player_collections = player.get("collections", {})
    
    embed = discord.Embed(
        title="🏆 Your Collections",
        description="Collect rare items from missions to unlock bonuses!",
        color=0xF1C40F
    )
    
    for collection_key, collection_info in COLLECTIONS.items():
        items_in_collection = [k for k, v in RARE_LOOT.items() if v.get("collection") == collection_key]
        owned = sum(1 for item in items_in_collection if player_collections.get(item, 0) > 0)
        total = collection_info["items_needed"]
        
        progress = f"{owned}/{total}"
        status = "✅ COMPLETE" if owned >= total else f"🔒 {progress}"
        
        item_list = []
        for item in items_in_collection:
            loot_info = RARE_LOOT.get(item, {})
            count = player_collections.get(item, 0)
            if count > 0:
                item_list.append(f"{loot_info.get('emoji', '📦')} {loot_info.get('name', item)} x{count}")
            else:
                item_list.append(f"❓ ???")
        
        bonus_text = ""
        if owned >= total:
            bonus_type = collection_info["bonus_type"]
            bonus_value = collection_info["bonus_value"]
            title = collection_info["title"]
            if "mult" in bonus_type:
                bonus_text = f"\n🎁 Bonus: {int((bonus_value - 1) * 100)}% {bonus_type.replace('_mult', '').replace('_', ' ')}"
            else:
                bonus_text = f"\n🎁 Bonus: +{bonus_value} {bonus_type.replace('_', ' ')}"
            bonus_text += f"\n👑 Title: {title}"
        
        embed.add_field(
            name=f"{collection_info['name']} [{status}]",
            value="\n".join(item_list[:5]) + bonus_text,
            inline=True
        )
    
    await ctx.send(embed=embed)

# =====================
# UPDATED JJK GUIDE
# =====================

# Run the bot
if __name__ == "__main__":
    token = os.getenv('DISCORD_BOT_TOKEN')
    if token:
        bot.run(token)
    else:
        print("Error: DISCORD_BOT_TOKEN not found")
