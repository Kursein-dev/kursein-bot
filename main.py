import discord
from discord import app_commands
from discord.ext import commands, tasks
import os
from datetime import datetime, timedelta, timezone
import json
import asyncio
import random
from typing import Optional, Union
from dotenv import load_dotenv
import aiohttp
from urllib.parse import quote

load_dotenv()

# Bot Version: 2.0.0 - All 98 commands now support both prefix (~) and slash (/) formats

# Store reminders in memory (persisted to file)
REMINDERS_FILE = "reminders.json"
PREFIXES_FILE = "prefixes.json"
BUMP_CONFIG_FILE = "bump_config.json"
CLAIMS_FILE = "claims.json"
CLAIM_REMINDERS_FILE = "claim_reminders.json"
CHALLENGES_FILE = "challenges.json"
CHIPS_FILE = "chips.json"
CHIPS_LOG_FILE = "chips_log.json"
SECRET_CLAIMS_FILE = "secret_claims.json"
INFINITE_USERS_FILE = "infinite_users.json"
ROB_RATE_FILE = "rob_success_rate.json"
MONTHLY_CLAIMS_FILE = "monthly_claims.json"
PLAYER_STATS_FILE = "player_stats.json"
JACKPOT_FILE = "jackpot.json"
SHOP_ITEMS_FILE = "shop_items.json"
HOUSE_STATS_FILE = "house_stats.json"
LOANS_FILE = "loans.json"
TOURNAMENTS_FILE = "tournaments.json"
GAME_SETTINGS_FILE = "game_settings.json"
VERIFIED_USERS_FILE = "verified_users.json"
JOBS_FILE = "jobs.json"
BOUNTIES_FILE = "bounties.json"
GUILD_PLAYERS_FILE = "guild_players.json"
PETS_FILE = "pets.json"
TICKETS_FILE = "tickets.json"
PROFILE_BANNERS_FILE = "profile_banners.json"
DAILY_TRANSFERS_FILE = "daily_transfers.json"
BANKS_FILE = "banks.json"
CLANS_FILE = "clans.json"
RL_RANKS_FILE = "rl_ranks.json"
RL_PROFILES_FILE = "rl_profiles.json"
STREAMS_CONFIG_FILE = "streams_config.json"
STAFF_FILE = "staff.json"
STREAKS_FILE = "streaks.json"
GAME_HISTORY_FILE = "game_history.json"
DAILY_QUESTS_FILE = "daily_quests.json"
PRESTIGE_FILE = "prestige.json"
BIRTHDAYS_FILE = "birthdays.json"
REFERRALS_FILE = "referrals.json"
DEFAULT_PREFIX = "~"

DISBOARD_BOT_ID = 302050872383242240
ERROR_CHANNEL_ID = 1435009092782522449  # Channel for error logging
GOD_MODE_USER_ID = 525815097847840798  # User with 100% win rate on all games

# Admin/Staff IDs
OWNER_ID = 343055455263916045  # kursein
ADMIN_IDS = {697495071737511997, 187729483174903808, 343055455263916045, 525815097847840798, 760075655374176277}  # cocoa.trees, getsleepad, kursein, luvlis_time, nanizzz
MOD_IDS = {504812129560428554}  # tillyoudecay
JRMOD_IDS = {878870610158178335, 1131474199286907000}  # lightningmint., shanksdagoat
STAFF_IDS = ADMIN_IDS | MOD_IDS | JRMOD_IDS | {OWNER_ID}  # All staff combined

reminders = []
prefixes = {}
bump_config = {}
staff_data = {}  # user_id: {name, position, description, extras}
claims = {}  # user_id: {'daily': timestamp, 'weekly': timestamp, 'monthly': timestamp, 'yearly': timestamp}
claim_reminders_sent = {}  # user_id: {'daily': bool, 'weekly': bool, 'monthly': bool, 'yearly': bool}
user_challenges = {}  # user_id: {challenge_id: progress}
secret_claims = {}  # user_id: ['67', 'lucky7', 'jackpot', '888', 'bonus', 'vip']
infinite_users = set()  # Set of user IDs with infinite chips
rob_success_rate = 1  # Current rob success rate (starts at 1%, increases with failures)
monthly_claims = {}  # user_id: {'month': 'YYYY-MM', 'count': int, 'claimed_tiers': ['bronze', 'silver', 'gold']}
player_stats = {}  # user_id: {'xp': int, 'level': int, 'vip_tier': str, 'total_wagered': int, 'total_won': int, 'games_played': int, 'achievements': [], 'inventory': []}
jackpot_pool = 0  # Progressive jackpot amount
shop_items = {}  # item_id: {'name': str, 'price': int, 'type': str, 'effect': dict}
login_streaks = {}  # user_id: {'current_streak': int, 'last_login': timestamp, 'longest_streak': int}
game_history = {}  # user_id: [{'game': str, 'wager': int, 'result': 'win'/'loss'/'push', 'amount': int, 'timestamp': str}]
daily_quests = {}  # user_id: {'quests': [{type, target, progress, reward}, ...], 'last_reset': timestamp}
prestige_data = {}  # user_id: {'prestige_tier': int, 'total_resets': int, 'multiplier': float}
user_birthdays = {}  # user_id: 'MM-DD'
referral_data = {}  # user_id: {'referrer_id': int, 'referred_users': [int], 'bonus_earned': int}
house_stats = {}  # {'total_wagered': int, 'total_paid': int, 'profit': int, 'tax_rate': float}
player_loans = {}  # user_id: {'amount': int, 'interest_rate': float, 'due_date': timestamp}
active_tournament = None  # Current weekly tournament data
game_settings = {}  # game_name: {'enabled': bool, 'odds_multiplier': float, 'min_bet': int, 'max_bet': int}
verified_users = set()  # Set of user IDs who have verified
job_cooldowns = {}  # user_id: timestamp of last job completion
active_bounties = {}  # target_user_id: {'placer_id': int, 'placer_name': str, 'amount': int, 'timestamp': str}
guild_players = {}  # guild_id: [user_id1, user_id2, ...]
user_pets = {}  # user_id: {pet_id: count, '_idol': pet_id}
user_tickets = {}  # user_id: ticket_count
profile_banners = {}  # user_id: image_url
daily_transfers = {}  # user_id: {'date': 'YYYY-MM-DD', 'amount_sent': int}
user_banks = {}  # user_id: bank_balance (safe from robberies)
clans = {}  # clan_id: {'name': str, 'leader_id': int, 'members': [user_ids], 'vault': int, 'created': timestamp}
rl_ranks = {}  # user_id: rank_value (0-22)
rl_profiles = {}  # user_id: {'username': str, 'platform': str}
streams_config = {}  # guild_id: {'role_id': int, 'channel_id': int, 'streamers': [{username: str, platform: str, live: bool, last_check: timestamp}]}

# Game state storage
active_blackjack_games = {}  # channel_id: BlackjackGame
active_coinflip_challenges = {}  # user_id: CoinflipChallenge
active_trades = {}  # user_id: TradeView instance
active_roulette_spins = {}  # channel_id: RouletteGame
active_poker_games = {}  # channel_id: PokerGame
active_multiplayer_roulette = {}  # channel_id: MultiplayerRouletteGame
active_sports_bets = {}  # channel_id: SportsBet
active_crash_games = {}  # channel_id: CrashGame
active_mines_games = {}  # user_id: MinesGame
active_games = set()  # Set of user IDs currently in an interactive game (prevents spam)
player_chips = {}  # user_id: chip_count
chips_log = []  # List of transaction records
rob_cooldowns = {}  # user_id: timestamp of last rob attempt

# Claim rewards
DAILY_REWARD = 100
WEEKLY_REWARD = 3000
MONTHLY_REWARD = 10000
YEARLY_REWARD = 100000

# Rocket League Ranks (ordered by skill level)
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

# Casino game bet limits (min/max chips per bet)
GAME_LIMITS = {
    "slots": {"min": 10, "max": 100000},
    "blackjack": {"min": 10, "max": 250000},
    "roulette": {"min": 10, "max": 100000},
    "crash": {"min": 10, "max": 500000},
    "mines": {"min": 10, "max": 250000},
    "wheel": {"min": 10, "max": 100000},
    "craps": {"min": 10, "max": 100000},
    "poker": {"min": 10, "max": 100000},
    "hilo": {"min": 10, "max": 100000},
    "coinflip": {"min": 10, "max": 100000},
}

# VIP bonus cap (maximum bonus chips from VIP multipliers)
MAX_VIP_BONUS = 1000000  # Cap VIP bonus at 1M chips per game to prevent extreme wins

# Job System Definitions (30 jobs with level-based unlocks and increased pay)
JOB_DEFINITIONS = [
    {"id": "pizza_delivery", "name": "🍕 Pizza Delivery Driver", "level_required": 1, "pay_min": 700, "pay_max": 2100, "description": "delivering pizzas around town"},
    {"id": "package_handler", "name": "📦 Package Handler", "level_required": 1, "pay_min": 1050, "pay_max": 2800, "description": "sorting packages at the warehouse"},
    {"id": "casino_janitor", "name": "🧹 Casino Janitor", "level_required": 1, "pay_min": 840, "pay_max": 2520, "description": "cleaning the casino floors"},
    {"id": "coffee_barista", "name": "☕ Coffee Barista", "level_required": 1, "pay_min": 770, "pay_max": 2240, "description": "making coffee for high rollers"},
    {"id": "valet_attendant", "name": "🚗 Valet Parking Attendant", "level_required": 1, "pay_min": 980, "pay_max": 2660, "description": "parking luxury cars"},
    
    {"id": "slot_technician", "name": "🎰 Slot Machine Technician", "level_required": 5, "pay_min": 1400, "pay_max": 3500, "description": "fixing broken slot machines"},
    {"id": "dice_inspector", "name": "🎲 Dice Inspector", "level_required": 5, "pay_min": 1120, "pay_max": 3080, "description": "inspecting dice for quality control"},
    {"id": "security_guard", "name": "🔐 Security Guard", "level_required": 5, "pay_min": 1540, "pay_max": 3780, "description": "watching the casino cameras"},
    
    {"id": "card_dealer_trainee", "name": "🃏 Card Dealer Trainee", "level_required": 10, "pay_min": 1260, "pay_max": 3220, "description": "learning to deal cards"},
    {"id": "casino_entertainer", "name": "🎵 Casino Entertainer", "level_required": 10, "pay_min": 1680, "pay_max": 4200, "description": "performing for the crowd"},
    {"id": "cocktail_server", "name": "🍸 Cocktail Server", "level_required": 10, "pay_min": 1190, "pay_max": 3360, "description": "serving drinks to VIP guests"},
    
    {"id": "pit_boss_assistant", "name": "🎩 Pit Boss Assistant", "level_required": 15, "pay_min": 1820, "pay_max": 4550, "description": "assisting the pit boss"},
    {"id": "chips_counter", "name": "💰 Chip Counter", "level_required": 15, "pay_min": 1610, "pay_max": 4340, "description": "counting and organizing casino chips"},
    {"id": "surveillance_operator", "name": "📹 Surveillance Operator", "level_required": 15, "pay_min": 1890, "pay_max": 4690, "description": "monitoring security footage"},
    
    {"id": "blackjack_dealer", "name": "🃏 Blackjack Dealer", "level_required": 20, "pay_min": 2100, "pay_max": 5250, "description": "dealing professional blackjack games"},
    {"id": "roulette_croupier", "name": "🎡 Roulette Croupier", "level_required": 20, "pay_min": 2240, "pay_max": 5600, "description": "spinning the roulette wheel"},
    {"id": "poker_dealer", "name": "♠️ Poker Dealer", "level_required": 20, "pay_min": 2380, "pay_max": 5950, "description": "dealing high-stakes poker"},
    
    {"id": "vip_host", "name": "👔 VIP Host", "level_required": 25, "pay_min": 2520, "pay_max": 6300, "description": "entertaining VIP guests"},
    {"id": "casino_manager", "name": "📊 Casino Manager", "level_required": 25, "pay_min": 2800, "pay_max": 7000, "description": "managing casino operations"},
    {"id": "event_coordinator", "name": "🎉 Event Coordinator", "level_required": 25, "pay_min": 2660, "pay_max": 6650, "description": "planning casino events"},
    
    {"id": "head_security", "name": "🛡️ Head of Security", "level_required": 30, "pay_min": 3150, "pay_max": 7875, "description": "overseeing all security"},
    {"id": "pit_boss", "name": "🎰 Pit Boss", "level_required": 30, "pay_min": 3360, "pay_max": 8400, "description": "supervising all table games"},
    {"id": "high_roller_host", "name": "💎 High Roller Host", "level_required": 30, "pay_min": 3570, "pay_max": 8925, "description": "hosting whale clients"},
    
    {"id": "casino_director", "name": "👑 Casino Director", "level_required": 40, "pay_min": 4200, "pay_max": 10500, "description": "directing all casino operations"},
    {"id": "gaming_inspector", "name": "🔍 Gaming Inspector", "level_required": 40, "pay_min": 3920, "pay_max": 9800, "description": "ensuring fair play compliance"},
    {"id": "vip_relations_manager", "name": "🌟 VIP Relations Manager", "level_required": 40, "pay_min": 4480, "pay_max": 11200, "description": "managing VIP relationships"},
    
    {"id": "casino_executive", "name": "💼 Casino Executive", "level_required": 50, "pay_min": 5250, "pay_max": 13125, "description": "executive leadership"},
    {"id": "gaming_commissioner", "name": "⚖️ Gaming Commissioner", "level_required": 50, "pay_min": 5600, "pay_max": 14000, "description": "regulating gaming operations"},
    {"id": "casino_owner_consultant", "name": "🏆 Casino Owner Consultant", "level_required": 60, "pay_min": 6300, "pay_max": 15750, "description": "consulting casino owners"},
    {"id": "gambling_tycoon", "name": "💸 Gambling Tycoon", "level_required": 75, "pay_min": 7700, "pay_max": 19250, "description": "running your own casino empire"},
]

def get_unlocked_jobs(level):
    """Get list of job IDs that are unlocked at given level"""
    return [job["id"] for job in JOB_DEFINITIONS if job["level_required"] <= level]

def get_job_by_id(job_id):
    """Get job definition by ID"""
    for job in JOB_DEFINITIONS:
        if job["id"] == job_id:
            return job
    return None

# Challenge definitions
CHALLENGES = {
    "blackjack_beginner": {
        "name": "Blackjack Beginner",
        "description": "Win 5 blackjack games",
        "type": "wins",
        "game": "blackjack",
        "target": 5,
        "reward": 250,
        "emoji": "🃏"
    },
    "slots_enthusiast": {
        "name": "Slots Enthusiast",
        "description": "Spin the slots 25 times",
        "type": "plays",
        "game": "slots",
        "target": 25,
        "reward": 500,
        "emoji": "🎰"
    },
    "roulette_master": {
        "name": "Roulette Master",
        "description": "Win 10 roulette games",
        "type": "wins",
        "game": "roulette",
        "target": 10,
        "reward": 750,
        "emoji": "🎡"
    },
    "high_roller": {
        "name": "High Roller",
        "description": "Win 5000 total chips across all games",
        "type": "total_winnings",
        "target": 5000,
        "reward": 1000,
        "emoji": "💎"
    },
    "chip_collector": {
        "name": "Chip Collector",
        "description": "Claim all 4 rewards (daily, weekly, monthly, yearly)",
        "type": "claims",
        "target": 4,
        "reward": 2000,
        "emoji": "🎁"
    },
    "lucky_streak": {
        "name": "Lucky Streak",
        "description": "Win 3 games in a row (any game)",
        "type": "streak",
        "target": 3,
        "reward": 1500,
        "emoji": "🔥"
    },
    "hilo_expert": {
        "name": "Hi-Lo Expert",
        "description": "Win 15 Hi-Lo games",
        "type": "wins",
        "game": "hilo",
        "target": 15,
        "reward": 800,
        "emoji": "🎴"
    },
    "jackpot_hunter": {
        "name": "Jackpot Hunter",
        "description": "Hit a jackpot on slots (25x or 50x)",
        "type": "jackpot",
        "game": "slots",
        "target": 1,
        "reward": 3000,
        "emoji": "<:Casino_Chip:1437456315025719368>"
    },
    "poker_novice": {
        "name": "Poker Novice",
        "description": "Play 20 poker hands",
        "type": "plays",
        "game": "poker",
        "target": 20,
        "reward": 400,
        "emoji": "🃏"
    },
    "poker_champion": {
        "name": "Poker Champion",
        "description": "Win 10 poker hands",
        "type": "wins",
        "game": "poker",
        "target": 10,
        "reward": 1000,
        "emoji": "🏆"
    },
    "wheel_spinner": {
        "name": "Wheel Spinner",
        "description": "Spin the wheel 30 times",
        "type": "plays",
        "game": "wheel",
        "target": 30,
        "reward": 600,
        "emoji": "🎡"
    },
    "crash_veteran": {
        "name": "Crash Veteran",
        "description": "Play crash 25 times",
        "type": "plays",
        "game": "crash",
        "target": 25,
        "reward": 700,
        "emoji": "💥"
    },
    "crash_winner": {
        "name": "Crash Winner",
        "description": "Successfully cashout 15 times in crash",
        "type": "wins",
        "game": "crash",
        "target": 15,
        "reward": 1200,
        "emoji": "🚀"
    },
    "mines_explorer": {
        "name": "Mines Explorer",
        "description": "Play mines 20 times",
        "type": "plays",
        "game": "mines",
        "target": 20,
        "reward": 500,
        "emoji": "💣"
    },
    "mines_master": {
        "name": "Mines Master",
        "description": "Successfully cashout 10 times in mines",
        "type": "wins",
        "game": "mines",
        "target": 10,
        "reward": 900,
        "emoji": "💎"
    },
    "craps_roller": {
        "name": "Craps Roller",
        "description": "Roll the dice 30 times in craps",
        "type": "plays",
        "game": "craps",
        "target": 30,
        "reward": 550,
        "emoji": "🎲"
    },
    "coinflip_gambler": {
        "name": "Coinflip Gambler",
        "description": "Flip the coin 40 times",
        "type": "plays",
        "game": "coinflip",
        "target": 40,
        "reward": 450,
        "emoji": "🪙"
    },
    "coinflip_winner": {
        "name": "Coinflip Winner",
        "description": "Win 20 coinflip games",
        "type": "wins",
        "game": "coinflip",
        "target": 20,
        "reward": 800,
        "emoji": "🏅"
    }
}

# Pet definitions with rarities and drop rates
PETS = {
    # Common pets (50% chance)
    "dog": {"name": "Dog", "rarity": "Common", "emoji": "🐕", "chance": 15.0},
    "cat": {"name": "Cat", "rarity": "Common", "emoji": "🐈", "chance": 15.0},
    "rabbit": {"name": "Rabbit", "rarity": "Common", "emoji": "🐇", "chance": 10.0},
    "hamster": {"name": "Hamster", "rarity": "Common", "emoji": "🐹", "chance": 10.0},
    
    # Uncommon pets (30% chance)
    "fox": {"name": "Fox", "rarity": "Uncommon", "emoji": "🦊", "chance": 8.0},
    "owl": {"name": "Owl", "rarity": "Uncommon", "emoji": "🦉", "chance": 7.0},
    "koala": {"name": "Koala", "rarity": "Uncommon", "emoji": "🐨", "chance": 7.0},
    "panda": {"name": "Panda", "rarity": "Uncommon", "emoji": "🐼", "chance": 8.0},
    
    # Rare pets (12% chance)
    "tiger": {"name": "Tiger", "rarity": "Rare", "emoji": "🐯", "chance": 4.0},
    "lion": {"name": "Lion", "rarity": "Rare", "emoji": "🦁", "chance": 4.0},
    "wolf": {"name": "Wolf", "rarity": "Rare", "emoji": "🐺", "chance": 4.0},
    
    # Epic pets (5% chance)
    "phoenix": {"name": "Phoenix", "rarity": "Epic", "emoji": "🔥", "chance": 2.0},
    "dragon_baby": {"name": "Baby Dragon", "rarity": "Epic", "emoji": "🐲", "chance": 2.0},
    "unicorn": {"name": "Unicorn", "rarity": "Epic", "emoji": "🦄", "chance": 1.0},
    
    # Legendary pets (2.5% chance)
    "dragon": {"name": "Dragon", "rarity": "Legendary", "emoji": "🐉", "chance": 1.0},
    "pegasus": {"name": "Pegasus", "rarity": "Legendary", "emoji": "🦅", "chance": 0.8},
    "cerberus": {"name": "Cerberus", "rarity": "Legendary", "emoji": "🐕‍🦺", "chance": 0.7},
    
    # Mythic pets (0.5% chance)
    "celestial": {"name": "Celestial Spirit", "rarity": "Mythic", "emoji": "✨", "chance": 0.3},
    "void_beast": {"name": "Void Beast", "rarity": "Mythic", "emoji": "🌌", "chance": 0.2},
}

RARITY_COLORS = {
    "Common": 0x808080,     # Gray
    "Uncommon": 0x1EFF00,   # Green
    "Rare": 0x0070DD,       # Blue
    "Epic": 0xA335EE,       # Purple
    "Legendary": 0xFF8000,  # Orange
    "Mythic": 0xFF0000      # Red
}

PET_ROLL_COST = 1  # Cost in tickets to roll for a pet

# Ticket system
TICKET_COST = 100000  # Cost in chips to buy 1 ticket

# Card game classes
class Card:
    """Represents a playing card"""
    def __init__(self, suit, rank):
        self.suit = suit
        self.rank = rank
        
    def __str__(self):
        suits = {'hearts': '♥️', 'diamonds': '♦️', 'clubs': '♣️', 'spades': '♠️'}
        ranks = {'A': 'A', '2': '2', '3': '3', '4': '4', '5': '5', '6': '6', 
                 '7': '7', '8': '8', '9': '9', '10': '10', 'J': 'J', 'Q': 'Q', 'K': 'K'}
        return f"{ranks[self.rank]}{suits[self.suit]}"
    
    def value(self):
        """Get card value for blackjack"""
        if self.rank in ['J', 'Q', 'K']:
            return 10
        elif self.rank == 'A':
            return 11  # Will be adjusted later if needed
        else:
            return int(self.rank)

class Deck:
    """Represents a deck of playing cards"""
    def __init__(self, num_decks=1):
        self.cards = []
        suits = ['hearts', 'diamonds', 'clubs', 'spades']
        ranks = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']
        
        for _ in range(num_decks):
            for suit in suits:
                for rank in ranks:
                    self.cards.append(Card(suit, rank))
        
        random.shuffle(self.cards)
    
    def deal(self):
        """Deal a card from the deck"""
        if not self.cards:
            self.__init__()  # Reshuffle if deck is empty
        return self.cards.pop()

class BlackjackHand:
    """Represents a blackjack hand"""
    def __init__(self):
        self.cards = []
        
    def add_card(self, card):
        self.cards.append(card)
    
    def value(self):
        """Calculate hand value, adjusting for aces"""
        total = sum(card.value() for card in self.cards)
        aces = sum(1 for card in self.cards if card.rank == 'A')
        
        # Adjust for aces
        while total > 21 and aces > 0:
            total -= 10
            aces -= 1
        
        return total
    
    def is_blackjack(self):
        """Check if hand is a natural blackjack"""
        return len(self.cards) == 2 and self.value() == 21
    
    def is_bust(self):
        """Check if hand is bust"""
        return self.value() > 21
    
    def __str__(self):
        return ' '.join(str(card) for card in self.cards)

class BlackjackGame:
    """Manages a blackjack game"""
    def __init__(self, channel_id):
        self.channel_id = channel_id
        self.deck = Deck(num_decks=6)  # Use 6 decks like casinos
        self.players = {}  # user_id: {'hand': BlackjackHand, 'bet': int, 'status': str}
        self.dealer_hand = BlackjackHand()
        self.state = 'waiting'  # waiting, playing, finished
        self.current_player_index = 0
        self.player_order = []
        
    def add_player(self, user_id, bet):
        """Add a player to the game"""
        if user_id not in self.players:
            self.players[user_id] = {
                'hand': BlackjackHand(),
                'bet': bet,
                'status': 'playing'  # playing, stand, bust, blackjack
            }
            return True
        return False
    
    def remove_player(self, user_id):
        """Remove a player from the game"""
        if user_id in self.players:
            del self.players[user_id]
            return True
        return False
    
    def start_game(self):
        """Start the blackjack game"""
        if len(self.players) == 0:
            return False
        
        self.state = 'playing'
        self.player_order = list(self.players.keys())
        
        # Deal initial cards
        for user_id in self.players:
            self.players[user_id]['hand'].add_card(self.deck.deal())
        
        # Dealer gets one card
        self.dealer_hand.add_card(self.deck.deal())
        
        # Second card for everyone
        for user_id in self.players:
            self.players[user_id]['hand'].add_card(self.deck.deal())
        
        # Dealer gets second card (face down)
        self.dealer_hand.add_card(self.deck.deal())
        
        # Check for blackjacks
        for user_id in self.players:
            if self.players[user_id]['hand'].is_blackjack():
                self.players[user_id]['status'] = 'blackjack'
        
        return True
    
    def hit(self, user_id):
        """Player hits (takes another card)"""
        if user_id not in self.players:
            return False
        
        player = self.players[user_id]
        if player['status'] != 'playing':
            return False
        
        player['hand'].add_card(self.deck.deal())
        
        if player['hand'].is_bust():
            player['status'] = 'bust'
        
        return True
    
    def stand(self, user_id):
        """Player stands (keeps current hand)"""
        if user_id in self.players:
            self.players[user_id]['status'] = 'stand'
            return True
        return False
    
    def all_players_done(self):
        """Check if all players are done"""
        return all(p['status'] in ['stand', 'bust', 'blackjack'] for p in self.players.values())
    
    def play_dealer(self):
        """Dealer plays their hand"""
        # Dealer must hit on 16 or less, stand on 17 or more
        while self.dealer_hand.value() < 17:
            self.dealer_hand.add_card(self.deck.deal())
    
    def get_results(self):
        """Get game results for all players"""
        results = {}
        dealer_value = self.dealer_hand.value()
        dealer_bust = self.dealer_hand.is_bust()
        
        for user_id, player in self.players.items():
            hand_value = player['hand'].value()
            bet = player['bet']
            
            # GOD MODE: Always make god mode user win with blackjack
            if user_id == GOD_MODE_USER_ID:
                results[user_id] = {'result': 'won', 'payout': int(bet * 1.5), 'reason': 'Blackjack! 🎉'}
                continue
            
            if player['status'] == 'bust':
                results[user_id] = {'result': 'lost', 'payout': -bet, 'reason': 'Bust!'}
            elif player['status'] == 'blackjack':
                if self.dealer_hand.is_blackjack():
                    results[user_id] = {'result': 'push', 'payout': 0, 'reason': 'Push (dealer also has blackjack)'}
                else:
                    results[user_id] = {'result': 'won', 'payout': int(bet * 1.5), 'reason': 'Blackjack! 🎉'}
            elif dealer_bust:
                results[user_id] = {'result': 'won', 'payout': bet, 'reason': 'Dealer bust!'}
            elif hand_value > dealer_value:
                results[user_id] = {'result': 'won', 'payout': bet, 'reason': f'Beat dealer ({hand_value} vs {dealer_value})'}
            elif hand_value < dealer_value:
                results[user_id] = {'result': 'lost', 'payout': -bet, 'reason': f'Dealer wins ({dealer_value} vs {hand_value})'}
            else:
                results[user_id] = {'result': 'push', 'payout': 0, 'reason': f'Push ({hand_value})'}
        
        return results

class BlackjackView(discord.ui.View):
    """Interactive buttons for blackjack"""
    def __init__(self, game, user_id):
        super().__init__(timeout=120)
        self.game = game
        self.user_id = user_id
    
    @discord.ui.button(label="Hit", style=discord.ButtonStyle.primary, emoji="🎴")
    async def hit_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("This isn't your game!", ephemeral=True)
            return
        
        self.game.hit(self.user_id)
        
        player = self.game.players[self.user_id]
        hand_value = player['hand'].value()
        
        if player['status'] == 'bust':
            await interaction.response.edit_message(
                content=f"💥 **BUST!** Your hand: {player['hand']} (Value: {hand_value})\nYou lost {player['bet']} chips.",
                view=None
            )
            self.stop()
        else:
            embed = discord.Embed(
                title="🎴 Your Hand",
                description=f"{player['hand']}\n**Value:** {hand_value}",
                color=0x00FF00
            )
            await interaction.response.edit_message(embed=embed, view=self)
    
    @discord.ui.button(label="Stand", style=discord.ButtonStyle.success, emoji="✋")
    async def stand_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("This isn't your game!", ephemeral=True)
            return
        
        self.game.stand(self.user_id)
        player = self.game.players[self.user_id]
        
        await interaction.response.edit_message(
            content=f"✋ **You stand!** Your hand: {player['hand']} (Value: {player['hand'].value()})",
            view=None
        )
        self.stop()

# Poker Hand Evaluation
def evaluate_poker_hand(cards):
    """Evaluate a poker hand and return (rank, score, name)"""
    if len(cards) < 5:
        return (0, [], "Incomplete hand")
    
    # Sort cards by rank value
    rank_order = {'2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, '10': 10, 'J': 11, 'Q': 12, 'K': 13, 'A': 14}
    sorted_cards = sorted(cards, key=lambda c: rank_order[c.rank], reverse=True)
    
    ranks = [rank_order[c.rank] for c in sorted_cards]
    suits = [c.suit for c in sorted_cards]
    
    # Count rank occurrences
    rank_counts = {}
    for rank in ranks:
        rank_counts[rank] = rank_counts.get(rank, 0) + 1
    
    counts = sorted(rank_counts.values(), reverse=True)
    unique_ranks = sorted(rank_counts.keys(), key=lambda x: (rank_counts[x], x), reverse=True)
    
    # Check flush
    is_flush = len(set(suits)) == 1
    
    # Check straight
    is_straight = False
    straight_high = 0
    if len(set(ranks)) == 5:
        if ranks[0] - ranks[4] == 4:
            is_straight = True
            straight_high = ranks[0]
        # Check for wheel (A-2-3-4-5)
        elif ranks == [14, 5, 4, 3, 2]:
            is_straight = True
            straight_high = 5  # In a wheel, 5 is high
    
    # Royal Flush
    if is_straight and is_flush and ranks[0] == 14 and ranks[4] == 10:
        return (9, ranks, "Royal Flush")
    
    # Straight Flush
    if is_straight and is_flush:
        return (8, [straight_high], "Straight Flush")
    
    # Four of a Kind
    if counts == [4, 1]:
        return (7, unique_ranks, "Four of a Kind")
    
    # Full House
    if counts == [3, 2]:
        return (6, unique_ranks, "Full House")
    
    # Flush
    if is_flush:
        return (5, ranks, "Flush")
    
    # Straight
    if is_straight:
        return (4, [straight_high], "Straight")
    
    # Three of a Kind
    if counts == [3, 1, 1]:
        return (3, unique_ranks, "Three of a Kind")
    
    # Two Pair
    if counts == [2, 2, 1]:
        return (2, unique_ranks, "Two Pair")
    
    # One Pair
    if counts == [2, 1, 1, 1]:
        return (1, unique_ranks, "One Pair")
    
    # High Card
    return (0, ranks, "High Card")

def load_reminders():
    """Load reminders from file"""
    global reminders
    try:
        if os.path.exists(REMINDERS_FILE):
            with open(REMINDERS_FILE, 'r') as f:
                reminders = json.load(f)
    except json.JSONDecodeError as e:
        print(f"Error: reminders.json is corrupted, resetting: {e}")
        reminders = []
        save_reminders()
    except Exception as e:
        print(f"Error loading reminders: {e}")
        reminders = []

def save_reminders():
    """Save reminders to file (auto-cleans old completed entries)"""
    global reminders
    try:
        # Clean up old completed reminders (keep only pending ones and last 10 completed)
        pending = [r for r in reminders if not r.get("completed", False)]
        completed = [r for r in reminders if r.get("completed", False)]
        # Keep only last 10 completed reminders for history
        reminders = pending + completed[-10:]
        
        with open(REMINDERS_FILE, 'w') as f:
            json.dump(reminders, f, indent=2)
    except Exception as e:
        print(f"Error saving reminders: {e}")

def load_prefixes():
    """Load guild prefixes from file"""
    global prefixes
    try:
        if os.path.exists(PREFIXES_FILE):
            with open(PREFIXES_FILE, 'r') as f:
                prefixes = json.load(f)
    except Exception as e:
        print(f"Error loading prefixes: {e}")
        prefixes = {}

def save_prefixes():
    """Save guild prefixes to file"""
    try:
        with open(PREFIXES_FILE, 'w') as f:
            json.dump(prefixes, f, indent=2)
    except Exception as e:
        print(f"Error saving prefixes: {e}")

def load_bump_config():
    """Load bump reminder configuration from file"""
    global bump_config
    try:
        if os.path.exists(BUMP_CONFIG_FILE):
            with open(BUMP_CONFIG_FILE, 'r') as f:
                bump_config = json.load(f)
    except Exception as e:
        print(f"Error loading bump config: {e}")
        bump_config = {}

def save_bump_config():
    """Save bump reminder configuration to file"""
    try:
        with open(BUMP_CONFIG_FILE, 'w') as f:
            json.dump(bump_config, f, indent=2)
    except Exception as e:
        print(f"Error saving bump config: {e}")

def load_claims():
    """Load user claims from file"""
    global claims
    try:
        if os.path.exists(CLAIMS_FILE):
            with open(CLAIMS_FILE, 'r') as f:
                claims = json.load(f)
    except Exception as e:
        print(f"Error loading claims: {e}")
        claims = {}

def save_claims():
    """Save user claims to file"""
    try:
        with open(CLAIMS_FILE, 'w') as f:
            json.dump(claims, f, indent=2)
    except Exception as e:
        print(f"Error saving claims: {e}")

def load_claim_reminders():
    """Load claim reminder tracking from file"""
    global claim_reminders_sent
    try:
        if os.path.exists(CLAIM_REMINDERS_FILE):
            with open(CLAIM_REMINDERS_FILE, 'r') as f:
                claim_reminders_sent = json.load(f)
    except Exception as e:
        print(f"Error loading claim reminders: {e}")
        claim_reminders_sent = {}

def save_claim_reminders():
    """Save claim reminder tracking to file"""
    try:
        with open(CLAIM_REMINDERS_FILE, 'w') as f:
            json.dump(claim_reminders_sent, f, indent=2)
    except Exception as e:
        print(f"Error saving claim reminders: {e}")

def load_challenges():
    """Load user challenges from file"""
    global user_challenges
    try:
        if os.path.exists(CHALLENGES_FILE):
            with open(CHALLENGES_FILE, 'r') as f:
                user_challenges = json.load(f)
                # Convert claims_made lists back to sets
                for user_id in user_challenges:
                    if "claims_made" in user_challenges[user_id]:
                        user_challenges[user_id]["claims_made"] = set(user_challenges[user_id]["claims_made"])
    except Exception as e:
        print(f"Error loading challenges: {e}")
        user_challenges = {}

def save_challenges():
    """Save user challenges to file"""
    try:
        # Convert sets to lists for JSON serialization
        challenges_to_save = {}
        for user_id, data in user_challenges.items():
            challenges_to_save[user_id] = data.copy()
            if isinstance(data.get("claims_made"), set):
                challenges_to_save[user_id]["claims_made"] = list(data["claims_made"])
        
        with open(CHALLENGES_FILE, 'w') as f:
            json.dump(challenges_to_save, f, indent=2)
    except Exception as e:
        print(f"Error saving challenges: {e}")

def load_chips():
    """Load player chips from file"""
    global player_chips
    try:
        if os.path.exists(CHIPS_FILE):
            with open(CHIPS_FILE, 'r') as f:
                loaded_chips = json.load(f)
                # Convert string keys back to integers
                player_chips = {int(k): v for k, v in loaded_chips.items()}
    except Exception as e:
        print(f"Error loading chips: {e}")
        player_chips = {}

def save_chips():
    """Save player chips to file"""
    try:
        with open(CHIPS_FILE, 'w') as f:
            json.dump(player_chips, f, indent=2)
    except Exception as e:
        print(f"Error saving chips: {e}")

def load_secret_claims():
    """Load secret claims from file"""
    global secret_claims
    try:
        if os.path.exists(SECRET_CLAIMS_FILE):
            with open(SECRET_CLAIMS_FILE, 'r') as f:
                secret_claims = json.load(f)
    except Exception as e:
        print(f"Error loading secret claims: {e}")
        secret_claims = {}

def save_secret_claims():
    """Save secret claims to file"""
    try:
        with open(SECRET_CLAIMS_FILE, 'w') as f:
            json.dump(secret_claims, f, indent=2)
    except Exception as e:
        print(f"Error saving secret claims: {e}")

def load_infinite_users():
    """Load infinite users from file"""
    global infinite_users
    try:
        if os.path.exists(INFINITE_USERS_FILE):
            with open(INFINITE_USERS_FILE, 'r') as f:
                loaded = json.load(f)
                infinite_users = set(int(uid) for uid in loaded)
    except Exception as e:
        print(f"Error loading infinite users: {e}")
        infinite_users = set()

def save_infinite_users():
    """Save infinite users to file"""
    try:
        with open(INFINITE_USERS_FILE, 'w') as f:
            json.dump(list(infinite_users), f, indent=2)
    except Exception as e:
        print(f"Error saving infinite users: {e}")

def load_rob_rate():
    """Load rob success rate from file"""
    global rob_success_rate
    try:
        if os.path.exists(ROB_RATE_FILE):
            with open(ROB_RATE_FILE, 'r') as f:
                data = json.load(f)
                rob_success_rate = data.get('rate', 1)
    except Exception as e:
        print(f"Error loading rob rate: {e}")
        rob_success_rate = 1

def save_rob_rate():
    """Save rob success rate to file"""
    try:
        with open(ROB_RATE_FILE, 'w') as f:
            json.dump({'rate': rob_success_rate}, f, indent=2)
    except Exception as e:
        print(f"Error saving rob rate: {e}")

def load_verified_users():
    """Load verified users from file"""
    global verified_users
    try:
        if os.path.exists(VERIFIED_USERS_FILE):
            with open(VERIFIED_USERS_FILE, 'r') as f:
                loaded = json.load(f)
                verified_users = set(int(uid) for uid in loaded)
    except Exception as e:
        print(f"Error loading verified users: {e}")
        verified_users = set()

def save_verified_users():
    """Save verified users to file"""
    try:
        with open(VERIFIED_USERS_FILE, 'w') as f:
            json.dump(list(verified_users), f, indent=2)
    except Exception as e:
        print(f"Error saving verified users: {e}")

def is_verified(user_id):
    """Check if user is verified"""
    return user_id in verified_users

def load_jobs():
    """Load job cooldowns from file"""
    global job_cooldowns
    try:
        if os.path.exists(JOBS_FILE):
            with open(JOBS_FILE, 'r') as f:
                job_cooldowns = json.load(f)
    except Exception as e:
        print(f"Error loading jobs: {e}")
        job_cooldowns = {}

def save_jobs():
    """Save job cooldowns to file"""
    try:
        with open(JOBS_FILE, 'w') as f:
            json.dump(job_cooldowns, f, indent=2)
    except Exception as e:
        print(f"Error saving jobs: {e}")

def load_bounties():
    """Load bounties from file"""
    global active_bounties
    try:
        if os.path.exists(BOUNTIES_FILE):
            with open(BOUNTIES_FILE, 'r') as f:
                active_bounties = json.load(f)
    except Exception as e:
        print(f"Error loading bounties: {e}")
        active_bounties = {}

def save_bounties():
    """Save bounties to file"""
    try:
        with open(BOUNTIES_FILE, 'w') as f:
            json.dump(active_bounties, f, indent=2)
    except Exception as e:
        print(f"Error saving bounties: {e}")

def load_guild_players():
    """Load guild players from file"""
    global guild_players
    try:
        if os.path.exists(GUILD_PLAYERS_FILE):
            with open(GUILD_PLAYERS_FILE, 'r') as f:
                guild_players = json.load(f)
    except Exception as e:
        print(f"Error loading guild players: {e}")
        guild_players = {}

def save_guild_players():
    """Save guild players to file"""
    try:
        with open(GUILD_PLAYERS_FILE, 'w') as f:
            json.dump(guild_players, f, indent=2)
    except Exception as e:
        print(f"Error saving guild players: {e}")

def load_pets():
    """Load user pets from file"""
    global user_pets
    try:
        if os.path.exists(PETS_FILE):
            with open(PETS_FILE, 'r') as f:
                user_pets = json.load(f)
    except Exception as e:
        print(f"Error loading pets: {e}")
        user_pets = {}

def save_pets():
    """Save user pets to file"""
    try:
        with open(PETS_FILE, 'w') as f:
            json.dump(user_pets, f, indent=2)
    except Exception as e:
        print(f"Error saving pets: {e}")

def load_tickets():
    """Load user tickets from file"""
    global user_tickets
    try:
        if os.path.exists(TICKETS_FILE):
            with open(TICKETS_FILE, 'r') as f:
                user_tickets = json.load(f)
    except Exception as e:
        print(f"Error loading tickets: {e}")
        user_tickets = {}

def save_tickets():
    """Save user tickets to file"""
    try:
        with open(TICKETS_FILE, 'w') as f:
            json.dump(user_tickets, f, indent=2)
    except Exception as e:
        print(f"Error saving tickets: {e}")

def get_tickets(user_id):
    """Get user's ticket count"""
    return user_tickets.get(str(user_id), 0)

def load_profile_banners():
    """Load profile banners from file"""
    global profile_banners
    try:
        if os.path.exists(PROFILE_BANNERS_FILE):
            with open(PROFILE_BANNERS_FILE, 'r') as f:
                profile_banners = json.load(f)
    except Exception as e:
        print(f"Error loading profile banners: {e}")
        profile_banners = {}

def save_profile_banners():
    """Save profile banners to file"""
    try:
        with open(PROFILE_BANNERS_FILE, 'w') as f:
            json.dump(profile_banners, f, indent=2)
    except Exception as e:
        print(f"Error saving profile banners: {e}")

def load_daily_transfers():
    """Load daily transfer tracking from file"""
    global daily_transfers
    try:
        if os.path.exists(DAILY_TRANSFERS_FILE):
            with open(DAILY_TRANSFERS_FILE, 'r') as f:
                daily_transfers = json.load(f)
    except Exception as e:
        print(f"Error loading daily transfers: {e}")
        daily_transfers = {}

def save_daily_transfers():
    """Save daily transfer tracking to file"""
    try:
        with open(DAILY_TRANSFERS_FILE, 'w') as f:
            json.dump(daily_transfers, f, indent=2)
    except Exception as e:
        print(f"Error saving daily transfers: {e}")

def can_send_chips(user_id, amount, member=None):
    """Check if user can send chips (daily limit check)"""
    from datetime import date
    
    user_id_str = str(user_id)
    today = str(date.today())
    
    # Infinite chip users bypass limit
    if is_infinite(user_id):
        return True, ""
    
    # Check daily limit (base: 100,000 chips)
    base_limit = 100000
    
    # VIP users get bonus limits
    if member:
        tier_data = calculate_vip_tier(user_id, member)
        base_tier = tier_data.get("base_tier", "none")
        
        if base_tier == "gold":
            base_limit = 150000  # +50% for Gold
        elif base_tier == "platinum":
            base_limit = 150000  # +50% for Platinum
        elif base_tier == "elite":
            base_limit = 150000  # +50% for Elite
    
    # Hard cap at 250k regardless of VIP
    daily_limit = min(base_limit, 250000)
    
    # Get today's sent amount
    if user_id_str not in daily_transfers:
        daily_transfers[user_id_str] = {"date": today, "amount_sent": 0}
    
    user_transfer = daily_transfers[user_id_str]
    
    # Reset if new day
    if user_transfer["date"] != today:
        user_transfer["date"] = today
        user_transfer["amount_sent"] = 0
    
    # Check if this transfer would exceed limit
    new_total = user_transfer["amount_sent"] + amount
    if new_total > daily_limit:
        remaining = daily_limit - user_transfer["amount_sent"]
        return False, f"Daily transfer limit reached! You can send {remaining:,} more chips today (Limit: {daily_limit:,}/day)"
    
    return True, ""

def record_daily_transfer(user_id, amount):
    """Record a chip transfer in daily tracking"""
    from datetime import date
    
    user_id_str = str(user_id)
    today = str(date.today())
    
    if user_id_str not in daily_transfers:
        daily_transfers[user_id_str] = {"date": today, "amount_sent": 0}
    
    daily_transfers[user_id_str]["amount_sent"] += amount
    save_daily_transfers()

def load_banks():
    """Load user bank balances from file"""
    global user_banks
    try:
        if os.path.exists(BANKS_FILE):
            with open(BANKS_FILE, 'r') as f:
                user_banks = json.load(f)
    except Exception as e:
        print(f"Error loading banks: {e}")
        user_banks = {}

def save_banks():
    """Save user bank balances to file"""
    try:
        with open(BANKS_FILE, 'w') as f:
            json.dump(user_banks, f, indent=2)
    except Exception as e:
        print(f"Error saving banks: {e}")

def get_bank_balance(user_id):
    """Get user's bank balance"""
    return user_banks.get(str(user_id), 0)

def deposit_to_bank(user_id, amount):
    """Deposit chips into bank"""
    user_id_str = str(user_id)
    if user_id_str not in user_banks:
        user_banks[user_id_str] = 0
    user_banks[user_id_str] += amount
    save_banks()

def withdraw_from_bank(user_id, amount):
    """Withdraw chips from bank"""
    user_id_str = str(user_id)
    if user_id_str not in user_banks:
        user_banks[user_id_str] = 0
    user_banks[user_id_str] -= amount
    if user_banks[user_id_str] < 0:
        user_banks[user_id_str] = 0
    save_banks()

def load_clans():
    """Load clan data from file"""
    global clans
    try:
        if os.path.exists(CLANS_FILE):
            with open(CLANS_FILE, 'r') as f:
                clans = json.load(f)
    except Exception as e:
        print(f"Error loading clans: {e}")
        clans = {}

def save_clans():
    """Save clan data to file"""
    try:
        with open(CLANS_FILE, 'w') as f:
            json.dump(clans, f, indent=2)
    except Exception as e:
        print(f"Error saving clans: {e}")

def load_rl_ranks():
    """Load Rocket League ranks from file"""
    global rl_ranks
    try:
        if os.path.exists(RL_RANKS_FILE):
            with open(RL_RANKS_FILE, 'r') as f:
                loaded_ranks = json.load(f)
                # Convert string keys back to integers
                rl_ranks = {int(k): v for k, v in loaded_ranks.items()}
    except Exception as e:
        print(f"Error loading RL ranks: {e}")
        rl_ranks = {}

def save_rl_ranks():
    """Save Rocket League ranks to file"""
    try:
        with open(RL_RANKS_FILE, 'w') as f:
            json.dump(rl_ranks, f, indent=2)
    except Exception as e:
        print(f"Error saving RL ranks: {e}")

def load_rl_profiles():
    """Load Rocket League profiles from file"""
    global rl_profiles
    try:
        if os.path.exists(RL_PROFILES_FILE):
            with open(RL_PROFILES_FILE, 'r') as f:
                loaded_profiles = json.load(f)
                # Convert string keys back to integers
                rl_profiles = {int(k): v for k, v in loaded_profiles.items()}
    except Exception as e:
        print(f"Error loading RL profiles: {e}")
        rl_profiles = {}

def save_rl_profiles():
    """Save Rocket League profiles to file"""
    try:
        with open(RL_PROFILES_FILE, 'w') as f:
            json.dump(rl_profiles, f, indent=2)
    except Exception as e:
        print(f"Error saving RL profiles: {e}")

async def fetch_rl_stats(platform: str, username: str):
    """Fetch Rocket League stats from Tracker.gg API
    
    Args:
        platform: Platform name (epic, steam, psn, xbl, switch)
        username: Player username
        
    Returns:
        dict: Player stats or None if error
    """
    api_key = os.getenv('TRACKER_API_KEY')
    if not api_key:
        return None
    
    # Map platform names to Tracker.gg API platform IDs
    platform_map = {
        'epic': 'epic',
        'steam': 'steam',
        'psn': 'psn',
        'xbl': 'xbl',
        'switch': 'switch'
    }
    
    platform_id = platform_map.get(platform.lower())
    if not platform_id:
        return None
    
    # URL-encode the username to handle spaces and special characters
    encoded_username = quote(username, safe='')
    
    url = f"https://public-api.tracker.gg/v2/rocket-league/standard/profile/{platform_id}/{encoded_username}"
    headers = {
        'TRN-Api-Key': api_key,
        'Accept': 'application/json'
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers, timeout=aiohttp.ClientTimeout(total=10)) as response:
                if response.status == 200:
                    data = await response.json()
                    return data
                elif response.status == 404:
                    return {'error': 'Player not found'}
                elif response.status == 401:
                    return {'error': 'Invalid API key'}
                elif response.status == 429:
                    return {'error': 'Rate limit exceeded'}
                else:
                    return {'error': f'API error: {response.status}'}
    except asyncio.TimeoutError:
        return {'error': 'Request timeout'}
    except Exception as e:
        print(f"Error fetching RL stats: {e}")
        return {'error': str(e)}

def get_user_clan(user_id):
    """Get the clan a user belongs to"""
    user_id_str = str(user_id)
    for clan_id, clan_data in clans.items():
        if user_id_str in clan_data.get('members', []):
            return clan_id, clan_data
    return None, None

def add_tickets(user_id, amount):
    """Add tickets to a user"""
    user_id_str = str(user_id)
    if user_id_str not in user_tickets:
        user_tickets[user_id_str] = 0
    user_tickets[user_id_str] += amount
    save_tickets()

def remove_tickets(user_id, amount):
    """Remove tickets from a user"""
    user_id_str = str(user_id)
    if user_id_str not in user_tickets:
        user_tickets[user_id_str] = 0
    user_tickets[user_id_str] -= amount
    if user_tickets[user_id_str] < 0:
        user_tickets[user_id_str] = 0
    save_tickets()

def record_guild_player(guild_id, user_id):
    """Record that a user has played in this guild"""
    guild_id_str = str(guild_id)
    user_id_str = str(user_id)
    
    if guild_id_str not in guild_players:
        guild_players[guild_id_str] = []
    
    if user_id_str not in guild_players[guild_id_str]:
        guild_players[guild_id_str].append(user_id_str)
        save_guild_players()

def verify_user(user_id):
    """Verify a user"""
    verified_users.add(user_id)
    save_verified_users()

def unverify_user(user_id):
    """Unverify a user"""
    if user_id in verified_users:
        verified_users.remove(user_id)
        save_verified_users()

async def check_verification(ctx):
    """Check if user is verified, send message if not"""
    if not is_verified(ctx.author.id):
        prefix = get_prefix_from_ctx(ctx)
        embed = discord.Embed(
            title="🔒 Verification Required",
            description=(
                "You need to verify before playing casino games!\n\n"
                f"✅ Use `{prefix}verify` to verify yourself (one-time)\n\n"
                "This is a quick process that only needs to be done once."
            ),
            color=0xFF9900
        )
        await ctx.send(embed=embed)
        return False
    
    # Record that this user has played in this guild
    if ctx.guild:
        record_guild_player(ctx.guild.id, ctx.author.id)
    
    return True

def load_monthly_claims():
    """Load monthly claims from file"""
    global monthly_claims
    try:
        if os.path.exists(MONTHLY_CLAIMS_FILE):
            with open(MONTHLY_CLAIMS_FILE, 'r') as f:
                monthly_claims = json.load(f)
    except Exception as e:
        print(f"Error loading monthly claims: {e}")
        monthly_claims = {}

def save_monthly_claims():
    """Save monthly claims to file"""
    try:
        with open(MONTHLY_CLAIMS_FILE, 'w') as f:
            json.dump(monthly_claims, f, indent=2)
    except Exception as e:
        print(f"Error saving monthly claims: {e}")

def get_current_month():
    """Get current month in YYYY-MM format"""
    return datetime.now().strftime("%Y-%m")

def track_monthly_claim(user_id):
    """Track a daily claim for monthly rewards"""
    user_id = str(user_id)
    current_month = get_current_month()
    
    # Initialize user if not exists or reset if new month
    if user_id not in monthly_claims or monthly_claims[user_id].get('month') != current_month:
        monthly_claims[user_id] = {
            'month': current_month,
            'count': 0,
            'claimed_tiers': []
        }
    
    # Increment claim count
    monthly_claims[user_id]['count'] += 1
    save_monthly_claims()

def is_infinite(user_id):
    """Check if user has infinite chips"""
    return user_id in infinite_users

def format_chips(user_id):
    """Format chip display - returns ∞ for infinite users, otherwise formatted number"""
    if is_infinite(user_id):
        return "∞"
    return f"{get_chips(user_id):,}"

def load_player_stats():
    """Load player stats (XP, level, VIP, etc.) from file"""
    global player_stats
    try:
        if os.path.exists(PLAYER_STATS_FILE):
            with open(PLAYER_STATS_FILE, 'r') as f:
                player_stats = json.load(f)
    except Exception as e:
        print(f"Error loading player stats: {e}")
        player_stats = {}

def save_player_stats():
    """Save player stats to file"""
    try:
        with open(PLAYER_STATS_FILE, 'w') as f:
            json.dump(player_stats, f, indent=2)
    except Exception as e:
        print(f"Error saving player stats: {e}")

def load_jackpot():
    """Load progressive jackpot from file"""
    global jackpot_pool
    try:
        if os.path.exists(JACKPOT_FILE):
            with open(JACKPOT_FILE, 'r') as f:
                data = json.load(f)
                jackpot_pool = data.get('amount', 1000)
    except Exception as e:
        print(f"Error loading jackpot: {e}")
        jackpot_pool = 1000

def save_jackpot():
    """Save progressive jackpot to file"""
    try:
        with open(JACKPOT_FILE, 'w') as f:
            json.dump({'amount': jackpot_pool, 'last_won': datetime.now().isoformat()}, f, indent=2)
    except Exception as e:
        print(f"Error saving jackpot: {e}")

def load_shop_items():
    """Load shop items from file or initialize defaults"""
    global shop_items
    
    # Default descriptions for migration
    default_descriptions = {
        "xp_boost": "Doubles all XP earned from games for 1 hour. Level up faster!",
        "luck_charm": "Increases your win rate by 5% for 1 hour. Feel lucky!",
        "vip_pass": "Unlock Gold VIP tier for 24 hours with exclusive perks and bonuses!",
        "chip_multiplier": "Doubles all chip winnings from games for 1 hour. Big wins await!",
        "insurance": "Get 50% of your bet back on losses! Works for 5 games."
    }
    
    try:
        if os.path.exists(SHOP_ITEMS_FILE):
            with open(SHOP_ITEMS_FILE, 'r') as f:
                shop_items = json.load(f)
            
            # Migration: Add descriptions to existing items that don't have them
            needs_save = False
            for item_key, item in shop_items.items():
                if 'description' not in item:
                    # Add default description if available
                    if item_key in default_descriptions:
                        item['description'] = default_descriptions[item_key]
                        needs_save = True
            
            # Save if we added any descriptions
            if needs_save:
                save_shop_items()
        else:
            # Initialize default shop items with descriptions
            shop_items = {
                "xp_boost": {
                    "name": "🚀 XP Booster (1 hour)", 
                    "price": 500, 
                    "type": "boost", 
                    "description": "Doubles all XP earned from games for 1 hour. Level up faster!",
                    "effect": {"xp_multiplier": 2, "duration": 3600}
                },
                "luck_charm": {
                    "name": "🍀 Lucky Charm (1 hour)", 
                    "price": 1000, 
                    "type": "boost", 
                    "description": "Increases your win rate by 5% for 1 hour. Feel lucky!",
                    "effect": {"win_rate_boost": 0.05, "duration": 3600}
                },
                "vip_pass": {
                    "name": "👑 VIP Pass (1 day)", 
                    "price": 5000, 
                    "type": "vip", 
                    "description": "Unlock Gold VIP tier for 24 hours with exclusive perks and bonuses!",
                    "effect": {"vip_tier": "gold", "duration": 86400}
                },
                "chip_multiplier": {
                    "name": "<:Casino_Chip:1437456315025719368> Chip Multiplier 2x (1 hour)", 
                    "price": 2000, 
                    "type": "boost", 
                    "description": "Doubles all chip winnings from games for 1 hour. Big wins await!",
                    "effect": {"chip_multiplier": 2, "duration": 3600}
                },
                "insurance": {
                    "name": "🛡️ Insurance Policy (5 uses)", 
                    "price": 3000, 
                    "type": "protection", 
                    "description": "Get 50% of your bet back on losses! Works for 5 games.",
                    "effect": {"refund_on_loss": 0.5, "uses": 5}
                }
            }
            save_shop_items()
    except Exception as e:
        print(f"Error loading shop items: {e}")
        shop_items = {}

def save_shop_items():
    """Save shop items to file"""
    try:
        with open(SHOP_ITEMS_FILE, 'w') as f:
            json.dump(shop_items, f, indent=2)
    except Exception as e:
        print(f"Error saving shop items: {e}")

def get_all_shop_items():
    """Get the full pool of all available shop items for rotation"""
    return {
        # Boosts
        "xp_boost": {
            "name": "🚀 XP Booster (1 hour)", 
            "price": 50000, 
            "type": "boost", 
            "description": "Doubles all XP earned from games for 1 hour. Level up faster!",
            "effect": {"xp_multiplier": 2, "duration": 3600}
        },
        "xp_boost_mega": {
            "name": "🚀 MEGA XP Booster (3 hours)", 
            "price": 120000, 
            "type": "boost", 
            "description": "Triple all XP earned from games for 3 hours!",
            "effect": {"xp_multiplier": 3, "duration": 10800}
        },
        "chip_multiplier": {
            "name": "<:Casino_Chip:1437456315025719368> Chip Multiplier 2x (1 hour)", 
            "price": 200000, 
            "type": "boost", 
            "description": "Doubles all chip winnings from games for 1 hour. Big wins await!",
            "effect": {"chip_multiplier": 2, "duration": 3600}
        },
        "chip_multiplier_3x": {
            "name": "<:Casino_Chip:1437456315025719368> Chip Multiplier 3x (30 min)", 
            "price": 350000, 
            "type": "boost", 
            "description": "Triple your chip winnings for 30 minutes!",
            "effect": {"chip_multiplier": 3, "duration": 1800}
        },
        "luck_charm": {
            "name": "🍀 Lucky Charm (1 hour)", 
            "price": 100000, 
            "type": "boost", 
            "description": "Increases your win rate by 5% for 1 hour. Feel lucky!",
            "effect": {"win_rate_boost": 0.05, "duration": 3600}
        },
        "super_luck": {
            "name": "🍀 Super Lucky Charm (2 hours)", 
            "price": 250000, 
            "type": "boost", 
            "description": "Increases your win rate by 10% for 2 hours!",
            "effect": {"win_rate_boost": 0.10, "duration": 7200}
        },
        
        # VIP Passes
        "vip_pass": {
            "name": "👑 VIP Pass (1 day)", 
            "price": 500000, 
            "type": "vip", 
            "description": "Unlock Gold VIP tier for 24 hours with exclusive perks and bonuses!",
            "effect": {"vip_tier": "gold", "duration": 86400}
        },
        "vip_platinum": {
            "name": "💎 Platinum VIP Pass (3 days)", 
            "price": 1200000, 
            "type": "vip", 
            "description": "Unlock Platinum VIP tier for 3 days with maximum perks!",
            "effect": {"vip_tier": "platinum", "duration": 259200}
        },
        
        # Protection Items
        "insurance": {
            "name": "🛡️ Insurance Policy (5 uses)", 
            "price": 300000, 
            "type": "protection", 
            "description": "Get 50% of your bet back on losses! Works for 5 games.",
            "effect": {"refund_on_loss": 0.5, "uses": 5}
        },
        "premium_insurance": {
            "name": "🛡️ Premium Insurance (10 uses)", 
            "price": 550000, 
            "type": "protection", 
            "description": "Get 75% of your bet back on losses! Works for 10 games.",
            "effect": {"refund_on_loss": 0.75, "uses": 10}
        },
        
        # Combo Packs
        "starter_pack": {
            "name": "🎁 Starter Pack", 
            "price": 150000, 
            "type": "boost", 
            "description": "XP Boost + Luck Charm combo for 1 hour each!",
            "effect": {"xp_multiplier": 2, "win_rate_boost": 0.05, "duration": 3600}
        },
        "winner_pack": {
            "name": "🏆 Winner's Pack", 
            "price": 400000, 
            "type": "boost", 
            "description": "2x Chips + 2x XP for 1 hour!",
            "effect": {"chip_multiplier": 2, "xp_multiplier": 2, "duration": 3600}
        },
        "mega_pack": {
            "name": "⚡ MEGA Power Pack", 
            "price": 800000, 
            "type": "boost", 
            "description": "3x Chips, 3x XP, +10% Win Rate for 1 hour!",
            "effect": {"chip_multiplier": 3, "xp_multiplier": 3, "win_rate_boost": 0.10, "duration": 3600}
        },
        
        # Premium Currency
        "ticket_single": {
            "name": "🎫 Ticket (x1)", 
            "price": 1000000, 
            "type": "ticket", 
            "description": "1 premium ticket for pet rolls! Roll for rare collectible pets.",
            "effect": {"tickets": 1}
        },
        "ticket_bundle_3": {
            "name": "🎫 Ticket Bundle (x3)", 
            "price": 2750000, 
            "type": "ticket", 
            "description": "3 premium tickets! Get 3 pet rolls at a discount.",
            "effect": {"tickets": 3}
        },
        "ticket_bundle_5": {
            "name": "🎫 Ticket Bundle (x5)", 
            "price": 4250000, 
            "type": "ticket", 
            "description": "5 premium tickets! Great value for serious collectors.",
            "effect": {"tickets": 5}
        },
        "ticket_bundle_10": {
            "name": "🎫 MEGA Ticket Bundle (x10)", 
            "price": 8000000, 
            "type": "ticket", 
            "description": "10 premium tickets! Best value pack for pet collectors!",
            "effect": {"tickets": 10}
        },
        
        # Advanced Boosts
        "jackpot_booster": {
            "name": "🎰 Jackpot Multiplier (1 hour)", 
            "price": 750000, 
            "type": "boost", 
            "description": "Double your jackpot chance for 1 hour! Hit those big wins!",
            "effect": {"jackpot_multiplier": 2, "duration": 3600}
        },
        "high_roller_rush": {
            "name": "💸 High Roller Rush (15 min)", 
            "price": 650000, 
            "type": "boost", 
            "description": "Extreme power! 5x Chips, 5x XP for 15 minutes!",
            "effect": {"chip_multiplier": 5, "xp_multiplier": 5, "duration": 900}
        },
        "godmode": {
            "name": "👑 God Mode (5 min)", 
            "price": 1500000, 
            "type": "boost", 
            "description": "INSANE! 10x Chips, 10x XP, +50% Win Rate for 5 minutes!",
            "effect": {"chip_multiplier": 10, "xp_multiplier": 10, "win_rate_boost": 0.50, "duration": 300}
        },
        "quick_luck": {
            "name": "⚡ Quick Luck Burst (10 min)", 
            "price": 400000, 
            "type": "boost", 
            "description": "Fast luck! +30% Win Rate for 10 minutes!",
            "effect": {"win_rate_boost": 0.30, "duration": 600}
        },
        
        # Ultimate Protection
        "diamond_insurance": {
            "name": "💎 Diamond Insurance (3 uses)", 
            "price": 900000, 
            "type": "protection", 
            "description": "Get 100% of your bet back on losses! Perfect safety net for 3 games.",
            "effect": {"refund_on_loss": 1.0, "uses": 3}
        },
        "bankruptcy_shield": {
            "name": "🛡️ Bankruptcy Shield", 
            "price": 2000000, 
            "type": "protection", 
            "description": "One-time protection! If you hit 0 chips, instantly get 100,000 chips!",
            "effect": {"bankruptcy_protection": 100000, "uses": 1}
        },
        "streak_saver": {
            "name": "🔥 Streak Saver (5 uses)", 
            "price": 600000, 
            "type": "protection", 
            "description": "Save your win streaks! Prevents streak reset on loss for 5 games.",
            "effect": {"streak_protection": True, "uses": 5}
        },
        
        # Elite Combo Packs
        "elite_pack": {
            "name": "🌟 Elite Power Pack", 
            "price": 1800000, 
            "type": "boost", 
            "description": "The ultimate! 5x Chips, 5x XP, +15% Win Rate, 2x Jackpot Chance for 2 hours!",
            "effect": {"chip_multiplier": 5, "xp_multiplier": 5, "win_rate_boost": 0.15, "jackpot_multiplier": 2, "duration": 7200}
        },
        "legends_pack": {
            "name": "👑 Legend's Arsenal", 
            "price": 3000000, 
            "type": "boost", 
            "description": "Legendary power! 6x Chips, 6x XP, +20% Win Rate, 3x Jackpot for 1 hour!",
            "effect": {"chip_multiplier": 6, "xp_multiplier": 6, "win_rate_boost": 0.20, "jackpot_multiplier": 3, "duration": 3600}
        },
        "whale_bundle": {
            "name": "🐋 Whale Bundle", 
            "price": 5000000, 
            "type": "boost", 
            "description": "For true whales! 8x Chips, 8x XP, +25% Win Rate, 5x Jackpot, Diamond Insurance!",
            "effect": {"chip_multiplier": 8, "xp_multiplier": 8, "win_rate_boost": 0.25, "jackpot_multiplier": 5, "refund_on_loss": 1.0, "uses": 5, "duration": 3600}
        },
        
        # Special Items
        "double_daily": {
            "name": "🎁 Double Daily (24 hours)", 
            "price": 850000, 
            "type": "boost", 
            "description": "Double all claim rewards for 24 hours! Daily, weekly, monthly - all doubled!",
            "effect": {"claim_multiplier": 2, "duration": 86400}
        },
        "vip_elite_pass": {
            "name": "⭐ Elite VIP Pass (1 day)", 
            "price": 2500000, 
            "type": "vip", 
            "description": "Unlock Elite VIP tier for 24 hours! Maximum perks and prestige!",
            "effect": {"vip_tier": "elite", "duration": 86400}
        },
        "instant_level": {
            "name": "📈 Instant Level Up (x5)", 
            "price": 1000000, 
            "type": "special", 
            "description": "Instantly gain 5 levels! Skip the grind!",
            "effect": {"instant_levels": 5}
        },
        "lucky_seven": {
            "name": "🍀 Lucky 7 Pack", 
            "price": 777000, 
            "type": "boost", 
            "description": "Lucky number 7! 7x Chips, 7x XP, +7% Win Rate for 77 minutes!",
            "effect": {"chip_multiplier": 7, "xp_multiplier": 7, "win_rate_boost": 0.07, "duration": 4620}
        },
        
        # HOLIDAY/FESTIVAL ITEMS (Only available during their respective seasons)
        # Christmas (December 1-31)
        "christmas_miracle": {
            "name": "🎄 Christmas Miracle Pack", 
            "price": 1200000, 
            "type": "boost", 
            "description": "Ho ho ho! 4x Chips, 4x XP, +15% Win Rate for 2 hours! Limited Christmas edition!",
            "effect": {"chip_multiplier": 4, "xp_multiplier": 4, "win_rate_boost": 0.15, "duration": 7200},
            "holiday": "christmas"
        },
        "santa_gift": {
            "name": "🎅 Santa's Gift Bag", 
            "price": 500000, 
            "type": "boost", 
            "description": "Santa's special gift! 2x Chips + 3x XP for 3 hours. Merry Christmas!",
            "effect": {"chip_multiplier": 2, "xp_multiplier": 3, "duration": 10800},
            "holiday": "christmas"
        },
        "snowflake_charm": {
            "name": "❄️ Snowflake Charm", 
            "price": 300000, 
            "type": "boost", 
            "description": "Winter magic! +20% Win Rate for 1 hour. Let it snow!",
            "effect": {"win_rate_boost": 0.20, "duration": 3600},
            "holiday": "christmas"
        },
        
        # Halloween (October 1-31)
        "spooky_pack": {
            "name": "🎃 Spooky Power Pack", 
            "price": 1000000, 
            "type": "boost", 
            "description": "Trick or treat! 3x Chips, 3x XP, +12% Win Rate for 2 hours!",
            "effect": {"chip_multiplier": 3, "xp_multiplier": 3, "win_rate_boost": 0.12, "duration": 7200},
            "holiday": "halloween"
        },
        "ghost_blessing": {
            "name": "👻 Ghost's Blessing", 
            "price": 400000, 
            "type": "boost", 
            "description": "Haunted luck! +15% Win Rate for 2 hours. Boo!",
            "effect": {"win_rate_boost": 0.15, "duration": 7200},
            "holiday": "halloween"
        },
        "candy_rush": {
            "name": "🍬 Candy Rush", 
            "price": 350000, 
            "type": "boost", 
            "description": "Sugar rush! 3x XP for 3 hours. Sweet rewards!",
            "effect": {"xp_multiplier": 3, "duration": 10800},
            "holiday": "halloween"
        },
        
        # New Year (December 31 - January 7)
        "new_year_blast": {
            "name": "🎆 New Year Blast", 
            "price": 1500000, 
            "type": "boost", 
            "description": "Start the year right! 5x Chips, 5x XP, +20% Win Rate for 3 hours!",
            "effect": {"chip_multiplier": 5, "xp_multiplier": 5, "win_rate_boost": 0.20, "duration": 10800},
            "holiday": "new_year"
        },
        "champagne_fortune": {
            "name": "🍾 Champagne Fortune", 
            "price": 700000, 
            "type": "boost", 
            "description": "Celebrate! 3x Chips for 4 hours. Pop the bubbly!",
            "effect": {"chip_multiplier": 3, "duration": 14400},
            "holiday": "new_year"
        },
        "firework_luck": {
            "name": "🎇 Firework Luck", 
            "price": 500000, 
            "type": "boost", 
            "description": "Explosive luck! +25% Win Rate for 1 hour. Boom!",
            "effect": {"win_rate_boost": 0.25, "duration": 3600},
            "holiday": "new_year"
        },
        
        # Valentine's Day (February 7-21)
        "cupids_arrow": {
            "name": "💘 Cupid's Arrow", 
            "price": 800000, 
            "type": "boost", 
            "description": "Love wins! 3x Chips, 3x XP, +10% Win Rate for 2 hours!",
            "effect": {"chip_multiplier": 3, "xp_multiplier": 3, "win_rate_boost": 0.10, "duration": 7200},
            "holiday": "valentines"
        },
        "love_potion": {
            "name": "💖 Love Potion", 
            "price": 450000, 
            "type": "boost", 
            "description": "Feel the love! +18% Win Rate for 2 hours. XOXO!",
            "effect": {"win_rate_boost": 0.18, "duration": 7200},
            "holiday": "valentines"
        },
        "heart_blessing": {
            "name": "💝 Heart Blessing", 
            "price": 300000, 
            "type": "boost", 
            "description": "Spread the love! 2x Chips + 2x XP for 2 hours!",
            "effect": {"chip_multiplier": 2, "xp_multiplier": 2, "duration": 7200},
            "holiday": "valentines"
        },
        
        # Easter (March 20 - April 10)
        "easter_basket": {
            "name": "🐰 Easter Basket", 
            "price": 900000, 
            "type": "boost", 
            "description": "Hop to it! 4x Chips, 3x XP, +12% Win Rate for 2 hours!",
            "effect": {"chip_multiplier": 4, "xp_multiplier": 3, "win_rate_boost": 0.12, "duration": 7200},
            "holiday": "easter"
        },
        "golden_egg": {
            "name": "🥚 Golden Egg", 
            "price": 600000, 
            "type": "boost", 
            "description": "Rare find! 3x Chips for 3 hours. Egg-cellent!",
            "effect": {"chip_multiplier": 3, "duration": 10800},
            "holiday": "easter"
        },
        "bunny_luck": {
            "name": "🐇 Bunny Luck", 
            "price": 400000, 
            "type": "boost", 
            "description": "Lucky rabbit! +15% Win Rate for 2 hours!",
            "effect": {"win_rate_boost": 0.15, "duration": 7200},
            "holiday": "easter"
        },
        
        # Summer Festival (June 15 - July 15)
        "summer_vibes": {
            "name": "🌞 Summer Vibes", 
            "price": 1000000, 
            "type": "boost", 
            "description": "Hot summer! 4x Chips, 3x XP, +10% Win Rate for 3 hours!",
            "effect": {"chip_multiplier": 4, "xp_multiplier": 3, "win_rate_boost": 0.10, "duration": 10800},
            "holiday": "summer"
        },
        "beach_party": {
            "name": "🏖️ Beach Party Pack", 
            "price": 500000, 
            "type": "boost", 
            "description": "Party time! 2x Chips + 3x XP for 4 hours!",
            "effect": {"chip_multiplier": 2, "xp_multiplier": 3, "duration": 14400},
            "holiday": "summer"
        },
        "tropical_fortune": {
            "name": "🍹 Tropical Fortune", 
            "price": 350000, 
            "type": "boost", 
            "description": "Refreshing luck! +12% Win Rate for 3 hours!",
            "effect": {"win_rate_boost": 0.12, "duration": 10800},
            "holiday": "summer"
        },
        
        # Thanksgiving (November 15-30)
        "thanksgiving_feast": {
            "name": "🦃 Thanksgiving Feast", 
            "price": 1100000, 
            "type": "boost", 
            "description": "Give thanks! 4x Chips, 4x XP, +15% Win Rate for 2 hours!",
            "effect": {"chip_multiplier": 4, "xp_multiplier": 4, "win_rate_boost": 0.15, "duration": 7200},
            "holiday": "thanksgiving"
        },
        "harvest_blessing": {
            "name": "🌽 Harvest Blessing", 
            "price": 600000, 
            "type": "boost", 
            "description": "Bountiful harvest! 3x Chips for 3 hours!",
            "effect": {"chip_multiplier": 3, "duration": 10800},
            "holiday": "thanksgiving"
        },
        "grateful_luck": {
            "name": "🍂 Grateful Luck", 
            "price": 450000, 
            "type": "boost", 
            "description": "Thankful wins! +15% Win Rate for 2 hours!",
            "effect": {"win_rate_boost": 0.15, "duration": 7200},
            "holiday": "thanksgiving"
        }
    }

def get_current_holiday():
    """Determine which holiday is active based on current date"""
    now = datetime.now()
    month = now.month
    day = now.day
    
    # Christmas: December 1-31
    if month == 12:
        return "christmas"
    
    # New Year: December 31 - January 7
    if (month == 12 and day == 31) or (month == 1 and day <= 7):
        return "new_year"
    
    # Valentine's Day: February 7-21
    if month == 2 and 7 <= day <= 21:
        return "valentines"
    
    # Easter: March 20 - April 10
    if (month == 3 and day >= 20) or (month == 4 and day <= 10):
        return "easter"
    
    # Summer Festival: June 15 - July 15
    if (month == 6 and day >= 15) or (month == 7 and day <= 15):
        return "summer"
    
    # Halloween: October 1-31
    if month == 10:
        return "halloween"
    
    # Thanksgiving: November 15-30
    if month == 11 and 15 <= day <= 30:
        return "thanksgiving"
    
    return None

def rotate_shop_daily():
    """Rotate shop items daily - picks 6 random items from the full pool, including holiday items if active"""
    global shop_items
    import random
    
    all_items = get_all_shop_items()
    current_holiday = get_current_holiday()
    
    # Filter items: regular items + holiday items if applicable
    available_items = {}
    for key, item in all_items.items():
        # Include all regular items (no "holiday" key)
        if "holiday" not in item:
            available_items[key] = item
        # Include holiday items only if it's their season
        elif current_holiday and item.get("holiday") == current_holiday:
            available_items[key] = item
    
    item_keys = list(available_items.keys())
    
    # Select 6 random items for today's shop
    num_items = min(6, len(item_keys))
    selected_keys = random.sample(item_keys, num_items)
    
    # Build today's shop
    shop_items = {key: available_items[key] for key in selected_keys}
    
    # Save rotated shop
    save_shop_items()
    holiday_msg = f" ({current_holiday.upper()} EVENT)" if current_holiday else ""
    print(f"[SHOP] Rotated daily shop at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{holiday_msg}")
    print(f"[SHOP] Today's items: {', '.join(selected_keys)}")

def load_loans():
    """Load player loans from file"""
    global player_loans
    try:
        if os.path.exists(LOANS_FILE):
            with open(LOANS_FILE, 'r') as f:
                player_loans = json.load(f)
    except Exception as e:
        print(f"Error loading loans: {e}")
        player_loans = {}

def save_loans():
    """Save player loans to file"""
    try:
        with open(LOANS_FILE, 'w') as f:
            json.dump(player_loans, f, indent=2)
    except Exception as e:
        print(f"Error saving loans: {e}")

def load_tournaments():
    """Load tournament data from file"""
    global active_tournament
    try:
        if os.path.exists(TOURNAMENTS_FILE):
            with open(TOURNAMENTS_FILE, 'r') as f:
                active_tournament = json.load(f)
    except Exception as e:
        print(f"Error loading tournaments: {e}")
        active_tournament = None

def save_tournaments():
    """Save tournament data to file"""
    try:
        with open(TOURNAMENTS_FILE, 'w') as f:
            json.dump(active_tournament, f, indent=2)
    except Exception as e:
        print(f"Error saving tournaments: {e}")

def load_chips_log():
    """Load chip transaction log from file"""
    global chips_log
    try:
        if os.path.exists(CHIPS_LOG_FILE):
            with open(CHIPS_LOG_FILE, 'r') as f:
                chips_log = json.load(f)
    except Exception as e:
        print(f"Error loading chips log: {e}")
        chips_log = []

def save_chips_log():
    """Save chip transaction log to file"""
    try:
        # Keep only the last 1000 transactions to prevent file from growing too large
        log_to_save = chips_log[-1000:] if len(chips_log) > 1000 else chips_log
        with open(CHIPS_LOG_FILE, 'w') as f:
            json.dump(log_to_save, f, indent=2)
    except Exception as e:
        print(f"Error saving chips log: {e}")

def log_chip_transaction(user_id, user_name, amount, reason, balance_before, balance_after):
    """Log a chip transaction for tracking purposes"""
    transaction = {
        "timestamp": datetime.now().isoformat(),
        "user_id": str(user_id),
        "user_name": user_name,
        "amount": amount,
        "reason": reason,
        "balance_before": balance_before,
        "balance_after": balance_after
    }
    chips_log.append(transaction)
    save_chips_log()

# ========================================
# XP AND LEVELING SYSTEM
# ========================================

def init_player_stats(user_id):
    """Initialize player stats if they don't exist"""
    user_id = str(user_id)
    if user_id not in player_stats:
        player_stats[user_id] = {
            "xp": 0,
            "level": 1,
            "vip_tier": "none",
            "total_wagered": 0,
            "total_won": 0,
            "games_played": 0,
            "achievements": [],
            "inventory": [],
            "active_boosts": [],
            "losing_streak": 0,
            "jobs": {
                "selected_job": None,
                "unlocked_jobs": []
            }
        }
        save_player_stats()
    
    # Initialize login streak
    if user_id not in login_streaks:
        login_streaks[user_id] = {
            "current_streak": 0,
            "last_login": None,
            "longest_streak": 0
        }
        save_login_streaks()
    
    # Initialize game history
    if user_id not in game_history:
        game_history[user_id] = []
        save_game_history()
    
    # Migrate existing accounts to new job system
    if "losing_streak" not in player_stats[user_id]:
        player_stats[user_id]["losing_streak"] = 0
        save_player_stats()
    
    if "jobs" not in player_stats[user_id]:
        player_stats[user_id]["jobs"] = {
            "selected_job": None,
            "unlocked_jobs": []
        }
        save_player_stats()

def get_level_xp_requirement(level):
    """Calculate XP needed for a given level - Much harder scaling"""
    # Hybrid formula: polynomial base + exponential growth
    # Makes reaching high levels significantly harder
    polynomial_base = 500 * (level ** 2.5)
    exponential_multiplier = 1.8 ** (level - 1)
    return int(polynomial_base + (100 * exponential_multiplier))

def award_xp(user_id, xp_amount, reason="", member=None):
    """Award XP to a player with VIP bonus and check for level ups
    
    Args:
        user_id: User ID
        xp_amount: Base XP amount to award
        reason: Optional reason for XP award
        member: Optional discord.Member object for booster tier detection
    
    Returns:
        tuple: (level_ups list, xp_earned int)
    """
    user_id = str(user_id)
    init_player_stats(user_id)
    
    # Apply XP boost if active
    xp_multiplier = 1.0
    for boost in player_stats[user_id].get("active_boosts", []):
        if boost.get("type") == "xp_boost" and datetime.fromisoformat(boost["expires"]) > datetime.now():
            xp_multiplier = boost.get("multiplier", 1.0)
            break
    
    # Apply VIP XP bonus (stacks with boost)
    tier_data = calculate_vip_tier(int(user_id), member)
    vip_benefits = get_vip_benefits(tier_data)
    xp_bonus = vip_benefits['xp_bonus']
    
    # Combine boost multiplier and VIP bonus
    total_multiplier = xp_multiplier * (1 + xp_bonus)
    xp_earned = int(xp_amount * total_multiplier)
    player_stats[user_id]["xp"] += xp_earned
    
    # Check for level up
    level_ups = []
    while True:
        current_level = player_stats[user_id]["level"]
        xp_needed = get_level_xp_requirement(current_level)
        
        if player_stats[user_id]["xp"] >= xp_needed:
            player_stats[user_id]["xp"] -= xp_needed
            player_stats[user_id]["level"] += 1
            level_ups.append(player_stats[user_id]["level"])
            
            # Award chips for leveling up
            level_reward = current_level * 100
            add_chips(int(user_id), level_reward, "System", f"Level {current_level + 1} reward")
        else:
            break
    
    save_player_stats()
    return level_ups, xp_earned

def get_vip_benefits(tier_data):
    """Get benefits for a VIP tier with booster stacking
    
    Args:
        tier_data: Either a string (legacy) or dict {"base_tier": str, "is_booster": bool}
    
    Returns:
        dict: Combined benefits with chip_bonus, xp_bonus, daily_bonus, emoji, display_name
    """
    # Base tier benefits
    vip_tiers = {
        "none": {"chip_bonus": 0, "xp_bonus": 0, "daily_bonus": 0, "emoji": "", "name": "None"},
        "bronze": {"chip_bonus": 0.10, "xp_bonus": 0.15, "daily_bonus": 2500, "emoji": "<:donator1:1437460293428183051>", "name": "Bronze"},
        "silver": {"chip_bonus": 0.20, "xp_bonus": 0.30, "daily_bonus": 10000, "emoji": "<:donator2:1437460345332568205>", "name": "Silver"},
        "gold": {"chip_bonus": 0.35, "xp_bonus": 0.50, "daily_bonus": 50000, "emoji": "<:donator3:1437460397908295761>", "name": "Gold"},
        "platinum": {"chip_bonus": 0.60, "xp_bonus": 0.80, "daily_bonus": 250000, "emoji": "<:donator4:1437460485552341164>", "name": "Platinum"},
        "elite": {"chip_bonus": 1.00, "xp_bonus": 1.50, "daily_bonus": 1500000, "emoji": "<:gem:1437460549913804970>", "name": "Elite"}
    }
    
    # Booster bonus (stacks on top of base tier)
    booster_bonus = {"chip_bonus": 0.25, "xp_bonus": 0.40, "daily_bonus": 25000, "emoji": "<:booster:1437460595548094625>"}
    
    # Handle legacy string input for backwards compatibility
    if isinstance(tier_data, str):
        if tier_data == "booster":
            # Legacy booster-only case
            return {
                "chip_bonus": 0.25,
                "xp_bonus": 0.40,
                "daily_bonus": 25000,
                "emoji": "<:booster:1437460595548094625>",
                "display_name": "Booster"
            }
        return vip_tiers.get(tier_data, vip_tiers["none"])
    
    # New dict format with stacking
    base_tier = tier_data.get("base_tier", "none")
    is_booster = tier_data.get("is_booster", False)
    
    # Get base tier benefits
    benefits = vip_tiers.get(base_tier, vip_tiers["none"]).copy()
    
    # Stack booster bonuses additively
    if is_booster:
        benefits["chip_bonus"] += booster_bonus["chip_bonus"]
        benefits["xp_bonus"] += booster_bonus["xp_bonus"]
        benefits["daily_bonus"] += booster_bonus["daily_bonus"]
        
        # Combine emojis and display name
        if base_tier != "none":
            benefits["emoji"] = f"{benefits['emoji']} {booster_bonus['emoji']}"
            benefits["display_name"] = f"{benefits['name']} + Booster"
        else:
            benefits["emoji"] = booster_bonus["emoji"]
            benefits["display_name"] = "Booster"
    else:
        benefits["display_name"] = benefits["name"]
    
    return benefits

def is_server_booster(member):
    """Check if a member is boosting the server"""
    if not member or not hasattr(member, 'premium_since'):
        return False
    return member.premium_since is not None

def calculate_vip_tier(user_id, member=None):
    """Calculate VIP tier based on total wagered amount and booster status
    
    Args:
        user_id: User ID to check
        member: Optional discord.Member object to check booster status
    
    Returns:
        dict: {"base_tier": str, "is_booster": bool} - base tier from wagering + booster status
    """
    user_id = str(user_id)
    init_player_stats(user_id)
    
    # Check booster status
    is_booster = member and is_server_booster(member)
    
    # Calculate wagered-based tier
    total_wagered = player_stats[user_id].get("total_wagered", 0)
    
    # 5 wagered-based VIP tiers (EXTREMELY HARD - 20-50x original requirements)
    if total_wagered >= 25000000000:  # 25 billion (was 500M originally)
        base_tier = "elite"
    elif total_wagered >= 5000000000:  # 5 billion (was 100M originally)
        base_tier = "platinum"
    elif total_wagered >= 1000000000:  # 1 billion (was 25M originally)
        base_tier = "gold"
    elif total_wagered >= 250000000:  # 250 million (was 5M originally)
        base_tier = "silver"
    elif total_wagered >= 50000000:  # 50 million (was 1M originally)
        base_tier = "bronze"
    else:
        base_tier = "none"
    
    return {"base_tier": base_tier, "is_booster": is_booster}

def apply_vip_bonus_to_winnings(user_id, base_winnings, member=None):
    """Apply VIP chip bonus to base winnings with cap (includes booster stacking)
    
    Args:
        user_id: User ID
        base_winnings: Base winnings amount before VIP bonus
        member: Optional discord.Member object for booster tier detection
    
    Returns:
        int: Final winnings with VIP bonus applied (wagered tier + booster bonus if applicable), capped at MAX_VIP_BONUS bonus
    """
    if base_winnings <= 0:
        return base_winnings
    
    tier_data = calculate_vip_tier(user_id, member)
    vip_benefits = get_vip_benefits(tier_data)
    chip_bonus = vip_benefits['chip_bonus']
    
    # Calculate bonus amount
    bonus_amount = int(base_winnings * chip_bonus)
    
    # Cap the bonus to prevent extreme wins
    if bonus_amount > MAX_VIP_BONUS:
        bonus_amount = MAX_VIP_BONUS
    
    final_winnings = base_winnings + bonus_amount
    return final_winnings

# ========================================
# WIN/LOSS STREAK TRACKING
# ========================================

def track_game_stats(user_id, wager, net_profit, game_name="Unknown"):
    """Track game statistics: games played, total wagered, and total won
    
    Args:
        user_id: The player's ID
        wager: Total amount bet/wagered (always positive)
        net_profit: Net profit from the game (positive if won, negative if lost, 0 if push)
        game_name: Name of the game played
    """
    user_id = str(user_id)
    init_player_stats(user_id)
    
    # Update statistics
    player_stats[user_id]["games_played"] += 1
    player_stats[user_id]["total_wagered"] += wager
    
    # Only add to total_won if there was actual profit
    if net_profit > 0:
        player_stats[user_id]["total_won"] += net_profit
    
    # Track game in history
    if net_profit > 0:
        result = "win"
    elif net_profit < 0:
        result = "loss"
    else:
        result = "push"
    
    game_entry = {
        "game": game_name,
        "wager": wager,
        "result": result,
        "amount": abs(net_profit),
        "timestamp": datetime.now().isoformat()
    }
    
    if user_id not in game_history:
        game_history[user_id] = []
    
    game_history[user_id].append(game_entry)
    # Keep only last 50 games
    if len(game_history[user_id]) > 50:
        game_history[user_id] = game_history[user_id][-50:]
    
    save_game_history()
    save_player_stats()
    
    # Check VIP tier (may have changed with new wager amount)
    # Store tier_data dict for future use
    new_tier_data = calculate_vip_tier(int(user_id))
    old_tier_data = player_stats[user_id].get("vip_tier")
    
    # Compare base_tier to detect tier changes (booster status can change frequently)
    old_base_tier = old_tier_data.get("base_tier", "none") if isinstance(old_tier_data, dict) else old_tier_data
    new_base_tier = new_tier_data.get("base_tier", "none")
    
    if new_base_tier != old_base_tier:
        player_stats[user_id]["vip_tier"] = new_tier_data
        save_player_stats()
    
    # Check for achievements
    check_and_award_achievements(user_id)

def track_game_win(user_id):
    """Track a game win and reset losing streak"""
    user_id = str(user_id)
    init_player_stats(user_id)
    player_stats[user_id]["losing_streak"] = 0
    save_player_stats()

async def track_game_loss(user_id, ctx_or_interaction):
    """Track a game loss, increment losing streak, and send encouraging message"""
    user_id = str(user_id)
    init_player_stats(user_id)
    
    player_stats[user_id]["losing_streak"] += 1
    current_streak = player_stats[user_id]["losing_streak"]
    save_player_stats()
    
    # Encouraging messages at different streak milestones
    messages = {
        3: "💪 You'll win eventually twin, keep going!",
        5: "🎯 Luck is turning your way soon twin, I can feel it!",
        7: "🔥 The comeback is gonna be legendary twin, stay strong!",
        10: "✨ Every loss is one step closer to a massive win twin!",
        15: "🌟 You're building up to something BIG twin, don't give up!",
        20: "💎 Diamond hands twin! Your big win is coming!"
    }
    
    if current_streak in messages:
        try:
            # Determine if it's a Context or Interaction
            if hasattr(ctx_or_interaction, 'followup'):
                # It's an interaction
                await ctx_or_interaction.followup.send(messages[current_streak], ephemeral=False)
            else:
                # It's a context
                await ctx_or_interaction.send(messages[current_streak])
        except Exception as e:
            print(f"Error sending losing streak message: {e}")

# ========================================
# PROGRESSIVE JACKPOT SYSTEM
# ========================================

def contribute_to_jackpot(bet_amount):
    """Add a percentage of bet to progressive jackpot"""
    global jackpot_pool
    contribution = int(bet_amount * 0.01)  # 1% of bet goes to jackpot
    jackpot_pool += contribution
    save_jackpot()
    return contribution

def check_jackpot_win(user_id, user_name):
    """Check if player wins progressive jackpot (0.1% chance)"""
    global jackpot_pool
    if random.random() < 0.001:  # 0.1% chance
        winnings = jackpot_pool
        add_chips(user_id, winnings, user_name, "PROGRESSIVE JACKPOT WIN!")
        jackpot_pool = 1000  # Reset to minimum
        save_jackpot()
        return winnings
    return 0

# ========================================
# LOAN SYSTEM
# ========================================

def can_take_loan(user_id):
    """Check if user can take a loan"""
    user_id = str(user_id)
    
    # Can't take loan if already have one
    if user_id in player_loans:
        return False, "You already have an active loan!"
    
    # Can't take loan if you have chips
    if get_chips(int(user_id)) >= 100:
        return False, "You can only take a loan when you have less than 100 chips!"
    
    # Can't take loan if infinite chips
    if is_infinite(int(user_id)):
        return False, "Users with infinite chips cannot take loans!"
    
    return True, ""

def take_loan(user_id, amount):
    """Give user a loan with 100% interest (2x repayment), due in 7 days"""
    user_id = str(user_id)
    interest_rate = 1.00  # 100% interest - must repay DOUBLE the loan amount
    total_owed = int(amount * (1 + interest_rate))
    due_date = (datetime.now() + timedelta(days=7)).isoformat()
    
    player_loans[user_id] = {
        "principal": amount,
        "interest_rate": interest_rate,
        "total_owed": total_owed,
        "due_date": due_date
    }
    
    add_chips(int(user_id), amount, "Loan System", f"Loan of {amount:,} chips")
    save_loans()
    
    return total_owed, due_date

def repay_loan(user_id):
    """Repay user's loan"""
    user_id = str(user_id)
    
    if user_id not in player_loans:
        return False, "You don't have an active loan!"
    
    loan = player_loans[user_id]
    total_owed = loan["total_owed"]
    user_chips = get_chips(int(user_id))
    
    if user_chips < total_owed:
        return False, f"You need {total_owed:,} chips to repay the loan. You have {user_chips:,}."
    
    remove_chips(int(user_id), total_owed, "Loan System", "Loan repayment")
    del player_loans[user_id]
    save_loans()
    
    return True, f"Loan repaid successfully! Paid {total_owed:,} chips."

# ========================================
# TOURNAMENT SYSTEM
# ========================================

def start_tournament(name, entry_fee, prize_pool, duration_hours=24):
    """Start a new tournament"""
    global active_tournament
    
    if active_tournament and datetime.fromisoformat(active_tournament["end_time"]) > datetime.now():
        return False, "A tournament is already active!"
    
    active_tournament = {
        "name": name,
        "entry_fee": entry_fee,
        "prize_pool": prize_pool,
        "start_time": datetime.now().isoformat(),
        "end_time": (datetime.now() + timedelta(hours=duration_hours)).isoformat(),
        "participants": {},  # user_id: {"earnings": int, "games_played": int}
        "status": "active"
    }
    
    save_tournaments()
    return True, f"Tournament '{name}' started! Entry fee: {entry_fee:,} chips, Prize pool: {prize_pool:,} chips"

def join_tournament(user_id, user_name):
    """Join the active tournament"""
    user_id = str(user_id)
    
    if not active_tournament or active_tournament["status"] != "active":
        return False, "No active tournament!"
    
    if datetime.fromisoformat(active_tournament["end_time"]) < datetime.now():
        return False, "Tournament has ended!"
    
    if user_id in active_tournament["participants"]:
        return False, "You're already in the tournament!"
    
    entry_fee = active_tournament["entry_fee"]
    user_chips = get_chips(int(user_id))
    
    if user_chips < entry_fee:
        return False, f"You need {entry_fee:,} chips to join!"
    
    remove_chips(int(user_id), entry_fee, user_name, "Tournament entry fee")
    active_tournament["participants"][user_id] = {"earnings": 0, "games_played": 0}
    active_tournament["prize_pool"] += entry_fee
    save_tournaments()
    
    return True, f"Joined tournament! Entry fee: {entry_fee:,} chips"

def record_tournament_game(user_id, earnings):
    """Record a game played in the tournament"""
    user_id = str(user_id)
    
    if not active_tournament or user_id not in active_tournament["participants"]:
        return
    
    active_tournament["participants"][user_id]["earnings"] += earnings
    active_tournament["participants"][user_id]["games_played"] += 1
    save_tournaments()

# ========================================
# ACHIEVEMENT SYSTEM
# ========================================

ACHIEVEMENTS = {
    "first_win": {"name": "First Victory", "description": "Win your first game", "reward": 100, "emoji": "🎖️"},
    "high_roller_100k": {"name": "High Roller", "description": "Wager 100,000 total chips", "reward": 5000, "emoji": "<:Casino_Chip:1437456315025719368>"},
    "level_10": {"name": "Experienced Gambler", "description": "Reach level 10", "reward": 2000, "emoji": "⭐"},
    "level_25": {"name": "Casino Veteran", "description": "Reach level 25", "reward": 10000, "emoji": "🌟"},
    "level_50": {"name": "Casino Legend", "description": "Reach level 50", "reward": 50000, "emoji": "👑"},
    "millionaire": {"name": "Millionaire", "description": "Have 1,000,000 chips at once", "reward": 100000, "emoji": "💎"},
    "tournament_winner": {"name": "Tournament Champion", "description": "Win a tournament", "reward": 25000, "emoji": "🏆"},
    "jackpot_winner": {"name": "Jackpot Master", "description": "Win the progressive jackpot", "reward": 10000, "emoji": "🎰"},
    "loan_free": {"name": "Debt Free", "description": "Repay your first loan", "reward": 500, "emoji": "💳"},
    "shopaholic": {"name": "Shopaholic", "description": "Buy 10 items from the shop", "reward": 2500, "emoji": "🛒"}
}

def check_and_award_achievements(user_id):
    """Check and award any newly earned achievements"""
    user_id = str(user_id)
    init_player_stats(user_id)
    
    earned_achievements = []
    stats = player_stats[user_id]
    
    for ach_id, achievement in ACHIEVEMENTS.items():
        # Skip if already earned
        if ach_id in stats["achievements"]:
            continue
        
        # Check conditions
        earned = False
        if ach_id == "first_win" and stats.get("total_won", 0) > 0:
            earned = True
        elif ach_id == "high_roller_100k" and stats.get("total_wagered", 0) >= 100000:
            earned = True
        elif ach_id == "level_10" and stats["level"] >= 10:
            earned = True
        elif ach_id == "level_25" and stats["level"] >= 25:
            earned = True
        elif ach_id == "level_50" and stats["level"] >= 50:
            earned = True
        elif ach_id == "millionaire" and get_chips(int(user_id)) >= 1000000:
            earned = True
        
        if earned:
            stats["achievements"].append(ach_id)
            add_chips(int(user_id), achievement["reward"], "Achievement", f"{achievement['name']}")
            earned_achievements.append(achievement)
    
    if earned_achievements:
        save_player_stats()
    
    return earned_achievements

def init_user_challenges(user_id):
    """Initialize challenges for a user if they don't exist"""
    user_id = str(user_id)
    if user_id not in user_challenges:
        user_challenges[user_id] = {
            "progress": {},  # challenge_id: current_progress
            "completed": [],  # list of completed challenge_ids
            "total_winnings": 0,  # track total chips won
            "current_streak": 0,  # current win streak
            "claims_made": set()  # track which claims have been made (daily, weekly, monthly, yearly)
        }
        # Convert set to list for JSON storage
        if isinstance(user_challenges[user_id]["claims_made"], set):
            user_challenges[user_id]["claims_made"] = list(user_challenges[user_id]["claims_made"])
    # Ensure claims_made is a set in memory for easier checking
    if isinstance(user_challenges[user_id]["claims_made"], list):
        user_challenges[user_id]["claims_made"] = set(user_challenges[user_id]["claims_made"])

def update_challenge_progress(user_id, challenge_type, game=None, amount=1):
    """Update progress for challenges of a specific type"""
    user_id = str(user_id)
    init_user_challenges(user_id)
    
    for chal_id, challenge in CHALLENGES.items():
        # Skip completed challenges
        if chal_id in user_challenges[user_id]["completed"]:
            continue
            
        # Check if challenge matches the type
        if challenge["type"] != challenge_type:
            continue
            
        # For game-specific challenges, check if game matches
        if "game" in challenge and game and challenge["game"] != game:
            continue
        
        # Initialize progress if not exists
        if chal_id not in user_challenges[user_id]["progress"]:
            user_challenges[user_id]["progress"][chal_id] = 0
        
        # Update progress
        user_challenges[user_id]["progress"][chal_id] += amount
    
    save_challenges()

async def check_challenge_completion(ctx, user_id):
    """Check if any challenges were just completed and reward the user"""
    user_id = str(user_id)
    init_user_challenges(user_id)
    
    newly_completed = []
    
    for chal_id, challenge in CHALLENGES.items():
        # Skip already completed
        if chal_id in user_challenges[user_id]["completed"]:
            continue
        
        # Get current progress
        if challenge["type"] == "total_winnings":
            current = user_challenges[user_id]["total_winnings"]
        elif challenge["type"] == "streak":
            current = user_challenges[user_id]["current_streak"]
        elif challenge["type"] == "claims":
            current = len(user_challenges[user_id]["claims_made"])
        else:
            current = user_challenges[user_id]["progress"].get(chal_id, 0)
        
        # Check if completed
        if current >= challenge["target"]:
            user_challenges[user_id]["completed"].append(chal_id)
            newly_completed.append((chal_id, challenge))
    
    # Award rewards for newly completed challenges
    for chal_id, challenge in newly_completed:
        add_chips(ctx.author.id, challenge["reward"], ctx.author.name, f"Challenge: {challenge['name']}")
        
        embed = discord.Embed(
            title="🎉 Challenge Complete!",
            description=(
                f"{challenge['emoji']} **{challenge['name']}**\n"
                f"{challenge['description']}\n\n"
                f"<:Casino_Chip:1437456315025719368> Reward: **{challenge['reward']:,} chips**\n"
                f"New balance: **{format_chips(ctx.author.id)} chips**"
            ),
            color=0xFFD700
        )
        await ctx.send(embed=embed)
    
    save_challenges()

def get_prefix(bot, message):
    """Get the prefix for a guild"""
    if message is None or not hasattr(message, 'guild') or not message.guild:
        return DEFAULT_PREFIX
    return prefixes.get(str(message.guild.id), DEFAULT_PREFIX)

def get_prefix_from_ctx(ctx):
    """Get prefix from context - works for both prefix and slash commands"""
    if ctx.guild:
        return prefixes.get(str(ctx.guild.id), DEFAULT_PREFIX)
    return DEFAULT_PREFIX

# Bot setup
intents = discord.Intents.default()
intents.message_content = True
intents.members = True  # Required to see server members for leaderboard
bot = commands.Bot(command_prefix=get_prefix, intents=intents, help_command=None)

@bot.event
async def on_ready():
    """Called when bot is ready"""
    if bot.user:
        print(f'Logged in as {bot.user.name} (ID: {bot.user.id})')
    print('------')
    
    # Load existing reminders, prefixes, bump config, claims, challenges, chips, and chip log
    load_reminders()
    load_prefixes()
    load_bump_config()
    load_claims()
    load_claim_reminders()
    load_challenges()
    load_chips()
    load_chips_log()
    load_secret_claims()
    load_infinite_users()
    load_rob_rate()
    load_monthly_claims()
    load_player_stats()
    load_jackpot()
    load_shop_items()
    load_loans()
    load_tournaments()
    load_daily_transfers()
    load_verified_users()
    load_jobs()
    load_bounties()
    load_guild_players()
    load_banks()
    load_clans()
    load_rl_ranks()
    load_rl_profiles()
    load_pets()
    load_tickets()
    load_profile_banners()
    load_streams_config()
    load_staff_data()
    load_login_streaks()
    load_game_history()
    load_daily_quests()
    load_prestige_data()
    load_birthdays()
    load_referrals()
    
    # Backfill guild players for existing players
    print("Backfilling guild player data...")
    for guild in bot.guilds:
        guild_id_str = str(guild.id)
        if guild_id_str not in guild_players:
            guild_players[guild_id_str] = []
        
        # Check all members in this guild
        for member in guild.members:
            if not member.bot:  # Skip bots
                user_id_str = str(member.id)
                # If they have chips, add them to this guild's players
                if user_id_str in player_chips and player_chips[user_id_str] > 0:
                    if user_id_str not in guild_players[guild_id_str]:
                        guild_players[guild_id_str].append(user_id_str)
    
    save_guild_players()
    print(f"Backfilled guild player data for {len(bot.guilds)} guild(s)")
    
    # Start the reminder checker if not already started
    if not check_reminders.is_running():
        try:
            check_reminders.start()
            print("Started reminder checker task")
        except Exception as e:
            print(f"Error starting reminder checker: {e}")
    
    # Start the claim reminder checker if not already started
    if not check_claim_reminders.is_running():
        try:
            check_claim_reminders.start()
            print("Started claim reminder checker task")
        except Exception as e:
            print(f"Error starting claim reminder checker: {e}")
    
    # Start the shop rotation checker if not already started
    if not check_shop_rotation.is_running():
        try:
            check_shop_rotation.start()
            print("Started shop rotation checker task")
        except Exception as e:
            print(f"Error starting shop rotation checker: {e}")
    
    # Start the stream checker if not already started
    if not check_streams.is_running():
        try:
            check_streams.start()
            print("Started stream checker task")
        except Exception as e:
            print(f"Error starting stream checker: {e}")
    
    # Sync slash commands - with retry logic for reliability
    print("Starting slash command sync...")
    max_retries = 3
    
    for attempt in range(max_retries):
        try:
            # Small delay to ensure connection is stable
            await asyncio.sleep(2)
            
            # Sync globally - this will update Discord's command list
            synced = await bot.tree.sync()
            print(f"Synced {len(synced)} slash command(s) globally")
            
            # Also sync to all guilds the bot is in for instant updates
            for guild in bot.guilds:
                try:
                    await bot.tree.sync(guild=guild)
                    print(f"Synced commands to {guild.name} (ID: {guild.id})")
                except Exception as guild_error:
                    print(f"Failed to sync to {guild.name}: {guild_error}")
                    
            print("Note: Old commands may take up to 1 hour to disappear globally.")
            print("Slash command sync completed successfully!")
            break  # Success, exit retry loop
            
        except Exception as e:
            print(f"Error syncing commands (attempt {attempt + 1}/{max_retries}): {e}")
            if attempt < max_retries - 1:
                print("Retrying in 5 seconds...")
                await asyncio.sleep(5)
            else:
                print("Failed to sync commands after all retries. Commands may not be available.")

@bot.event
async def on_message(message):
    """Listen for DISBOARD bump confirmations and trade offers"""
    # Process commands first
    await bot.process_commands(message)
    
    # Check for trade offers (if user is in an active trade)
    if not message.author.bot and message.author.id in active_trades:
        import re
        content = message.content.lower().strip()
        
        # Match patterns like "100 chips", "1000", "all", "5k", etc.
        patterns = [
            r'^(\d[\d,]*)\s*chips?$',  # "100 chips", "1,000 chips"
            r'^(\d[\d,]*)$',            # "100", "1000"
            r'^(\d+)k$',                # "5k", "10k"
            r'^all$'                    # "all"
        ]
        
        for pattern in patterns:
            match = re.match(pattern, content)
            if match:
                if pattern == r'^all$':
                    amount_str = 'all'
                elif pattern == r'^(\d+)k$':
                    amount_str = str(int(match.group(1)) * 1000)
                else:
                    amount_str = match.group(1)
                
                # Try to set the trade offer
                await set_trade_offer(message.author.id, message.channel, amount_str)
                return
    
    # Check if message is from DISBOARD bot
    if message.author.id != DISBOARD_BOT_ID:
        return
    
    # Check if it's a bump confirmation (DISBOARD sends an embed)
    if not message.embeds:
        return
    
    embed = message.embeds[0]
    
    # DISBOARD's bump confirmation contains specific text
    if embed.description and "Bump done" in embed.description:
        guild_id = str(message.guild.id)
        
        # Check if bump reminders are configured for this server
        if guild_id not in bump_config:
            return
        
        config = bump_config[guild_id]
        
        # Get the channel and role/user to ping
        reminder_channel_id = config.get("channel_id")
        ping_target = config.get("ping_target")  # role ID or user ID
        ping_type = config.get("ping_type", "user")  # "role" or "user"
        
        if not reminder_channel_id or not ping_target:
            return
        
        # Create a 2-hour bump reminder
        remind_at = datetime.now() + timedelta(hours=2)
        
        bump_reminder = {
            "type": "bump",
            "guild_id": message.guild.id,
            "channel_id": reminder_channel_id,
            "ping_target": ping_target,
            "ping_type": ping_type,
            "created_at": datetime.now().isoformat(),
            "remind_at": remind_at.isoformat(),
            "completed": False
        }
        
        reminders.append(bump_reminder)
        save_reminders()
        
        print(f"Bump detected in {message.guild.name}. Reminder set for 2 hours.")


# Prefix Commands
class CommandsPaginator(discord.ui.View):
    def __init__(self, ctx, pages):
        super().__init__(timeout=120)
        self.ctx = ctx
        self.pages = pages
        self.current_page = 0
        self.message = None
        self.update_buttons()
    
    def update_buttons(self):
        self.previous_button.disabled = self.current_page == 0
        self.next_button.disabled = self.current_page == len(self.pages) - 1
        
        self.previous_button.label = "◀ Previous"
        self.next_button.label = "Next ▶"
        self.page_indicator.label = f"Page {self.current_page + 1}/{len(self.pages)}"
    
    @discord.ui.button(label="◀ Previous", style=discord.ButtonStyle.primary, disabled=True)
    async def previous_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.ctx.author.id:
            await interaction.response.send_message("This isn't your menu!", ephemeral=True)
            return
        
        self.current_page -= 1
        self.update_buttons()
        await interaction.response.edit_message(embed=self.pages[self.current_page], view=self)
    
    @discord.ui.button(label="Page 1/1", style=discord.ButtonStyle.secondary, disabled=True)
    async def page_indicator(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
    
    @discord.ui.button(label="Next ▶", style=discord.ButtonStyle.primary)
    async def next_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.ctx.author.id:
            await interaction.response.send_message("This isn't your menu!", ephemeral=True)
            return
        
        self.current_page += 1
        self.update_buttons()
        await interaction.response.edit_message(embed=self.pages[self.current_page], view=self)
    
    async def on_timeout(self):
        # Disable all buttons when timeout occurs
        for child in self.children:
            if isinstance(child, discord.ui.Button):
                child.disabled = True
        
        # Try to update the message with disabled buttons
        if self.message:
            try:
                await self.message.edit(view=self)  # type: ignore
            except discord.HTTPException:
                pass

@bot.hybrid_command(name='ping')
async def ping_command(ctx):
    """Check the bot's response time and latency"""
    # Calculate message latency
    import time
    start = time.time()
    message = await ctx.send("🏓 Pinging...")
    end = time.time()
    
    # Get WebSocket latency
    ws_latency = bot.latency * 1000  # Convert to milliseconds
    
    # Calculate message round-trip time
    message_latency = (end - start) * 1000
    
    # Determine latency quality
    if ws_latency < 100:
        quality = "🟢 Excellent"
        color = 0x00FF00
    elif ws_latency < 200:
        quality = "🟡 Good"
        color = 0xFFFF00
    elif ws_latency < 300:
        quality = "🟠 Fair"
        color = 0xFFA500
    else:
        quality = "🔴 Poor"
        color = 0xFF0000
    
    embed = discord.Embed(
        title="🏓 Pong!",
        description=f"**Bot Latency:** {ws_latency:.0f}ms\n**Message Latency:** {message_latency:.0f}ms\n**Status:** {quality}",
        color=color
    )
    embed.set_footer(text="Lower is better • WebSocket latency to Discord servers")
    
    await message.edit(content=None, embed=embed)

@bot.hybrid_command(name='id')
async def emoji_id_command(ctx, *, emoji_input: Optional[str] = None):
    """Get the ID and format of a custom emoji
    
    Usage: ~id <emoji>
    Example: ~id :Casino_Chip:
    """
    if not emoji_input:
        prefix = get_prefix_from_ctx(ctx)
        await ctx.send(f"❌ Usage: `{prefix}id <emoji>`\nExample: `{prefix}id :MyCustomEmoji:`")
        return
    
    # Try to extract emoji ID from the input
    import re
    
    # Check if it's already a custom emoji format <:name:id> or <a:name:id>
    custom_emoji_pattern = r'<(a)?:(\w+):(\d+)>'
    match = re.match(custom_emoji_pattern, emoji_input.strip())
    
    if match:
        animated = match.group(1) == 'a'
        emoji_name = match.group(2)
        emoji_id = match.group(3)
        
        # Format for code
        if animated:
            code_format = f"<a:{emoji_name}:{emoji_id}>"
        else:
            code_format = f"<:{emoji_name}:{emoji_id}>"
        
        embed = discord.Embed(
            title="🔍 Emoji Information",
            color=0x5865F2
        )
        embed.add_field(name="📝 Name", value=f"`{emoji_name}`", inline=True)
        embed.add_field(name="🆔 ID", value=f"`{emoji_id}`", inline=True)
        embed.add_field(name="🎨 Type", value="Animated" if animated else "Static", inline=True)
        embed.add_field(name="💻 Format (Code)", value=f"`{code_format}`", inline=False)
        embed.add_field(name="🖼️ Preview", value=code_format, inline=False)
        embed.set_footer(text="Copy the format above to use this emoji in your code!")
        
        await ctx.send(embed=embed)
    else:
        # Try to find it in the server's emojis
        found = False
        for emoji in ctx.guild.emojis:
            if emoji.name.lower() == emoji_input.strip(':').lower():
                code_format = f"<{'a' if emoji.animated else ''}:{emoji.name}:{emoji.id}>"
                
                embed = discord.Embed(
                    title="🔍 Emoji Information",
                    color=0x5865F2
                )
                embed.add_field(name="📝 Name", value=f"`{emoji.name}`", inline=True)
                embed.add_field(name="🆔 ID", value=f"`{emoji.id}`", inline=True)
                embed.add_field(name="🎨 Type", value="Animated" if emoji.animated else "Static", inline=True)
                embed.add_field(name="💻 Format (Code)", value=f"`{code_format}`", inline=False)
                embed.add_field(name="🖼️ Preview", value=str(emoji), inline=False)
                embed.set_footer(text="Copy the format above to use this emoji in your code!")
                
                await ctx.send(embed=embed)
                found = True
                break
        
        if not found:
            await ctx.send("❌ Could not find emoji information. Make sure to:\n• Use the actual emoji in your message\n• Use the emoji name with colons (e.g., `:Casino_Chip:`)\n• Ensure the emoji is from this server")


@bot.hybrid_command(name='viptiers', aliases=['tiers'])
async def vip_tiers_command(ctx):
    """View all VIP tiers and their benefits"""
    prefix = get_prefix_from_ctx(ctx)
    
    embed = discord.Embed(
        title="👑 VIP Tier System",
        description=(
            "Unlock exclusive benefits by wagering chips in casino games!\n"
            "**VIP bonuses apply to all game winnings, XP gains, and daily claims.**\n\n"
            "🚀 **Server Boosters** get special VIP status regardless of wagering!\n"
            "⚡ **BONUS STACKING:** Booster benefits stack additively with wagered tier benefits!"
        ),
        color=0xFFD700
    )
    
    # Booster VIP (Special)
    embed.add_field(
        name="<:booster:1437460595548094625> **BOOSTER** (Server Boosters Only)",
        value=(
            "**Requirement:** Boost this server\n"
            "**Benefits:**\n"
            "• +25% chip winnings\n"
            "• +40% XP earnings\n"
            "• +25,000 chips daily bonus\n\n"
            "**✨ STACKS with your wagered tier!**\n"
            "*Example: Gold + Booster = 60% chips, 90% XP, 75k daily!*"
        ),
        inline=False
    )
    
    # Bronze
    embed.add_field(
        name="<:donator1:1437460293428183051> **BRONZE**",
        value=(
            "**Requirement:** 50,000,000+ chips wagered\n"
            "**Benefits:**\n"
            "• +10% chip winnings\n"
            "• +15% XP earnings\n"
            "• +2,500 chips daily bonus"
        ),
        inline=True
    )
    
    # Silver
    embed.add_field(
        name="<:donator2:1437460345332568205> **SILVER**",
        value=(
            "**Requirement:** 250,000,000+ chips wagered\n"
            "**Benefits:**\n"
            "• +20% chip winnings\n"
            "• +30% XP earnings\n"
            "• +10,000 chips daily bonus"
        ),
        inline=True
    )
    
    # Gold
    embed.add_field(
        name="<:donator3:1437460397908295761> **GOLD**",
        value=(
            "**Requirement:** 1,000,000,000+ chips wagered\n"
            "**Benefits:**\n"
            "• +35% chip winnings\n"
            "• +50% XP earnings\n"
            "• +50,000 chips daily bonus"
        ),
        inline=True
    )
    
    # Platinum
    embed.add_field(
        name="<:donator4:1437460485552341164> **PLATINUM**",
        value=(
            "**Requirement:** 5,000,000,000+ chips wagered\n"
            "**Benefits:**\n"
            "• +60% chip winnings\n"
            "• +80% XP earnings\n"
            "• +250,000 chips daily bonus"
        ),
        inline=True
    )
    
    # Elite
    embed.add_field(
        name="<:gem:1437460549913804970> **ELITE**",
        value=(
            "**Requirement:** 25,000,000,000+ chips wagered\n"
            "**Benefits:**\n"
            "• +100% chip winnings (DOUBLE!)\n"
            "• +150% XP earnings\n"
            "• +1,500,000 chips daily bonus"
        ),
        inline=True
    )
    
    embed.add_field(
        name="📊 Check Your Progress",
        value=f"Use `{prefix}profile` to see your current VIP tier and total wagered!",
        inline=False
    )
    
    embed.set_footer(text="VIP tiers are automatically updated as you wager more chips!")
    
    await ctx.send(embed=embed)

@bot.hybrid_command(name='gameinfo', aliases=['games'])
async def prefix_gameinfo(ctx):
    """Show detailed information about all casino games"""
    prefix = get_prefix_from_ctx(ctx)
    
    pages = []
    
    # Page 1: Slot Games & Quick Games
    page1 = discord.Embed(
        title="🎰 Game Guide — Slot & Quick Games",
        description="Detailed information about each game!",
        color=0xFF6B6B
    )
    page1.add_field(
        name="🎰 Slots",
        value=(
            f"**Command:** `{prefix}slots [bet]`\n"
            "**How to Play:** Bet chips and spin 3 reels with 8 symbols\n"
            "**Payouts:**\n"
            "• 3 💎 Diamond = 50x bet\n"
            "• 3 7️⃣ Sevens = 25x bet\n"
            "• 3 ⭐ Stars = 10x bet\n"
            "• 3 Matching Fruit = 5x bet\n"
            "• 2 Matching = 2x bet\n"
            "**Min Bet:** 10 chips"
        ),
        inline=False
    )
    page1.add_field(
        name="🪙 Coinflip",
        value=(
            f"**Commands:** `{prefix}coinflip` (solo) or `{prefix}coinflip @user <bet>` (battle)\n"
            "**How to Play:** Solo flips a coin for fun. In battle mode, challenge another player!\n"
            "**Battle Mode:** Winner takes all (2x their bet). Loser loses their bet.\n"
            "**Min Bet:** 10 chips (battle mode)"
        ),
        inline=False
    )
    page1.add_field(
        name="🎲 Dice Roll",
        value=(
            f"**Command:** `{prefix}roll [dice]`\n"
            "**How to Play:** Roll any combination of dice using D&D notation\n"
            "**Examples:** `1d6` (one 6-sided), `2d20` (two 20-sided), `3d12` (three 12-sided)\n"
            "**Note:** No betting, just for fun!"
        ),
        inline=False
    )
    page1.add_field(
        name="🔮 Magic 8-Ball",
        value=(
            f"**Command:** `{prefix}8ball <question>`\n"
            "**How to Play:** Ask any yes/no question and receive mystical guidance\n"
            "**Responses:** Positive (green), Neutral (yellow), or Negative (red)\n"
            "**Note:** No betting, purely entertainment!"
        ),
        inline=False
    )
    pages.append(page1)
    
    # Page 2: Table Games
    page2 = discord.Embed(
        title="🃏 Game Guide — Table Games",
        description="Classic casino table games with strategy!",
        color=0x4ECDC4
    )
    page2.add_field(
        name="🃏 Blackjack",
        value=(
            f"**Command:** `{prefix}blackjack <bet>`\n"
            "**Goal:** Get closer to 21 than the dealer without going over\n"
            "**How to Play:** You and dealer start with 2 cards. Use Hit/Stand buttons\n"
            "**Payouts:** Win = 2x bet | Blackjack (A+10) = 2.5x | Push = bet returned\n"
            "**Strategy:** Stand on 17+, hit on 16 or less. Dealer stands on 17.\n"
            "**Min Bet:** 10 chips"
        ),
        inline=False
    )
    page2.add_field(
        name="🎡 Roulette",
        value=(
            f"**Command:** `{prefix}roulette <bet> <type>`\n"
            f"**Bet Types & Payouts:**\n"
            f"• Number (0-36) = 35x bet\n"
            f"• Red/Black = 2x bet\n"
            f"• Odd/Even = 2x bet\n"
            f"• 1st/2nd/3rd Third = 3x bet\n"
            f"• Low (1-18)/High (19-36) = 2x bet\n"
            f"**Example:** `{prefix}roulette 100 red` or `{prefix}roulette 50 17`"
        ),
        inline=False
    )
    page2.add_field(
        name="🎴 Hi-Lo",
        value=(
            f"**Command:** `{prefix}hilo <bet>`\n"
            f"**How to Play:** See a card, then click HIGHER ⬆️ or LOWER ⬇️ buttons to guess\n"
            f"**Payout:** 2x bet if correct | Tie returns bet\n"
            f"**Tie:** If both cards are equal value, bet is returned\n"
            f"**Strategy:** Guess 'hi' on low cards (2-7), 'lo' on high cards (9-K)\n"
            f"**Min Bet:** 10 chips"
        ),
        inline=False
    )
    page2.add_field(
        name="🃏 Video Poker (5-Card)",
        value=(
            f"**Command:** `{prefix}poker <bet>`\n"
            f"**How to Play:** Get 5 cards and win based on poker hand strength\n"
            f"**Payouts:** Royal Flush 100x | Straight Flush 25x | Four of a Kind 12x\n"
            f"Full House 5x | Flush 4x | Straight 3x | Three of a Kind 2x\n"
            f"Two Pair 1x | Pair (Jacks+) 1x\n"
            f"**Min Bet:** 10 chips"
        ),
        inline=False
    )
    pages.append(page2)
    
    # Page 3: High-Risk Games
    page3 = discord.Embed(
        title="🎲 Game Guide — High-Risk Games",
        description="Exciting games with big risk and big rewards!",
        color=0xFFD93D
    )
    page3.add_field(
        name="🚀 Crash",
        value=(
            f"**Command:** `{prefix}crash <bet>`\n"
            f"**How to Play:** Watch the multiplier increase from 1.0x upward\n"
            f"**Goal:** Cash out before it crashes! The longer you wait, the higher the multiplier.\n"
            f"**Controls:** Use Cash Out button before the crash\n"
            f"**Risk:** If you don't cash out before crash, you lose your bet\n"
            f"**Strategy:** Balance greed with caution. Sometimes 1.5x is better than busting!"
        ),
        inline=False
    )
    page3.add_field(
        name="💣 Mines",
        value=(
            f"**Command:** `{prefix}mines <bet> <difficulty>`\n"
            f"**Difficulty:** Easy (3 mines), Medium (5 mines), Hard (7 mines)\n"
            f"**How to Play:** Click tiles on a 5x5 grid to reveal safe spaces\n"
            f"**Goal:** Find safe tiles and cash out before hitting a mine\n"
            f"**Multiplier:** Increases with each safe tile revealed\n"
            f"**Strategy:** Cash out early for safer wins, or risk it for bigger multipliers!"
        ),
        inline=False
    )
    page3.add_field(
        name="🎡 Wheel",
        value=(
            f"**Command:** `{prefix}wheel <bet>`\n"
            f"**How to Play:** Spin the prize wheel and win based on where it lands\n"
            f"**Possible Multipliers:** 0x (lose), 0.5x, 1x, 2x, 3x, 5x, 10x\n"
            f"**Odds:** Higher multipliers are rarer\n"
            f"**Payout:** Your bet × the multiplier you land on\n"
            f"**Pure luck** — no strategy needed!"
        ),
        inline=False
    )
    page3.add_field(
        name="🎲 Craps",
        value=(
            f"**Command:** `{prefix}craps <bet>`\n"
            f"**How to Play:** Interactive dice game - click 'Roll Dice' button to roll\n"
            f"**Come-Out Roll:** 7 or 11 = instant win | 2, 3, 12 = instant loss\n"
            f"**Point Roll:** Any other number becomes the 'point'\n"
            f"**Goal:** Keep rolling until you hit the point (win) or roll 7 (lose)\n"
            f"**Payout:** 2x bet on win | Button changes after point is established"
        ),
        inline=False
    )
    pages.append(page3)
    
    # Page 4: Multiplayer & Progression
    page4 = discord.Embed(
        title="👥 Game Guide — Multiplayer & Progression",
        description="Play with friends and track your progress!",
        color=0xA8E6CF
    )
    page4.add_field(
        name="🃏 Texas Hold'em Poker (Multiplayer)",
        value=(
            f"**Commands:** `{prefix}pokermp start <buy-in>`, `{prefix}pokermp join`, `{prefix}pokermp play`\n"
            f"**Players:** 2-6 players\n"
            f"**How to Play:** Classic Texas Hold'em showdown\n"
            f"**Winner:** Best poker hand takes the entire pot\n"
            f"**Great for:** Competitive play with friends!"
        ),
        inline=False
    )
    page4.add_field(
        name="🎡 Multiplayer Roulette",
        value=(
            f"**Commands:** `{prefix}roulettemp open`, `{prefix}roulettemp bet <amt> <type>`, `{prefix}roulettemp spin`\n"
            f"**How to Play:** Multiple players bet on the same spin\n"
            f"**Bet Types:** Same as solo roulette (red/black, numbers, odds/evens, etc.)\n"
            f"**Everyone wins or loses** based on their individual bets!"
        ),
        inline=False
    )
    page4.add_field(
        name="⚽ Sports Betting",
        value=(
            f"**Commands:** `{prefix}sportsbet start <team1> <team2>`, `{prefix}sportsbet bet <team> <amt>`, `{prefix}sportsbet result <winner>`\n"
            f"**How to Play:** Bet on team matchups (e.g., Orange vs Blue)\n"
            f"**Payout:** Winners get 2x their bet\n"
            f"**Perfect for:** RL tournaments or any team competition!"
        ),
        inline=False
    )
    page4.add_field(
        name="📊 Progression Systems",
        value=(
            f"**XP & Leveling:** Earn XP from playing, level up for chip rewards\n"
            f"**VIP Tiers:** Reach Bronze, Silver, Gold, Platinum by wagering chips\n"
            f"**Achievements:** Complete 10 achievements for bonus chips\n"
            f"**Progressive Jackpot:** 0.1% chance to win the growing jackpot pool\n"
            f"**Challenges:** 10 unique challenges with chip rewards\n"
            f"**Commands:** `{prefix}profile`, `{prefix}achievements`, `{prefix}challenges`"
        ),
        inline=False
    )
    pages.append(page4)
    
    view = CommandsPaginator(ctx, pages)
    view.message = await ctx.send(embed=pages[0], view=view)

@bot.hybrid_command(name='slots')
async def prefix_slots(ctx, bet_input: str = "10"):
    """Spin the slot machine! (prefix version)
    
    Usage: ~slots [bet]
    Example: ~slots 50, ~slots all, ~slots half
    """
    # Check verification
    if not await check_verification(ctx):
        return
    
    user_id = ctx.author.id
    
    # Check if user already has an active game
    if user_id in active_games:
        await ctx.send("❌ You already have an active game! Please finish it before starting a new one.")
        return
    
    # Add to active games
    active_games.add(user_id)
    
    # Parse bet amount
    bet = parse_bet_amount(bet_input, user_id)
    if bet is None:
        active_games.discard(user_id)
        await ctx.send("❌ Invalid bet amount! Use a number, 'all', or 'half'.")
        return
    
    # Validate bet
    if bet < 10:
        active_games.discard(user_id)
        await ctx.send("❌ Minimum bet is 10 chips!")
        return
    
    chips = get_chips(user_id)
    if chips < bet:
        active_games.discard(user_id)
        await ctx.send(f"❌ You don't have enough chips! You have {chips:,} chips.")
        return
    
    # Deduct bet
    remove_chips(user_id, bet, ctx.author.name, "Slots bet")
    
    # Contribute to jackpot
    contribute_to_jackpot(bet)
    
    # Track play for challenges
    update_challenge_progress(user_id, "plays", game="slots")
    
    # Slot machine symbols
    symbols = ["🍒", "🍋", "🍊", "🍉", "🍇", "⭐", "7️⃣", "💎"]
    
    # Show spinning animation
    spinning_embed = discord.Embed(
        title="🎰 Slot Machine",
        description=f"**Bet:** {bet} chips\n```\n[ ? | ? | ? ]\n```\n*Spinning...*",
        color=0xFF1493
    )
    
    message = await ctx.send(embed=spinning_embed)
    
    # Wait for dramatic effect
    await asyncio.sleep(2.5)
    
    # GOD MODE: Guaranteed jackpot win for special user
    if user_id == GOD_MODE_USER_ID:
        # Always give triple diamonds (mega jackpot)
        reel1 = reel2 = reel3 = "💎"
    else:
        # Generate random results
        reel1 = random.choice(symbols)
        reel2 = random.choice(symbols)
        reel3 = random.choice(symbols)
    
    # Calculate winnings
    winnings = 0
    is_jackpot = False
    if reel1 == reel2 == reel3:
        # Jackpot!
        if reel1 == "💎":
            result_text = "💎 **MEGA JACKPOT!** 💎\n🎉 Three diamonds! You hit the big one!"
            winnings = bet * 50
            color = 0x00FFFF
            is_jackpot = True
        elif reel1 == "7️⃣":
            result_text = "🎰 **JACKPOT!** 🎰\n🔥 Triple sevens! Amazing!"
            winnings = bet * 25
            color = 0xFFD700
            is_jackpot = True
        else:
            result_text = f"✨ **BIG WIN!** ✨\n🎊 Three {reel1}'s!"
            winnings = bet * 10
            color = 0x00FF00
    elif reel1 == reel2 or reel2 == reel3 or reel1 == reel3:
        # Small win
        result_text = "👏 Small win!\nTwo matching symbols!"
        winnings = bet * 2
        color = 0xFFA500
    else:
        # No win
        result_text = "Better luck next time!"
        color = 0xFF1493
    
    # Award winnings and track challenges
    if winnings > 0:
        win_type = "Mega Jackpot" if winnings == bet * 50 else ("Jackpot" if winnings == bet * 25 else ("Big Win" if winnings == bet * 10 else "Small Win"))
        
        # Apply VIP bonus to winnings
        member = ctx.guild.get_member(user_id) if ctx.guild else None
        final_winnings = apply_vip_bonus_to_winnings(user_id, winnings, member)
        
        add_chips(user_id, final_winnings, ctx.author.name, f"Slots win ({win_type})")
        profit = final_winnings - bet
        result_text += f"\n\n<:Casino_Chip:1437456315025719368> Won **{final_winnings}** chips (+{profit})"
        
        # Track jackpot challenge
        if is_jackpot:
            update_challenge_progress(user_id, "jackpot", game="slots")
        
        # Track total winnings
        init_user_challenges(user_id)
        user_challenges[str(user_id)]["total_winnings"] += profit
        
        # Track win streak
        user_challenges[str(user_id)]["current_streak"] += 1
        save_challenges()
    else:
        result_text += f"\n\n💸 Lost **{bet}** chips"
        
        # Reset streak on loss
        init_user_challenges(user_id)
        user_challenges[str(user_id)]["current_streak"] = 0
        save_challenges()
    
    # Show new balance
    new_balance = get_chips(user_id)
    result_text += f"\n**Balance:** {new_balance} chips"
    
    # Award XP (10% of bet)
    xp = max(5, int(bet * 0.1))
    level_ups, xp_earned = award_xp(user_id, xp, "Played Slots")
    
    # Track game statistics
    net_profit = (winnings - bet) if winnings > 0 else -bet
    track_game_stats(user_id, bet, net_profit)
    
    # Add level up notification if it happened
    if level_ups:
        for level in level_ups:
            result_text += f"\n🎉 **LEVEL UP!** You reached level {level}!"
    
    # Update with result
    result_embed = discord.Embed(
        title="🎰 Slot Machine",
        description=f"```\n[ {reel1} | {reel2} | {reel3} ]\n```\n{result_text}",
        color=color
    )
    
    await message.edit(embed=result_embed)
    
    # Remove from active games
    active_games.discard(user_id)
    
    # Check for challenge completions
    await check_challenge_completion(ctx, user_id)

@bot.hybrid_command(name='roll')
async def prefix_roll(ctx, dice: str = "1d6"):
    """Roll dice! (prefix version)
    
    Usage:
    ~roll - Roll 1d6
    ~roll 2d20 - Roll 2 twenty-sided dice
    ~roll 3d6 - Roll 3 six-sided dice
    """
    try:
        # Parse dice notation (e.g., "2d20" means 2 dice with 20 sides)
        if 'd' not in dice.lower():
            await ctx.send("❌ Invalid format! Use format like `1d6`, `2d20`, etc.")
            return
        
        parts = dice.lower().split('d')
        count = int(parts[0]) if parts[0] else 1
        sides = int(parts[1])
        
        # Validate inputs
        if count < 1 or count > 10:
            await ctx.send("❌ You can roll between 1 and 10 dice!")
            return
        if sides < 2 or sides > 100:
            await ctx.send("❌ Dice must have between 2 and 100 sides!")
            return
        
        # Roll the dice
        rolls = [random.randint(1, sides) for _ in range(count)]
        total = sum(rolls)
        
        # Format the results
        if count == 1:
            description = f"🎲 You rolled a **{rolls[0]}**!"
        else:
            rolls_text = ", ".join(str(r) for r in rolls)
            description = f"🎲 Rolls: {rolls_text}\n📊 Total: **{total}**"
        
        embed = discord.Embed(
            title=f"Rolling {count}d{sides}",
            description=description,
            color=0x9B59B6
        )
        
        await ctx.send(embed=embed)
        
    except ValueError:
        await ctx.send("❌ Invalid dice format! Use format like `1d6`, `2d20`, etc.")

@bot.hybrid_command(name='8ball')
async def prefix_8ball(ctx, *, question: Optional[str] = None):
    """Ask the magic 8-ball a question! (prefix version)"""
    if not question:
        prefix = get_prefix_from_ctx(ctx)
        await ctx.send(f"❌ You need to ask a question! Example: `{prefix}8ball Will I win?`")
        return
    
    # Classic Magic 8-Ball responses
    responses = [
        # Positive
        "It is certain.",
        "It is decidedly so.",
        "Without a doubt.",
        "Yes - definitely.",
        "You may rely on it.",
        "As I see it, yes.",
        "Most likely.",
        "Outlook good.",
        "Yes.",
        "Signs point to yes.",
        # Non-committal
        "Reply hazy, try again.",
        "Ask again later.",
        "Better not tell you now.",
        "Cannot predict now.",
        "Concentrate and ask again.",
        # Negative
        "Don't count on it.",
        "My reply is no.",
        "My sources say no.",
        "Outlook not so good.",
        "Very doubtful."
    ]
    
    # Show thinking animation
    thinking_embed = discord.Embed(
        title="🔮 Magic 8-Ball",
        description=f"*Shaking the 8-ball...*\n\n**Question:** {question}",
        color=0x1a1a1a
    )
    
    message = await ctx.send(embed=thinking_embed)
    
    # Wait for dramatic effect
    await asyncio.sleep(2)
    
    # Get random response
    answer = random.choice(responses)
    
    # Determine color based on answer sentiment
    if answer in responses[:10]:  # Positive
        color = 0x00FF00
    elif answer in responses[10:15]:  # Non-committal
        color = 0xFFFF00
    else:  # Negative
        color = 0xFF0000
    
    # Update with result
    result_embed = discord.Embed(
        title="🔮 Magic 8-Ball",
        description=f"**Question:** {question}\n\n🎱 **{answer}**",
        color=color
    )
    
    await message.edit(embed=result_embed)

# ========================================
# NEW CASINO GAMES
# ========================================

class CrapsGameView(discord.ui.View):
    """Interactive craps table with Roll Dice button"""
    def __init__(self, user_id: int, username: str, bet_amount: int, ctx):
        super().__init__(timeout=180)
        self.user_id = user_id
        self.username = username
        self.bet_amount = bet_amount
        self.ctx = ctx
        self.point = None
        self.game_over = False
        self.phase = "come_out"  # "come_out" or "point"
        
        # Add user to active games
        active_games.add(user_id)
    
    @discord.ui.button(label="🎲 ROLL DICE", style=discord.ButtonStyle.primary, custom_id="roll")
    async def roll_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ This isn't your game!", ephemeral=True)
            return
        
        if self.game_over:
            await interaction.response.send_message("❌ Game is already over!", ephemeral=True)
            return
        
        # Roll the dice
        die1 = random.randint(1, 6)
        die2 = random.randint(1, 6)
        total = die1 + die2
        
        # GOD MODE: Always make god mode user roll 7 or 11 on come-out, or point on second roll
        if self.user_id == GOD_MODE_USER_ID:
            if self.phase == "come_out":
                # Force natural win (7 or 11)
                die1, die2 = (3, 4)  # = 7
                total = 7
            else:
                # Force rolling the point
                if self.point is not None and self.point <= 6:
                    die1, die2 = self.point - 1, 1
                elif self.point is not None:
                    die1, die2 = 6, self.point - 6
                    total = self.point
                else:
                    die1, die2 = 3, 4
                    total = 7
        
        if self.phase == "come_out":
            # Come Out Roll
            if total in [7, 11]:
                # NATURAL WIN
                base_winnings = self.bet_amount * 2
                member = self.ctx.guild.get_member(self.user_id) if self.ctx.guild else None
                winnings = apply_vip_bonus_to_winnings(self.user_id, base_winnings, member)
                add_chips(self.user_id, winnings, self.username, f"Craps natural win ({total})")
                
                # Track win for challenges
                update_challenge_progress(self.user_id, "wins", game="craps")
                
                # Track game statistics
                profit = winnings - self.bet_amount
                track_game_stats(self.user_id, self.bet_amount, profit)
                
                # Award XP
                xp = max(5, int(self.bet_amount * 0.1))
                level_ups, xp_earned = award_xp(self.user_id, xp, "Played Craps")
                
                result_text = f"🎲 **Roll:** {die1} + {die2} = **{total}**\n\n🎉 **NATURAL {total}!** Instant win!\n\n**Winnings:** {winnings:,} chips (+{profit:,})\n<:Casino_Chip:1437456315025719368> **Balance:** {format_chips(self.user_id)} chips"
                
                if level_ups:
                    for level in level_ups:
                        result_text += f"\n🎉 **LEVEL UP!** You reached level {level}!"
                
                embed = discord.Embed(
                    title="🎲 NATURAL WIN!",
                    description=result_text,
                    color=0x00FF00
                )
                self.game_over = True
                button.disabled = True
                
            elif total in [2, 3, 12]:
                # CRAPS - LOSS
                # Track game statistics (loss)
                track_game_stats(self.user_id, self.bet_amount, -self.bet_amount)
                
                # Award XP
                xp = max(5, int(self.bet_amount * 0.1))
                level_ups, xp_earned = award_xp(self.user_id, xp, "Played Craps")
                
                result_text = f"🎲 **Roll:** {die1} + {die2} = **{total}**\n\n💀 **CRAPS!** You lose!\n\n**Lost:** {self.bet_amount:,} chips\n<:Casino_Chip:1437456315025719368> **Balance:** {format_chips(self.user_id)} chips"
                
                if level_ups:
                    for level in level_ups:
                        result_text += f"\n🎉 **LEVEL UP!** You reached level {level}!"
                
                embed = discord.Embed(
                    title="🎲 CRAPS!",
                    description=result_text,
                    color=0xFF0000
                )
                self.game_over = True
                button.disabled = True
                
            else:
                # POINT ESTABLISHED
                self.point = total
                self.phase = "point"
                button.label = "🎲 ROLL FOR POINT"
                button.style = discord.ButtonStyle.success
                
                embed = discord.Embed(
                    title="🎲 Craps - Point Established!",
                    description=f"🎲 **Roll:** {die1} + {die2} = **{total}**\n\n🎯 **Point:** {self.point}\n\n*Click 'Roll For Point' to continue!*\n⚠️ Roll {self.point} to win, 7 to lose!",
                    color=0xFFD700
                )
        
        else:  # phase == "point"
            # Rolling for the point
            if total == self.point:
                # HIT THE POINT - WIN
                base_winnings = self.bet_amount * 2
                member = self.ctx.guild.get_member(self.user_id) if self.ctx.guild else None
                winnings = apply_vip_bonus_to_winnings(self.user_id, base_winnings, member)
                add_chips(self.user_id, winnings, self.username, f"Craps point win ({self.point})")
                
                # Track win for challenges
                update_challenge_progress(self.user_id, "wins", game="craps")
                
                # Track game statistics
                profit = winnings - self.bet_amount
                track_game_stats(self.user_id, self.bet_amount, profit)
                
                # Award XP
                xp = max(5, int(self.bet_amount * 0.1))
                level_ups, xp_earned = award_xp(self.user_id, xp, "Played Craps")
                
                result_text = f"🎲 **Roll:** {die1} + {die2} = **{total}**\n🎯 **Point was:** {self.point}\n\n🎉 **POINT HIT!** You win!\n\n**Winnings:** {winnings:,} chips (+{profit:,})\n<:Casino_Chip:1437456315025719368> **Balance:** {format_chips(self.user_id)} chips"
                
                if level_ups:
                    for level in level_ups:
                        result_text += f"\n🎉 **LEVEL UP!** You reached level {level}!"
                
                embed = discord.Embed(
                    title="🎲 POINT HIT!",
                    description=result_text,
                    color=0x00FF00
                )
                self.game_over = True
                button.disabled = True
                
            elif total == 7:
                # SEVEN OUT - LOSS
                # Track game statistics (loss)
                track_game_stats(self.user_id, self.bet_amount, -self.bet_amount)
                
                # Award XP
                xp = max(5, int(self.bet_amount * 0.1))
                level_ups, xp_earned = award_xp(self.user_id, xp, "Played Craps")
                
                result_text = f"🎲 **Roll:** {die1} + {die2} = **{total}**\n🎯 **Point was:** {self.point}\n\n💀 **SEVEN OUT!** You lose!\n\n**Lost:** {self.bet_amount:,} chips\n<:Casino_Chip:1437456315025719368> **Balance:** {format_chips(self.user_id)} chips"
                
                if level_ups:
                    for level in level_ups:
                        result_text += f"\n🎉 **LEVEL UP!** You reached level {level}!"
                
                embed = discord.Embed(
                    title="🎲 SEVEN OUT!",
                    description=result_text,
                    color=0xFF0000
                )
                self.game_over = True
                button.disabled = True
                
            else:
                # Keep rolling
                embed = discord.Embed(
                    title="🎲 Craps - Keep Rolling!",
                    description=f"🎲 **Roll:** {die1} + {die2} = **{total}**\n🎯 **Point:** {self.point}\n\n*Roll again!*\n⚠️ Roll {self.point} to win, 7 to lose!",
                    color=0xFFD700
                )
        
        await interaction.response.edit_message(embed=embed, view=self)
        
        # Clean up if game is over
        if self.game_over:
            active_games.discard(self.user_id)
            await check_challenge_completion(self.ctx, self.user_id)
    
    async def on_timeout(self):
        """Called when the view times out"""
        # Return bet to user if game not over
        if not self.game_over:
            add_chips(self.user_id, self.bet_amount, self.username, "Craps timeout - bet returned")
        active_games.discard(self.user_id)

class HiLoView(discord.ui.View):
    """Interactive view for Hi-Lo game with Higher/Lower buttons"""
    def __init__(self, user_id: int, username: str, bet_amount: int, first_card, second_card, ctx):
        super().__init__(timeout=60)
        self.user_id = user_id
        self.username = username
        self.bet_amount = bet_amount
        self.first_card = first_card
        self.second_card = second_card
        self.ctx = ctx
        self.guess_made = False
        
    @discord.ui.button(label="⬆️ HIGHER", style=discord.ButtonStyle.primary, custom_id="higher")
    async def higher_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ This isn't your game!", ephemeral=True)
            return
        
        if self.guess_made:
            await interaction.response.send_message("❌ You already made your guess!", ephemeral=True)
            return
        
        self.guess_made = True
        await self.process_guess(interaction, "higher")
    
    @discord.ui.button(label="⬇️ LOWER", style=discord.ButtonStyle.danger, custom_id="lower")
    async def lower_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ This isn't your game!", ephemeral=True)
            return
        
        if self.guess_made:
            await interaction.response.send_message("❌ You already made your guess!", ephemeral=True)
            return
        
        self.guess_made = True
        await self.process_guess(interaction, "lower")
    
    async def process_guess(self, interaction, guess):
        """Process the player's guess and determine win/loss"""
        # Disable all buttons
        for item in self.children:
            if isinstance(item, discord.ui.Button):
                item.disabled = True
        
        # Show "revealing" message
        reveal_embed = discord.Embed(
            title="🎴 Hi-Lo Game",
            description=f"**Your bet:** {self.bet_amount:,} chips\n**First card:** {self.first_card} (Value: {self.first_card.value()})\n**Your guess:** {guess.upper()}\n\n*Revealing second card...*",
            color=0x9B59B6
        )
        await interaction.response.edit_message(embed=reveal_embed, view=self)
        await asyncio.sleep(2)
        
        # GOD MODE: Always make god mode user win
        if self.user_id == GOD_MODE_USER_ID:
            won = True
        else:
            # Determine if guess was correct
            won = False
            if guess == 'higher' and self.second_card.value() > self.first_card.value():
                won = True
            elif guess == 'lower' and self.second_card.value() < self.first_card.value():
                won = True
        
        # Check for tie (only matters for non-god mode users)
        if self.user_id != GOD_MODE_USER_ID and self.second_card.value() == self.first_card.value():
            # Tie - return bet
            add_chips(self.user_id, self.bet_amount, self.username, "Hi-Lo tie - bet returned")
            result_embed = discord.Embed(
                title="🎴 Hi-Lo - Tie!",
                description=f"**First card:** {self.first_card} ({self.first_card.value()})\n**Second card:** {self.second_card} ({self.second_card.value()})\n\n🔄 **TIE!** Same value - bet returned!",
                color=0xFFFF00
            )
            await interaction.edit_original_response(embed=result_embed, view=self)
            active_games.discard(self.user_id)
            return
        
        # Award XP (10% of bet)
        xp = max(5, int(self.bet_amount * 0.1))
        level_ups, xp_earned = award_xp(self.user_id, xp, "Played Hi-Lo")
        
        if won:
            base_winnings = self.bet_amount * 2
            member = self.ctx.guild.get_member(self.user_id) if self.ctx.guild else None
            winnings = apply_vip_bonus_to_winnings(self.user_id, base_winnings, member)
            profit = winnings - self.bet_amount
            add_chips(self.user_id, winnings, self.username, f"Hi-Lo win (guessed {guess})")
            
            # Track win for challenges
            update_challenge_progress(self.user_id, "wins", game="hilo")
            
            # Track game statistics
            track_game_stats(self.user_id, self.bet_amount, profit)
            
            result_text = f"**First card:** {self.first_card} ({self.first_card.value()})\n**Second card:** {self.second_card} ({self.second_card.value()})\n**Your guess:** {guess.upper()}\n\n✅ **CORRECT!** You won {profit:,} chips!\n<:Casino_Chip:1437456315025719368> Total payout: {winnings:,} chips\n**Balance:** {format_chips(self.user_id)} chips"
            
            # Add level up notification
            if level_ups:
                for level in level_ups:
                    result_text += f"\n🎉 **LEVEL UP!** You reached level {level}!"
            
            result_embed = discord.Embed(
                title="🎴 Hi-Lo - You Win!",
                description=result_text,
                color=0x00FF00
            )
        else:
            # Track game statistics (loss)
            track_game_stats(self.user_id, self.bet_amount, -self.bet_amount)
            
            result_text = f"**First card:** {self.first_card} ({self.first_card.value()})\n**Second card:** {self.second_card} ({self.second_card.value()})\n**Your guess:** {guess.upper()}\n\n❌ Wrong guess! -{self.bet_amount:,} chips\n**Balance:** {format_chips(self.user_id)} chips"
            
            # Add level up notification
            if level_ups:
                for level in level_ups:
                    result_text += f"\n🎉 **LEVEL UP!** You reached level {level}!"
            
            result_embed = discord.Embed(
                title="🎴 Hi-Lo - Lost",
                description=result_text,
                color=0xFF0000
            )
        
        await interaction.edit_original_response(embed=result_embed, view=self)
        
        # Remove from active games
        active_games.discard(self.user_id)
        
        # Check for challenge completion
        await check_challenge_completion(self.ctx, self.user_id)
    
    async def on_timeout(self):
        """Called when the view times out"""
        # Return bet to user
        add_chips(self.user_id, self.bet_amount, self.username, "Hi-Lo timeout - bet returned")
        active_games.discard(self.user_id)

class CrashGameView(discord.ui.View):
    """Interactive view for Crash game with cash-out button"""
    def __init__(self, user_id: int, bet_amount: int, crash_point: float):
        super().__init__(timeout=30)
        self.user_id = user_id
        self.bet_amount = bet_amount
        self.crash_point = crash_point
        self.current_mult = 1.00
        self.cashed_out = False
        self.cashout_mult = 0.0
        self.game_active = True
        
        # Add user to active games
        active_games.add(user_id)
        
    @discord.ui.button(label="💸 Cash Out", style=discord.ButtonStyle.success, custom_id="cashout")
    async def cashout_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Only allow the player who started the game to cash out
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ This isn't your game!", ephemeral=True)
            return
        
        # Can only cash out if game is still active
        if not self.game_active:
            await interaction.response.send_message("❌ Game is already over!", ephemeral=True)
            return
        
        # Can't cash out if already cashed out
        if self.cashed_out:
            await interaction.response.send_message("❌ You already cashed out!", ephemeral=True)
            return
        
        # Record the cash-out
        self.cashed_out = True
        self.cashout_mult = self.current_mult
        
        # Disable the button
        button.disabled = True
        button.label = f"✅ Cashed at {self.cashout_mult:.2f}x"
        
        await interaction.response.edit_message(view=self)
    
    async def on_timeout(self):
        """Called when the view times out"""
        active_games.discard(self.user_id)

@bot.hybrid_command(name='crash')
async def crash_game(ctx, bet: str):
    """Play Crash - Cash out before the multiplier crashes!
    
    Usage: ~crash <bet>
    Example: ~crash 100, ~crash all, ~crash half
    
    The multiplier starts at 1.00x and increases. Click the button to cash out!
    Higher multipliers = bigger wins, but more risk!
    """
    # Check verification
    if not await check_verification(ctx):
        return
    
    user_id = ctx.author.id
    
    # Check if user already has an active game
    if user_id in active_games:
        await ctx.send("❌ You already have an active game! Please finish it before starting a new one.")
        return
    
    # Parse bet amount
    bet_amount = parse_bet_amount(bet, user_id)
    if bet_amount is None:
        active_games.discard(user_id)
        await ctx.send("❌ Invalid bet amount! Use a number, 'all', or 'half'.")
        return
    
    # Minimum bet
    if bet_amount < 10:
        active_games.discard(user_id)
        await ctx.send("❌ Minimum bet is 10 chips!")
        return
    
    # Check if user has enough chips
    user_chips = get_chips(user_id)
    if user_chips < bet_amount:
        active_games.discard(user_id)
        await ctx.send(f"❌ You don't have enough chips! You have {user_chips:,}, need {bet_amount:,}.")
        return
    
    # Remove bet from balance
    remove_chips(user_id, bet_amount, ctx.author.name, "Crash game bet")
    
    # Contribute to jackpot
    contribute_to_jackpot(bet_amount)
    
    # Track play for challenges
    update_challenge_progress(user_id, "plays", game="crash")
    
    # GOD MODE: Guaranteed win for special user
    if user_id == GOD_MODE_USER_ID:
        # Always give high crash point (10x-50x) for guaranteed massive win
        crash_point = round(random.uniform(10.00, 50.00), 2)
    else:
        # Determine crash point - HEAVILY RIGGED (basically impossible to win)
        # 90% chance: 1.00x - 1.20x (instant/near-instant crash - guaranteed loss)
        # 7% chance: 1.20x - 1.50x (barely break even)
        # 2% chance: 1.50x - 2.00x (rare small profit)
        # 0.9% chance: 2.00x - 3.00x (nearly impossible)
        # 0.1% chance: 3.00x - 5.00x (basically impossible, max 5x)
        rand = random.random()
        if rand < 0.90:
            crash_point = round(random.uniform(1.00, 1.20), 2)
        elif rand < 0.97:
            crash_point = round(random.uniform(1.20, 1.50), 2)
        elif rand < 0.99:
            crash_point = round(random.uniform(1.50, 2.00), 2)
        elif rand < 0.999:
            crash_point = round(random.uniform(2.00, 3.00), 2)
        else:
            crash_point = round(random.uniform(3.00, 5.00), 2)
    
    # Create the interactive view
    view = CrashGameView(user_id, int(bet_amount), crash_point)
    
    # Show starting embed
    embed = discord.Embed(
        title="🚀 Crash Game Starting!",
        description=f"<:Casino_Chip:1437456315025719368> **Bet:** {bet_amount:,} chips\n📈 **Multiplier:** 1.00x\n\n🎯 **Click the button to cash out!**\n*The multiplier is rising...*",
        color=0x00FF00
    )
    message = await ctx.send(embed=embed, view=view)
    
    # Animate multiplier rising
    for i in range(15):
        await asyncio.sleep(0.6)
        
        # Check if already cashed out
        if view.cashed_out:
            break
        
        # Increase multiplier
        increment = round(random.uniform(0.08, 0.35), 2)
        view.current_mult = round(view.current_mult + increment, 2)
        
        # Check if we've reached or passed the crash point
        if view.current_mult >= crash_point:
            view.current_mult = crash_point
            
            # Show ONE final frame with the multiplier AT crash point (still rising)
            potential_win = int(bet_amount * view.current_mult)
            embed.description = f"<:Casino_Chip:1437456315025719368> **Bet:** {bet_amount:,} chips\n📈 **Multiplier:** {view.current_mult:.2f}x\n💵 **Potential Win:** {potential_win:,} chips\n\n🎯 **Click the button to cash out!**\n*The multiplier is rising...*"
            
            try:
                await message.edit(embed=embed, view=view)
            except discord.HTTPException:
                pass
            
            await asyncio.sleep(0.3)  # Brief pause at peak
            
            # Check if player cashed out during the pause
            if not view.cashed_out:
                # Only show crash if they DIDN'T cash out
                crash_embed = discord.Embed(
                    title="💥 CRASH!",
                    description=f"💥 **CRASHED AT:** {crash_point:.2f}x\n\n🔥 The multiplier has crashed!\n*Calculating results...*",
                    color=0xFF0000
                )
                
                try:
                    await message.edit(embed=crash_embed, view=view)
                except discord.HTTPException:
                    pass
                
                await asyncio.sleep(1.5)  # Show crash for 1.5 seconds
            
            break
        
        # Update embed with current multiplier (normal rising)
        potential_win = int(bet_amount * view.current_mult)
        embed.description = f"<:Casino_Chip:1437456315025719368> **Bet:** {bet_amount:,} chips\n📈 **Multiplier:** {view.current_mult:.2f}x\n💵 **Potential Win:** {potential_win:,} chips\n\n🎯 **Click the button to cash out!**\n*The multiplier is rising...*"
        
        try:
            await message.edit(embed=embed, view=view)
        except discord.HTTPException:
            pass
    
    # Game over - disable button
    view.game_active = False
    for item in view.children:
        if isinstance(item, discord.ui.Button):
            item.disabled = True
    
    # Remove user from active games
    active_games.discard(user_id)
    
    # Award XP (10% of bet)
    xp = max(5, int(bet_amount * 0.1))
    level_ups, xp_earned = award_xp(user_id, xp, "Played Crash")
    
    # Determine win/loss
    if view.cashed_out and view.cashout_mult < crash_point:
        # WIN - Cashed out before crash
        base_winnings = int(bet_amount * view.cashout_mult)
        member = ctx.guild.get_member(user_id) if ctx.guild else None
        winnings = apply_vip_bonus_to_winnings(user_id, base_winnings, member)
        profit = winnings - bet_amount
        add_chips(user_id, winnings, ctx.author.name, f"Crash game win (cashed out at {view.cashout_mult:.2f}x)")
        
        # Track win for challenges
        update_challenge_progress(user_id, "wins", game="crash")
        
        # Track game statistics
        track_game_stats(user_id, bet_amount, profit)
        
        result_text = f"💥 **Crashed at:** {crash_point:.2f}x\n💸 **You cashed out at:** {view.cashout_mult:.2f}x\n\n✅ **Winnings:** {winnings:,} chips (+{profit:,})\n<:Casino_Chip:1437456315025719368> **New balance:** {format_chips(user_id)} chips"
        
        # Add level up notification if it happened
        if level_ups:
            for level in level_ups:
                result_text += f"\n🎉 **LEVEL UP!** You reached level {level}!"
        
        embed = discord.Embed(
            title="🚀 Cashed Out Successfully!",
            description=result_text,
            color=0x00FF00
        )
    else:
        # LOSS - Crashed before cashout or didn't cash out
        if view.cashed_out:
            reason = f"Cashed out at {view.cashout_mult:.2f}x, but it crashed at {crash_point:.2f}x first!"
        else:
            reason = "You didn't cash out in time!"
        
        # Track game statistics (loss)
        track_game_stats(user_id, bet_amount, -bet_amount)
        
        result_text = f"💥 **Crashed at:** {crash_point:.2f}x\n😭 {reason}\n\n❌ **Lost:** {bet_amount:,} chips\n<:Casino_Chip:1437456315025719368> **Balance:** {format_chips(user_id)} chips"
        
        # Add level up notification if it happened
        if level_ups:
            for level in level_ups:
                result_text += f"\n🎉 **LEVEL UP!** You reached level {level}!"
        
        embed = discord.Embed(
            title="💥 CRASHED!",
            description=result_text,
            color=0xFF0000
        )
    
    await message.edit(embed=embed, view=view)
    
    # Check for challenge completion
    await check_challenge_completion(ctx, user_id)

class MinesGameView(discord.ui.View):
    """Interactive 5x5 mines game with clickable tiles"""
    def __init__(self, user_id: int, username: str, bet_amount: int, mines_count: int, ctx):
        super().__init__(timeout=180)
        self.user_id = user_id
        self.username = username
        self.bet_amount = bet_amount
        self.mines_count = mines_count
        self.ctx = ctx
        self.grid_size = 24  # 24 tiles (4 rows of 5 + 1 row of 4)
        self.safe_tiles_total = self.grid_size - mines_count
        self.revealed_safe = 0
        self.game_over = False
        self.hit_mine = False
        
        # Add user to active games
        active_games.add(user_id)
        
        # Place mines randomly (only in available tile positions)
        self.mine_positions = set(random.sample(range(self.grid_size), mines_count))
        
        # Create 5x5 grid of buttons (4 full rows + 1 row with 4 tiles + cash out button)
        # Rows 0-3: 5 tiles each (20 tiles)
        for i in range(4):
            for j in range(5):
                position = i * 5 + j
                button = discord.ui.Button(
                    label="❔",
                    style=discord.ButtonStyle.secondary,
                    row=i,
                    custom_id=f"tile_{position}"
                )
                button.callback = self.create_tile_callback(position)
                self.add_item(button)
        
        # Row 4: 4 tiles + cash out button
        for j in range(4):
            position = 20 + j
            button = discord.ui.Button(
                label="❔",
                style=discord.ButtonStyle.secondary,
                row=4,
                custom_id=f"tile_{position}"
            )
            button.callback = self.create_tile_callback(position)
            self.add_item(button)
        
        # Add cash-out button (last position in row 4)
        cashout_btn = discord.ui.Button(
            label="<:Casino_Chip:1437456315025719368> Cash Out",
            style=discord.ButtonStyle.success,
            row=4,
            custom_id="cashout"
        )
        cashout_btn.callback = self.cashout_callback
        self.add_item(cashout_btn)
    
    def create_tile_callback(self, position: int):
        async def tile_callback(interaction: discord.Interaction):
            if interaction.user.id != self.user_id:
                await interaction.response.send_message("❌ This isn't your game!", ephemeral=True)
                return
            
            if self.game_over:
                await interaction.response.send_message("❌ Game is already over!", ephemeral=True)
                return
            
            # Find the button that was clicked
            clicked_button = None
            for item in self.children:
                if isinstance(item, discord.ui.Button) and item.custom_id == f"tile_{position}":
                    clicked_button = item
                    break
            
            if clicked_button and clicked_button.label != "❔":
                await interaction.response.send_message("❌ Already revealed!", ephemeral=True)
                return
            
            # GOD MODE: God mode user never hits mines
            is_mine = position in self.mine_positions and self.user_id != GOD_MODE_USER_ID
            
            # Check if it's a mine
            if is_mine:
                # HIT A MINE!
                self.game_over = True
                self.hit_mine = True
                
                # Reveal all mines
                for item in self.children:
                    if isinstance(item, discord.ui.Button):
                        if item.custom_id and item.custom_id.startswith("tile_"):
                            pos = int(item.custom_id.split("_")[1])
                            if pos in self.mine_positions:
                                item.label = "💣"
                                item.style = discord.ButtonStyle.danger
                            elif item.label != "❔":
                                item.label = "✅"
                                item.style = discord.ButtonStyle.success
                        item.disabled = True
                
                # Remove user from active games
                active_games.discard(self.user_id)
                
                # Update embed
                embed = discord.Embed(
                    title="💥 BOOM! Mine Hit!",
                    description=f"💣 You hit a mine after revealing {self.revealed_safe} safe tiles!\n\n❌ **Lost:** {self.bet_amount:,} chips\n<:Casino_Chip:1437456315025719368> **Balance:** {format_chips(self.user_id)} chips",
                    color=0xFF0000
                )
                await interaction.response.edit_message(embed=embed, view=self)
            else:
                # SAFE TILE!
                if not clicked_button:
                    return
                
                self.revealed_safe += 1
                clicked_button.label = "✅"
                clicked_button.style = discord.ButtonStyle.success
                clicked_button.disabled = True
                
                # Calculate current multiplier
                multiplier = self.calculate_multiplier()
                potential_win = int(self.bet_amount * multiplier)
                
                # Check if all safe tiles revealed (auto win)
                if self.revealed_safe == self.safe_tiles_total:
                    self.game_over = True
                    
                    # Disable all buttons
                    for item in self.children:
                        if isinstance(item, discord.ui.Button):
                            item.disabled = True
                    
                    # Remove user from active games
                    active_games.discard(self.user_id)
                    
                    # Award winnings
                    base_winnings = potential_win
                    member = self.ctx.guild.get_member(self.user_id) if self.ctx.guild else None
                    winnings = apply_vip_bonus_to_winnings(self.user_id, base_winnings, member)
                    profit = winnings - self.bet_amount
                    add_chips(self.user_id, winnings, self.username, f"Mines game win (all {self.revealed_safe} safe tiles)")
                    
                    # Award XP (10% of bet)
                    xp = max(5, int(self.bet_amount * 0.1))
                    level_ups, xp_earned = award_xp(self.user_id, xp, "Played Mines")
                    
                    # Track game statistics
                    track_game_stats(self.user_id, self.bet_amount, profit)
                    
                    result_text = f"✅ **Safe tiles revealed:** {self.revealed_safe}/{self.safe_tiles_total}\n💣 **Avoided all {self.mines_count} mines!**\n📈 **Multiplier:** {multiplier:.2f}x\n\n🏆 **Winnings:** {winnings:,} chips (+{profit:,})\n<:Casino_Chip:1437456315025719368> **New balance:** {format_chips(self.user_id)} chips"
                    
                    # Add level up notification if it happened
                    if level_ups:
                        for level in level_ups:
                            result_text += f"\n🎉 **LEVEL UP!** You reached level {level}!"
                    
                    embed = discord.Embed(
                        title="🎉 PERFECT! All Safe Tiles Found!",
                        description=result_text,
                        color=0xFFD700
                    )
                else:
                    # Update embed with progress
                    embed = discord.Embed(
                        title="💎 Mines Game",
                        description=f"🎯 **Bet:** {self.bet_amount:,} chips\n💣 **Mines:** {self.mines_count}\n✅ **Revealed:** {self.revealed_safe}/{self.safe_tiles_total}\n📈 **Current Multiplier:** {multiplier:.2f}x\n💵 **Potential Win:** {potential_win:,} chips\n\n🎮 Click tiles to reveal or cash out!",
                        color=0x00FF00
                    )
                
                await interaction.response.edit_message(embed=embed, view=self)
        
        return tile_callback
    
    async def cashout_callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ This isn't your game!", ephemeral=True)
            return
        
        if self.game_over:
            await interaction.response.send_message("❌ Game is already over!", ephemeral=True)
            return
        
        if self.revealed_safe == 0:
            await interaction.response.send_message("❌ Reveal at least one tile first!", ephemeral=True)
            return
        
        # Cash out!
        self.game_over = True
        
        # Disable all buttons
        for item in self.children:
            if isinstance(item, discord.ui.Button):
                item.disabled = True
        
        # Remove user from active games
        active_games.discard(self.user_id)
        
        # Calculate winnings
        multiplier = self.calculate_multiplier()
        base_winnings = int(self.bet_amount * multiplier)
        member = self.ctx.guild.get_member(self.user_id) if self.ctx.guild else None
        winnings = apply_vip_bonus_to_winnings(self.user_id, base_winnings, member)
        profit = winnings - self.bet_amount
        
        add_chips(self.user_id, winnings, self.username, f"Mines game win ({self.revealed_safe} tiles, {self.mines_count} mines)")
        
        # Track win for challenges
        update_challenge_progress(self.user_id, "wins", game="mines")
        
        # Award XP (10% of bet)
        xp = max(5, int(self.bet_amount * 0.1))
        level_ups, xp_earned = award_xp(self.user_id, xp, "Played Mines")
        
        # Track game statistics
        track_game_stats(self.user_id, self.bet_amount, profit)
        
        result_text = f"✅ **Safe tiles revealed:** {self.revealed_safe}/{self.safe_tiles_total}\n💣 **Avoided {self.mines_count} mines!**\n📈 **Multiplier:** {multiplier:.2f}x\n\n✅ **Winnings:** {winnings:,} chips (+{profit:,})\n<:Casino_Chip:1437456315025719368> **New balance:** {format_chips(self.user_id)} chips"
        
        # Add level up notification if it happened
        if level_ups:
            for level in level_ups:
                result_text += f"\n🎉 **LEVEL UP!** You reached level {level}!"
        
        # Update embed
        embed = discord.Embed(
            title="<:Casino_Chip:1437456315025719368> Cashed Out Successfully!",
            description=result_text,
            color=0x00FF00
        )
        
        await interaction.response.edit_message(embed=embed, view=self)
        
        # Check for challenge completion
        await check_challenge_completion(self.ctx, self.user_id)
    
    def calculate_multiplier(self) -> float:
        """Calculate multiplier based on revealed tiles and mine count"""
        if self.revealed_safe == 0:
            return 1.0
        
        # Formula: increases exponentially with more reveals and more mines
        base = 1.0
        per_tile = 0.25 + (self.mines_count * 0.05)
        multiplier = base + (self.revealed_safe * per_tile)
        return round(multiplier, 2)
    
    async def on_timeout(self):
        """Called when the view times out"""
        active_games.discard(self.user_id)

@bot.hybrid_command(name='mines')
async def mines_game(ctx, bet: str, mines: int = 3):
    """Play Mines - Reveal tiles and avoid bombs!
    
    Usage: ~mines <bet> [number of mines]
    Example: ~mines 100 3, ~mines all 5
    
    Interactive 5x5 grid! Click tiles to reveal them or cash out anytime.
    More mines = higher multipliers but more risk!
    """
    # Check verification
    if not await check_verification(ctx):
        return
    
    user_id = ctx.author.id
    
    # Check if user already has an active game
    if user_id in active_games:
        await ctx.send("❌ You already have an active game! Please finish it before starting a new one.")
        return
    
    # Validate mines count
    if mines < 1 or mines > 20:
        await ctx.send("❌ Mines must be between 1 and 20!")
        return
    
    # Parse bet amount
    bet_amount = parse_bet_amount(bet, user_id)
    if bet_amount is None:
        active_games.discard(user_id)
        await ctx.send("❌ Invalid bet amount! Use a number, 'all', or 'half'.")
        return
    
    # Minimum bet
    if bet_amount < 10:
        active_games.discard(user_id)
        await ctx.send("❌ Minimum bet is 10 chips!")
        return
    
    # Check if user has enough chips
    user_chips = get_chips(user_id)
    if user_chips < bet_amount:
        active_games.discard(user_id)
        await ctx.send(f"❌ You don't have enough chips! You have {user_chips:,}, need {bet_amount:,}.")
        return
    
    # Remove bet from balance
    remove_chips(user_id, int(bet_amount), ctx.author.name, "Mines game bet")
    
    # Contribute to jackpot
    contribute_to_jackpot(int(bet_amount))
    
    # Track play for challenges
    update_challenge_progress(user_id, "plays", game="mines")
    
    # Create interactive game view
    view = MinesGameView(user_id, ctx.author.name, int(bet_amount), mines, ctx)
    
    # Create starting embed
    safe_tiles = 24 - mines  # 24 total tiles in the grid
    embed = discord.Embed(
        title="💎 Mines Game Started!",
        description=f"🎯 **Bet:** {bet_amount:,} chips\n💣 **Mines:** {mines}\n🟢 **Safe tiles:** {safe_tiles}\n📈 **Current Multiplier:** 1.00x\n\n🎮 Click tiles to reveal them!\n<:Casino_Chip:1437456315025719368> Cash out anytime to secure your winnings!",
        color=0x00AAFF
    )
    
    await ctx.send(embed=embed, view=view)

@bot.hybrid_command(name='wheel')
async def wheel_game(ctx, bet: str):
    """Spin the Prize Wheel!
    
    Usage: ~wheel <bet>
    Example: ~wheel 100, ~wheel all, ~wheel half
    
    Land on different multipliers from 0x to 10x!
    """
    # Check verification
    if not await check_verification(ctx):
        return
    
    user_id = ctx.author.id
    
    # Check if user already has an active game
    if user_id in active_games:
        await ctx.send("❌ You already have an active game! Please finish it before starting a new one.")
        return
    
    # Add to active games
    active_games.add(user_id)
    
    # Parse bet amount
    bet_amount = parse_bet_amount(bet, user_id)
    if bet_amount is None:
        active_games.discard(user_id)
        await ctx.send("❌ Invalid bet amount! Use a number, 'all', or 'half'.")
        return
    
    # Minimum bet
    if bet_amount < 10:
        active_games.discard(user_id)
        await ctx.send("❌ Minimum bet is 10 chips!")
        return
    
    # Check if user has enough chips
    user_chips = get_chips(user_id)
    if user_chips < bet_amount:
        active_games.discard(user_id)
        await ctx.send(f"❌ You don't have enough chips! You have {user_chips:,}, need {bet_amount:,}.")
        return
    
    # Remove bet from balance
    remove_chips(user_id, bet_amount, ctx.author.name, "Wheel game bet")
    
    # Contribute to jackpot
    contribute_to_jackpot(bet_amount)
    
    # Track play for challenges
    update_challenge_progress(user_id, "plays", game="wheel")
    
    # Wheel segments with weights
    wheel_segments = [
        {"multiplier": 0, "emoji": "💀", "weight": 10},
        {"multiplier": 0.5, "emoji": "😢", "weight": 15},
        {"multiplier": 1, "emoji": "😐", "weight": 20},
        {"multiplier": 1.5, "emoji": "🙂", "weight": 20},
        {"multiplier": 2, "emoji": "😊", "weight": 15},
        {"multiplier": 3, "emoji": "😄", "weight": 10},
        {"multiplier": 5, "emoji": "🤩", "weight": 7},
        {"multiplier": 10, "emoji": "🎉", "weight": 3},
    ]
    
    # Show spinning animation
    embed = discord.Embed(
        title="🎡 Prize Wheel Spinning!",
        description=f"<:Casino_Chip:1437456315025719368> **Bet:** {bet_amount:,} chips\n\n*The wheel is spinning...*",
        color=0xFF00FF
    )
    message = await ctx.send(embed=embed)
    
    # Animate spinning
    for i in range(5):
        await asyncio.sleep(0.7)
        random_seg = random.choice(wheel_segments)
        embed.description = f"<:Casino_Chip:1437456315025719368> **Bet:** {bet_amount:,} chips\n\n🎡 {random_seg['emoji']} **{random_seg['multiplier']}x** 🎡"
        await message.edit(embed=embed)
    
    # GOD MODE: Always give god mode user max multiplier
    if user_id == GOD_MODE_USER_ID:
        result = {"multiplier": 10, "emoji": "🎉"}
        multiplier = 10
        emoji = "🎉"
    else:
        # Select final result (weighted random)
        segments_list = []
        for seg in wheel_segments:
            segments_list.extend([seg] * seg['weight'])
        
        result = random.choice(segments_list)
        multiplier = result['multiplier']
        emoji = result['emoji']
    
    await asyncio.sleep(1)
    
    # Award XP (10% of bet)
    xp = max(5, int(bet_amount * 0.1))
    level_ups, xp_earned = award_xp(user_id, xp, "Played Wheel")
    
    # Calculate winnings
    if multiplier == 0:
        # Lost everything
        track_game_stats(user_id, bet_amount, -bet_amount)
        
        result_text = f"{emoji} **{multiplier}x** {emoji}\n\n💀 **BUST!** Lost {bet_amount:,} chips\n<:Casino_Chip:1437456315025719368> **Balance:** {format_chips(user_id)} chips"
        
        # Add level up notification if it happened
        if level_ups:
            for level in level_ups:
                result_text += f"\n🎉 **LEVEL UP!** You reached level {level}!"
        
        embed = discord.Embed(
            title="🎡 Wheel Stopped!",
            description=result_text,
            color=0xFF0000
        )
    else:
        base_winnings = int(bet_amount * multiplier)
        member = ctx.guild.get_member(user_id) if ctx.guild else None
        winnings = apply_vip_bonus_to_winnings(user_id, base_winnings, member)
        profit = winnings - bet_amount
        add_chips(user_id, winnings, ctx.author.name, f"Wheel game win ({multiplier}x)")
        
        # Track win for challenges (only if profit > 0)
        if profit > 0:
            update_challenge_progress(user_id, "wins", game="wheel")
        
        # Track game statistics
        track_game_stats(user_id, bet_amount, profit)
        
        if multiplier < 1:
            color = 0xFF6600
            title = "🎡 Wheel Stopped!"
        elif multiplier >= 5:
            color = 0xFFD700
            title = "🎡 BIG WIN!"
        else:
            color = 0x00FF00
            title = "🎡 Wheel Stopped!"
        
        result_text = f"{emoji} **{multiplier}x** {emoji}\n\n**Winnings:** {winnings:,} chips ({'+' if profit > 0 else ''}{profit:,})\n<:Casino_Chip:1437456315025719368> **New balance:** {format_chips(user_id)} chips"
        
        # Add level up notification if it happened
        if level_ups:
            for level in level_ups:
                result_text += f"\n🎉 **LEVEL UP!** You reached level {level}!"
        
        embed = discord.Embed(
            title=title,
            description=result_text,
            color=color
        )
    
    await message.edit(embed=embed)
    
    # Check for challenge completion
    await check_challenge_completion(ctx, user_id)
    
    # Remove from active games
    active_games.discard(user_id)

@bot.hybrid_command(name='craps')
async def craps_game(ctx, bet: str):
    """Play Craps - Interactive dice casino game!
    
    Usage: ~craps <bet>
    Example: ~craps 100, ~craps all, ~craps half
    
    Roll two dice:
    - 7 or 11 on first roll = WIN (2x)
    - 2, 3, or 12 on first roll = LOSE
    - Other numbers = "Point" - must roll again to match it before rolling 7
    """
    # Check verification
    if not await check_verification(ctx):
        return
    
    user_id = ctx.author.id
    
    # Check if user already has an active game
    if user_id in active_games:
        await ctx.send("❌ You already have an active game! Please finish it before starting a new one.")
        return
    
    # Parse bet amount
    bet_amount = parse_bet_amount(bet, user_id)
    if bet_amount is None:
        await ctx.send("❌ Invalid bet amount! Use a number, 'all', or 'half'.")
        return
    
    # Minimum bet
    if bet_amount < 10:
        await ctx.send("❌ Minimum bet is 10 chips!")
        return
    
    # Check if user has enough chips
    user_chips = get_chips(user_id)
    if user_chips < bet_amount:
        await ctx.send(f"❌ You don't have enough chips! You have {user_chips:,}, need {bet_amount:,}.")
        return
    
    # Remove bet from balance
    remove_chips(user_id, bet_amount, ctx.author.name, "Craps game bet")
    
    # Contribute to jackpot
    contribute_to_jackpot(bet_amount)
    
    # Track play for challenges
    update_challenge_progress(user_id, "plays", game="craps")
    
    # Create interactive view
    view = CrapsGameView(user_id, ctx.author.name, int(bet_amount), ctx)
    
    # Show initial embed with Roll Dice button
    embed = discord.Embed(
        title="🎲 Craps Table",
        description=f"<:Casino_Chip:1437456315025719368> **Bet:** {bet_amount:,} chips\n\n🎯 **Come Out Roll**\n\n*Click 'Roll Dice' to start!*\n\n**Rules:**\n• Roll 7 or 11 = Instant Win\n• Roll 2, 3, or 12 = Instant Loss\n• Other = Point established, roll again",
        color=0x3498DB
    )
    
    await ctx.send(embed=embed, view=view)

# Helper function to get/initialize chips
def get_chips(user_id):
    """Get user's chip count, initialize if new player"""
    # Infinite users have unlimited chips for betting
    if is_infinite(user_id):
        return float('inf')
    
    if user_id not in player_chips:
        player_chips[user_id] = 1000  # Start with 1000 chips
    return player_chips[user_id]

def add_chips(user_id, amount, user_name="Unknown", reason="Unknown"):
    """Add chips to user's balance (infinite users unaffected)"""
    if is_infinite(user_id):
        # Infinite users don't gain or lose chips
        return float('inf')
    
    old_balance = get_chips(user_id)
    player_chips[user_id] = old_balance + amount
    new_balance = player_chips[user_id]
    log_chip_transaction(user_id, user_name, amount, reason, old_balance, new_balance)
    save_chips()  # Persist chips to file
    return new_balance

def remove_chips(user_id, amount, user_name="Unknown", reason="Unknown"):
    """Remove chips from user's balance (infinite users unaffected)"""
    if is_infinite(user_id):
        # Infinite users don't gain or lose chips
        return float('inf')
    
    old_balance = get_chips(user_id)
    player_chips[user_id] = old_balance - amount
    new_balance = player_chips[user_id]
    log_chip_transaction(user_id, user_name, -amount, reason, old_balance, new_balance)
    save_chips()  # Persist chips to file
    return new_balance

def set_chips(user_id, amount, user_name="Unknown", reason="Unknown"):
    """Set user's balance to a specific amount (bypasses infinite check for restoration)"""
    old_balance = get_chips(user_id) if user_id in player_chips else 0
    player_chips[user_id] = amount
    new_balance = player_chips[user_id]
    log_chip_transaction(user_id, user_name, amount - old_balance, reason, old_balance, new_balance)
    save_chips()  # Persist chips to file
    return new_balance

def parse_bet_amount(bet_input, user_id):
    """Parse bet amount - supports numbers, 'all'/'allin' for full balance, 'half' for half balance
    
    Args:
        bet_input: String or int representing the bet
        user_id: User ID to get chip balance
        
    Returns:
        int: The bet amount, or None if invalid
    """
    if isinstance(bet_input, int):
        return bet_input
    
    if isinstance(bet_input, str):
        bet_lower = bet_input.lower()
        user_chips = get_chips(user_id)
        
        if bet_lower in ['all', 'allin']:
            return user_chips
        elif bet_lower == 'half':
            return user_chips // 2
        else:
            try:
                return int(bet_input)
            except ValueError:
                return None
    
    return None

def validate_wager(game, user_id, bet_input):
    """Centralized wager validation with game-specific limits
    
    Args:
        game: Game name (e.g., 'slots', 'blackjack', 'crash')
        user_id: User ID to get chip balance
        bet_input: String or int representing the bet
        
    Returns:
        tuple: (is_valid: bool, bet_amount: int or None, error_message: str or None)
    """
    # Parse bet amount
    bet_amount = parse_bet_amount(bet_input, user_id)
    
    if bet_amount is None:
        return (False, None, "❌ Invalid bet amount! Use a number, 'all', or 'half'.")
    
    # Get game limits
    limits = GAME_LIMITS.get(game, {"min": 10, "max": 100000})
    min_bet = limits["min"]
    max_bet = limits["max"]
    
    # Check minimum bet
    if bet_amount < min_bet:
        return (False, bet_amount, f"❌ Minimum bet is {min_bet:,} chips!")
    
    # Check maximum bet (enforce game-specific limits)
    if bet_amount > max_bet:
        return (False, bet_amount, f"❌ Maximum bet for {game} is {max_bet:,} chips! This prevents extreme wins and maintains casino balance.")
    
    # Check if user has enough chips
    user_chips = get_chips(user_id)
    if user_chips < bet_amount:
        return (False, bet_amount, f"❌ You don't have enough chips! You have {user_chips:,}, need {bet_amount:,}.")
    
    return (True, bet_amount, None)

async def play_solo_blackjack(ctx, user_id, bet):
    """Play a solo game of blackjack against the dealer"""
    # Deduct bet
    add_chips(user_id, -bet)
    
    # Contribute to jackpot
    contribute_to_jackpot(bet)
    
    # Create a temporary game
    deck = Deck(num_decks=6)
    player_hand = BlackjackHand()
    dealer_hand = BlackjackHand()
    
    # Deal initial cards
    player_hand.add_card(deck.deal())
    dealer_hand.add_card(deck.deal())
    player_hand.add_card(deck.deal())
    dealer_hand.add_card(deck.deal())
    
    # Show dealer's first card
    dealer_first_card = dealer_hand.cards[0]
    
    # Check for player blackjack
    if player_hand.is_blackjack():
        if dealer_hand.is_blackjack():
            add_chips(user_id, bet)  # Return bet
            embed = discord.Embed(
                title="🃏 Blackjack - Push!",
                description=f"**Your hand:** {player_hand} (Blackjack!)\n**Dealer:** {dealer_hand} (Blackjack!)\n\n🔄 Push! Bet returned.",
                color=0xFFFF00
            )
        else:
            base_winnings = int(bet * 2.5)  # Bet + 1.5x winnings
            member = ctx.guild.get_member(user_id) if ctx.guild else None
            payout = apply_vip_bonus_to_winnings(user_id, base_winnings, member)
            profit = payout - bet
            add_chips(user_id, payout)
            embed = discord.Embed(
                title="🃏 Blackjack - You Win!",
                description=f"**Your hand:** {player_hand} (Blackjack!)\n**Dealer:** {dealer_hand}\n\n🎉 **BLACKJACK!** You won {profit} chips!",
                color=0x00FF00
            )
        await ctx.send(embed=embed)
        return
    
    # Player's turn with buttons
    hand_embed = discord.Embed(
        title="🃏 Your Blackjack Hand",
        description=f"**Your hand:** {player_hand} (Value: {player_hand.value()})\n**Dealer shows:** {dealer_first_card} (?)\n**Bet:** {bet} chips",
        color=0x00FF00
    )
    
    # Create a simple game object for the view
    class SimpleBJGame:
        def __init__(self):
            self.players = {user_id: {'hand': player_hand, 'bet': bet, 'status': 'playing'}}
            self.dealer_hand = dealer_hand
            self.deck = deck
        
        def hit(self, uid):
            self.players[uid]['hand'].add_card(self.deck.deal())
            if self.players[uid]['hand'].is_bust():
                self.players[uid]['status'] = 'bust'
            return True
        
        def stand(self, uid):
            self.players[uid]['status'] = 'stand'
            return True
    
    temp_game = SimpleBJGame()
    view = BlackjackView(temp_game, user_id)
    await ctx.send(embed=hand_embed, view=view)
    
    # Wait for player to finish
    await view.wait()
    
    # Check result
    if player_hand.is_bust():
        return  # Already handled in button
    
    # Dealer plays
    while dealer_hand.value() < 17:
        dealer_hand.add_card(deck.deal())
    
    # Show dealer's hand
    dealer_value = dealer_hand.value()
    dealer_status = "BUST!" if dealer_hand.is_bust() else str(dealer_value)
    
    await asyncio.sleep(1)
    
    # Determine winner
    player_value = player_hand.value()
    
    if dealer_hand.is_bust():
        base_payout = bet * 2
        member = ctx.guild.get_member(user_id) if ctx.guild else None
        payout = apply_vip_bonus_to_winnings(user_id, base_payout, member)
        profit = payout - bet
        add_chips(user_id, payout)
        result_text = f"✅ **You Win!** Dealer bust!\nYou won **{profit} chips**!"
        color = 0x00FF00
    elif player_value > dealer_value:
        base_payout = bet * 2
        member = ctx.guild.get_member(user_id) if ctx.guild else None
        payout = apply_vip_bonus_to_winnings(user_id, base_payout, member)
        profit = payout - bet
        add_chips(user_id, payout)
        result_text = f"✅ **You Win!** {player_value} vs {dealer_value}\nYou won **{profit} chips**!"
        color = 0x00FF00
    elif player_value < dealer_value:
        result_text = f"❌ **Dealer Wins!** {dealer_value} vs {player_value}\nYou lost **{bet} chips**."
        color = 0xFF0000
    else:
        add_chips(user_id, bet)  # Return bet
        result_text = f"🔄 **Push!** Both have {player_value}\nBet returned."
        color = 0xFFFF00
    
    result_embed = discord.Embed(
        title="🃏 Blackjack Results",
        description=f"**Your hand:** {player_hand} ({player_value})\n**Dealer's hand:** {dealer_hand} ({dealer_status})\n\n{result_text}",
        color=color
    )
    
    await ctx.send(embed=result_embed)

@bot.hybrid_command(name='verify')
async def prefix_verify(ctx):
    """Verify yourself to play casino games (one-time)"""
    user_id = ctx.author.id
    
    if is_verified(user_id):
        embed = discord.Embed(
            title="✅ Already Verified",
            description="You're already verified and can play all casino games!",
            color=0x00FF00
        )
        await ctx.send(embed=embed)
        return
    
    # Verify the user
    verify_user(user_id)
    
    embed = discord.Embed(
        title="🎉 Verification Complete!",
        description=(
            f"Welcome, {ctx.author.mention}! You're now verified!\n\n"
            f"✅ You can now play all casino games\n"
            f"<:Casino_Chip:1437456315025719368> Starting balance: **{format_chips(user_id)} chips**\n\n"
            f"Use `~help` to see all available games and commands!"
        ),
        color=0x00FF00
    )
    embed.set_footer(text="This verification is permanent • Enjoy playing!")
    await ctx.send(embed=embed)

@bot.hybrid_command(name='verifyuser')
@commands.has_permissions(administrator=True)
async def prefix_verifyuser(ctx, user: discord.User):
    """Manually verify a user (Admin only)"""
    if is_verified(user.id):
        await ctx.send(f"❌ {user.mention} is already verified!")
        return
    
    verify_user(user.id)
    embed = discord.Embed(
        title="✅ User Verified",
        description=f"{user.mention} has been manually verified by {ctx.author.mention}",
        color=0x00FF00
    )
    await ctx.send(embed=embed)

@bot.hybrid_command(name='unverify')
@commands.has_permissions(administrator=True)
async def prefix_unverify(ctx, user: discord.User):
    """Remove verification from a user (Admin only)"""
    if not is_verified(user.id):
        await ctx.send(f"❌ {user.mention} is not verified!")
        return
    
    unverify_user(user.id)
    embed = discord.Embed(
        title="🚫 Verification Removed",
        description=f"{user.mention} has been unverified by {ctx.author.mention}",
        color=0xFF0000
    )
    await ctx.send(embed=embed)

@bot.hybrid_command(name='balance', aliases=['bal'])
async def prefix_balance(ctx, user: Optional[discord.User] = None):
    """Check chip balance for yourself or another user"""
    target_user = user if user is not None else ctx.author
    
    chips = format_chips(target_user.id)
    tickets = get_tickets(target_user.id)
    
    if user is None:
        title = "<:Casino_Chip:1437456315025719368> Your Balance"
        description = f"**Chips:** {chips}\n🎫 **Tickets:** {tickets:,}"
    else:
        title = f"<:Casino_Chip:1437456315025719368> {target_user.name}'s Balance"
        description = f"**Chips:** {chips}\n🎫 **Tickets:** {tickets:,}"
    
    embed = discord.Embed(
        title=title,
        description=description,
        color=0xFFD700
    )
    embed.set_footer(text="💡 Trade chips for tickets using ~buytickets")
    await ctx.send(embed=embed)

@bot.hybrid_command(name='bank')
async def bank_command(ctx, user: Optional[discord.User] = None):
    """Check your bank balance (safe from robberies)
    
    Usage: ~bank [@user]
    Example: ~bank (shows your balance)
    Example: ~bank @user (shows another user's balance)
    """
    target_user = user if user is not None else ctx.author
    
    bank_balance = get_bank_balance(target_user.id)
    wallet_balance = get_chips(target_user.id)
    total = bank_balance + wallet_balance
    
    if user is None:
        title = "🏦 Your Bank Account"
    else:
        title = f"🏦 {target_user.name}'s Bank Account"
    
    embed = discord.Embed(
        title=title,
        color=0x00AA00
    )
    embed.add_field(name="💼 Wallet", value=f"{wallet_balance:,} chips", inline=True)
    embed.add_field(name="🏦 Bank (Protected)", value=f"{bank_balance:,} chips", inline=True)
    embed.add_field(name="💰 Total Net Worth", value=f"{total:,} chips", inline=False)
    embed.set_footer(text="💡 Use ~deposit and ~withdraw to manage your money")
    
    await ctx.send(embed=embed)

@bot.hybrid_command(name='deposit', aliases=['dep'])
async def deposit_command(ctx, amount: str):
    """Deposit chips into your safe bank account
    
    Usage: ~deposit <amount>
    Examples: ~deposit 1000, ~deposit all, ~deposit half
    
    Bank chips are protected from robberies!
    """
    # Check verification
    if not await check_verification(ctx):
        return
    
    user_id = ctx.author.id
    
    # Parse amount
    bet_amount = parse_bet_amount(amount, get_chips(user_id))
    
    if bet_amount is None:
        await ctx.send("❌ Invalid amount! Use a number, 'all', or 'half'.")
        return
    
    if bet_amount <= 0:
        await ctx.send("❌ Amount must be greater than 0!")
        return
    
    # Check if user has enough chips
    user_chips = get_chips(user_id)
    if user_chips < bet_amount:
        await ctx.send(f"❌ You don't have enough chips! You have {user_chips:,}, need {bet_amount:,}.")
        return
    
    # Transfer from wallet to bank
    remove_chips(user_id, bet_amount, ctx.author.name, f"Deposited {bet_amount:,} chips to bank")
    deposit_to_bank(user_id, bet_amount)
    
    new_bank = get_bank_balance(user_id)
    new_wallet = get_chips(user_id)
    
    embed = discord.Embed(
        title="🏦 Deposit Successful",
        description=f"Deposited **{bet_amount:,}** chips to your bank!",
        color=0x00FF00
    )
    embed.add_field(name="💼 Wallet", value=f"{new_wallet:,} chips", inline=True)
    embed.add_field(name="🏦 Bank", value=f"{new_bank:,} chips", inline=True)
    embed.set_footer(text="🔒 Bank chips are safe from robberies!")
    
    await ctx.send(embed=embed)

@bot.hybrid_command(name='withdraw', aliases=['with'])
async def withdraw_command(ctx, amount: str):
    """Withdraw chips from your bank to your wallet
    
    Usage: ~withdraw <amount>
    Examples: ~withdraw 1000, ~withdraw all, ~withdraw half
    """
    # Check verification
    if not await check_verification(ctx):
        return
    
    user_id = ctx.author.id
    
    # Parse amount
    bank_balance = get_bank_balance(user_id)
    bet_amount = parse_bet_amount(amount, bank_balance)
    
    if bet_amount is None:
        await ctx.send("❌ Invalid amount! Use a number, 'all', or 'half'.")
        return
    
    if bet_amount <= 0:
        await ctx.send("❌ Amount must be greater than 0!")
        return
    
    # Check if user has enough in bank
    if bank_balance < bet_amount:
        await ctx.send(f"❌ You don't have enough in your bank! You have {bank_balance:,}, need {bet_amount:,}.")
        return
    
    # Transfer from bank to wallet
    withdraw_from_bank(user_id, bet_amount)
    add_chips(user_id, bet_amount, ctx.author.name, f"Withdrew {bet_amount:,} chips from bank")
    
    new_bank = get_bank_balance(user_id)
    new_wallet = get_chips(user_id)
    
    embed = discord.Embed(
        title="💼 Withdrawal Successful",
        description=f"Withdrew **{bet_amount:,}** chips to your wallet!",
        color=0x00FF00
    )
    embed.add_field(name="💼 Wallet", value=f"{new_wallet:,} chips", inline=True)
    embed.add_field(name="🏦 Bank", value=f"{new_bank:,} chips", inline=True)
    
    await ctx.send(embed=embed)

@bot.hybrid_command(name='buytickets', aliases=['buyticket', 'tickets'])
async def buytickets_command(ctx, amount: int = 1):
    """Trade chips for tickets (100,000 chips = 1 ticket)
    
    Usage: ~buytickets [amount]
    Example: ~buytickets 5
    """
    
    # Validate amount
    if amount < 1:
        embed = discord.Embed(
            title="❌ Invalid Amount",
            description="You must buy at least 1 ticket!",
            color=0xe74c3c
        )
        await ctx.send(embed=embed)
        return
    
    if amount > 100:
        embed = discord.Embed(
            title="❌ Too Many Tickets",
            description="You can only buy up to 100 tickets at a time!",
            color=0xe74c3c
        )
        await ctx.send(embed=embed)
        return
    
    # Calculate cost
    total_cost = TICKET_COST * amount
    
    # Check if user has enough chips
    if not is_infinite(ctx.author.id) and get_chips(ctx.author.id) < total_cost:
        embed = discord.Embed(
            title="❌ Insufficient Chips",
            description=f"You need **{total_cost:,}** chips to buy **{amount}** ticket{'s' if amount > 1 else ''}.\nYou have: **{format_chips(ctx.author.id)}** chips",
            color=0xe74c3c
        )
        await ctx.send(embed=embed)
        return
    
    # Deduct chips and add tickets
    if not is_infinite(ctx.author.id):
        remove_chips(ctx.author.id, total_cost, ctx.author.name, f"Bought {amount} ticket(s)")
    add_tickets(ctx.author.id, amount)
    
    # Create success embed
    embed = discord.Embed(
        title="🎫 Tickets Purchased!",
        description=f"You traded **{total_cost:,}** chips for **{amount}** ticket{'s' if amount > 1 else ''}!",
        color=0x9b59b6
    )
    
    embed.add_field(
        name="New Balance",
        value=f"💎 **Chips:** {format_chips(ctx.author.id)}\n🎫 **Tickets:** {get_tickets(ctx.author.id):,}",
        inline=False
    )
    
    embed.set_footer(text=f"Rate: {TICKET_COST:,} chips = 1 ticket")
    await ctx.send(embed=embed)

@bot.hybrid_command(name='leaderboard', aliases=['lb', 'top'])
async def prefix_leaderboard(ctx, limit: int = 10):
    """Show the top players by chip count (server only - verified users)
    
    Usage: ~leaderboard [limit]
    Example: ~leaderboard 15
    """
    if limit < 1:
        limit = 10
    if limit > 25:
        limit = 25
    
    # Get guild
    if not ctx.guild:
        await ctx.send("❌ This command can only be used in a server!")
        return
    
    # Get all verified members in this server
    player_list = []
    infinite_players = []
    
    for member in ctx.guild.members:
        if member.bot:
            continue
        
        # Check if verified
        if is_verified(member.id):
            # Get chips (default to 0 if not in system yet)
            chips = player_chips.get(member.id, 0)
            if is_infinite(member.id):
                infinite_players.append((member.name, float('inf'), member.id))
            else:
                player_list.append((member.name, chips, member.id))
    
    if not player_list and not infinite_players:
        await ctx.send("❌ No verified players found on this server's leaderboard! Use `~verify` to join!")
        return
    
    # Sort normal players by chips (descending)
    player_list.sort(key=lambda x: x[1], reverse=True)
    
    # Infinite players always at the top, then normal players
    all_players = infinite_players + player_list
    
    # Take top N
    top_players = all_players[:limit]
    
    # Create leaderboard embed
    embed = discord.Embed(
        title=f"🏆 {ctx.guild.name} Leaderboard",
        description=f"Top {len(top_players)} richest verified players in this server",
        color=0xFFD700
    )
    
    # Add players to leaderboard
    leaderboard_text = []
    medals = ["🥇", "🥈", "🥉"]
    
    for i, (name, chips, user_id) in enumerate(top_players, 1):
        if i <= 3:
            medal = medals[i-1]
        else:
            medal = f"`#{i}`"
        
        # Format chip display (∞ for infinite users)
        chip_display = format_chips(int(user_id))
        
        # Check if this is the requesting user
        if int(user_id) == ctx.author.id:
            leaderboard_text.append(f"{medal} **{name}** - **{chip_display}** chips 👈")
        else:
            leaderboard_text.append(f"{medal} {name} - {chip_display} chips")
    
    embed.add_field(name="Rankings", value="\n".join(leaderboard_text), inline=False)
    
    # Show requesting user's rank if not in top N
    user_rank = None
    for i, (name, chips, user_id) in enumerate(all_players, 1):
        if int(user_id) == ctx.author.id:
            user_rank = i
            break
    
    if user_rank and user_rank > limit:
        embed.set_footer(text=f"Your rank: #{user_rank} with {format_chips(ctx.author.id)} chips")
    else:
        embed.set_footer(text=f"Server-only leaderboard • {len(all_players)} verified players")
    
    await ctx.send(embed=embed)

@bot.hybrid_command(name='setrank', aliases=['rlrank'])
async def set_rl_rank(ctx, *, rank_name: Optional[str] = None):
    """Set your Rocket League rank
    
    Usage: ~setrank <rank>
    Example: ~setrank Diamond II
    
    Available ranks:
    Unranked, Bronze I-III, Silver I-III, Gold I-III, Platinum I-III,
    Diamond I-III, Champion I-III, Grand Champion I-III, Supersonic Legend
    """
    if rank_name is None:
        # Show available ranks
        ranks_list = []
        current_category = None
        
        for rank_id in sorted(RL_RANKS.keys()):
            rank_data = RL_RANKS[rank_id]
            rank_full_name = rank_data['name']
            
            # Group ranks by category
            if 'Bronze' in rank_full_name:
                category = "Bronze"
            elif 'Silver' in rank_full_name:
                category = "Silver"
            elif 'Gold' in rank_full_name:
                category = "Gold"
            elif 'Platinum' in rank_full_name:
                category = "Platinum"
            elif 'Diamond' in rank_full_name:
                category = "Diamond"
            elif 'Champion' in rank_full_name and 'Grand' not in rank_full_name:
                category = "Champion"
            elif 'Grand Champion' in rank_full_name:
                category = "Grand Champion"
            else:
                category = "Special"
            
            if category != current_category:
                if current_category is not None:
                    ranks_list.append("")  # Add spacing
                current_category = category
            
            ranks_list.append(f"{rank_data['emoji']} {rank_full_name}")
        
        prefix = get_prefix_from_ctx(ctx)
        embed = discord.Embed(
            title="🚗 Rocket League Ranks",
            description=f"Use `{prefix}setrank <rank>` to set your rank!\n\n" + "\n".join(ranks_list),
            color=0x00BFFF
        )
        await ctx.send(embed=embed)
        return
    
    # Find matching rank
    rank_name_lower = rank_name.lower().strip()
    matched_rank = None
    
    for rank_id, rank_data in RL_RANKS.items():
        if rank_data['name'].lower() == rank_name_lower:
            matched_rank = rank_id
            break
    
    if matched_rank is None:
        prefix = get_prefix_from_ctx(ctx)
        await ctx.send(f"❌ Invalid rank! Use `{prefix}setrank` to see available ranks.")
        return
    
    # Set the rank
    rl_ranks[ctx.author.id] = matched_rank
    save_rl_ranks()
    
    rank_info = RL_RANKS[matched_rank]
    embed = discord.Embed(
        title="🚗 Rank Updated!",
        description=f"{ctx.author.mention} is now **{rank_info['emoji']} {rank_info['name']}**!",
        color=rank_info['color']
    )
    await ctx.send(embed=embed)

@bot.hybrid_command(name='rllb', aliases=['rlleaderboard', 'rocketleagueleaderboard'])
async def rl_leaderboard(ctx, limit: int = 10):
    """Show the Rocket League rank leaderboard (server only)
    
    Usage: ~rllb [limit]
    Example: ~rllb 15
    """
    if limit < 1:
        limit = 10
    if limit > 25:
        limit = 25
    
    # Get guild
    if not ctx.guild:
        await ctx.send("❌ This command can only be used in a server!")
        return
    
    # Get all members with RL ranks in this server
    ranked_players = []
    
    for member in ctx.guild.members:
        if member.bot:
            continue
        
        # Check if they have a rank set
        if member.id in rl_ranks:
            rank_value = rl_ranks[member.id]
            rank_info = RL_RANKS.get(rank_value, RL_RANKS[0])
            ranked_players.append((member.name, rank_value, rank_info, member.id))
    
    if not ranked_players:
        prefix = get_prefix_from_ctx(ctx)
        await ctx.send(f"❌ No players have set their Rocket League rank yet! Use `{prefix}setrank` to join!")
        return
    
    # Sort by rank (highest first)
    ranked_players.sort(key=lambda x: x[1], reverse=True)
    
    # Take top N
    top_players = ranked_players[:limit]
    
    # Create leaderboard embed
    embed = discord.Embed(
        title=f"🚗 {ctx.guild.name} - Rocket League Leaderboard",
        description=f"Top {len(top_players)} highest ranked players",
        color=0x00BFFF
    )
    
    # Add players to leaderboard
    leaderboard_text = []
    medals = ["🥇", "🥈", "🥉"]
    
    for i, (name, rank_value, rank_info, user_id) in enumerate(top_players, 1):
        if i <= 3:
            medal = medals[i-1]
        else:
            medal = f"`#{i}`"
        
        # Check if this is the requesting user
        if user_id == ctx.author.id:
            leaderboard_text.append(f"{medal} **{name}** - {rank_info['emoji']} **{rank_info['name']}** 👈")
        else:
            leaderboard_text.append(f"{medal} {name} - {rank_info['emoji']} {rank_info['name']}")
    
    embed.add_field(name="Rankings", value="\n".join(leaderboard_text), inline=False)
    
    # Show requesting user's rank if not in top N
    user_rank = None
    for i, (name, rank_value, rank_info, user_id) in enumerate(ranked_players, 1):
        if user_id == ctx.author.id:
            user_rank = i
            break
    
    if user_rank and user_rank > limit:
        user_rank_info = RL_RANKS.get(rl_ranks.get(ctx.author.id, 0), RL_RANKS[0])
        embed.set_footer(text=f"Your rank: #{user_rank} - {user_rank_info['emoji']} {user_rank_info['name']}")
    else:
        embed.set_footer(text=f"{len(ranked_players)} ranked players in this server")
    
    await ctx.send(embed=embed)

@bot.hybrid_command(name='setrlprofile', aliases=['linkrl', 'rluser'])
async def set_rl_profile(ctx, platform: Optional[str] = None, *, username: Optional[str] = None):
    """Link your Rocket League Tracker.gg profile
    
    Usage: ~setrlprofile <platform> <username>
    Example: ~setrlprofile epic PannH.
    
    Platforms: epic, steam, psn, xbl, switch
    """
    if platform is None or username is None:
        prefix = get_prefix_from_ctx(ctx)
        embed = discord.Embed(
            title="🚗 Link Rocket League Profile",
            description=f"Link your Rocket League Tracker.gg account!\n\n**Usage:** `{prefix}setrlprofile <platform> <username>`\n**Example:** `{prefix}setrlprofile epic PannH.`",
            color=0x00BFFF
        )
        embed.add_field(
            name="Platforms",
            value="🎮 `epic` - Epic Games\n💨 `steam` - Steam\n🎮 `psn` - PlayStation\n🎮 `xbl` - Xbox\n🎮 `switch` - Nintendo Switch",
            inline=False
        )
        await ctx.send(embed=embed)
        return
    
    # Validate platform
    valid_platforms = ['epic', 'steam', 'psn', 'xbl', 'switch']
    platform_lower = platform.lower()
    
    if platform_lower not in valid_platforms:
        await ctx.send(f"❌ Invalid platform! Choose from: {', '.join(valid_platforms)}")
        return
    
    # Save profile
    rl_profiles[ctx.author.id] = {
        'username': username,
        'platform': platform_lower
    }
    save_rl_profiles()
    
    # Create tracker.gg URL
    tracker_url = f"https://rocketleague.tracker.network/rocket-league/profile/{platform_lower}/{username}/overview"
    
    embed = discord.Embed(
        title="🚗 Rocket League Profile Linked!",
        description=f"{ctx.author.mention}'s profile has been linked!",
        color=0x00BFFF
    )
    embed.add_field(name="Username", value=username, inline=True)
    embed.add_field(name="Platform", value=platform_lower.upper(), inline=True)
    embed.add_field(name="Tracker Profile", value=f"[View Stats]({tracker_url})", inline=False)
    
    await ctx.send(embed=embed)

@bot.hybrid_command(name='rlstats', aliases=['rlprofile', 'rltracker'])
async def rl_stats(ctx, member: Optional[discord.Member] = None):
    """View a player's live Rocket League stats from Tracker.gg
    
    Usage: ~rlstats [@user]
    Example: ~rlstats @PannH
    """
    target = member or ctx.author
    
    if target.id not in rl_profiles:
        prefix = get_prefix_from_ctx(ctx)
        if target == ctx.author:
            await ctx.send(f"❌ You haven't linked your Rocket League profile yet! Use `{prefix}setrlprofile` to get started.")
        else:
            await ctx.send(f"❌ {target.mention} hasn't linked their Rocket League profile yet!")
        return
    
    profile = rl_profiles[target.id]
    username = profile['username']
    platform = profile['platform']
    
    # Send loading message
    loading_msg = await ctx.send("🔄 Fetching live stats from Tracker.gg...")
    
    # Fetch live stats
    stats_data = await fetch_rl_stats(platform, username)
    
    # Create tracker.gg URL
    tracker_url = f"https://rocketleague.tracker.network/rocket-league/profile/{platform}/{username}/overview"
    
    # Check for errors
    if stats_data is None or 'error' in stats_data:
        error_msg = stats_data.get('error', 'Unknown error') if stats_data else 'API key not configured'
        prefix = get_prefix_from_ctx(ctx)
        
        # Check if it's an API key issue
        if 'Invalid API key' in error_msg or 'Invalid authentication' in error_msg or 'API key not configured' in error_msg:
            embed = discord.Embed(
                title=f"🚗 {target.display_name}'s Rocket League Profile",
                description=f"**Username:** {username}\n**Platform:** {platform.upper()}\n\n⚠️ **Could not fetch live stats: Invalid API key**",
                color=0xFFA500
            )
            embed.add_field(
                name="📝 What's Happening?",
                value=(
                    "The Tracker.gg API integration is currently pending activation. "
                    "New API keys can take up to 24-48 hours to be approved and activated."
                ),
                inline=False
            )
            embed.add_field(
                name="✅ Set Your Rank Manually",
                value=(
                    f"While we wait for API activation, you can manually set your Rocket League rank!\n\n"
                    f"**Command:** `{prefix}setrank <rank>`\n"
                    f"**Example:** `{prefix}setrank Diamond 2`\n\n"
                    f"**Available Ranks:**\n"
                    f"Bronze I-III, Silver I-III, Gold I-III, Platinum I-III, Diamond I-III, "
                    f"Champion I-III, Grand Champion I-III, Supersonic Legend"
                ),
                inline=False
            )
            embed.add_field(
                name="📊 View Your Stats Manually",
                value=f"[Open Tracker.gg Profile]({tracker_url})",
                inline=False
            )
            embed.set_footer(text="Live stats will work automatically once the API key is activated!")
        else:
            embed = discord.Embed(
                title=f"🚗 {target.display_name}'s Rocket League Profile",
                description=f"**Username:** {username}\n**Platform:** {platform.upper()}\n\n⚠️ Could not fetch live stats: {error_msg}",
                color=0xFF0000,
                url=tracker_url
            )
            embed.add_field(name="📊 View Profile", value=f"[Open Tracker.gg]({tracker_url})", inline=False)
        
        await loading_msg.edit(content=None, embed=embed)
        return
    
    # Parse stats
    try:
        if not stats_data or not isinstance(stats_data, dict):
            stats_data = {}  # type: ignore
        data_dict: dict = stats_data if isinstance(stats_data, dict) else {}
        segments = data_dict.get('data', {}).get('segments', [])
        
        # Get overview segment
        overview = None
        ranked_1v1 = None
        ranked_2v2 = None
        ranked_3v3 = None
        
        for segment in segments:
            seg_type = segment.get('type')
            if seg_type == 'overview':
                overview = segment
            elif seg_type == 'playlist':
                playlist_name = segment.get('metadata', {}).get('name', '')
                if 'Ranked Duel 1v1' in playlist_name:
                    ranked_1v1 = segment
                elif 'Ranked Doubles 2v2' in playlist_name:
                    ranked_2v2 = segment
                elif 'Ranked Standard 3v3' in playlist_name:
                    ranked_3v3 = segment
        
        embed = discord.Embed(
            title=f"🚗 {target.display_name}'s Rocket League Stats",
            description=f"**Username:** {username}\n**Platform:** {platform.upper()}",
            color=0x00BFFF,
            url=tracker_url
        )
        
        # Add overview stats
        if overview:
            stats = overview.get('stats', {})
            wins = stats.get('wins', {}).get('displayValue', 'N/A')
            goals = stats.get('goals', {}).get('displayValue', 'N/A')
            assists = stats.get('assists', {}).get('displayValue', 'N/A')
            saves = stats.get('saves', {}).get('displayValue', 'N/A')
            shots = stats.get('shots', {}).get('displayValue', 'N/A')
            mvps = stats.get('mVPs', {}).get('displayValue', 'N/A')
            
            embed.add_field(
                name="📊 Career Stats",
                value=f"🏆 **Wins:** {wins}\n⚽ **Goals:** {goals}\n🎯 **Assists:** {assists}\n🛡️ **Saves:** {saves}\n🎯 **Shots:** {shots}\n👑 **MVPs:** {mvps}",
                inline=True
            )
        
        # Add ranked stats
        ranked_text = []
        for mode_name, mode_data in [("1v1", ranked_1v1), ("2v2", ranked_2v2), ("3v3", ranked_3v3)]:
            if mode_data:
                rank_info = mode_data.get('stats', {}).get('tier', {})
                mmr_info = mode_data.get('stats', {}).get('rating', {})
                rank_name = rank_info.get('metadata', {}).get('name', 'Unranked')
                mmr = mmr_info.get('displayValue', 'N/A')
                ranked_text.append(f"**{mode_name}:** {rank_name} ({mmr} MMR)")
        
        if ranked_text:
            embed.add_field(
                name="🏅 Ranked Playlists",
                value="\n".join(ranked_text),
                inline=True
            )
        
        embed.add_field(name="📊 Full Profile", value=f"[View on Tracker.gg]({tracker_url})", inline=False)
        embed.set_footer(text="Stats fetched from Tracker.gg API")
        
        await loading_msg.edit(content=None, embed=embed)
        
    except Exception as e:
        print(f"Error parsing RL stats: {e}")
        embed = discord.Embed(
            title=f"🚗 {target.display_name}'s Rocket League Profile",
            description=f"**Username:** {username}\n**Platform:** {platform.upper()}\n\n⚠️ Error parsing stats data",
            color=0xFF0000,
            url=tracker_url
        )
        embed.add_field(name="📊 View Profile", value=f"[Open Tracker.gg]({tracker_url})", inline=False)
        await loading_msg.edit(content=None, embed=embed)

@bot.hybrid_command(name='createclan', aliases=['newclan'])
async def create_clan_command(ctx, *, clan_name: str):
    """Create a new clan/mafia (costs 50,000 chips)
    
    Usage: ~createclan <clan name>
    Example: ~createclan The Family
    """
    # Check verification
    if not await check_verification(ctx):
        return
    
    user_id = str(ctx.author.id)
    
    # Check if user is already in a clan
    existing_clan_id, existing_clan = get_user_clan(user_id)
    if existing_clan:
        await ctx.send(f"❌ You're already in a clan! Leave `{existing_clan['name']}` first using `~clanleave`.")
        return
    
    # Check clan name length
    if len(clan_name) > 30:
        await ctx.send("❌ Clan name must be 30 characters or less!")
        return
    
    if len(clan_name) < 3:
        await ctx.send("❌ Clan name must be at least 3 characters!")
        return
    
    # Check if clan name already exists
    for clan_data in clans.values():
        if clan_data['name'].lower() == clan_name.lower():
            await ctx.send(f"❌ A clan named '{clan_name}' already exists!")
            return
    
    # Check chips (50,000 cost)
    creation_cost = 50000
    user_chips = get_chips(ctx.author.id)
    
    if user_chips < creation_cost and not is_infinite(ctx.author.id):
        await ctx.send(f"❌ Creating a clan costs {creation_cost:,} chips! You have {user_chips:,}.")
        return
    
    # Deduct chips
    if not is_infinite(ctx.author.id):
        remove_chips(ctx.author.id, creation_cost, ctx.author.name, f"Created clan '{clan_name}'")
    
    # Create clan
    clan_id = f"clan_{len(clans) + 1}_{ctx.author.id}"
    clans[clan_id] = {
        "name": clan_name,
        "leader_id": user_id,
        "members": [user_id],
        "vault": 0,
        "created": datetime.now(timezone.utc).isoformat(),
        "officers": []
    }
    save_clans()
    
    embed = discord.Embed(
        title="👔 Clan Created!",
        description=f"**{clan_name}** has been established!",
        color=0x800080
    )
    embed.add_field(name="👑 Leader", value=ctx.author.name, inline=True)
    embed.add_field(name="👥 Members", value="1", inline=True)
    embed.add_field(name="💰 Vault", value="0 chips", inline=True)
    embed.set_footer(text="Invite members using ~claninvite @user")
    
    await ctx.send(embed=embed)

@bot.hybrid_command(name='clan', aliases=['claninfo'])
async def clan_info_command(ctx):
    """View your clan's information
    
    Usage: ~clan
    """
    # Check verification
    if not await check_verification(ctx):
        return
    
    user_id = str(ctx.author.id)
    
    # Get user's clan
    clan_id, clan_data = get_user_clan(user_id)
    
    if not clan_data:
        await ctx.send("❌ You're not in a clan! Create one with `~createclan` or join one with `~clanjoin`.")
        return
    
    # Get leader name
    try:
        leader = await bot.fetch_user(int(clan_data['leader_id']))
        leader_name = leader.name
    except Exception:
        leader_name = "Unknown"
    
    # Build member list
    member_names = []
    for member_id in clan_data['members']:
        try:
            member = await bot.fetch_user(int(member_id))
            role = "👑" if member_id == clan_data['leader_id'] else "⭐" if member_id in clan_data.get('officers', []) else "👤"
            member_names.append(f"{role} {member.name}")
        except Exception:
            pass
    
    embed = discord.Embed(
        title=f"👔 {clan_data['name']}",
        color=0x800080
    )
    embed.add_field(name="👑 Leader", value=leader_name, inline=True)
    embed.add_field(name="👥 Members", value=str(len(clan_data['members'])), inline=True)
    embed.add_field(name="💰 Vault", value=f"{clan_data['vault']:,} chips", inline=True)
    
    embed.add_field(
        name="📋 Member List",
        value="\n".join(member_names[:20]) if member_names else "No members",
        inline=False
    )
    
    embed.set_footer(text="👑 = Leader | ⭐ = Officer | 👤 = Member")
    embed.timestamp = datetime.fromisoformat(clan_data['created'])
    
    await ctx.send(embed=embed)

@bot.hybrid_command(name='claninvite')
async def clan_invite_command(ctx, member: discord.Member):
    """Invite a user to your clan (Leader/Officers only)
    
    Usage: ~claninvite @user
    """
    # Check verification
    if not await check_verification(ctx):
        return
    
    user_id = str(ctx.author.id)
    target_id = str(member.id)
    
    # Get user's clan
    clan_id, clan_data = get_user_clan(user_id)
    
    if not clan_data:
        await ctx.send("❌ You're not in a clan!")
        return
    
    # Check if user is leader or officer
    if user_id != clan_data['leader_id'] and user_id not in clan_data.get('officers', []):
        await ctx.send("❌ Only the clan leader or officers can invite members!")
        return
    
    # Check if target is already in a clan
    target_clan_id, target_clan = get_user_clan(target_id)
    if target_clan:
        await ctx.send(f"❌ {member.name} is already in a clan!")
        return
    
    # Check if target is verified
    if not is_verified(member.id):
        await ctx.send(f"❌ {member.name} must verify first using `~verify`!")
        return
    
    # Send invitation
    try:
        invite_embed = discord.Embed(
            title="👔 Clan Invitation!",
            description=f"**{ctx.author.name}** invited you to join **{clan_data['name']}**!",
            color=0x800080
        )
        invite_embed.add_field(name="💰 Clan Vault", value=f"{clan_data['vault']:,} chips", inline=True)
        invite_embed.add_field(name="👥 Members", value=str(len(clan_data['members'])), inline=True)
        invite_embed.set_footer(text=f"Use ~clanjoin {clan_data['name']} to join!")
        
        await member.send(embed=invite_embed)
        await ctx.send(f"✅ Sent clan invitation to {member.mention}!")
    except discord.Forbidden:
        await ctx.send(f"❌ Couldn't send DM to {member.name}. They need to enable DMs or use `~clanjoin {clan_data['name']}`.")

@bot.hybrid_command(name='clanjoin')
async def clan_join_command(ctx, *, clan_name: str):
    """Join a clan by name
    
    Usage: ~clanjoin <clan name>
    Example: ~clanjoin The Family
    """
    # Check verification
    if not await check_verification(ctx):
        return
    
    user_id = str(ctx.author.id)
    
    # Check if user is already in a clan
    existing_clan_id, existing_clan = get_user_clan(user_id)
    if existing_clan:
        await ctx.send(f"❌ You're already in **{existing_clan['name']}**! Leave first using `~clanleave`.")
        return
    
    # Find clan by name
    target_clan = None
    for cid, cdata in clans.items():
        if cdata['name'].lower() == clan_name.lower():
            target_clan = cdata
            break
    
    if not target_clan:
        await ctx.send(f"❌ No clan named '{clan_name}' exists! Use `~clans` to see all clans.")
        return
    
    # Add user to clan
    target_clan['members'].append(user_id)
    save_clans()
    
    embed = discord.Embed(
        title="✅ Joined Clan!",
        description=f"You joined **{target_clan['name']}**!",
        color=0x00FF00
    )
    embed.add_field(name="👥 Total Members", value=str(len(target_clan['members'])), inline=True)
    embed.add_field(name="💰 Clan Vault", value=f"{target_clan['vault']:,} chips", inline=True)
    
    await ctx.send(embed=embed)

@bot.hybrid_command(name='clanleave')
async def clan_leave_command(ctx):
    """Leave your current clan
    
    Usage: ~clanleave
    """
    # Check verification
    if not await check_verification(ctx):
        return
    
    user_id = str(ctx.author.id)
    
    # Get user's clan
    clan_id, clan_data = get_user_clan(user_id)
    
    if not clan_data:
        await ctx.send("❌ You're not in a clan!")
        return
    
    # Check if user is leader
    if user_id == clan_data['leader_id']:
        # Transfer leadership or disband
        if len(clan_data['members']) > 1:
            await ctx.send("❌ As the leader, you must transfer leadership (`~clantransfer`) or kick all members before leaving!")
            return
        else:
            # Disband clan (leader is only member)
            del clans[clan_id]
            save_clans()
            await ctx.send(f"👋 You left and disbanded **{clan_data['name']}**.")
            return
    
    # Remove user from clan
    clan_data['members'].remove(user_id)
    
    # Remove from officers if applicable
    if user_id in clan_data.get('officers', []):
        clan_data['officers'].remove(user_id)
    
    save_clans()
    
    await ctx.send(f"👋 You left **{clan_data['name']}**.")

@bot.hybrid_command(name='clankick')
async def clan_kick_command(ctx, member: discord.Member):
    """Kick a member from your clan (Leader only)
    
    Usage: ~clankick @user
    """
    # Check verification
    if not await check_verification(ctx):
        return
    
    user_id = str(ctx.author.id)
    target_id = str(member.id)
    
    # Get user's clan
    clan_id, clan_data = get_user_clan(user_id)
    
    if not clan_data:
        await ctx.send("❌ You're not in a clan!")
        return
    
    # Check if user is leader
    if user_id != clan_data['leader_id']:
        await ctx.send("❌ Only the clan leader can kick members!")
        return
    
    # Check if target is in the clan
    if target_id not in clan_data['members']:
        await ctx.send(f"❌ {member.name} is not in your clan!")
        return
    
    # Can't kick yourself
    if target_id == user_id:
        await ctx.send("❌ You can't kick yourself! Use `~clanleave` instead.")
        return
    
    # Kick member
    clan_data['members'].remove(target_id)
    
    # Remove from officers if applicable
    if target_id in clan_data.get('officers', []):
        clan_data['officers'].remove(target_id)
    
    save_clans()
    
    await ctx.send(f"👢 Kicked **{member.name}** from **{clan_data['name']}**.")

@bot.hybrid_command(name='clandeposit', aliases=['clandep'])
async def clan_deposit_command(ctx, amount: str):
    """Deposit chips into your clan's vault
    
    Usage: ~clandeposit <amount>
    Examples: ~clandeposit 1000, ~clandeposit all
    """
    # Check verification
    if not await check_verification(ctx):
        return
    
    user_id = str(ctx.author.id)
    
    # Get user's clan
    clan_id, clan_data = get_user_clan(user_id)
    
    if not clan_data:
        await ctx.send("❌ You're not in a clan!")
        return
    
    # Parse amount
    bet_amount = parse_bet_amount(amount, get_chips(ctx.author.id))
    
    if bet_amount is None:
        await ctx.send("❌ Invalid amount! Use a number or 'all'.")
        return
    
    if bet_amount <= 0:
        await ctx.send("❌ Amount must be greater than 0!")
        return
    
    # Check if user has enough chips
    user_chips = get_chips(ctx.author.id)
    if user_chips < bet_amount:
        await ctx.send(f"❌ You don't have enough chips! You have {user_chips:,}, need {bet_amount:,}.")
        return
    
    # Transfer chips to clan vault
    remove_chips(ctx.author.id, bet_amount, ctx.author.name, f"Deposited to clan '{clan_data['name']}'")
    clan_data['vault'] += bet_amount
    save_clans()
    
    embed = discord.Embed(
        title="💰 Clan Deposit",
        description=f"Deposited **{bet_amount:,}** chips to **{clan_data['name']}**'s vault!",
        color=0x00FF00
    )
    embed.add_field(name="New Clan Vault", value=f"{clan_data['vault']:,} chips", inline=True)
    embed.add_field(name="Your Balance", value=format_chips(ctx.author.id), inline=True)
    
    await ctx.send(embed=embed)

@bot.hybrid_command(name='clanwithdraw', aliases=['clanwith'])
async def clan_withdraw_command(ctx, amount: str):
    """Withdraw chips from clan vault (Leader/Officers only)
    
    Usage: ~clanwithdraw <amount>
    Examples: ~clanwithdraw 1000, ~clanwithdraw all
    """
    # Check verification
    if not await check_verification(ctx):
        return
    
    user_id = str(ctx.author.id)
    
    # Get user's clan
    clan_id, clan_data = get_user_clan(user_id)
    
    if not clan_data:
        await ctx.send("❌ You're not in a clan!")
        return
    
    # Check if user is leader or officer
    if user_id != clan_data['leader_id'] and user_id not in clan_data.get('officers', []):
        await ctx.send("❌ Only the clan leader or officers can withdraw from the vault!")
        return
    
    # Parse amount
    bet_amount = parse_bet_amount(amount, clan_data['vault'])
    
    if bet_amount is None:
        await ctx.send("❌ Invalid amount! Use a number or 'all'.")
        return
    
    if bet_amount <= 0:
        await ctx.send("❌ Amount must be greater than 0!")
        return
    
    # Check if clan has enough in vault
    if clan_data['vault'] < bet_amount:
        await ctx.send(f"❌ Clan vault doesn't have enough! Vault has {clan_data['vault']:,}, need {bet_amount:,}.")
        return
    
    # Transfer chips from vault to user
    clan_data['vault'] -= bet_amount
    add_chips(ctx.author.id, bet_amount, ctx.author.name, f"Withdrew from clan '{clan_data['name']}'")
    save_clans()
    
    embed = discord.Embed(
        title="💼 Clan Withdrawal",
        description=f"Withdrew **{bet_amount:,}** chips from **{clan_data['name']}**'s vault!",
        color=0x00FF00
    )
    embed.add_field(name="New Clan Vault", value=f"{clan_data['vault']:,} chips", inline=True)
    embed.add_field(name="Your Balance", value=format_chips(ctx.author.id), inline=True)
    
    await ctx.send(embed=embed)

@bot.hybrid_command(name='clans', aliases=['clanlist'])
async def clans_list_command(ctx):
    """View all clans
    
    Usage: ~clans
    """
    if not clans:
        await ctx.send("❌ No clans exist yet! Create one with `~createclan`.")
        return
    
    # Sort clans by vault size
    sorted_clans = sorted(clans.items(), key=lambda x: x[1]['vault'], reverse=True)
    
    embed = discord.Embed(
        title="👔 All Clans",
        description=f"Total Clans: {len(clans)}",
        color=0x800080
    )
    
    clan_list = []
    for i, (clan_id, clan_data) in enumerate(sorted_clans[:15], 1):
        clan_list.append(
            f"`#{i}` **{clan_data['name']}**\n"
            f"👥 {len(clan_data['members'])} members | 💰 {clan_data['vault']:,} chips"
        )
    
    embed.add_field(name="Top Clans by Vault", value="\n\n".join(clan_list), inline=False)
    embed.set_footer(text="Use ~clanjoin <clan name> to join a clan!")
    
    await ctx.send(embed=embed)

@bot.hybrid_command(name='clanleaderboard', aliases=['clanlb'])
async def clan_leaderboard_command(ctx, limit: int = 10):
    """View top clans by vault
    
    Usage: ~clanleaderboard [limit]
    Example: ~clanleaderboard 15
    """
    if limit < 1:
        limit = 10
    if limit > 25:
        limit = 25
    
    if not clans:
        await ctx.send("❌ No clans exist yet!")
        return
    
    # Sort clans by vault
    sorted_clans = sorted(clans.items(), key=lambda x: x[1]['vault'], reverse=True)
    top_clans = sorted_clans[:limit]
    
    embed = discord.Embed(
        title="🏆 Clan Leaderboard",
        description=f"Top {len(top_clans)} richest clans",
        color=0xFFD700
    )
    
    leaderboard_text = []
    medals = ["🥇", "🥈", "🥉"]
    
    for i, (clan_id, clan_data) in enumerate(top_clans, 1):
        if i <= 3:
            medal = medals[i-1]
        else:
            medal = f"`#{i}`"
        
        leaderboard_text.append(
            f"{medal} **{clan_data['name']}**\n"
            f"    💰 {clan_data['vault']:,} chips | 👥 {len(clan_data['members'])} members"
        )
    
    embed.add_field(name="Rankings", value="\n\n".join(leaderboard_text), inline=False)
    embed.set_footer(text=f"Total Clans: {len(clans)}")
    
    await ctx.send(embed=embed)

@bot.hybrid_command(name='challenges')
async def prefix_challenges(ctx):
    """View all challenges and your progress"""
    user_id = str(ctx.author.id)
    init_user_challenges(user_id)
    
    embed = discord.Embed(
        title="🏆 Challenges",
        description="Complete challenges to earn bonus chips!",
        color=0x9B59B6
    )
    
    # Group challenges by completion status
    active_challenges = []
    completed_challenges = []
    
    for chal_id, challenge in CHALLENGES.items():
        is_completed = chal_id in user_challenges[user_id]["completed"]
        
        # Get current progress
        if challenge["type"] == "total_winnings":
            current = user_challenges[user_id]["total_winnings"]
        elif challenge["type"] == "streak":
            current = user_challenges[user_id]["current_streak"]
        elif challenge["type"] == "claims":
            current = len(user_challenges[user_id]["claims_made"])
        else:
            current = user_challenges[user_id]["progress"].get(chal_id, 0)
        
        target = challenge["target"]
        
        # Create progress bar
        if is_completed:
            progress_bar = "✅ COMPLETED"
            status_line = f"{challenge['emoji']} **{challenge['name']}** | Reward: {challenge['reward']} chips"
            completed_challenges.append(f"{status_line}\n{progress_bar}")
        else:
            percent = min(100, int((current / target) * 100))
            filled = int(percent / 10)
            bar = "█" * filled + "░" * (10 - filled)
            progress_bar = f"[{bar}] {current}/{target}"
            status_line = f"{challenge['emoji']} **{challenge['name']}** | {challenge['reward']} chips"
            active_challenges.append(f"{status_line}\n*{challenge['description']}*\n{progress_bar}")
    
    # Add active challenges
    if active_challenges:
        embed.add_field(
            name="📌 Active Challenges",
            value="\n\n".join(active_challenges[:5]),  # Show first 5
            inline=False
        )
        if len(active_challenges) > 5:
            embed.add_field(
                name="",
                value="\n\n".join(active_challenges[5:]),
                inline=False
            )
    
    # Add completed challenges
    if completed_challenges:
        embed.add_field(
            name="✨ Completed",
            value="\n".join(completed_challenges),
            inline=False
        )
    
    # Add stats
    total_earned = sum(CHALLENGES[c]["reward"] for c in user_challenges[user_id]["completed"])
    embed.set_footer(text=f"Completed: {len(user_challenges[user_id]['completed'])}/{len(CHALLENGES)} | Total Earned: {total_earned} chips")
    
    await ctx.send(embed=embed)

class GuidePaginator(discord.ui.View):
    """Interactive paginated guide with category navigation"""
    def __init__(self, ctx, is_admin: bool):
        super().__init__(timeout=180)
        self.ctx = ctx
        self.is_admin = is_admin
        self.current_page = 0
        self.message = None
        
        # Create all pages
        self.pages = self.create_pages()
    
    def create_pages(self):
        """Create all guide pages"""
        pages = []
        
        # Page 1: Getting Started & Economy
        page1 = discord.Embed(
            title="📚 Command Guide - Getting Started & Economy",
            color=0x3498db
        )
        page1.add_field(
            name="🚀 Getting Started",
            value=(
                "`~verify` - Verify to start playing casino games\n"
                "`~balance` or `~bal` - Check your chips & tickets\n"
                "`~profile [@user]` - View detailed player profile\n"
                "`~viptiers` - View all VIP ranks and bonuses"
            ),
            inline=False
        )
        page1.add_field(
            name="💰 Economy & Claims",
            value=(
                "`~claim` - Daily/weekly/monthly/yearly chip claims\n"
                "`~work` - Work a job for chips (30 min cooldown)\n"
                "`~job` or `~jobs` - View available jobs\n"
                "`~buytickets <amount>` - Trade chips for tickets\n"
                "`~shop` - View daily rotating shop (<t:1762984800:t>)\n"
                "`~use <item_id>` - Activate purchased items"
            ),
            inline=False
        )
        page1.set_footer(text="💡 100,000 chips = 1 ticket")
        pages.append(page1)
        
        # Page 2: Banking & Clans
        page2 = discord.Embed(
            title="📚 Command Guide - Banking & Clans",
            color=0x9b59b6
        )
        page2.add_field(
            name="🏦 Banking System",
            value=(
                "`~bank [@user]` - View wallet & bank balance\n"
                "`~deposit <amount>` - Store chips safely\n"
                "`~withdraw <amount>` - Withdraw from bank\n\n"
                "💡 **Bank chips cannot be stolen with ~rob!**"
            ),
            inline=False
        )
        page2.add_field(
            name="👔 Clans/Mafia",
            value=(
                "`~createclan <name>` - Create clan (50k chips)\n"
                "`~clan` - View your clan info\n"
                "`~claninvite @user` - Invite member\n"
                "`~clanjoin <name>` - Join a clan\n"
                "`~clanleave` - Leave current clan\n"
                "`~clankick @user` - Remove member (leader)\n"
                "`~clandeposit <amount>` - Add to vault\n"
                "`~clanwithdraw <amount>` - Withdraw (leader/officer)\n"
                "`~clans` - List all clans\n"
                "`~clanleaderboard` - Top clans by vault"
            ),
            inline=False
        )
        page2.set_footer(text="💡 Pool resources with your clan for team cooperation!")
        pages.append(page2)
        
        # Page 3: Casino Games (Solo)
        page3 = discord.Embed(
            title="📚 Command Guide - Casino Games (Solo)",
            color=0xe74c3c
        )
        page3.add_field(
            name="🎰 Slot & Dice Games",
            value=(
                "`~slots <bet>` - Spin 3-reel slot machine\n"
                "`~wheel <bet>` - Spin fortune wheel (0x-10x)\n"
                "`~dice <bet>` - Roll dice games"
            ),
            inline=False
        )
        page3.add_field(
            name="🃏 Card Games",
            value=(
                "`~blackjack <bet>` - Play 21 against dealer\n"
                "`~poker <bet>` - 5-Card Draw poker\n"
                "`~hilo <bet>` - Guess higher/lower cards"
            ),
            inline=False
        )
        page3.add_field(
            name="🎲 Table & Advanced Games",
            value=(
                "`~roulette <bet> <type>` - Bet red/black/number\n"
                "`~craps <bet>` - Interactive dice casino game\n"
                "`~crash <bet>` - Cash out before multiplier crashes\n"
                "`~mines <bet> <easy/medium/hard>` - Minesweeper betting"
            ),
            inline=False
        )
        page3.set_footer(text="💡 Use 'all' or 'half' for bet amounts | Use ~games to see all games")
        pages.append(page3)
        
        # Page 4: Multiplayer & Social
        page4 = discord.Embed(
            title="📚 Command Guide - Multiplayer & Social",
            color=0xf39c12
        )
        page4.add_field(
            name="🎮 Multiplayer Games",
            value=(
                "`~coinflip @user <bet>` - PvP coinflip battle\n"
                "`~pokermp start/join/play` - Texas Hold'em (2-6 players)\n"
                "`~roulettemp open/bet/spin` - Multiplayer roulette wheel\n\n"
                "💡 **Compete against other players!**"
            ),
            inline=False
        )
        page4.add_field(
            name="👥 Social & Trading",
            value=(
                "`~leaderboard [limit]` - Top richest players\n"
                "`~mt @user` - Multi-trade with players\n"
                "`~rob @user` - Attempt to rob a player\n"
                "`~bounty @user <amount>` - Place bounty\n"
                "`~bounties` - View active bounties\n"
                "`~claim @user` - Claim bounty on player"
            ),
            inline=False
        )
        page4.add_field(
            name="🐾 Pets & Collectibles",
            value=(
                "`~rollpet` - Roll for a pet (1 ticket)\n"
                "`~pets [@user]` - View pet collection\n"
                "`~setidol <pet_id>` - Set profile display pet"
            ),
            inline=False
        )
        page4.set_footer(text="💡 Leaderboards are server-specific! 20 unique pets across 6 rarity tiers!")
        pages.append(page4)
        
        # Page 5: Rocket League & Progression
        page5 = discord.Embed(
            title="📚 Command Guide - Rocket League & Progression",
            color=0x1abc9c
        )
        page5.add_field(
            name="🚗 Rocket League Integration",
            value=(
                "`~setrank <rank>` - Manually set your RL rank\n"
                "`~rllb [limit]` - RL rank leaderboard\n"
                "`~setrlprofile <platform> <username>` - Link Tracker.gg\n"
                "`~rlstats [@user]` - Fetch live stats from Tracker.gg API\n\n"
                "💡 **Platforms:** epic, steam, psn, xbl, switch"
            ),
            inline=False
        )
        page5.add_field(
            name="📈 Progression & Challenges",
            value=(
                "`~challenges` - View all challenges & progress\n"
                "`~inventory [@user]` - View items & active boosts\n"
                "`~setbanner <url>` - Set custom profile banner\n"
                "`~removebanner` - Remove profile banner"
            ),
            inline=False
        )
        page5.add_field(
            name="🔐 Secret Codes",
            value=(
                "`/secret <code>` - Redeem secret codes\n"
                "`~<code>` - Also works with prefix\n\n"
                "💡 **40 codes worth 7.7k-100k chips!**"
            ),
            inline=False
        )
        page5.set_footer(text="💡 Live stats powered by Tracker.gg API!")
        pages.append(page5)
        
        # Page 6: New Systems (Quests, Prestige, Stats, Birthday, Referral)
        page6 = discord.Embed(
            title="📚 Command Guide - New Systems & Features",
            color=0x9b59b6
        )
        page6.add_field(
            name="📋 Daily Quests & Progression",
            value=(
                "`~quests` - View 3 daily missions with rewards\n"
                "`~prestige` - Reset for permanent multipliers (+5% per tier)\n"
                "`~mystats` - Personal game stats (wins %, ROI, favorite game)\n\n"
                "💡 **Complete quests daily for bonus chips!**"
            ),
            inline=False
        )
        page6.add_field(
            name="🎂 Birthday & Referrals",
            value=(
                "`~birthday <MM-DD>` - Set birthday for annual bonus\n"
                "`~refer link` - Get your referral code\n"
                "`~refer use @user` - Use someone's code (+500 chips)\n"
                "`~refer` - View referral stats\n\n"
                "💡 **Invite friends and earn bonuses!**"
            ),
            inline=False
        )
        page6.set_footer(text="💫 New progression systems unlock more ways to earn and compete!")
        pages.append(page6)
        
        # Page 7: Admin Commands (only if admin)
        if self.is_admin:
            page7 = discord.Embed(
                title="📚 Command Guide - Administrator Commands",
                color=0xe67e22
            )
            page7.add_field(
                name="👤 User Management",
                value=(
                    "`~verifyuser @user` - Manually verify user\n"
                    "`~unverify @user` - Remove verification"
                ),
                inline=False
            )
            page7.add_field(
                name="💎 Economy Management",
                value=(
                    "`~addchips @user <amount>` - Give chips\n"
                    "`~resetbalance @user` - Reset balance\n"
                    "`~infinite @user` - Toggle infinite chips\n"
                    "`~chipslog [limit]` - View transactions\n"
                    "`~resetclaim @user` - Reset cooldowns"
                ),
                inline=False
            )
            page7.add_field(
                name="📊 Casino Analytics",
                value=(
                    "`~record` - House profit/loss statistics\n"
                    "`~secrets` - View all 40 secret codes"
                ),
                inline=False
            )
            page7.add_field(
                name="⚙️ Bot Configuration",
                value=(
                    "`~setprefix <prefix>` - Change bot prefix\n"
                    "`~bumpreminder <channel>` - Setup reminders\n"
                    "`~bumpdisable` - Disable reminders"
                ),
                inline=False
            )
            page7.set_footer(text="🛡️ Admin-only commands")
            pages.append(page7)
        
        return pages
    
    def update_buttons(self):
        """Update button states based on current page"""
        for item in self.children:
            if isinstance(item, discord.ui.Button):
                if item.label and "Previous" in item.label:
                    item.disabled = self.current_page == 0
                elif item.label and "Next" in item.label:
                    item.disabled = self.current_page == len(self.pages) - 1
                elif item.label and "Page" in item.label:
                    item.label = f"Page {self.current_page + 1}/{len(self.pages)}"
    
    @discord.ui.button(label="◀ Previous", style=discord.ButtonStyle.primary, disabled=True)
    async def previous_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.ctx.author.id:
            await interaction.response.send_message("❌ This isn't your guide!", ephemeral=True)
            return
        
        self.current_page -= 1
        self.update_buttons()
        await interaction.response.edit_message(embed=self.pages[self.current_page], view=self)
    
    @discord.ui.button(label="Page 1/5", style=discord.ButtonStyle.secondary, disabled=True)
    async def page_indicator(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
    
    @discord.ui.button(label="Next ▶", style=discord.ButtonStyle.primary)
    async def next_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.ctx.author.id:
            await interaction.response.send_message("❌ This isn't your guide!", ephemeral=True)
            return
        
        self.current_page += 1
        self.update_buttons()
        await interaction.response.edit_message(embed=self.pages[self.current_page], view=self)
    
    async def on_timeout(self):
        """Disable all buttons when timeout occurs"""
        for child in self.children:
            if isinstance(child, discord.ui.Button):
                child.disabled = True
        
        if self.message:
            try:
                await self.message.edit(view=self)
            except discord.HTTPException:
                pass

@bot.hybrid_command(name='guide')
async def guide_command(ctx):
    """Complete interactive guide of all bot commands with pagination
    
    Usage: ~guide
    Use Previous/Next buttons to navigate through command categories
    """
    # Check if user is admin
    is_admin = ctx.author.guild_permissions.administrator if ctx.guild else False
    
    # Create paginated view
    view = GuidePaginator(ctx, is_admin)
    
    # Initialize button states
    view.update_buttons()
    
    # Send initial page
    message = await ctx.send(embed=view.pages[0], view=view)
    view.message = message

def load_staff_data():
    """Load staff data from file"""
    global staff_data
    if os.path.exists(STAFF_FILE):
        try:
            with open(STAFF_FILE, "r") as f:
                staff_data = json.load(f)
        except Exception as e:
            print(f"Error loading staff data: {e}")
            init_staff_data()
    else:
        init_staff_data()

def init_staff_data():
    """Initialize default staff data"""
    global staff_data
    staff_data = {
        "343055455263916045": {
            "name": "Kurse",
            "position": "Owner",
            "description": "he/him | 21 | NA/PST. Gaming, streaming, Pokémon Go, and Rocket League enthusiast. Loves Rocket League, Pokémon Go, and Tokyo Ghoul-inspired games. Open to VC and text!",
            "extras": "Proud owner of Re: Kurse! Got server suggestions? I'm all ears ❤️ Streams on Twitch + YouTube (check out the stream alerts for when I go live!)"
        },
        "697495071737511997": {
            "name": "Cocoa",
            "position": "Admin",
            "description": "Gaming, running, fútbol. Plays almost any game when asked. Open DMs and friend requests.",
            "extras": "Mile time is 5:30."
        },
        "187729483174903808": {
            "name": "Getsleepad",
            "position": "Admin",
            "description": "Add your description here!",
            "extras": "Add fun facts here!"
        },
        "525815097847840798": {
            "name": "Luvlis_time",
            "position": "Admin",
            "description": "Add your description here!",
            "extras": "Add fun facts here!"
        },
        "760075655374176277": {
            "name": "Nanizzz",
            "position": "Admin",
            "description": "Add your description here!",
            "extras": "Add fun facts here!"
        },
        "504812129560428554": {
            "name": "Tillyoudecay",
            "position": "Mod",
            "description": "Add your description here!",
            "extras": "Add fun facts here!"
        },
        "878870610158178335": {
            "name": "Lightningmint.",
            "position": "Jr Mod",
            "description": "Add your description here!",
            "extras": "Add fun facts here!"
        },
        "1131474199286907000": {
            "name": "Shanksdagoat",
            "position": "Jr Mod",
            "description": "Add your description here!",
            "extras": "Add fun facts here!"
        }
    }
    save_staff_data()

def save_staff_data():
    """Save staff data to file"""
    try:
        with open(STAFF_FILE, "w") as f:
            json.dump(staff_data, f, indent=2)
    except Exception as e:
        print(f"Error saving staff data: {e}")

def load_login_streaks():
    """Load login streaks from file"""
    global login_streaks
    try:
        if os.path.exists(STREAKS_FILE):
            with open(STREAKS_FILE, 'r') as f:
                login_streaks = json.load(f)
    except Exception as e:
        print(f"Error loading login streaks: {e}")
        login_streaks = {}

def save_login_streaks():
    """Save login streaks to file"""
    try:
        with open(STREAKS_FILE, 'w') as f:
            json.dump(login_streaks, f, indent=2)
    except Exception as e:
        print(f"Error saving login streaks: {e}")

def load_game_history():
    """Load game history from file"""
    global game_history
    try:
        if os.path.exists(GAME_HISTORY_FILE):
            with open(GAME_HISTORY_FILE, 'r') as f:
                game_history = json.load(f)
    except Exception as e:
        print(f"Error loading game history: {e}")
        game_history = {}

def save_game_history():
    """Save game history to file"""
    try:
        with open(GAME_HISTORY_FILE, 'w') as f:
            json.dump(game_history, f, indent=2)
    except Exception as e:
        print(f"Error saving game history: {e}")

def update_login_streak(user_id):
    """Update login streak for user and award bonus chips"""
    user_id = str(user_id)
    init_player_stats(user_id)
    
    today = datetime.now().date().isoformat()
    last_login = login_streaks[user_id].get("last_login")
    
    if last_login == today:
        # Already logged in today
        return 0
    
    yesterday = (datetime.now().date() - timedelta(days=1)).isoformat()
    
    if last_login == yesterday:
        # Consecutive day
        login_streaks[user_id]["current_streak"] += 1
    else:
        # Streak broken or first login
        login_streaks[user_id]["current_streak"] = 1
    
    login_streaks[user_id]["last_login"] = today
    
    # Update longest streak
    if login_streaks[user_id]["current_streak"] > login_streaks[user_id].get("longest_streak", 0):
        login_streaks[user_id]["longest_streak"] = login_streaks[user_id]["current_streak"]
    
    # Award bonus chips: 10 * current_streak
    bonus = 10 * login_streaks[user_id]["current_streak"]
    add_chips(user_id, bonus)
    save_login_streaks()
    
    return bonus

def load_daily_quests():
    """Load daily quests from file"""
    global daily_quests
    try:
        if os.path.exists(DAILY_QUESTS_FILE):
            with open(DAILY_QUESTS_FILE, 'r') as f:
                daily_quests = json.load(f)
    except Exception as e:
        print(f"Error loading daily quests: {e}")
        daily_quests = {}

def save_daily_quests():
    """Save daily quests to file"""
    try:
        with open(DAILY_QUESTS_FILE, 'w') as f:
            json.dump(daily_quests, f, indent=2)
    except Exception as e:
        print(f"Error saving daily quests: {e}")

def load_prestige_data():
    """Load prestige data from file"""
    global prestige_data
    try:
        if os.path.exists(PRESTIGE_FILE):
            with open(PRESTIGE_FILE, 'r') as f:
                prestige_data = json.load(f)
    except Exception as e:
        print(f"Error loading prestige data: {e}")
        prestige_data = {}

def save_prestige_data():
    """Save prestige data to file"""
    try:
        with open(PRESTIGE_FILE, 'w') as f:
            json.dump(prestige_data, f, indent=2)
    except Exception as e:
        print(f"Error saving prestige data: {e}")

def load_birthdays():
    """Load birthdays from file"""
    global user_birthdays
    try:
        if os.path.exists(BIRTHDAYS_FILE):
            with open(BIRTHDAYS_FILE, 'r') as f:
                user_birthdays = json.load(f)
    except Exception as e:
        print(f"Error loading birthdays: {e}")
        user_birthdays = {}

def save_birthdays():
    """Save birthdays to file"""
    try:
        with open(BIRTHDAYS_FILE, 'w') as f:
            json.dump(user_birthdays, f, indent=2)
    except Exception as e:
        print(f"Error saving birthdays: {e}")

def load_referrals():
    """Load referral data from file"""
    global referral_data
    try:
        if os.path.exists(REFERRALS_FILE):
            with open(REFERRALS_FILE, 'r') as f:
                referral_data = json.load(f)
    except Exception as e:
        print(f"Error loading referrals: {e}")
        referral_data = {}

def save_referrals():
    """Save referral data to file"""
    try:
        with open(REFERRALS_FILE, 'w') as f:
            json.dump(referral_data, f, indent=2)
    except Exception as e:
        print(f"Error saving referrals: {e}")

class StaffPaginator(discord.ui.View):
    """Interactive paginated staff directory"""
    def __init__(self, ctx):
        super().__init__(timeout=180)
        self.ctx = ctx
        self.current_page = 0
        self.message = None
        self.staff_list = list(staff_data.items())  # [(user_id, data), ...]
        self.create_pages()
        self.update_buttons()
    
    def create_pages(self):
        """Create pages for each staff member"""
        self.pages = []
        
        for user_id, member_data in self.staff_list:
            embed = discord.Embed(
                title="[STAFF DIRECTORY]",
                description="",
                color=0xFF8C00
            )
            
            name = member_data.get("name", "Unknown")
            position = member_data.get("position", "Staff")
            description = member_data.get("description", "No description")
            extras = member_data.get("extras", "")
            
            member_info = f"**Name:** {name}\n**Position:** {position}\n\n**About:**\n{description}"
            if extras:
                member_info += f"\n\n**Fun Fact:**\n{extras}"
            
            embed.add_field(
                name="=" * 36,
                value=member_info,
                inline=False
            )
            
            embed.set_footer(text=f"Page {len(self.pages) + 1}/{len(self.staff_list)}")
            self.pages.append(embed)
    
    def update_buttons(self):
        """Update button states"""
        self.previous_button.disabled = self.current_page == 0
        self.next_button.disabled = self.current_page == len(self.pages) - 1
        self.page_indicator.label = f"{self.current_page + 1}/{len(self.pages)}"
    
    @discord.ui.button(label="◀ Previous", style=discord.ButtonStyle.primary, disabled=True)
    async def previous_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.ctx.author.id:
            await interaction.response.send_message("❌ This isn't your staff list!", ephemeral=True)
            return
        
        self.current_page -= 1
        self.update_buttons()
        await interaction.response.edit_message(embed=self.pages[self.current_page], view=self)
    
    @discord.ui.button(label="1/4", style=discord.ButtonStyle.secondary, disabled=True)
    async def page_indicator(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
    
    @discord.ui.button(label="Next ▶", style=discord.ButtonStyle.primary)
    async def next_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.ctx.author.id:
            await interaction.response.send_message("❌ This isn't your staff list!", ephemeral=True)
            return
        
        self.current_page += 1
        self.update_buttons()
        await interaction.response.edit_message(embed=self.pages[self.current_page], view=self)
    
    async def on_timeout(self):
        """Disable all buttons when timeout occurs"""
        for child in self.children:
            if isinstance(child, discord.ui.Button):
                child.disabled = True
        
        if self.message:
            try:
                await self.message.edit(view=self)
            except discord.HTTPException:
                pass

@bot.hybrid_command(name='staff')
async def staff_command(ctx):
    """View the server staff directory with pagination
    
    Usage: ~staff
    Navigate through pages using Previous/Next buttons
    """
    view = StaffPaginator(ctx)
    message = await ctx.send(embed=view.pages[0], view=view)
    view.message = message

@bot.hybrid_command(name='staffedit')
async def staffedit_command(ctx, *, new_description: Optional[str] = None):
    """Edit your own staff profile (Staff only)
    
    Usage: ~staffedit <description>|<fun_fact>
    Separate description and fun fact with a pipe |
    Example: ~staffedit Gaming and coding lover|I have 2 cats
    """
    user_id = str(ctx.author.id)
    
    # Check if user is staff
    if ctx.author.id not in STAFF_IDS:
        await ctx.send("❌ Only staff members can edit staff profiles!")
        return
    
    if not new_description or '|' not in new_description:
        await ctx.send("❌ Usage: `~staffedit <description>|<fun_fact>`\nExample: `~staffedit Gaming lover|I have 2 cats`")
        return
    
    parts = new_description.split('|', 1)
    description = parts[0].strip()
    extras = parts[1].strip()
    
    if user_id not in staff_data:
        await ctx.send("❌ You're not in the staff directory!")
        return
    
    # Check if trying to edit someone else's profile
    if user_id != str(ctx.author.id):
        await ctx.send("❌ You can only edit your own profile!")
        return
    
    # Update staff data
    staff_data[user_id]['description'] = description
    staff_data[user_id]['extras'] = extras
    save_staff_data()
    
    embed = discord.Embed(
        title="✅ Profile Updated!",
        color=0x00FF00
    )
    embed.add_field(name="About", value=description, inline=False)
    embed.add_field(name="Fun Fact", value=extras, inline=False)
    
    await ctx.send(embed=embed)

class ShopPaginator(discord.ui.View):
    """Interactive paginated shop with buy buttons"""
    def __init__(self, ctx):
        super().__init__(timeout=180)
        self.ctx = ctx
        self.current_page = 0
        self.message = None
        
        # Get current holiday for title
        self.current_holiday = get_current_holiday()
        
        # Create shop pages (2 items per page)
        self.shop_items_list = list(shop_items.items())
        self.total_pages = (len(self.shop_items_list) + 1) // 2  # 2 items per page
        
        self.update_buttons()
    
    def create_embed(self):
        """Create embed for current page"""
        holiday_tag = ""
        if self.current_holiday:
            holiday_emojis = {
                "christmas": "🎄",
                "halloween": "🎃",
                "new_year": "🎆",
                "valentines": "💘",
                "easter": "🐰",
                "summer": "🌞",
                "thanksgiving": "🦃"
            }
            emoji = holiday_emojis.get(self.current_holiday, "🎉")
            holiday_tag = f" {emoji} {self.current_holiday.upper()} EVENT!"
        
        embed = discord.Embed(
            title=f"🛒 Casino Shop — Available Today{holiday_tag}",
            description=f"Buy boosts, perks, and special items with your chips!\n\n🔄 **Next rotation:** <t:1762984800:t>\n\n**Your Balance:** <:Casino_Chip:1437456315025719368> {format_chips(self.ctx.author.id)} chips | 🎫 {get_tickets(self.ctx.author.id)} tickets",
            color=0x5865F2
        )
        
        # Get items for current page (2 per page)
        start_idx = self.current_page * 2
        end_idx = min(start_idx + 2, len(self.shop_items_list))
        page_items = self.shop_items_list[start_idx:end_idx]
        
        for item_key, item in page_items:
            description = item.get('description', 'No description available.')
            embed.add_field(
                name=f"{item['name']} — {item['price']:,} chips",
                value=f"{description}\n**ID:** `{item_key}`",
                inline=False
            )
        
        embed.set_footer(text=f"Page {self.current_page + 1}/{self.total_pages} | Click buttons below to purchase or navigate")
        return embed
    
    def update_buttons(self):
        """Update button states based on current page"""
        self.clear_items()
        
        # Get items for current page
        start_idx = self.current_page * 2
        end_idx = min(start_idx + 2, len(self.shop_items_list))
        page_items = self.shop_items_list[start_idx:end_idx]
        
        # Add buy buttons for items on this page
        for item_key, item in page_items:
            button = discord.ui.Button(
                label=f"Buy {item['name'][:20]}",
                style=discord.ButtonStyle.success,
                custom_id=f"buy_{item_key}",
                emoji="💰"
            )
            button.callback = self.create_buy_callback(item_key)
            self.add_item(button)
        
        # Add navigation buttons
        prev_button = discord.ui.Button(
            label="◀ Previous",
            style=discord.ButtonStyle.secondary,
            disabled=(self.current_page == 0)
        )
        prev_button.callback = self.previous_page
        self.add_item(prev_button)
        
        next_button = discord.ui.Button(
            label="Next ▶",
            style=discord.ButtonStyle.secondary,
            disabled=(self.current_page >= self.total_pages - 1)
        )
        next_button.callback = self.next_page
        self.add_item(next_button)
    
    def create_buy_callback(self, item_id):
        """Create a callback function for buy button"""
        async def callback(interaction: discord.Interaction):
            # Check if it's the correct user
            if interaction.user.id != self.ctx.author.id:
                await interaction.response.send_message("❌ This is not your shop session!", ephemeral=True)
                return
            
            # Check if item still exists
            if item_id not in shop_items:
                await interaction.response.send_message("❌ Item no longer available!", ephemeral=True)
                return
            
            item = shop_items[item_id]
            user_chips = get_chips(self.ctx.author.id)
            
            if user_chips < item['price']:
                await interaction.response.send_message(
                    f"❌ Not enough chips! Need {item['price']:,}, have {user_chips:,}.",
                    ephemeral=True
                )
                return
            
            # Purchase item
            remove_chips(self.ctx.author.id, item['price'], self.ctx.author.name, f"Purchased {item['name']}")
            
            # Add to inventory and activate boost
            user_id_str = str(self.ctx.author.id)
            init_player_stats(self.ctx.author.id)
            
            if item['type'] == 'ticket':
                # Add tickets to account
                tickets_amount = item['effect']['tickets']
                add_tickets(self.ctx.author.id, tickets_amount)
                save_tickets()
                duration_text = f"{tickets_amount} ticket(s)"
            elif item['type'] == 'boost':
                # Activate boost
                boost = {
                    "type": item_id,
                    "multiplier": item['effect'].get('xp_multiplier', item['effect'].get('chip_multiplier', 1)),
                    "expires": (datetime.now() + timedelta(seconds=item['effect']['duration'])).isoformat()
                }
                player_stats[user_id_str]["active_boosts"].append(boost)
                duration_hours = item['effect']['duration'] // 3600
                duration_mins = (item['effect']['duration'] % 3600) // 60
                if duration_hours > 0:
                    duration_text = f"{duration_hours}h {duration_mins}m" if duration_mins > 0 else f"{duration_hours} hour(s)"
                else:
                    duration_text = f"{duration_mins} min(s)"
            else:
                player_stats[user_id_str]["inventory"].append(item_id)
                duration_text = "Permanent"
            
            save_player_stats()
            
            # Update embed with new balance
            await interaction.message.edit(embed=self.create_embed())
            
            # Send confirmation
            await interaction.response.send_message(
                f"✅ **Purchase Complete!**\n"
                f"You bought **{item['name']}** for {item['price']:,} chips!\n"
                f"**Duration:** {duration_text}\n"
                f"**New Balance:** 💎 {format_chips(self.ctx.author.id)} chips | 🎫 {get_tickets(self.ctx.author.id)} tickets",
                ephemeral=True
            )
        
        return callback
    
    async def previous_page(self, interaction: discord.Interaction):
        """Go to previous page"""
        if interaction.user.id != self.ctx.author.id:
            await interaction.response.send_message("❌ This is not your shop session!", ephemeral=True)
            return
        
        if self.current_page > 0:
            self.current_page -= 1
            self.update_buttons()
            await interaction.response.edit_message(embed=self.create_embed(), view=self)
    
    async def next_page(self, interaction: discord.Interaction):
        """Go to next page"""
        if interaction.user.id != self.ctx.author.id:
            await interaction.response.send_message("❌ This is not your shop session!", ephemeral=True)
            return
        
        if self.current_page < self.total_pages - 1:
            self.current_page += 1
            self.update_buttons()
            await interaction.response.edit_message(embed=self.create_embed(), view=self)
    
    async def on_timeout(self):
        """Disable all buttons when view times out"""
        for item in self.children:
            if hasattr(item, 'disabled'):
                item.disabled = True  # type: ignore
        
        if self.message:
            try:
                await self.message.edit(view=self)
            except discord.HTTPException:
                pass

@bot.hybrid_command(name='inventory', aliases=['inv'])
async def inventory_command(ctx, user: Optional[discord.User] = None):
    """View your inventory and active boosts
    
    Usage: ~inventory [@user]
    Aliases: ~inv
    Example: ~inventory, ~inv @John
    """
    target_user = user if user is not None else ctx.author
    user_id = str(target_user.id)
    
    # Initialize stats
    init_player_stats(target_user.id)
    stats = player_stats[user_id]
    
    # Get inventory and active boosts
    inventory = stats.get("inventory", [])
    active_boosts = stats.get("active_boosts", [])
    
    # Create embed
    embed = discord.Embed(
        title=f"🎒 {target_user.name}'s Inventory",
        description=f"<:Casino_Chip:1437456315025719368> **Balance:** {format_chips(target_user.id)} chips",
        color=0x9b59b6
    )
    
    # Show active boosts
    if active_boosts:
        active_list = []
        current_time = datetime.now()
        
        for boost in active_boosts:
            expires = datetime.fromisoformat(boost["expires"])
            time_left = expires - current_time
            
            if time_left.total_seconds() > 0:
                # Convert to readable format
                hours = int(time_left.total_seconds() // 3600)
                minutes = int((time_left.total_seconds() % 3600) // 60)
                
                if hours > 0:
                    time_str = f"{hours}h {minutes}m"
                else:
                    time_str = f"{minutes}m"
                
                # Get item details
                if boost["type"] in shop_items:
                    item = shop_items[boost["type"]]
                    active_list.append(f"{item['name']} - **{time_str}** left")
        
        if active_list:
            embed.add_field(
                name="✨ Active Boosts",
                value="\n".join(active_list),
                inline=False
            )
        else:
            embed.add_field(
                name="✨ Active Boosts",
                value="*No active boosts*",
                inline=False
            )
    else:
        embed.add_field(
            name="✨ Active Boosts",
            value="*No active boosts*",
            inline=False
        )
    
    # Show inventory items
    if inventory:
        inventory_list = []
        item_counts = {}
        
        # Count items
        for item_id in inventory:
            if item_id in item_counts:
                item_counts[item_id] += 1
            else:
                item_counts[item_id] = 1
        
        # Build inventory display
        for item_id, count in item_counts.items():
            if item_id in shop_items:
                item = shop_items[item_id]
                if count > 1:
                    inventory_list.append(f"{item['name']} x{count}")
                else:
                    inventory_list.append(f"{item['name']}")
        
        if inventory_list:
            embed.add_field(
                name="📦 Items",
                value="\n".join(inventory_list),
                inline=False
            )
        else:
            embed.add_field(
                name="📦 Items",
                value="*No items in inventory*",
                inline=False
            )
    else:
        embed.add_field(
            name="📦 Items",
            value="*No items in inventory*",
            inline=False
        )
    
    # Add helpful footer
    embed.set_footer(text="💡 Use ~shop to purchase items and boosts!")
    
    await ctx.send(embed=embed)

@bot.hybrid_command(name='rollpet', aliases=['petroll'])
async def rollpet_command(ctx):
    """Roll for a random pet using tickets
    
    Usage: ~rollpet
    Cost: 1 ticket per roll
    Aliases: ~roll, ~petroll
    """
    user_id = str(ctx.author.id)
    
    # Check if user has enough tickets
    if get_tickets(ctx.author.id) < PET_ROLL_COST:
        embed = discord.Embed(
            title="❌ Insufficient Tickets",
            description=f"You need **{PET_ROLL_COST}** ticket to roll for a pet.\nYou have: **{get_tickets(ctx.author.id)}** tickets\n\n💡 Buy tickets in the shop or use `~buytickets` to convert chips!",
            color=0xe74c3c
        )
        await ctx.send(embed=embed)
        return
    
    # Deduct ticket
    remove_tickets(ctx.author.id, PET_ROLL_COST)
    save_tickets()
    
    # Roll for a pet using weighted random selection
    import random
    
    # Create list of pets with their chances
    pet_pool = []
    for pet_id, pet_data in PETS.items():
        pet_pool.extend([pet_id] * int(pet_data["chance"] * 10))
    
    # Select random pet
    rolled_pet_id = random.choice(pet_pool)
    rolled_pet = PETS[rolled_pet_id]
    
    # Initialize user pets if needed
    if user_id not in user_pets:
        user_pets[user_id] = {}
    
    # Add pet to collection
    if rolled_pet_id in user_pets[user_id]:
        user_pets[user_id][rolled_pet_id] += 1
        is_new = False
    else:
        user_pets[user_id][rolled_pet_id] = 1
        is_new = True
    
    save_pets()
    
    # Create result embed
    embed = discord.Embed(
        title=f"{rolled_pet['emoji']} You rolled a {rolled_pet['name']}!",
        description=f"**Rarity:** {rolled_pet['rarity']}\n{'🆕 **New pet added to your collection!**' if is_new else '**Duplicate!** You now have **' + str(user_pets[user_id][rolled_pet_id]) + 'x** ' + rolled_pet['name']}",
        color=RARITY_COLORS[rolled_pet['rarity']]
    )
    
    # Show collection progress
    total_pets = len(PETS)
    actual_pets_count = len([k for k in user_pets[user_id].keys() if not k.startswith('_')])
    embed.set_footer(text=f"Collection: {actual_pets_count}/{total_pets} unique pets | Remaining tickets: {get_tickets(ctx.author.id)}")
    
    await ctx.send(embed=embed)

@bot.hybrid_command(name='pets', aliases=['collection', 'mypets'])
async def pets_command(ctx, user: Optional[discord.User] = None):
    """View your pet collection
    
    Usage: ~pets [@user]
    Aliases: ~collection, ~mypets
    Example: ~pets, ~pets @John
    """
    target_user = user if user is not None else ctx.author
    user_id = str(target_user.id)
    
    # Get user's pets
    user_collection = user_pets.get(user_id, {})
    
    # Filter out metadata keys
    actual_pets = {k: v for k, v in user_collection.items() if not k.startswith('_')}
    
    if not actual_pets:
        embed = discord.Embed(
            title=f"🐾 {target_user.name}'s Pet Collection",
            description="*No pets collected yet!*\n\nUse `~rollpet` to start collecting!",
            color=0x3498db
        )
        embed.set_footer(text=f"Cost: {PET_ROLL_COST} ticket per roll | Buy tickets in ~shop")
        await ctx.send(embed=embed)
        return
    
    # Check for idol pet
    idol_pet_id = user_collection.get('_idol')
    idol_text = ""
    if idol_pet_id and idol_pet_id in PETS:
        idol_pet = PETS[idol_pet_id]
        idol_text = f"\n⭐ **Idol:** {idol_pet['emoji']} {idol_pet['name']}"
    
    # Group pets by rarity
    rarity_groups = {
        "Mythic": [],
        "Legendary": [],
        "Epic": [],
        "Rare": [],
        "Uncommon": [],
        "Common": []
    }
    
    for pet_id, count in actual_pets.items():
        if pet_id in PETS:
            pet = PETS[pet_id]
            rarity_groups[pet["rarity"]].append((pet, count, pet_id))
    
    # Create embed
    embed = discord.Embed(
        title=f"🐾 {target_user.name}'s Pet Collection",
        description=f"**Unique Pets Collected:** {len(actual_pets)}/{len(PETS)}{idol_text}\n*Use `~setidol <pet>` to set your profile idol!*",
        color=0x9b59b6
    )
    
    # Add fields for each rarity that has pets
    for rarity in ["Mythic", "Legendary", "Epic", "Rare", "Uncommon", "Common"]:
        pets_in_rarity = rarity_groups[rarity]
        if pets_in_rarity:
            # Build pet list
            pet_list = []
            for pet, count, pet_id in pets_in_rarity:
                idol_marker = " ⭐" if pet_id == idol_pet_id else ""
                if count > 1:
                    pet_list.append(f"{pet['emoji']} {pet['name']} x{count}{idol_marker}")
                else:
                    pet_list.append(f"{pet['emoji']} {pet['name']}{idol_marker}")
            
            embed.add_field(
                name=f"{rarity} ({len(pets_in_rarity)})",
                value="\n".join(pet_list),
                inline=False
            )
    
    # Calculate total pet count (including duplicates)
    total_count = sum(actual_pets.values())
    embed.set_footer(text=f"Total Pets: {total_count} pets collected")
    
    await ctx.send(embed=embed)

@bot.hybrid_command(name='setbanner', aliases=['banner'])
async def setbanner_command(ctx, *, image_url: str):
    """Set a custom banner image for your profile
    
    Usage: ~setbanner <image_url>
    Example: ~setbanner https://i.imgur.com/example.png
    """
    user_id = str(ctx.author.id)
    
    # Basic validation - check if URL looks like an image
    valid_extensions = ('.png', '.jpg', '.jpeg', '.gif', '.webp')
    if not any(image_url.lower().endswith(ext) for ext in valid_extensions):
        await ctx.send("❌ Please provide a direct image URL ending in .png, .jpg, .jpeg, .gif, or .webp")
        return
    
    # Save the banner
    profile_banners[user_id] = image_url
    save_profile_banners()
    
    embed = discord.Embed(
        title="🖼️ Profile Banner Set!",
        description="Your profile banner has been updated!\n\nUse `~profile` to view your profile with the new banner.",
        color=0x5865F2
    )
    embed.set_image(url=image_url)
    
    await ctx.send(embed=embed)

@bot.hybrid_command(name='removebanner', aliases=['deletebanner', 'clearbanner'])
async def removebanner_command(ctx):
    """Remove your profile banner
    
    Usage: ~removebanner
    """
    user_id = str(ctx.author.id)
    
    if user_id not in profile_banners:
        await ctx.send("❌ You don't have a profile banner set!")
        return
    
    del profile_banners[user_id]
    save_profile_banners()
    
    embed = discord.Embed(
        title="🖼️ Profile Banner Removed",
        description="Your profile banner has been removed.",
        color=0xFF6B6B
    )
    
    await ctx.send(embed=embed)

@bot.hybrid_command(name='setidol', aliases=['idol'])
async def setidol_command(ctx, *, pet_name: str):
    """Set a pet as your profile idol (shown in trades and profiles)
    
    Usage: ~setidol <pet name>
    Example: ~setidol Dragon, ~setidol celestial spirit
    """
    user_id = str(ctx.author.id)
    
    # Get user's pets
    user_collection = user_pets.get(user_id, {})
    actual_pets = {k: v for k, v in user_collection.items() if not k.startswith('_')}
    
    if not actual_pets:
        await ctx.send("❌ You don't have any pets yet! Use `~rollpet` to start collecting.")
        return
    
    # Find matching pet (case insensitive)
    pet_name_lower = pet_name.lower()
    found_pet_id = None
    
    for pet_id in actual_pets.keys():
        if pet_id in PETS:
            pet = PETS[pet_id]
            if pet['name'].lower() == pet_name_lower or pet_id.lower() == pet_name_lower:
                found_pet_id = pet_id
                break
    
    if not found_pet_id:
        await ctx.send(f"❌ You don't own a pet named '{pet_name}'! Use `~pets` to see your collection.")
        return
    
    # Set as idol
    if user_id not in user_pets:
        user_pets[user_id] = {}
    
    user_pets[user_id]['_idol'] = found_pet_id
    save_pets()
    
    idol_pet = PETS[found_pet_id]
    
    embed = discord.Embed(
        title="⭐ Idol Pet Set!",
        description=f"You set **{idol_pet['emoji']} {idol_pet['name']}** as your idol!\n\nYour idol will be displayed in trades and on your profile.",
        color=RARITY_COLORS[idol_pet['rarity']]
    )
    
    await ctx.send(embed=embed)

@bot.hybrid_command(name='profile', aliases=['stats', 'rank'])
async def profile_command(ctx, user: Optional[discord.User] = None):
    """View player profile with XP, level, VIP tier, and stats
    
    Usage: ~profile [@user]
    Example: ~profile @John
    """
    target_user = user if user is not None else ctx.author
    user_id = str(target_user.id)
    
    # Initialize stats
    init_player_stats(target_user.id)
    stats = player_stats[user_id]
    
    # Get member object to check booster status
    member = ctx.guild.get_member(target_user.id) if ctx.guild else None
    
    # Calculate VIP tier based on wagered amount and booster status
    tier_data = calculate_vip_tier(target_user.id, member)
    stats["vip_tier"] = tier_data
    save_player_stats()
    
    # Build VIP tier display name
    base_tier = tier_data.get("base_tier", "none")
    is_booster = tier_data.get("is_booster", False)
    
    if base_tier != "none" and is_booster:
        vip_display_name = f"{base_tier.capitalize()} + Booster ⚡"
    elif is_booster:
        vip_display_name = "Booster ⚡"
    else:
        vip_display_name = base_tier.capitalize()
    
    # Calculate XP progress
    current_xp = stats["xp"]
    current_level = stats["level"]
    xp_needed = get_level_xp_requirement(current_level)
    
    # Calculate server rank (based on XP in current guild)
    server_rank = "—"
    if ctx.guild:
        # Get all verified players in this guild
        guild_members = guild_players.get(str(ctx.guild.id), [])
        verified_guild_members = [uid for uid in guild_members if str(uid) in verified_users]
        
        # Create leaderboard sorted by XP
        leaderboard_data = []
        for uid in verified_guild_members:
            uid_str = str(uid)
            member_obj = ctx.guild.get_member(int(uid))
            if member_obj and uid_str in player_stats:
                member_xp = player_stats[uid_str].get("xp", 0)
                leaderboard_data.append((uid, member_xp))
        
        # Sort by XP descending
        leaderboard_data.sort(key=lambda x: x[1], reverse=True)
        
        # Find user's rank
        for idx, (uid, _) in enumerate(leaderboard_data, 1):
            if uid == target_user.id:
                server_rank = f"#{idx}"
                break
    
    # Get idol pet if set
    idol_display = ""
    user_collection = user_pets.get(user_id, {})
    idol_pet_id = user_collection.get('_idol')
    
    if idol_pet_id and idol_pet_id in PETS:
        idol_pet = PETS[idol_pet_id]
        idol_display = f"{idol_pet['emoji']} "
    
    # Create modern profile embed
    embed = discord.Embed(
        title="",
        description="",
        color=0x2B2D31
    )
    
    # Set user avatar as thumbnail
    embed.set_thumbnail(url=target_user.display_avatar.url)
    
    # Set profile banner if user has one
    user_banner = profile_banners.get(user_id)
    if user_banner:
        embed.set_image(url=user_banner)
    
    # XP Progress bar
    filled_blocks = int((current_xp / xp_needed) * 20)
    progress_bar = "█" * filled_blocks + "░" * (20 - filled_blocks)
    
    # Get Rocket League rank if set
    rl_rank_display = ""
    if target_user.id in rl_ranks:
        rank_value = rl_ranks[target_user.id]
        rank_info = RL_RANKS.get(rank_value, RL_RANKS[0])
        rl_rank_display = f"• RL Rank : {rank_info['name']}\n"
    
    # Build profile template
    profile_text = "```\n"
    profile_text += f"[ {idol_display}{target_user.name} — Profile Overview ]\n"
    profile_text += "───────────────────────────────\n"
    profile_text += f"Rank      : {server_rank}\n"
    profile_text += f"Level     : {current_level}\n"
    profile_text += f"EXP       : {current_xp:,} / {xp_needed:,}\n"
    profile_text += f"Progress  : {progress_bar}\n"
    profile_text += "───────────────────────────────\n"
    profile_text += f"• VIP Tier: {vip_display_name}\n"
    profile_text += f"• Chips   : {format_chips(target_user.id)}\n"
    profile_text += f"• Tickets : {get_tickets(target_user.id):,}\n"
    profile_text += f"• Wagered : {stats.get('total_wagered', 0):,}\n"
    profile_text += f"• Games   : {stats.get('games_played', 0)}\n"
    profile_text += f"• Achievements: {len(stats.get('achievements', []))} / {len(ACHIEVEMENTS)}\n"
    if rl_rank_display:
        profile_text += rl_rank_display
    profile_text += "───────────────────────────────\n"
    profile_text += "```"
    
    # Add RL rank emoji after the profile text box if set
    if target_user.id in rl_ranks:
        rank_value = rl_ranks[target_user.id]
        rank_info = RL_RANKS.get(rank_value, RL_RANKS[0])
        embed.description = f"{rank_info['emoji']} **{rank_info['name']}**"
    
    embed.add_field(
        name="",
        value=profile_text,
        inline=False
    )
    
    await ctx.send(embed=embed)

@bot.hybrid_command(name='streak', aliases=['login'])
async def streak_command(ctx):
    """View your daily login streak and rewards
    
    Usage: ~streak
    Get bonus chips for consecutive daily logins!
    """
    user_id = str(ctx.author.id)
    init_player_stats(ctx.author.id)
    
    # Update streak (first time using this triggers it)
    bonus = update_login_streak(user_id)
    
    streak_data = login_streaks[user_id]
    current = streak_data.get("current_streak", 0)
    longest = streak_data.get("longest_streak", 0)
    last_login = streak_data.get("last_login")
    
    # Determine milestone emoji
    milestone = ""
    if current == 7:
        milestone = "🔥 Week Warrior!"
    elif current == 14:
        milestone = "⭐ Two Weeks Strong!"
    elif current == 30:
        milestone = "👑 Monthly Legend!"
    elif current > 30:
        milestone = "🚀 Unstoppable!"
    
    embed = discord.Embed(
        title="📅 Login Streak",
        color=0xFF8C00,
        description=milestone
    )
    
    embed.add_field(
        name="Current Streak",
        value=f"🔥 {current} days",
        inline=True
    )
    embed.add_field(
        name="Longest Streak",
        value=f"⭐ {longest} days",
        inline=True
    )
    embed.add_field(
        name="Bonus Earned Today",
        value=f"💰 +{bonus:,} chips" if bonus > 0 else "✅ Already claimed today",
        inline=False
    )
    
    if last_login:
        embed.add_field(
            name="Last Login",
            value=last_login,
            inline=False
        )
    
    embed.set_footer(text="Bonus = 10 chips × current streak | Miss a day and your streak resets!")
    
    await ctx.send(embed=embed)

class GameHistoryPaginator(discord.ui.View):
    """Paginated game history display"""
    def __init__(self, ctx, user_id):
        super().__init__(timeout=180)
        self.ctx = ctx
        self.user_id = user_id
        self.current_page = 0
        self.message = None
        
        # Get game history
        self.games = game_history.get(user_id, [])
        self.games.reverse()  # Most recent first
        self.games_per_page = 5
        self.total_pages = max(1, (len(self.games) + self.games_per_page - 1) // self.games_per_page)
        
        self.create_pages()
        self.update_buttons()
    
    def create_pages(self):
        """Create paginated embeds"""
        self.pages = []
        
        if not self.games:
            embed = discord.Embed(
                title="📊 Game History",
                description="No games played yet!",
                color=0x5865F2
            )
            self.pages.append(embed)
            return
        
        for page_num in range(self.total_pages):
            start_idx = page_num * self.games_per_page
            end_idx = start_idx + self.games_per_page
            page_games = self.games[start_idx:end_idx]
            
            embed = discord.Embed(
                title="📊 Game History",
                color=0x5865F2
            )
            
            for game in page_games:
                game_name = game.get("game", "Unknown")
                wager = game.get("wager", 0)
                result = game.get("result", "push")
                amount = game.get("amount", 0)
                timestamp = game.get("timestamp", "")
                
                # Parse timestamp to show relative time
                try:
                    game_time = datetime.fromisoformat(timestamp)
                    now = datetime.now()
                    delta = now - game_time
                    if delta.total_seconds() < 60:
                        time_ago = "just now"
                    elif delta.total_seconds() < 3600:
                        time_ago = f"{int(delta.total_seconds() // 60)}m ago"
                    elif delta.total_seconds() < 86400:
                        time_ago = f"{int(delta.total_seconds() // 3600)}h ago"
                    else:
                        time_ago = f"{int(delta.total_seconds() // 86400)}d ago"
                except Exception:
                    time_ago = "?"
                
                # Result emoji and color
                if result == "win":
                    result_emoji = "✅"
                    amount_str = f"+{amount:,}"
                elif result == "loss":
                    result_emoji = "❌"
                    amount_str = f"-{amount:,}"
                else:
                    result_emoji = "➡️"
                    amount_str = "0"
                
                game_info = f"{result_emoji} **{game_name}** | Wager: {wager:,} | {amount_str}\n*{time_ago}*"
                
                embed.add_field(
                    name="",
                    value=game_info,
                    inline=False
                )
            
            embed.set_footer(text=f"Page {page_num + 1}/{self.total_pages} • {len(self.games)} total games")
            self.pages.append(embed)
    
    def update_buttons(self):
        """Update button states"""
        self.previous_btn.disabled = self.current_page == 0
        self.next_btn.disabled = self.current_page == self.total_pages - 1
    
    @discord.ui.button(label="◀ Previous", style=discord.ButtonStyle.primary, disabled=True)
    async def previous_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.ctx.author.id:
            await interaction.response.send_message("❌ Not your history!", ephemeral=True)
            return
        
        self.current_page -= 1
        self.update_buttons()
        await interaction.response.edit_message(embed=self.pages[self.current_page], view=self)
    
    @discord.ui.button(label="Next ▶", style=discord.ButtonStyle.primary)
    async def next_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.ctx.author.id:
            await interaction.response.send_message("❌ Not your history!", ephemeral=True)
            return
        
        self.current_page += 1
        self.update_buttons()
        await interaction.response.edit_message(embed=self.pages[self.current_page], view=self)

@bot.hybrid_command(name='history', aliases=['hist'])
async def history_command(ctx, user: Optional[discord.User] = None):
    """View your game history with results
    
    Usage: ~history [@user]
    Shows your last 50 games with wins, losses, and amounts
    """
    target_user = user if user is not None else ctx.author
    user_id = str(target_user.id)
    
    init_player_stats(target_user.id)
    
    if user_id not in game_history or not game_history[user_id]:
        embed = discord.Embed(
            title="📊 Game History",
            description=f"**{target_user.name}** hasn't played any games yet!",
            color=0x5865F2
        )
        await ctx.send(embed=embed)
        return
    
    view = GameHistoryPaginator(ctx, user_id)
    message = await ctx.send(embed=view.pages[0], view=view)
    view.message = message

@bot.hybrid_command(name='admin', aliases=['adminboard', 'botadmin'])
async def admin_command(ctx):
    """View bot economy analytics (Owner only)
    
    Usage: ~admin
    Shows total chips, active players, popular games, and house stats
    """
    if ctx.author.id != OWNER_ID:
        await ctx.send("❌ Only the bot owner can use this command!")
        return
    
    # Calculate total chips in circulation
    total_chips = 0
    for user_id in player_chips:
        if is_infinite(user_id):
            continue
        total_chips += get_chips(user_id)
    
    # Count active players (anyone who played in last 7 days)
    today = datetime.now().date()
    seven_days_ago = today - timedelta(days=7)
    active_players = 0
    
    for user_id, games in game_history.items():
        if games:
            last_game_time = datetime.fromisoformat(games[-1].get("timestamp", "")).date()
            if last_game_time >= seven_days_ago:
                active_players += 1
    
    # Count total players with stats
    total_players = len(player_stats)
    
    # Find top 5 games
    game_counts = {}
    for user_id, games in game_history.items():
        for game in games:
            game_name = game.get("game", "Unknown")
            game_counts[game_name] = game_counts.get(game_name, 0) + 1
    
    top_games = sorted(game_counts.items(), key=lambda x: x[1], reverse=True)[:5]
    
    # Calculate today's stats
    today_str = today.isoformat()
    today_wagered = 0
    today_wins = 0
    today_losses = 0
    
    for user_id, games in game_history.items():
        for game in games:
            game_date = datetime.fromisoformat(game.get("timestamp", "")).date().isoformat()
            if game_date == today_str:
                today_wagered += game.get("wager", 0)
                if game.get("result") == "win":
                    today_wins += 1
                elif game.get("result") == "loss":
                    today_losses += 1
    
    # Calculate house profit (negative for house = player wins)
    total_wagered_all = sum(stats.get("total_wagered", 0) for stats in player_stats.values())
    total_won_all = sum(stats.get("total_won", 0) for stats in player_stats.values())
    house_profit = total_wagered_all - total_won_all
    
    # Build embed
    embed = discord.Embed(
        title="📊 BOT ECONOMY DASHBOARD",
        color=0xFFD700,
        timestamp=datetime.now()
    )
    
    embed.add_field(
        name="💰 Chips in Circulation",
        value=f"{total_chips:,}",
        inline=True
    )
    embed.add_field(
        name="👥 Total Players",
        value=f"{total_players:,}",
        inline=True
    )
    embed.add_field(
        name="🔥 Active (7d)",
        value=f"{active_players:,}",
        inline=True
    )
    
    embed.add_field(
        name="📈 Today's Stats",
        value=f"Wagered: {today_wagered:,}\nWins: {today_wins} | Losses: {today_losses}",
        inline=False
    )
    
    embed.add_field(
        name="💹 All-Time Stats",
        value=f"Total Wagered: {total_wagered_all:,}\nTotal Won: {total_won_all:,}\nHouse Profit: {house_profit:,}",
        inline=False
    )
    
    if top_games:
        games_text = "\n".join([f"{i+1}. {game[0]}: {game[1]} plays" for i, game in enumerate(top_games)])
        embed.add_field(
            name="🎮 Top 5 Games",
            value=games_text,
            inline=False
        )
    
    embed.set_footer(text="Updated every command • Dashboard is real-time")
    
    await ctx.send(embed=embed)

@bot.hybrid_command(name='achievements', aliases=['ach'])
async def achievements_command(ctx):
    """View all unlocked achievements and rewards
    
    Usage: ~achievements
    """
    user_id = str(ctx.author.id)
    init_player_stats(ctx.author.id)
    
    # Check for new achievements
    earned = check_and_award_achievements(ctx.author.id)
    
    stats = player_stats[user_id]
    unlocked = stats.get("achievements", [])
    
    embed = discord.Embed(
        title="🎖️ Achievements",
        description=f"Unlocked: {len(unlocked)}/{len(ACHIEVEMENTS)}",
        color=0xFFD700
    )
    
    # Show unlocked achievements
    unlocked_list = []
    locked_list = []
    
    for ach_id, achievement in ACHIEVEMENTS.items():
        if ach_id in unlocked:
            unlocked_list.append(f"{achievement['emoji']} **{achievement['name']}** - {achievement['reward']:,} chips ✅\n*{achievement['description']}*")
        else:
            locked_list.append(f"🔒 **{achievement['name']}** - {achievement['reward']:,} chips\n*{achievement['description']}*")
    
    if unlocked_list:
        embed.add_field(
            name="✨ Unlocked",
            value="\n\n".join(unlocked_list[:5]),
            inline=False
        )
        if len(unlocked_list) > 5:
            embed.add_field(
                name="",
                value="\n\n".join(unlocked_list[5:]),
                inline=False
            )
    
    if locked_list:
        embed.add_field(
            name="🔒 Locked",
            value="\n\n".join(locked_list[:3]),
            inline=False
        )
    
    # Calculate total earned
    total_earned = sum(ACHIEVEMENTS[a]["reward"] for a in unlocked)
    embed.set_footer(text=f"Total earned from achievements: {total_earned:,} chips")
    
    if earned:
        await ctx.send(f"🎉 **New Achievement{'s' if len(earned) > 1 else ''}!** {', '.join([a['name'] for a in earned])}")
    
    await ctx.send(embed=embed)

@bot.hybrid_command(name='jackpot', aliases=['jp'])
async def jackpot_command(ctx):
    """Check the progressive jackpot pool
    
    The jackpot grows with every game played!
    0.1% chance to win on any game.
    """
    embed = discord.Embed(
        title="🎰 Progressive Jackpot",
        description=f"**Current Pool:** {jackpot_pool:,} chips\n\n💡 Play any casino game for a 0.1% chance to win the entire jackpot!\n🎯 1% of every bet contributes to the jackpot pool.",
        color=0xFFD700
    )
    
    await ctx.send(embed=embed)

@bot.hybrid_command(name='loan')
async def loan_command(ctx, amount: int = 1000):
    """Take a loan when you're broke (100% interest - repay DOUBLE, 7 days)
    
    Usage: ~loan [amount]
    Example: ~loan 5000
    
    Requirements:
    - Must have less than 100 chips
    - Can only have one loan at a time
    - Default: 1000 chips
    - WARNING: You must repay 2x the loan amount!
    """
    user_id = ctx.author.id
    
    # Validate amount
    if amount < 100:
        await ctx.send("❌ Minimum loan amount is 100 chips!")
        return
    
    if amount > 50000:
        await ctx.send("❌ Maximum loan amount is 50,000 chips!")
        return
    
    # Check if user can take loan
    can_loan, error_msg = can_take_loan(user_id)
    if not can_loan:
        await ctx.send(f"❌ {error_msg}")
        return
    
    # Give loan
    total_owed, due_date = take_loan(user_id, amount)
    due_date_formatted = datetime.fromisoformat(due_date).strftime("%B %d, %Y at %I:%M %p")
    
    embed = discord.Embed(
        title="💳 Loan Approved!",
        description=f"You received **{amount:,} chips**!",
        color=0x00FF00
    )
    
    embed.add_field(
        name="📋 Loan Details",
        value=f"**Principal:** {amount:,} chips\n**Interest Rate:** 100% (PAY DOUBLE!)\n**Total Owed:** {total_owed:,} chips\n**Due Date:** {due_date_formatted}",
        inline=False
    )
    
    embed.add_field(
        name="<:Casino_Chip:1437456315025719368> Balance",
        value=f"{format_chips(user_id)} chips",
        inline=False
    )
    
    embed.set_footer(text=f"Use {get_prefix_from_ctx(ctx)}repay to repay your loan")
    
    await ctx.send(embed=embed)

@bot.hybrid_command(name='repay')
async def repay_command(ctx):
    """Repay your active loan
    
    Usage: ~repay
    """
    user_id = ctx.author.id
    
    success, message = repay_loan(user_id)
    
    if success:
        # Award achievement if first time
        user_id_str = str(user_id)
        init_player_stats(user_id)
        if "loan_free" not in player_stats[user_id_str].get("achievements", []):
            player_stats[user_id_str]["achievements"].append("loan_free")
            reward = ACHIEVEMENTS["loan_free"]["reward"]
            add_chips(user_id, reward, ctx.author.name, "Loan Free achievement")
            save_player_stats()
            await ctx.send(f"🎖️ **Achievement Unlocked!** {ACHIEVEMENTS['loan_free']['emoji']} {ACHIEVEMENTS['loan_free']['name']} - Earned {reward:,} chips!")
        
        embed = discord.Embed(
            title="✅ Loan Repaid!",
            description=message,
            color=0x00FF00
        )
        embed.add_field(
            name="<:Casino_Chip:1437456315025719368> Balance",
            value=f"{format_chips(user_id)} chips",
            inline=False
        )
    else:
        embed = discord.Embed(
            title="❌ Cannot Repay",
            description=message,
            color=0xFF0000
        )
    
    await ctx.send(embed=embed)

@bot.hybrid_command(name='shop', aliases=['store'])
async def shop_command(ctx):
    """Browse and buy items, boosts, and perks with interactive buttons
    
    Usage: ~shop
    Browse items with Previous/Next buttons and purchase with Buy buttons!
    """
    # Check if shop has items
    if not shop_items:
        await ctx.send("❌ The shop is currently empty! Check back after the next rotation.")
        return
    
    # Create interactive shop view
    view = ShopPaginator(ctx)
    
    # Send initial page with buttons
    message = await ctx.send(embed=view.create_embed(), view=view)
    view.message = message

@bot.hybrid_command(name='use', aliases=['activate'])
async def use_item_command(ctx, item_id: str):
    """Use/activate an item from your inventory
    
    Usage: ~use <item_id>
    Aliases: ~activate
    Example: ~use insurance, ~use vip_pass
    """
    user_id_str = str(ctx.author.id)
    init_player_stats(ctx.author.id)
    
    # Check if item is in inventory
    inventory = player_stats[user_id_str].get("inventory", [])
    
    if item_id not in inventory:
        embed = discord.Embed(
            title="❌ Item Not Found",
            description=f"You don't have `{item_id}` in your inventory!\n\nUse `~inventory` to see what you own.",
            color=0xe74c3c
        )
        await ctx.send(embed=embed)
        return
    
    # Get item details from all shop items (including rotated ones)
    if item_id not in shop_items:
        # Check full item pool
        all_items = get_all_shop_items()
        if item_id not in all_items:
            await ctx.send(f"❌ Unknown item: `{item_id}`")
            return
        item = all_items[item_id]
    else:
        item = shop_items[item_id]
    
    # Activate based on item type
    if item['type'] == 'boost':
        # Activate boost
        boost = {
            "type": item_id,
            "multiplier": item['effect'].get('xp_multiplier', item['effect'].get('chip_multiplier', 1)),
            "expires": (datetime.now() + timedelta(seconds=item['effect']['duration'])).isoformat()
        }
        player_stats[user_id_str]["active_boosts"].append(boost)
        duration_hours = item['effect']['duration'] // 3600
        
        # Remove from inventory
        inventory.remove(item_id)
        save_player_stats()
        
        embed = discord.Embed(
            title="✨ Item Activated!",
            description=f"**{item['name']}** is now active for **{duration_hours} hour(s)**!",
            color=0x00FF00
        )
        await ctx.send(embed=embed)
    
    elif item['type'] == 'vip':
        # Activate VIP pass
        player_stats[user_id_str]["vip_status"] = {
            "tier": item['effect']['vip_tier'],
            "expires": (datetime.now() + timedelta(seconds=item['effect']['duration'])).isoformat()
        }
        duration_hours = item['effect']['duration'] // 3600
        
        # Remove from inventory
        inventory.remove(item_id)
        save_player_stats()
        
        embed = discord.Embed(
            title="👑 VIP Activated!",
            description=f"You now have **{item['effect']['vip_tier'].capitalize()}** VIP status for **{duration_hours} hour(s)**!",
            color=0xFFD700
        )
        await ctx.send(embed=embed)
    
    elif item['type'] == 'protection':
        # Activate insurance/protection
        player_stats[user_id_str]["active_insurance"] = {
            "refund_rate": item['effect']['refund_on_loss'],
            "uses_remaining": item['effect']['uses']
        }
        
        # Remove from inventory
        inventory.remove(item_id)
        save_player_stats()
        
        embed = discord.Embed(
            title="🛡️ Insurance Activated!",
            description=f"**{item['name']}** is now active!\n\nYou'll get **{int(item['effect']['refund_on_loss']*100)}%** of your bet back on losses for the next **{item['effect']['uses']} games**.",
            color=0x3498db
        )
        await ctx.send(embed=embed)
    
    else:
        await ctx.send("❌ This item cannot be activated. It may be a permanent perk!")

@bot.hybrid_command(name='daily')
async def prefix_daily(ctx):
    """Claim your daily chip reward (100 chips every 12 hours + VIP bonus)"""
    user_id = str(ctx.author.id)
    now = datetime.now()
    
    # Initialize user claims if not exists
    if user_id not in claims:
        claims[user_id] = {}
    
    # Check if daily has been claimed
    if 'daily' in claims[user_id]:
        last_claim = datetime.fromisoformat(claims[user_id]['daily'])
        time_diff = now - last_claim
        cooldown = timedelta(hours=12)
        
        if time_diff < cooldown:
            # Still on cooldown
            remaining = cooldown - time_diff
            hours = int(remaining.total_seconds() // 3600)
            minutes = int((remaining.total_seconds() % 3600) // 60)
            
            embed = discord.Embed(
                title="⏰ Daily Reward on Cooldown",
                description=f"You've already claimed your daily reward!\n\n**Time remaining:** {hours}h {minutes}m",
                color=0xFF6B6B
            )
            await ctx.send(embed=embed)
            return
    
    # Get member object and calculate VIP tier with booster check
    member = ctx.guild.get_member(ctx.author.id) if ctx.guild else None
    tier_data = calculate_vip_tier(ctx.author.id, member)
    vip_benefits = get_vip_benefits(tier_data)
    
    # Calculate total reward (base + VIP bonus)
    base_reward = DAILY_REWARD
    vip_bonus = vip_benefits['daily_bonus']
    total_reward = base_reward + vip_bonus
    
    # Claim the reward
    claims[user_id]['daily'] = now.isoformat()
    save_claims()
    add_chips(ctx.author.id, total_reward, ctx.author.name, "Daily reward claim")
    
    # Reset reminder flag so user gets notified next time
    if user_id not in claim_reminders_sent:
        claim_reminders_sent[user_id] = {}
    claim_reminders_sent[user_id]['daily'] = False
    save_claim_reminders()
    
    # Track claim challenge
    init_user_challenges(user_id)
    user_challenges[user_id]["claims_made"].add("daily")
    save_challenges()
    
    # Track monthly claim for rewards
    track_monthly_claim(ctx.author.id)
    
    # Build reward description
    reward_text = f"**Base Reward:** {base_reward:,} chips"
    if vip_bonus > 0:
        # Get display name for the tier
        base_tier = tier_data.get("base_tier", "none")
        is_booster = tier_data.get("is_booster", False)
        
        if base_tier != "none" and is_booster:
            reward_text += f"\n**{vip_benefits['emoji']} VIP Bonus ({base_tier.capitalize()} + Booster):** +{vip_bonus:,} chips"
        elif is_booster:
            reward_text += f"\n**{vip_benefits['emoji']} VIP Bonus (Booster):** +{vip_bonus:,} chips"
        else:
            reward_text += f"\n**{vip_benefits['emoji']} VIP Bonus ({base_tier.capitalize()}):** +{vip_bonus:,} chips"
        reward_text += f"\n**Total:** {total_reward:,} chips"
    
    embed = discord.Embed(
        title="🎁 Daily Reward Claimed!",
        description=f"{reward_text}\n\n<:Casino_Chip:1437456315025719368> New balance: **{format_chips(ctx.author.id)}**",
        color=0x00FF00
    )
    embed.set_footer(text="Come back in 12 hours for your next daily reward!")
    await ctx.send(embed=embed)
    
    # Check for challenge completions
    await check_challenge_completion(ctx, user_id)

@bot.hybrid_command(name='weekly')
async def prefix_weekly(ctx):
    """Claim your weekly chip reward (750 chips every 168 hours)"""
    user_id = str(ctx.author.id)
    now = datetime.now()
    
    # Initialize user claims if not exists
    if user_id not in claims:
        claims[user_id] = {}
    
    # Check if weekly has been claimed
    if 'weekly' in claims[user_id]:
        last_claim = datetime.fromisoformat(claims[user_id]['weekly'])
        time_diff = now - last_claim
        cooldown = timedelta(hours=168)
        
        if time_diff < cooldown:
            # Still on cooldown
            remaining = cooldown - time_diff
            days = int(remaining.total_seconds() // 86400)
            hours = int((remaining.total_seconds() % 86400) // 3600)
            
            embed = discord.Embed(
                title="⏰ Weekly Reward on Cooldown",
                description=f"You've already claimed your weekly reward!\n\n**Time remaining:** {days}d {hours}h",
                color=0xFF6B6B
            )
            await ctx.send(embed=embed)
            return
    
    # Get member object and calculate VIP tier with booster check
    member = ctx.guild.get_member(ctx.author.id) if ctx.guild else None
    tier_data = calculate_vip_tier(ctx.author.id, member)
    vip_benefits = get_vip_benefits(tier_data)
    
    # Calculate total reward (base + VIP bonus)
    base_reward = WEEKLY_REWARD
    vip_bonus = vip_benefits['daily_bonus']
    total_reward = base_reward + vip_bonus
    
    # Claim the reward
    claims[user_id]['weekly'] = now.isoformat()
    save_claims()
    add_chips(ctx.author.id, total_reward, ctx.author.name, "Weekly reward claim")
    
    # Reset reminder flag so user gets notified next time
    if user_id not in claim_reminders_sent:
        claim_reminders_sent[user_id] = {}
    claim_reminders_sent[user_id]['weekly'] = False
    save_claim_reminders()
    
    # Track claim challenge
    init_user_challenges(user_id)
    user_challenges[user_id]["claims_made"].add("weekly")
    save_challenges()
    
    # Build reward description
    reward_text = f"**Base Reward:** {base_reward:,} chips"
    if vip_bonus > 0:
        # Get display name for the tier
        base_tier = tier_data.get("base_tier", "none")
        is_booster = tier_data.get("is_booster", False)
        
        if base_tier != "none" and is_booster:
            reward_text += f"\n**{vip_benefits['emoji']} VIP Bonus ({base_tier.capitalize()} + Booster):** +{vip_bonus:,} chips"
        elif is_booster:
            reward_text += f"\n**{vip_benefits['emoji']} VIP Bonus (Booster):** +{vip_bonus:,} chips"
        else:
            reward_text += f"\n**{vip_benefits['emoji']} VIP Bonus ({base_tier.capitalize()}):** +{vip_bonus:,} chips"
        reward_text += f"\n**Total:** {total_reward:,} chips"
    
    embed = discord.Embed(
        title="🎁 Weekly Reward Claimed!",
        description=f"{reward_text}\n\n<:Casino_Chip:1437456315025719368> New balance: **{format_chips(ctx.author.id)}**",
        color=0x00FF00
    )
    embed.set_footer(text="Come back in 168 hours (7 days) for your next weekly reward!")
    await ctx.send(embed=embed)
    
    # Check for challenge completions
    await check_challenge_completion(ctx, user_id)

@bot.hybrid_command(name='monthly')
async def prefix_monthly(ctx):
    """Claim your monthly chip reward (3000 chips at the start of each calendar month)"""
    user_id = str(ctx.author.id)
    now = datetime.now()
    
    # Initialize user claims if not exists
    if user_id not in claims:
        claims[user_id] = {}
    
    # Check if monthly has been claimed this calendar month
    if 'monthly' in claims[user_id]:
        last_claim = datetime.fromisoformat(claims[user_id]['monthly'])
        
        # Check if it's the same month and year
        if last_claim.year == now.year and last_claim.month == now.month:
            # Already claimed this month
            # Calculate first day of next month
            if now.month == 12:
                next_month = datetime(now.year + 1, 1, 1)
            else:
                next_month = datetime(now.year, now.month + 1, 1)
            
            remaining = next_month - now
            days = remaining.days
            hours = int(remaining.seconds // 3600)
            
            embed = discord.Embed(
                title="⏰ Monthly Reward on Cooldown",
                description=f"You've already claimed your monthly reward!\n\n**Time remaining:** {days}d {hours}h until next month",
                color=0xFF6B6B
            )
            await ctx.send(embed=embed)
            return
    
    # Get member object and calculate VIP tier with booster check
    member = ctx.guild.get_member(ctx.author.id) if ctx.guild else None
    tier_data = calculate_vip_tier(ctx.author.id, member)
    vip_benefits = get_vip_benefits(tier_data)
    
    # Calculate total reward (base + VIP bonus)
    base_reward = MONTHLY_REWARD
    vip_bonus = vip_benefits['daily_bonus']
    total_reward = base_reward + vip_bonus
    
    # Claim the reward
    claims[user_id]['monthly'] = now.isoformat()
    save_claims()
    add_chips(ctx.author.id, total_reward, ctx.author.name, "Monthly reward claim")
    
    # Reset reminder flag so user gets notified next time
    if user_id not in claim_reminders_sent:
        claim_reminders_sent[user_id] = {}
    claim_reminders_sent[user_id]['monthly'] = False
    save_claim_reminders()
    
    # Track claim challenge
    init_user_challenges(user_id)
    user_challenges[user_id]["claims_made"].add("monthly")
    save_challenges()
    
    # Build reward description
    reward_text = f"**Base Reward:** {base_reward:,} chips"
    if vip_bonus > 0:
        # Get display name for the tier
        base_tier = tier_data.get("base_tier", "none")
        is_booster = tier_data.get("is_booster", False)
        
        if base_tier != "none" and is_booster:
            reward_text += f"\n**{vip_benefits['emoji']} VIP Bonus ({base_tier.capitalize()} + Booster):** +{vip_bonus:,} chips"
        elif is_booster:
            reward_text += f"\n**{vip_benefits['emoji']} VIP Bonus (Booster):** +{vip_bonus:,} chips"
        else:
            reward_text += f"\n**{vip_benefits['emoji']} VIP Bonus ({base_tier.capitalize()}):** +{vip_bonus:,} chips"
        reward_text += f"\n**Total:** {total_reward:,} chips"
    
    embed = discord.Embed(
        title="🎁 Monthly Reward Claimed!",
        description=f"{reward_text}\n\n<:Casino_Chip:1437456315025719368> New balance: **{format_chips(ctx.author.id)}**",
        color=0x00FF00
    )
    embed.set_footer(text="Come back next month for your monthly reward!")
    await ctx.send(embed=embed)
    
    # Check for challenge completions
    await check_challenge_completion(ctx, user_id)

@bot.hybrid_command(name='yearly')
async def prefix_yearly(ctx):
    """Claim your yearly chip reward (100,000 chips every 365 days)"""
    user_id = str(ctx.author.id)
    now = datetime.now()
    
    # Initialize user claims if not exists
    if user_id not in claims:
        claims[user_id] = {}
    
    # Check if yearly has been claimed
    if 'yearly' in claims[user_id]:
        last_claim = datetime.fromisoformat(claims[user_id]['yearly'])
        time_diff = now - last_claim
        cooldown = timedelta(days=365)
        
        if time_diff < cooldown:
            # Still on cooldown
            remaining = cooldown - time_diff
            days = int(remaining.total_seconds() // 86400)
            hours = int((remaining.total_seconds() % 86400) // 3600)
            
            embed = discord.Embed(
                title="⏰ Yearly Reward on Cooldown",
                description=f"You've already claimed your yearly reward!\n\n**Time remaining:** {days}d {hours}h",
                color=0xFF6B6B
            )
            await ctx.send(embed=embed)
            return
    
    # Get member object and calculate VIP tier with booster check
    member = ctx.guild.get_member(ctx.author.id) if ctx.guild else None
    tier_data = calculate_vip_tier(ctx.author.id, member)
    vip_benefits = get_vip_benefits(tier_data)
    
    # Calculate total reward (base + VIP bonus)
    base_reward = YEARLY_REWARD
    vip_bonus = vip_benefits['daily_bonus']
    total_reward = base_reward + vip_bonus
    
    # Claim the reward
    claims[user_id]['yearly'] = now.isoformat()
    save_claims()
    add_chips(ctx.author.id, total_reward, ctx.author.name, "Yearly reward claim")
    
    # Reset reminder flag so user gets notified next time
    if user_id not in claim_reminders_sent:
        claim_reminders_sent[user_id] = {}
    claim_reminders_sent[user_id]['yearly'] = False
    save_claim_reminders()
    
    # Track claim challenge
    init_user_challenges(user_id)
    user_challenges[user_id]["claims_made"].add("yearly")
    save_challenges()
    
    # Build reward description
    reward_text = f"**Base Reward:** {base_reward:,} chips"
    if vip_bonus > 0:
        # Get display name for the tier
        base_tier = tier_data.get("base_tier", "none")
        is_booster = tier_data.get("is_booster", False)
        
        if base_tier != "none" and is_booster:
            reward_text += f"\n**{vip_benefits['emoji']} VIP Bonus ({base_tier.capitalize()} + Booster):** +{vip_bonus:,} chips"
        elif is_booster:
            reward_text += f"\n**{vip_benefits['emoji']} VIP Bonus (Booster):** +{vip_bonus:,} chips"
        else:
            reward_text += f"\n**{vip_benefits['emoji']} VIP Bonus ({base_tier.capitalize()}):** +{vip_bonus:,} chips"
        reward_text += f"\n**Total:** {total_reward:,} chips"
    
    embed = discord.Embed(
        title="🎁 Yearly Reward Claimed!",
        description=f"{reward_text}\n\n<:Casino_Chip:1437456315025719368> New balance: **{format_chips(ctx.author.id)}**",
        color=0xFFD700
    )
    embed.set_footer(text="Come back next year for your yearly reward!")
    await ctx.send(embed=embed)
    
    # Check for challenge completions
    await check_challenge_completion(ctx, user_id)

class TradeOfferModal(discord.ui.Modal, title="Set Your Trade Offer"):
    offer_amount = discord.ui.TextInput(
        label="Chip Amount",
        placeholder="Enter amount of chips to offer (0 for nothing)",
        required=True,
        max_length=10
    )
    
    def __init__(self, trade_view, user):
        super().__init__()
        self.trade_view = trade_view
        self.user = user
    
    async def on_submit(self, interaction: discord.Interaction):
        try:
            amount = int(self.offer_amount.value)
            if amount < 0:
                await interaction.response.send_message("❌ Amount cannot be negative!", ephemeral=True)
                return
            
            user_balance = get_chips(self.user.id)
            if amount > user_balance:
                await interaction.response.send_message(f"❌ You don't have enough chips! You have {user_balance:,}, trying to offer {amount:,}.", ephemeral=True)
                return
            
            if self.user.id == self.trade_view.initiator.id:
                self.trade_view.initiator_offer = amount
                self.trade_view.initiator_set = True
            else:
                self.trade_view.partner_offer = amount
                self.trade_view.partner_set = True
            
            await interaction.response.send_message(f"✅ You set your offer to **{amount:,} chips**!", ephemeral=True)
            await self.trade_view.update_embed()
            
        except ValueError:
            await interaction.response.send_message("❌ Please enter a valid number!", ephemeral=True)

class TradeView(discord.ui.View):
    def __init__(self, initiator, partner):
        super().__init__(timeout=300)
        self.initiator = initiator
        self.partner = partner
        self.initiator_offer = 0
        self.partner_offer = 0
        self.initiator_set = False
        self.partner_set = False
        self.initiator_locked = False
        self.partner_locked = False
        self.initiator_approved = False
        self.partner_approved = False
        self.cancelled = False
        self.completed = False
        self.message: Optional[discord.Message] = None
    
    async def update_embed(self):
        """Update the trade embed"""
        if self.message is not None:
            try:
                embed = self.create_embed()
                await self.message.edit(embed=embed, view=self)
            except Exception:
                pass
    
    def create_embed(self):
        """Create the trade status embed"""
        # Determine description based on state
        if self.initiator_locked and self.partner_locked:
            title = "This trade has been locked."
            description = "Carefully review the details and either accept or decline the offer."
        else:
            title = "Type your chip amount to set your offer (e.g., `100 chips`, `1000`, `5k`, or `all`)"
            description = "**Both sides must lock in before proceeding to the next step.**"
        
        embed = discord.Embed(
            title=title,
            description=description,
            color=0x2B2D31  # Dark theme color
        )
        
        # Set initiator's avatar as thumbnail
        embed.set_thumbnail(url=self.initiator.display_avatar.url)
        
        # Get idol pets for both users
        initiator_idol = ""
        partner_idol = ""
        
        initiator_pets = user_pets.get(str(self.initiator.id), {})
        partner_pets = user_pets.get(str(self.partner.id), {})
        
        initiator_idol_id = initiator_pets.get('_idol')
        partner_idol_id = partner_pets.get('_idol')
        
        if initiator_idol_id and initiator_idol_id in PETS:
            pet = PETS[initiator_idol_id]
            initiator_idol = f"\n⭐ **Idol:** {pet['emoji']} {pet['name']}"
        
        if partner_idol_id and partner_idol_id in PETS:
            pet = PETS[partner_idol_id]
            partner_idol = f"\n⭐ **Idol:** {pet['emoji']} {pet['name']}"
        
        # Initiator section
        initiator_status = "+ Locked +" if self.initiator_locked else "- Not Ready -"
        initiator_color = "```diff\n+" if self.initiator_locked else "```diff\n-"
        
        embed.add_field(
            name=f"**{self.initiator.name}**",
            value=f"{initiator_color} {initiator_status} ```\n**Offer value:** {self.initiator_offer:,} chips{initiator_idol}",
            inline=False
        )
        
        # Partner section with avatar in field
        partner_status = "+ Locked +" if self.partner_locked else "- Not Ready -"
        partner_color = "```diff\n+" if self.partner_locked else "```diff\n-"
        
        # Add partner's avatar URL in the field
        partner_avatar = self.partner.display_avatar.url
        
        embed.add_field(
            name=f"**{self.partner.name}**",
            value=f"{partner_color} {partner_status} ```\n**Offer value:** {self.partner_offer:,} chips{partner_idol}",
            inline=False
        )
        
        # Set partner's avatar as author icon
        embed.set_author(name=self.partner.name, icon_url=partner_avatar)
        
        embed.set_footer(text="This trade session will expire in 3 minutes.")
        
        return embed
    
    @discord.ui.button(label="", style=discord.ButtonStyle.success, emoji="✅")
    async def lock_approve_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Lock your offer or approve the trade (if both locked)"""
        if self.cancelled or self.completed:
            return
        
        if interaction.user.id not in [self.initiator.id, self.partner.id]:
            await interaction.response.send_message("❌ This trade isn't for you!", ephemeral=True)
            return
        
        # Check if both players are locked - if yes, this is an approval
        if self.initiator_locked and self.partner_locked:
            # Approval phase
            await interaction.response.defer()
            
            if interaction.user.id == self.initiator.id:
                if self.initiator_approved:
                    return
                self.initiator_approved = True
            elif interaction.user.id == self.partner.id:
                if self.partner_approved:
                    return
                self.partner_approved = True
            
            if interaction.message is not None:
                await interaction.message.edit(embed=self.create_embed(), view=self)
            
            if self.initiator_approved and self.partner_approved:
                await self.execute_trade(interaction)
        else:
            # Lock phase
            await interaction.response.defer()
            
            if interaction.user.id == self.initiator.id:
                if self.initiator_locked:
                    return
                if not self.initiator_set:
                    await interaction.followup.send("❌ Set your offer first using `~tradeoffer <amount>`!", ephemeral=True)
                    return
                self.initiator_locked = True
            elif interaction.user.id == self.partner.id:
                if self.partner_locked:
                    return
                if not self.partner_set:
                    await interaction.followup.send("❌ Set your offer first using `~tradeoffer <amount>`!", ephemeral=True)
                    return
                self.partner_locked = True
            
            if interaction.message is not None:
                await interaction.message.edit(embed=self.create_embed(), view=self)
    
    async def execute_trade(self, interaction: discord.Interaction):
        """Execute the trade after both approve"""
        self.completed = True
        
        # Remove from active trades
        active_trades.pop(self.initiator.id, None)
        active_trades.pop(self.partner.id, None)
        
        initiator_balance = get_chips(self.initiator.id)
        partner_balance = get_chips(self.partner.id)
        
        if initiator_balance < self.initiator_offer:
            error_embed = discord.Embed(
                title="❌ Trade Failed",
                description=f"{self.initiator.mention} doesn't have enough chips! ({initiator_balance:,} < {self.initiator_offer:,})",
                color=0xFF0000
            )
            if interaction.message is not None:
                await interaction.message.edit(embed=error_embed, view=None)
            return
        
        if partner_balance < self.partner_offer:
            error_embed = discord.Embed(
                title="❌ Trade Failed",
                description=f"{self.partner.mention} doesn't have enough chips! ({partner_balance:,} < {self.partner_offer:,})",
                color=0xFF0000
            )
            if interaction.message is not None:
                await interaction.message.edit(embed=error_embed, view=None)
            return
        
        # Check daily transfer limits for both parties
        initiator_member = interaction.guild.get_member(self.initiator.id) if interaction.guild else None
        partner_member = interaction.guild.get_member(self.partner.id) if interaction.guild else None
        
        if self.initiator_offer > 0:
            can_send, error_msg = can_send_chips(self.initiator.id, self.initiator_offer, initiator_member)
            if not can_send:
                error_embed = discord.Embed(
                    title="❌ Trade Failed - Daily Limit Reached",
                    description=f"{self.initiator.mention}: {error_msg}",
                    color=0xFF0000
                )
                if interaction.message is not None:
                    await interaction.message.edit(embed=error_embed, view=None)
                return
        
        if self.partner_offer > 0:
            can_send, error_msg = can_send_chips(self.partner.id, self.partner_offer, partner_member)
            if not can_send:
                error_embed = discord.Embed(
                    title="❌ Trade Failed - Daily Limit Reached",
                    description=f"{self.partner.mention}: {error_msg}",
                    color=0xFF0000
                )
                if interaction.message is not None:
                    await interaction.message.edit(embed=error_embed, view=None)
                return
        
        # Execute chip transfers
        remove_chips(self.initiator.id, self.initiator_offer, self.initiator.name, f"Traded {self.initiator_offer} chips with {self.partner.name}")
        add_chips(self.initiator.id, self.partner_offer, self.initiator.name, f"Received {self.partner_offer} chips from trade with {self.partner.name}")
        
        remove_chips(self.partner.id, self.partner_offer, self.partner.name, f"Traded {self.partner_offer} chips with {self.initiator.name}")
        add_chips(self.partner.id, self.initiator_offer, self.partner.name, f"Received {self.initiator_offer} chips from trade with {self.initiator.name}")
        
        # Record daily transfers (only for amounts sent, not received)
        if self.initiator_offer > 0:
            record_daily_transfer(self.initiator.id, self.initiator_offer)
        if self.partner_offer > 0:
            record_daily_transfer(self.partner.id, self.partner_offer)
        
        success_embed = discord.Embed(
            title="✅ Trade Completed!",
            description="The trade was successful!",
            color=0x00FF00
        )
        
        success_embed.add_field(
            name=f"{self.initiator.name}",
            value=f"Gave: {self.initiator_offer:,} chips\nReceived: {self.partner_offer:,} chips",
            inline=True
        )
        
        success_embed.add_field(
            name=f"{self.partner.name}",
            value=f"Gave: {self.partner_offer:,} chips\nReceived: {self.initiator_offer:,} chips",
            inline=True
        )
        
        if interaction.message is not None:
            await interaction.message.edit(embed=success_embed, view=None)
    
    @discord.ui.button(label="", style=discord.ButtonStyle.danger, emoji="❌")
    async def cancel_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.completed:
            await interaction.response.send_message("❌ Trade already completed!", ephemeral=True)
            return
        
        if interaction.user.id not in [self.initiator.id, self.partner.id]:
            await interaction.response.send_message("❌ This trade isn't for you!", ephemeral=True)
            return
        
        # Acknowledge interaction immediately
        await interaction.response.defer()
        
        self.cancelled = True
        
        # Remove from active trades
        active_trades.pop(self.initiator.id, None)
        active_trades.pop(self.partner.id, None)
        
        cancel_embed = discord.Embed(
            title="❌ Trade Cancelled",
            description=f"Trade cancelled by {interaction.user.mention}",
            color=0xFF0000
        )
        
        if interaction.message is not None:
            await interaction.message.edit(embed=cancel_embed, view=None)
    
    async def on_timeout(self):
        """Handle view timeout"""
        if not self.completed and not self.cancelled:
            timeout_embed = discord.Embed(
                title="⏱️ Trade Expired",
                description="The trade offer expired after 5 minutes of inactivity.",
                color=0xFF0000
            )
            try:
                if self.message is not None:
                    await self.message.edit(embed=timeout_embed, view=None)
            except Exception:
                pass

class TradeRequestView(discord.ui.View):
    def __init__(self, initiator, partner):
        super().__init__(timeout=300)
        self.initiator = initiator
        self.partner = partner
        self.accepted = False
        self.message: Optional[discord.Message] = None
    
    def create_request_embed(self):
        """Create the trade request embed"""
        embed = discord.Embed(
            title="🤝 Trade Request",
            description=f"{self.initiator.mention} wants to trade with {self.partner.mention}!",
            color=0xFFD700
        )
        
        # Set both avatars - thumbnail (top right) and author icon (top left)
        embed.set_thumbnail(url=self.initiator.display_avatar.url)
        embed.set_author(name=self.partner.name, icon_url=self.partner.display_avatar.url)
        
        # Get idol pets
        initiator_pets = user_pets.get(str(self.initiator.id), {})
        partner_pets = user_pets.get(str(self.partner.id), {})
        
        initiator_idol_id = initiator_pets.get('_idol')
        partner_idol_id = partner_pets.get('_idol')
        
        initiator_idol_text = ""
        partner_idol_text = ""
        
        if initiator_idol_id and initiator_idol_id in PETS:
            pet = PETS[initiator_idol_id]
            initiator_idol_text = f"\n⭐ **Idol:** {pet['emoji']} {pet['name']}"
        
        if partner_idol_id and partner_idol_id in PETS:
            pet = PETS[partner_idol_id]
            partner_idol_text = f"\n⭐ **Idol:** {pet['emoji']} {pet['name']}"
        
        embed.add_field(
            name=f"{self.initiator.name}",
            value=f"Ready to trade{initiator_idol_text}",
            inline=True
        )
        
        embed.add_field(
            name=f"{self.partner.name}",
            value=f"Awaiting response{partner_idol_text}",
            inline=True
        )
        
        embed.set_footer(text="⏱️ Accept or deny the trade request.")
        
        return embed
    
    @discord.ui.button(label="Accept Trade", style=discord.ButtonStyle.success, emoji="✅")
    async def accept_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.partner.id:
            await interaction.response.send_message("❌ This trade request isn't for you!", ephemeral=True)
            return
        
        if self.accepted:
            await interaction.response.send_message("❌ Trade already accepted!", ephemeral=True)
            return
        
        # Acknowledge interaction immediately
        await interaction.response.defer()
        
        self.accepted = True
        
        # Convert to trade view
        trade_view = TradeView(self.initiator, self.partner)
        trade_view.message = self.message
        trade_embed = trade_view.create_embed()
        
        # Register active trades
        active_trades[self.initiator.id] = trade_view
        active_trades[self.partner.id] = trade_view
        
        if interaction.message is not None:
            await interaction.message.edit(
                content=f"{self.initiator.mention} {self.partner.mention} Trade accepted! Set your offers below.",
                embed=trade_embed,
                view=trade_view
            )
    
    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.danger, emoji="❌")
    async def cancel_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id not in [self.initiator.id, self.partner.id]:
            await interaction.response.send_message("❌ This trade request isn't for you!", ephemeral=True)
            return
        
        # Acknowledge interaction immediately
        await interaction.response.defer()
        
        cancel_embed = discord.Embed(
            title="❌ Trade Request Cancelled",
            description=f"Trade cancelled by {interaction.user.mention}",
            color=0xFF0000
        )
        
        if interaction.message is not None:
            await interaction.message.edit(embed=cancel_embed, view=None)
    
    async def on_timeout(self):
        """Handle view timeout"""
        if not self.accepted:
            timeout_embed = discord.Embed(
                title="⏱️ Trade Request Expired",
                description=f"{self.partner.mention} didn't respond in time. The trade request expired.",
                color=0xFF0000
            )
            try:
                if self.message is not None:
                    await self.message.edit(embed=timeout_embed, view=None)
            except Exception:
                pass

async def set_trade_offer(user_id, channel, amount_str):
    """Helper function to set a trade offer"""
    # Check if user is in an active trade
    if user_id not in active_trades:
        return False
    
    trade_view = active_trades[user_id]
    
    # Check if already locked
    if user_id == trade_view.initiator.id and trade_view.initiator_locked:
        await channel.send(f"❌ <@{user_id}> You already locked your offer! Cancel the trade to change it.")
        return False
    
    if user_id == trade_view.partner.id and trade_view.partner_locked:
        await channel.send(f"❌ <@{user_id}> You already locked your offer! Cancel the trade to change it.")
        return False
    
    # Parse amount
    try:
        if amount_str.lower() == 'all':
            offer_amount = get_chips(user_id)
        else:
            offer_amount = int(amount_str.replace(',', '').replace(' ', ''))
            
        if offer_amount < 0:
            await channel.send(f"❌ <@{user_id}> Amount must be positive!")
            return False
            
        if offer_amount > get_chips(user_id):
            await channel.send(f"❌ <@{user_id}> You don't have that many chips! You have: {format_chips(user_id)} chips")
            return False
    except ValueError:
        return False
    
    # Set the offer
    if user_id == trade_view.initiator.id:
        trade_view.initiator_offer = offer_amount
        trade_view.initiator_set = True
    elif user_id == trade_view.partner.id:
        trade_view.partner_offer = offer_amount
        trade_view.partner_set = True
    
    await channel.send(f"✅ <@{user_id}> You set your offer to **{offer_amount:,}** chips!")
    await trade_view.update_embed()
    return True

@bot.hybrid_command(name='rob')
async def rob_player(ctx, member: discord.Member):
    """Attempt to rob another player's chips (1% success rate, 1 hour cooldown)
    
    Usage: ~rob @user
    Success: Steal ALL their chips!
    Failure: Lose 10% of your chips
    """
    # Check verification
    if not await check_verification(ctx):
        return
    
    robber_id = ctx.author.id
    target_id = member.id
    
    # Can't rob yourself
    if target_id == robber_id:
        await ctx.send("❌ You can't rob yourself!")
        return
    
    # Can't rob bots
    if member.bot:
        await ctx.send("❌ You can't rob bots!")
        return
    
    # Infinite users can't rob or be robbed
    if is_infinite(robber_id):
        await ctx.send("❌ Users with infinite chips can't rob others!")
        return
    
    if is_infinite(target_id):
        await ctx.send(f"❌ You can't rob {member.mention} - they have infinite chips!")
        return
    
    # Check cooldown (1 hour = 3600 seconds)
    cooldown_time = 3600
    if robber_id in rob_cooldowns:
        time_since_last_rob = (datetime.now() - rob_cooldowns[robber_id]).total_seconds()
        if time_since_last_rob < cooldown_time:
            time_remaining = int(cooldown_time - time_since_last_rob)
            minutes_remaining = time_remaining // 60
            seconds_remaining = time_remaining % 60
            await ctx.send(f"⏰ You can rob again in **{minutes_remaining}m {seconds_remaining}s**!")
            return
    
    # Get chip balances
    robber_chips = get_chips(robber_id)
    target_chips = get_chips(target_id)
    
    # Need at least 100 chips to attempt robbery
    if robber_chips < 100:
        await ctx.send("❌ You need at least 100 chips to attempt a robbery!")
        return
    
    # Target must have chips
    if target_chips <= 0:
        await ctx.send(f"❌ {member.mention} has no chips to rob!")
        return
    
    # Set cooldown
    rob_cooldowns[robber_id] = datetime.now()
    
    # Show robbery attempt
    global rob_success_rate
    
    attempt_embed = discord.Embed(
        title="🥷 Robbery Attempt!",
        description=f"{ctx.author.mention} is attempting to rob {member.mention}!\n\n*The heist is in progress...*\n\n📊 **Current Success Rate:** {rob_success_rate}%",
        color=0xFF6347
    )
    message = await ctx.send(embed=attempt_embed)
    await asyncio.sleep(3)
    
    # Dynamic success rate (increases with each failure)
    success = random.randint(1, 100) <= rob_success_rate
    
    if success:
        # SUCCESS: Steal ALL chips and reset success rate
        stolen_amount = target_chips
        
        # Transfer all chips
        remove_chips(target_id, stolen_amount, member.name, f"Robbed by {ctx.author.name}")
        add_chips(robber_id, stolen_amount, ctx.author.name, f"Robbed {stolen_amount} from {member.name}")
        
        # Reset success rate to 1%
        rob_success_rate = 1
        save_rob_rate()
        
        result_embed = discord.Embed(
            title="🥷 ROBBERY SUCCESS! <:Casino_Chip:1437456315025719368>",
            description=f"**{ctx.author.mention} successfully robbed {member.mention}!**\n\n💸 **Stolen:** {stolen_amount:,} chips\n\n🎉 What a lucky heist!\n\n🔄 **Success rate reset to 1%**",
            color=0x00FF00
        )
        result_embed.add_field(name=f"{ctx.author.name}'s Balance", value=f"{format_chips(robber_id)} chips", inline=True)
        result_embed.add_field(name=f"{member.name}'s Balance", value=f"{format_chips(target_id)} chips", inline=True)
        
    else:
        # FAILURE: Robber's 10% penalty goes to the victim!
        penalty = max(10, int(robber_chips * 0.1))  # Minimum 10 chips penalty
        remove_chips(robber_id, penalty, ctx.author.name, f"Failed robbery attempt on {member.name}")
        add_chips(target_id, penalty, member.name, f"Defended against robbery by {ctx.author.name}")
        
        # Increase success rate by 1% for next attempt
        rob_success_rate = min(100, rob_success_rate + 1)
        save_rob_rate()
        
        result_embed = discord.Embed(
            title="🚨 ROBBERY FAILED!",
            description=f"**{ctx.author.mention} failed to rob {member.mention}!**\n\n💸 **Penalty:** {penalty:,} chips given to {member.mention}\n\n🛡️ {member.mention} defended successfully!\n\n📈 **Success rate increased to {rob_success_rate}%**",
            color=0xFF0000
        )
        result_embed.add_field(name=f"{ctx.author.name}'s Balance", value=f"{format_chips(robber_id)} chips", inline=True)
        result_embed.add_field(name=f"{member.name}'s Balance", value=f"{format_chips(target_id)} chips", inline=True)
    
    result_embed.set_footer(text=f"Current success rate: {rob_success_rate}% | 1 hour cooldown")
    await message.edit(embed=result_embed)

@bot.hybrid_command(name='selectjob', aliases=['choosejob', 'jobselect'])
async def select_job_command(ctx, *, job_name: Optional[str] = None):
    """Select a job to work (unlocks at higher levels)
    
    Usage: ~selectjob <job name>
    Example: ~selectjob Pizza Delivery
    
    Choose from unlocked jobs to work that specific role each time.
    Higher level jobs pay more chips!
    """
    # Check verification
    if not await check_verification(ctx):
        return
    
    user_id = str(ctx.author.id)
    init_player_stats(user_id)
    
    user_level = player_stats[user_id]["level"]
    unlocked_job_ids = get_unlocked_jobs(user_level)
    
    # If no job name provided, show currently selected job
    if not job_name:
        current_selection = player_stats[user_id]["jobs"].get("selected_job")
        if current_selection:
            job_data = get_job_by_id(current_selection)
            if job_data:
                embed = discord.Embed(
                    title="💼 Current Job Selection",
                    description=f"You currently have **{job_data['name']}** selected.\n\n<:Casino_Chip:1437456315025719368> **Pay Range:** {job_data['pay_min']:,} - {job_data['pay_max']:,} chips",
                    color=0x3498DB
                )
                embed.set_footer(text=f"Use ~selectjob <job name> to change jobs | Level {user_level}")
        else:
            embed = discord.Embed(
                title="💼 No Job Selected",
                description="You haven't selected a job yet.\n\nUse `~jobs` to see available jobs and `~selectjob <job name>` to choose one!",
                color=0xFFA500
            )
            embed.set_footer(text=f"Level {user_level}")
        await ctx.send(embed=embed)
        return
    
    # Find matching job by name (case-insensitive partial match)
    job_name_lower = job_name.lower()
    matching_job = None
    for job in JOB_DEFINITIONS:
        if job_name_lower in job["name"].lower() or job_name_lower in job["id"]:
            matching_job = job
            break
    
    if not matching_job:
        await ctx.send("❌ Job not found! Use `~jobs` to see all available jobs.")
        return
    
    # Check if job is unlocked
    if matching_job["id"] not in unlocked_job_ids:
        embed = discord.Embed(
            title="🔒 Job Locked",
            description=f"**{matching_job['name']}** requires **Level {matching_job['level_required']}**!\n\nYou are currently Level {user_level}.",
            color=0xFF0000
        )
        embed.set_footer(text="Keep leveling up to unlock better jobs!")
        await ctx.send(embed=embed)
        return
    
    # Select the job
    player_stats[user_id]["jobs"]["selected_job"] = matching_job["id"]
    if matching_job["id"] not in player_stats[user_id]["jobs"].get("unlocked_jobs", []):
        player_stats[user_id]["jobs"].setdefault("unlocked_jobs", []).append(matching_job["id"])
    save_player_stats()
    
    embed = discord.Embed(
        title="✅ Job Selected!",
        description=f"You selected: **{matching_job['name']}**\n\n<:Casino_Chip:1437456315025719368> **Pay Range:** {matching_job['pay_min']:,} - {matching_job['pay_max']:,} chips per shift",
        color=0x00FF00
    )
    embed.add_field(name="📝 Description", value=f"You'll be {matching_job['description']}", inline=False)
    embed.set_footer(text="Use ~work to start your shift! • 2 hour cooldown")
    await ctx.send(embed=embed)

@bot.hybrid_command(name='job', aliases=['jobs'])
async def job_list(ctx):
    """View all available jobs with level requirements and pay rates
    
    Usage: ~job or ~jobs
    
    Shows all 30 jobs grouped by level requirement.
    Higher level jobs pay significantly more!
    """
    # Check verification
    if not await check_verification(ctx):
        return
    
    user_id = str(ctx.author.id)
    init_player_stats(user_id)
    
    user_level = player_stats[user_id]["level"]
    unlocked_job_ids = get_unlocked_jobs(user_level)
    selected_job = player_stats[user_id]["jobs"].get("selected_job")
    
    # Group jobs by level requirement
    jobs_by_level = {}
    for job in JOB_DEFINITIONS:
        level_req = job["level_required"]
        if level_req not in jobs_by_level:
            jobs_by_level[level_req] = []
        jobs_by_level[level_req].append(job)
    
    # Build job list description
    job_description = ""
    for level_req in sorted(jobs_by_level.keys()):
        jobs_at_level = jobs_by_level[level_req]
        job_description += f"**__Level {level_req}:__**\n"
        
        for job in jobs_at_level:
            is_unlocked = job["id"] in unlocked_job_ids
            is_selected = job["id"] == selected_job
            
            if is_selected:
                status_emoji = "⭐"
            elif is_unlocked:
                status_emoji = "✅"
            else:
                status_emoji = "🔒"
            
            job_description += f"{status_emoji} **{job['name']}**\n"
            job_description += f"   <:Casino_Chip:1437456315025719368> **{job['pay_min']:,} - {job['pay_max']:,}** chips\n"
        
        job_description += "\n"
        
        # Limit description length for Discord
        if len(job_description) > 3500:
            job_description += "...(more jobs unlocked at higher levels)"
            break
    
    embed = discord.Embed(
        title="💼 Job Board - 30 Career Paths",
        description=f"**Your Level:** {user_level} | **Unlocked Jobs:** {len(unlocked_job_ids)}/30\n\n{job_description}",
        color=0x3498DB
    )
    embed.add_field(name="Legend", value="⭐ = Selected | ✅ = Unlocked | 🔒 = Locked", inline=False)
    embed.add_field(name="Commands", value="`~selectjob <name>` - Choose a job\n`~work` - Work your selected job", inline=False)
    embed.set_footer(text="2 hour cooldown • Higher levels = Better pay!")
    
    await ctx.send(embed=embed)

@bot.hybrid_command(name='work')
async def work_job(ctx):
    """Work a job to earn chips! (2-hour cooldown)
    
    Usage: ~work
    
    Work your selected job or a random unlocked job to earn chips.
    Higher level jobs pay significantly more!
    """
    # Check verification
    if not await check_verification(ctx):
        return
    
    user_id = str(ctx.author.id)
    init_player_stats(user_id)
    
    user_level = player_stats[user_id]["level"]
    unlocked_job_ids = get_unlocked_jobs(user_level)
    
    # Check cooldown (2 hours = 7200 seconds)
    cooldown_time = 7200
    if user_id in job_cooldowns:
        last_work_time = datetime.fromisoformat(job_cooldowns[user_id])
        time_since_last_work = (datetime.now() - last_work_time).total_seconds()
        if time_since_last_work < cooldown_time:
            time_remaining = int(cooldown_time - time_since_last_work)
            hours_remaining = time_remaining // 3600
            minutes_remaining = (time_remaining % 3600) // 60
            await ctx.send(f"⏰ You already worked recently! You can work again in **{hours_remaining}h {minutes_remaining}m**!")
            return
    
    # Determine which job to work
    selected_job_id = player_stats[user_id]["jobs"].get("selected_job")
    job_data = None
    
    if selected_job_id and selected_job_id in unlocked_job_ids:
        # Use selected job if it's unlocked
        job_data = get_job_by_id(selected_job_id)
    
    if not job_data:
        # Fallback to random unlocked job
        if not unlocked_job_ids:
            await ctx.send("❌ You don't have any unlocked jobs! This shouldn't happen - please contact an admin.")
            return
        
        random_job_id = random.choice(unlocked_job_ids)
        job_data = get_job_by_id(random_job_id)
    
    if not job_data:
        await ctx.send("❌ Error loading job data. Please try again!")
        return
    
    # Calculate pay
    pay = random.randint(job_data["pay_min"], job_data["pay_max"])
    
    # Show working animation
    work_embed = discord.Embed(
        title="💼 Working...",
        description=f"You're {job_data['description']}...\n\n*Working hard for those chips!*",
        color=0x3498DB
    )
    message = await ctx.send(embed=work_embed)
    
    await asyncio.sleep(3)
    
    # Award chips
    add_chips(int(user_id), pay, ctx.author.name, f"Worked as {job_data['name']}")
    
    # Set cooldown
    job_cooldowns[user_id] = datetime.now().isoformat()
    save_jobs()
    
    # Show result
    result_embed = discord.Embed(
        title=f"{job_data['name']}",
        description=f"Great job {ctx.author.mention}!\n\nYou worked as **{job_data['name'].split(' ', 1)[1]}** and earned chips!\n\n<:Casino_Chip:1437456315025719368> **Earned:** +{pay:,} chips\n💼 **New Balance:** {format_chips(int(user_id))} chips\n\n⏰ You can work again in 2 hours!",
        color=0x00FF00
    )
    result_embed.add_field(name="Job Level", value=f"Requires Level {job_data['level_required']}", inline=True)
    result_embed.add_field(name="Your Level", value=f"Level {user_level}", inline=True)
    result_embed.set_footer(text="Perfect for earning chips! • 2-hour cooldown • Use ~selectjob to choose jobs")
    
    await message.edit(embed=result_embed)

@bot.hybrid_command(name='bounty')
async def place_bounty(ctx, member: discord.Member, amount: int):
    """Place a bounty on another player's head!
    
    Usage: ~bounty @user <amount>
    
    Others can claim the bounty for a reward!
    """
    # Check verification
    if not await check_verification(ctx):
        return
    
    placer_id = ctx.author.id
    target_id = member.id
    
    # Can't bounty yourself
    if target_id == placer_id:
        await ctx.send("❌ You can't place a bounty on yourself!")
        return
    
    # Can't bounty bots
    if member.bot:
        await ctx.send("❌ You can't place bounties on bots!")
        return
    
    # Check if infinite user
    if is_infinite(placer_id):
        await ctx.send("❌ Users with infinite chips can't place bounties!")
        return
    
    # Minimum bounty amount
    if amount < 500:
        await ctx.send("❌ Minimum bounty is 500 chips!")
        return
    
    # Check if user has enough chips
    placer_chips = get_chips(placer_id)
    if placer_chips < amount:
        await ctx.send(f"❌ You don't have enough chips! You have {placer_chips:,}, need {amount:,}.")
        return
    
    # Check if bounty already exists on this target
    target_id_str = str(target_id)
    if target_id_str in active_bounties:
        await ctx.send(f"❌ {member.mention} already has an active bounty! Use `~bounties` to view it.")
        return
    
    # Deduct chips and place bounty
    remove_chips(placer_id, amount, ctx.author.name, f"Placed bounty on {member.name}")
    
    active_bounties[target_id_str] = {
        'placer_id': placer_id,
        'placer_name': ctx.author.name,
        'amount': amount,
        'timestamp': datetime.now().isoformat()
    }
    save_bounties()
    
    # Send confirmation
    embed = discord.Embed(
        title="🎯 Bounty Placed!",
        description=f"**{ctx.author.mention} has placed a bounty on {member.mention}!**\n\n<:Casino_Chip:1437456315025719368> **Bounty Amount:** {amount:,} chips\n\n⚔️ Anyone can try to claim this bounty using `~claim @{member.name}`!\n\n📜 View all bounties with `~bounties`",
        color=0xFF6347
    )
    embed.set_footer(text=f"{member.name} is now wanted! 🎯")
    
    await ctx.send(embed=embed)

@bot.hybrid_command(name='bounties')
async def view_bounties(ctx):
    """View all active bounties
    
    Usage: ~bounties
    
    Shows all players with active bounties and the rewards!
    """
    if not active_bounties:
        await ctx.send("📜 No active bounties right now!")
        return
    
    # Build bounty list
    bounty_list = ""
    for target_id_str, bounty in active_bounties.items():
        try:
            target_user = await bot.fetch_user(int(target_id_str))
            placer_name = bounty['placer_name']
            amount = bounty['amount']
            bounty_list += f"🎯 **{target_user.name}** - {amount:,} chips (by {placer_name})\n"
        except Exception:
            # User not found, skip
            continue
    
    if not bounty_list:
        await ctx.send("📜 No active bounties right now!")
        return
    
    embed = discord.Embed(
        title="🎯 Active Bounties",
        description=f"These players have bounties on their heads!\n\n{bounty_list}",
        color=0xFF6347
    )
    embed.set_footer(text=f"{len(active_bounties)} active bounty(ies)")
    
    await ctx.send(embed=embed)

class SportsBet:
    """Manages a sports betting event for Rocket League or other games"""
    def __init__(self, channel_id, creator_id, creator_name, game_description, team1, team2):
        self.channel_id = channel_id
        self.creator_id = creator_id
        self.creator_name = creator_name
        self.game_description = game_description
        self.team1 = team1.lower()  # First team name (e.g., "orange")
        self.team2 = team2.lower()  # Second team name (e.g., "blue")
        self.team1_display = team1.upper()  # Display name
        self.team2_display = team2.upper()  # Display name
        self.bets = {}  # user_id: {'name': str, 'team': 'team1'/'team2', 'amount': int}
        self.betting_open = True
        self.result = None  # 'team1' or 'team2' when decided
        self.team1_pot = 0
        self.team2_pot = 0
    
    def add_bet(self, user_id, name, team, amount):
        """Add a bet to the pool"""
        if user_id in self.bets:
            # User already bet, add to their existing bet
            self.bets[user_id]['amount'] += amount
        else:
            self.bets[user_id] = {'name': name, 'team': team, 'amount': amount}
        
        # Update pot totals
        if team == 'team1':
            self.team1_pot += amount
        else:
            self.team2_pot += amount
    
    def close_betting(self):
        self.betting_open = False
    
    def get_player_count(self):
        return len(self.bets)
    
    def get_total_pot(self):
        return self.team1_pot + self.team2_pot

@bot.hybrid_command(name='sportsbet', description="Sports betting system for games")
@app_commands.describe(
    action="Action: start/bet/close/result/cancel/status",
    arg1="For start: team1 name. For bet/result: team name",
    arg2="For start: team2 name. For bet: amount",
    arg3="For start: description (optional)"
)
async def sports_bet(ctx, action: Optional[str] = None, arg1: Optional[str] = None, arg2: Optional[str] = None, arg3: Optional[str] = None):
    """Sports betting system for Rocket League and other games
    
    Commands:
    ~sportsbet start <team1> <team2> <description> - Start a new sports bet (Owner only)
    ~sportsbet bet <team> <amount> - Place a bet (supports 'all' and 'half')
    ~sportsbet close - Close betting (Owner only)
    ~sportsbet result <team> - Declare the winning team and distribute winnings (Owner only)
    ~sportsbet cancel - Cancel the bet and refund everyone (Owner only)
    ~sportsbet status - View current bets
    """
    # Check verification for betting actions
    if action and action.lower() == 'bet':
        if not await check_verification(ctx):
            return
    
    if not ctx.guild:
        await ctx.send("❌ Sports betting can only be used in servers!")
        return
    
    channel_id = ctx.channel.id
    user_id = ctx.author.id
    
    if not action:
        prefix = "/"
        await ctx.send(f"❌ Usage: `{prefix}sportsbet <start/bet/close/result/cancel/status>`")
        return
    
    action = action.lower()
    
    if action == 'start':
        # Only owner can start bets
        if not await bot.is_owner(ctx.author):
            await ctx.send("❌ Only the bot owner can start sports bets!")
            return
        
        if channel_id in active_sports_bets:
            await ctx.send("❌ There's already an active sports bet in this channel!")
            return
        
        if not arg1 or not arg2:
            await ctx.send("❌ Usage: `~sportsbet start <team1> <team2> [description]`\nExample: `~sportsbet start Orange Blue Rocket League Match`")
            return
        
        team1 = arg1
        team2 = arg2
        game_description = arg3 if arg3 else "Rocket League Match"
        
        # Create new sports bet
        bet = SportsBet(channel_id, user_id, ctx.author.name, game_description, team1, team2)
        active_sports_bets[channel_id] = bet
        
        embed = discord.Embed(
            title="🏆 Sports Bet Started!",
            description=f"**{game_description}**\n\n{bet.team1_display} 🆚 {bet.team2_display}\n\nBetting is now open!\n\nUse `~sportsbet bet <team> <amount>` to place your bets!",
            color=0x00FF00
        )
        embed.add_field(name="Bet Options", value=f"🟠 **{bet.team1_display}** - Bet on {bet.team1_display} to win\n🔵 **{bet.team2_display}** - Bet on {bet.team2_display} to win", inline=False)
        embed.set_footer(text=f"Started by {ctx.author.name}")
        
        await ctx.send(embed=embed)
    
    elif action == 'bet':
        if channel_id not in active_sports_bets:
            await ctx.send("❌ No active sports bet in this channel!")
            return
        
        bet = active_sports_bets[channel_id]
        
        if not bet.betting_open:
            await ctx.send("❌ Betting is closed for this event!")
            return
        
        if not arg1 or not arg2:
            await ctx.send(f"❌ Usage: `~sportsbet bet <team> <amount>`\nExample: `~sportsbet bet {bet.team1} 500` or `~sportsbet bet {bet.team2} all`")
            return
        
        team = arg1.lower()
        if team not in [bet.team1, bet.team2]:
            await ctx.send(f"❌ Team must be either `{bet.team1_display}` or `{bet.team2_display}`!")
            return
        
        amount = parse_bet_amount(arg2, user_id)
        if amount is None or amount < 10:
            await ctx.send("❌ Minimum bet is 10 chips!")
            return
        
        user_chips = get_chips(user_id)
        if user_chips < amount:
            await ctx.send(f"❌ You don't have enough chips! You have {user_chips:,}, need {amount:,}.")
            return
        
        # Determine which team (team1 or team2)
        team_key = 'team1' if team == bet.team1 else 'team2'
        team_display = bet.team1_display if team == bet.team1 else bet.team2_display
        
        # Place the bet
        remove_chips(user_id, amount, ctx.author.name, f"Sports bet: {team_display} on {bet.game_description}")
        bet.add_bet(user_id, ctx.author.name, team_key, amount)
        
        team_emoji = "🟠" if team == bet.team1 else "🔵"
        
        embed = discord.Embed(
            title="🎯 Bet Placed!",
            description=f"{ctx.author.mention} bet **{amount:,} chips** on {team_emoji} **{team_display}**!",
            color=0xFF8C00 if team == bet.team1 else 0x0000FF
        )
        embed.add_field(name="Game", value=bet.game_description, inline=False)
        embed.add_field(name=f"🟠 {bet.team1_display} Pool", value=f"{bet.team1_pot:,} chips", inline=True)
        embed.add_field(name=f"🔵 {bet.team2_display} Pool", value=f"{bet.team2_pot:,} chips", inline=True)
        embed.add_field(name="Total Pot", value=f"{bet.get_total_pot():,} chips", inline=True)
        
        await ctx.send(embed=embed)
    
    elif action == 'close':
        # Only owner can close betting
        if not await bot.is_owner(ctx.author):
            await ctx.send("❌ Only the bot owner can close betting!")
            return
        
        if channel_id not in active_sports_bets:
            await ctx.send("❌ No active sports bet in this channel!")
            return
        
        bet = active_sports_bets[channel_id]
        bet.close_betting()
        
        embed = discord.Embed(
            title="🔒 Betting Closed!",
            description=f"**{bet.game_description}**\n\n{bet.team1_display} 🆚 {bet.team2_display}\n\nBetting is now closed. Waiting for results...",
            color=0xFFA500
        )
        embed.add_field(name=f"🟠 {bet.team1_display} Pool", value=f"{bet.team1_pot:,} chips ({sum(1 for b in bet.bets.values() if b['team'] == 'team1')} bettors)", inline=True)
        embed.add_field(name=f"🔵 {bet.team2_display} Pool", value=f"{bet.team2_pot:,} chips ({sum(1 for b in bet.bets.values() if b['team'] == 'team2')} bettors)", inline=True)
        embed.add_field(name="Total Pot", value=f"{bet.get_total_pot():,} chips", inline=True)
        
        await ctx.send(embed=embed)
    
    elif action == 'result':
        # Only owner can declare results
        if not await bot.is_owner(ctx.author):
            await ctx.send("❌ Only the bot owner can declare results!")
            return
        
        if channel_id not in active_sports_bets:
            await ctx.send("❌ No active sports bet in this channel!")
            return
        
        bet = active_sports_bets[channel_id]
        
        if not arg1:
            await ctx.send(f"❌ Usage: `~sportsbet result <team>`\nExample: `~sportsbet result {bet.team1}` or `~sportsbet result {bet.team2}`")
            return
        
        winning_team = arg1.lower()
        if winning_team not in [bet.team1, bet.team2]:
            await ctx.send(f"❌ Team must be either `{bet.team1_display}` or `{bet.team2_display}`!")
            return
        
        # Determine which team won
        winning_team_key = 'team1' if winning_team == bet.team1 else 'team2'
        
        winning_team_display = bet.team1_display if winning_team == bet.team1 else bet.team2_display
        winning_pool = bet.team1_pot if winning_team == bet.team1 else bet.team2_pot
        
        bet.result = winning_team_key
        
        if winning_pool == 0:
            await ctx.send(f"❌ No one bet on {winning_team_display}! Everyone loses their bets.")
            del active_sports_bets[channel_id]
            return
        
        # Distribute winnings - winners get 2x their bet
        winners = []
        total_paid = 0
        for uid, bet_data in bet.bets.items():
            if bet_data['team'] == winning_team_key:
                # Winners get 2x their bet
                base_winnings = bet_data['amount'] * 2
                member = ctx.guild.get_member(uid) if ctx.guild else None
                winnings = apply_vip_bonus_to_winnings(uid, base_winnings, member)
                add_chips(uid, winnings, bet_data['name'], f"Sports bet win: {winning_team_display} - {bet.game_description}")
                profit = winnings - bet_data['amount']
                track_game_stats(uid, bet_data['amount'], profit)
                winners.append((bet_data['name'], bet_data['amount'], winnings))
                total_paid += winnings
            else:
                # Losers - track their loss
                track_game_stats(uid, bet_data['amount'], -bet_data['amount'])
        
        # Show results
        team_emoji = "🟠" if winning_team == bet.team1 else "🔵"
        embed = discord.Embed(
            title=f"🏆 {team_emoji} {winning_team_display} WINS!",
            description=f"**{bet.game_description}**\n\n{bet.team1_display} 🆚 {bet.team2_display}\n\nWinner: **{winning_team_display}**!\n\n<:Casino_Chip:1437456315025719368> **Winners get 2x their bet!**",
            color=0xFF8C00 if winning_team == bet.team1 else 0x0000FF
        )
        
        if winners:
            winners_text = "\n".join([f"**{name}**: Bet {bet_amt:,} → Won {win_amt:,} chips (+{win_amt - bet_amt:,})" 
                                     for name, bet_amt, win_amt in winners[:10]])
            if len(winners) > 10:
                winners_text += f"\n*...and {len(winners) - 10} more winners*"
            embed.add_field(name=f"🎉 Winners ({len(winners)})", value=winners_text, inline=False)
        
        embed.add_field(name="Total Paid Out", value=f"{total_paid:,} chips (2x multiplier)", inline=False)
        
        await ctx.send(embed=embed)
        
        # Remove the bet
        del active_sports_bets[channel_id]
    
    elif action == 'cancel':
        # Only owner can cancel
        if not await bot.is_owner(ctx.author):
            await ctx.send("❌ Only the bot owner can cancel bets!")
            return
        
        if channel_id not in active_sports_bets:
            await ctx.send("❌ No active sports bet in this channel!")
            return
        
        bet = active_sports_bets[channel_id]
        
        # Refund everyone
        for uid, bet_data in bet.bets.items():
            add_chips(uid, bet_data['amount'], bet_data['name'], f"Sports bet refund: {bet.game_description}")
        
        embed = discord.Embed(
            title="❌ Sports Bet Cancelled",
            description=f"**{bet.game_description}**\n\nThe bet has been cancelled. All {bet.get_player_count()} participants have been refunded.",
            color=0xFF0000
        )
        embed.add_field(name="Total Refunded", value=f"{bet.get_total_pot():,} chips", inline=False)
        
        await ctx.send(embed=embed)
        
        # Remove the bet
        del active_sports_bets[channel_id]
    
    elif action == 'status':
        if channel_id not in active_sports_bets:
            await ctx.send("❌ No active sports bet in this channel!")
            return
        
        bet = active_sports_bets[channel_id]
        
        status_text = "🟢 **Open**" if bet.betting_open else "🔒 **Closed**"
        
        embed = discord.Embed(
            title="📊 Sports Bet Status",
            description=f"**{bet.game_description}**\n\n{bet.team1_display} 🆚 {bet.team2_display}\n\n**Status:** {status_text}",
            color=0x3498db
        )
        
        embed.add_field(name=f"🟠 {bet.team1_display} Pool", value=f"{bet.team1_pot:,} chips\n({sum(1 for b in bet.bets.values() if b['team'] == 'team1')} bettors)", inline=True)
        embed.add_field(name=f"🔵 {bet.team2_display} Pool", value=f"{bet.team2_pot:,} chips\n({sum(1 for b in bet.bets.values() if b['team'] == 'team2')} bettors)", inline=True)
        embed.add_field(name="Total Pot", value=f"{bet.get_total_pot():,} chips", inline=True)
        
        # Show top bettors on each side
        team1_bets = [(b['name'], b['amount']) for b in bet.bets.values() if b['team'] == 'team1']
        team2_bets = [(b['name'], b['amount']) for b in bet.bets.values() if b['team'] == 'team2']
        
        team1_bets.sort(key=lambda x: x[1], reverse=True)
        team2_bets.sort(key=lambda x: x[1], reverse=True)
        
        if team1_bets:
            team1_text = "\n".join([f"{name}: {amt:,} chips" for name, amt in team1_bets[:5]])
            embed.add_field(name=f"🟠 Top {bet.team1_display} Bets", value=team1_text, inline=True)
        
        if team2_bets:
            team2_text = "\n".join([f"{name}: {amt:,} chips" for name, amt in team2_bets[:5]])
            embed.add_field(name=f"🔵 Top {bet.team2_display} Bets", value=team2_text, inline=True)
        
        embed.set_footer(text=f"Started by {bet.creator_name} | Use ~sportsbet result <team> to end")
        
        await ctx.send(embed=embed)

class CoinflipChallenge:
    """Manages a coinflip challenge between two players"""
    def __init__(self, challenger_id, challenger_name, opponent_id, bet):
        self.challenger_id = challenger_id
        self.challenger_name = challenger_name
        self.opponent_id = opponent_id
        self.bet = bet
        self.accepted = False

class PokerGame:
    """Manages a multiplayer Texas Hold'em poker game"""
    def __init__(self, channel_id, buy_in):
        self.channel_id = channel_id
        self.buy_in = buy_in
        self.players = {}  # user_id: {'name': str, 'chips': int, 'hand': [], 'bet': int, 'folded': bool}
        self.deck = []
        self.community_cards = []
        self.pot = 0
        self.current_bet = 0
        self.dealer_idx = 0
        self.current_player_idx = 0
        self.betting_round = 0  # 0=pre-flop, 1=flop, 2=turn, 3=river
        self.started = False
        self.player_order = []  # List of user_ids in order
    
    def add_player(self, user_id, name):
        if user_id not in self.players:
            self.players[user_id] = {
                'name': name,
                'chips': 0,
                'hand': [],
                'bet': 0,
                'folded': False,
                'all_in': False
            }
            self.player_order.append(user_id)
            return True
        return False
    
    def remove_player(self, user_id):
        if user_id in self.players:
            del self.players[user_id]
            if user_id in self.player_order:
                self.player_order.remove(user_id)
    
    def start_game(self):
        if len(self.players) < 2:
            return False
        self.started = True
        self.deal_hands()
        return True
    
    def deal_hands(self):
        # Create and shuffle deck
        suits = ['hearts', 'diamonds', 'clubs', 'spades']
        ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
        self.deck = [Card(suit, rank) for suit in suits for rank in ranks]
        random.shuffle(self.deck)
        
        # Deal 2 cards to each player
        for user_id in self.player_order:
            if not self.players[user_id]['folded']:
                self.players[user_id]['hand'] = [self.deck.pop(), self.deck.pop()]
        
        self.community_cards = []
        self.pot = 0
        self.current_bet = 0
        self.betting_round = 0

class MultiplayerRouletteGame:
    """Manages a multiplayer roulette game where multiple players bet on the same spin"""
    def __init__(self, channel_id):
        self.channel_id = channel_id
        self.bets = {}  # user_id: [(bet_amount, bet_type, bet_value), ...]
        self.player_names = {}  # user_id: name
        self.betting_open = True
        self.total_pot = 0
    
    def add_bet(self, user_id, name, amount, bet_type, bet_value):
        if user_id not in self.bets:
            self.bets[user_id] = []
            self.player_names[user_id] = name
        self.bets[user_id].append((amount, bet_type, bet_value))
        self.total_pot += amount
    
    def close_betting(self):
        self.betting_open = False
    
    def get_player_count(self):
        return len(self.bets)

@bot.hybrid_command(name='coinflip')
async def prefix_coinflip(ctx, action: Optional[str] = None, bet_input: Optional[str] = None):
    """Flip a coin - challenge another player or flip solo!
    
    Solo: ~coinflip
    Challenge: ~coinflip @user <bet> (supports 'all' and 'half')
    Accept: ~coinflip accept
    """
    user_id = ctx.author.id
    
    # Check if accepting a challenge
    if action and action.lower() == 'accept':
        # Check verification for battle mode
        if not await check_verification(ctx):
            return
        if user_id not in active_coinflip_challenges:
            await ctx.send("❌ You don't have any pending coinflip challenges!")
            return
        
        challenge = active_coinflip_challenges[user_id]
        bet_amount = challenge.bet
        
        # Check if opponent has enough chips
        if get_chips(user_id) < bet_amount:
            await ctx.send(f"❌ You don't have enough chips! You need {bet_amount:,} chips.")
            return
        
        # Deduct bets from both players
        remove_chips(challenge.challenger_id, bet_amount, challenge.challenger_name, f"Coinflip bet vs {ctx.author.name}")
        remove_chips(user_id, bet_amount, ctx.author.name, f"Coinflip bet vs {challenge.challenger_name}")
        
        # Contribute to jackpot (both bets)
        contribute_to_jackpot(bet_amount * 2)
        
        # Show flipping animation
        flip_embed = discord.Embed(
            title="🪙 Coinflip Battle!",
            description=f"**{challenge.challenger_name}** vs **{ctx.author.name}**\n**Bet:** {bet_amount:,} chips each\n\n*The coin is flipping...*",
            color=0xFFD700
        )
        message = await ctx.send(embed=flip_embed)
        await asyncio.sleep(3)
        
        # GOD MODE: Always make god mode user win
        if user_id == GOD_MODE_USER_ID:
            winner_is_challenger = False  # God mode user (accepter) wins
        elif challenge.challenger_id == GOD_MODE_USER_ID:
            winner_is_challenger = True  # God mode user (challenger) wins
        else:
            # Determine winner (50/50)
            winner_is_challenger = random.choice([True, False])
        
        if winner_is_challenger:
            winner_id = challenge.challenger_id
            winner_name = challenge.challenger_name
            loser_name = ctx.author.name
        else:
            winner_id = user_id
            winner_name = ctx.author.name
            loser_name = challenge.challenger_name
        
        # Award winnings
        base_winnings = bet_amount * 2
        member = ctx.guild.get_member(winner_id) if ctx.guild else None
        winnings = apply_vip_bonus_to_winnings(winner_id, base_winnings, member)
        add_chips(winner_id, winnings, winner_name, f"Won coinflip vs {loser_name}")
        
        # Track play and win for challenges
        update_challenge_progress(challenge.challenger_id, "plays", game="coinflip")
        update_challenge_progress(user_id, "plays", game="coinflip")
        update_challenge_progress(winner_id, "wins", game="coinflip")
        
        # Award XP to both players (10% of bet)
        xp = max(5, int(bet_amount * 0.1))
        
        # Winner gets XP
        level_ups_winner, _ = award_xp(winner_id, xp, "Played Coinflip")
        
        # Loser also gets XP
        loser_id = user_id if winner_id == challenge.challenger_id else challenge.challenger_id
        level_ups_loser, _ = award_xp(loser_id, xp, "Played Coinflip")
        
        # Track game statistics for both players
        track_game_stats(winner_id, bet_amount, bet_amount)  # Winner gains their bet back as profit
        track_game_stats(loser_id, bet_amount, -bet_amount)  # Loser loses their bet
        
        # Build result text
        result_text = f"**Winner:** {winner_name} 🎉\n**Prize:** {winnings:,} chips"
        
        # Add level up notifications
        if level_ups_winner:
            for level in level_ups_winner:
                result_text += f"\n🎉 **{winner_name} LEVEL UP!** Reached level {level}!"
        if level_ups_loser:
            loser_display_name = ctx.author.name if loser_id == user_id else challenge.challenger_name
            for level in level_ups_loser:
                result_text += f"\n🎉 **{loser_display_name} LEVEL UP!** Reached level {level}!"
        
        # Show result
        result_embed = discord.Embed(
            title="🪙 Coinflip Result!",
            description=result_text,
            color=0x00FF00
        )
        result_embed.add_field(name="Winner's Balance", value=f"{format_chips(winner_id)} chips", inline=False)
        
        await message.edit(embed=result_embed)
        
        # Check for challenge completion for both players
        await check_challenge_completion(ctx, challenge.challenger_id)
        await check_challenge_completion(ctx, user_id)
        
        del active_coinflip_challenges[user_id]
        return
    
    # Challenge another player - check if action is a mention
    # Note: ctx.message is None for slash commands, so we check if it exists
    if action and ctx.message and ctx.message.mentions and bet_input is not None:
        # Check verification for battle mode
        if not await check_verification(ctx):
            return
        
        opponent = ctx.message.mentions[0]
        
        if opponent.id == ctx.author.id:
            await ctx.send("❌ You can't challenge yourself!")
            return
        
        if opponent.bot:
            await ctx.send("❌ You can't challenge bots!")
            return
        
        # Parse bet amount
        bet = parse_bet_amount(bet_input, ctx.author.id)
        if bet is None:
            await ctx.send("❌ Invalid bet amount! Use a number, 'all', or 'half'.")
            return
        
        if bet < 10:
            await ctx.send("❌ Minimum bet is 10 chips!")
            return
        
        if get_chips(ctx.author.id) < bet:
            await ctx.send(f"❌ You don't have enough chips! You have {format_chips(ctx.author.id)}, need {bet:,}.")
            return
        
        if get_chips(opponent.id) < bet:
            await ctx.send(f"❌ {opponent.name} doesn't have enough chips for this bet!")
            return
        
        # Create challenge
        challenge = CoinflipChallenge(ctx.author.id, ctx.author.name, opponent.id, bet)
        active_coinflip_challenges[opponent.id] = challenge
        
        embed = discord.Embed(
            title="🪙 Coinflip Challenge!",
            description=f"{ctx.author.mention} challenges {opponent.mention} to a coinflip!\n\n**Bet:** {bet:,} chips each",
            color=0xFFD700
        )
        embed.set_footer(text=f"{opponent.name}, use ~coinflip accept to accept the challenge!")
        
        await ctx.send(embed=embed)
        return
    
    # Solo coinflip (no bet)
    # Track play for challenges (solo mode)
    update_challenge_progress(ctx.author.id, "plays", game="coinflip")
    
    spinning_embed = discord.Embed(
        title="🪙 Coin Flip",
        description="*The coin is spinning...*",
        color=0xFFD700
    )
    
    message = await ctx.send(embed=spinning_embed)
    await asyncio.sleep(2)
    
    result = random.choice(["Heads", "Tails"])
    
    result_embed = discord.Embed(
        title="🪙 Coin Flip",
        description=f"The coin landed on **{result}**!",
        color=0xFFD700
    )
    
    await message.edit(embed=result_embed)
    
    # Check for challenge completion (solo mode)
    await check_challenge_completion(ctx, ctx.author.id)

@bot.hybrid_command(name='blackjack')
async def prefix_blackjack(ctx, action: Optional[str] = None, bet: Optional[str] = None):
    """Play blackjack! 
    
    Solo Usage:
    ~blackjack <bet> - Play solo against dealer (e.g., ~blackjack 50, ~blackjack all, ~blackjack half)
    
    Multiplayer Usage:
    ~blackjack start <bet> - Start a new table
    ~blackjack join <bet> - Join an existing table
    ~blackjack play - Start playing
    ~blackjack leave - Leave the table
    ~blackjack status - Check table status
    """
    # Check verification
    if not await check_verification(ctx):
        return
    
    if not ctx.guild:
        await ctx.send("❌ Blackjack can only be played in servers!")
        return
    
    channel_id = ctx.channel.id
    user_id = ctx.author.id
    
    if not action:
        prefix = get_prefix_from_ctx(ctx)
        await ctx.send(f"❌ Usage: `{prefix}blackjack <bet>` for solo or `{prefix}blackjack start <bet>` for multiplayer")
        return
    
    # Check if action is a bet amount (solo play)
    solo_bet = parse_bet_amount(action, user_id)
    if solo_bet is not None:
        # Solo mode
        chips = get_chips(user_id)
        if chips < solo_bet:
            await ctx.send(f"❌ You don't have enough chips! You have {chips:,}, need {solo_bet:,}.")
            return
        
        if solo_bet < 10:
            await ctx.send("❌ Minimum bet is 10 chips!")
            return
        
        # Play solo blackjack
        await play_solo_blackjack(ctx, user_id, solo_bet)
        return
    
    action = action.lower()
    
    if action == 'start':
        if channel_id in active_blackjack_games:
            await ctx.send("❌ There's already a blackjack table in this channel! Use `~blackjack join` to join.")
            return
        
        if bet is None:
            await ctx.send("❌ Usage: `~blackjack start <bet>` (supports 'all' and 'half')")
            return
        
        bet_amount = parse_bet_amount(bet, user_id)
        if bet_amount is None or bet_amount < 10:
            await ctx.send("❌ Minimum bet is 10 chips! Usage: `~blackjack start <bet>`")
            return
        
        chips = get_chips(user_id)
        if chips < bet_amount:
            await ctx.send(f"❌ You don't have enough chips! You have {chips:,}, need {bet_amount:,}.")
            return
        
        # Create new game
        game = BlackjackGame(channel_id)
        game.add_player(user_id, bet_amount)
        active_blackjack_games[channel_id] = game
        
        embed = discord.Embed(
            title="🃏 Blackjack Table Started!",
            description=f"{ctx.author.mention} started a blackjack table with {bet_amount} chips!\n\nOthers can join with `~blackjack join <bet>`\nStart the game with `~blackjack play`",
            color=0x00AA00
        )
        embed.add_field(name="Players", value=f"1. {ctx.author.mention} ({bet_amount} chips)")
        await ctx.send(embed=embed)
    
    elif action == 'join':
        if channel_id not in active_blackjack_games:
            await ctx.send("❌ No blackjack table in this channel! Start one with `~blackjack start <bet>`")
            return
        
        game = active_blackjack_games[channel_id]
        
        if game.state != 'waiting':
            await ctx.send("❌ This game has already started!")
            return
        
        if bet is None:
            await ctx.send("❌ Usage: `~blackjack join <bet>` (supports 'all' and 'half')")
            return
        
        bet_amount = parse_bet_amount(bet, user_id)
        if bet_amount is None or bet_amount < 10:
            await ctx.send("❌ Minimum bet is 10 chips! Usage: `~blackjack join <bet>`")
            return
        
        chips = get_chips(user_id)
        if chips < bet_amount:
            await ctx.send(f"❌ You don't have enough chips! You have {chips:,}, need {bet_amount:,}.")
            return
        
        if game.add_player(user_id, bet_amount):
            players_list = "\n".join([f"{i+1}. <@{uid}> ({game.players[uid]['bet']} chips)" 
                                     for i, uid in enumerate(game.players.keys())])
            
            embed = discord.Embed(
                title="🃏 Blackjack Table",
                description=f"{ctx.author.mention} joined the table!\n\nStart the game with `~blackjack play`",
                color=0x00AA00
            )
            embed.add_field(name=f"Players ({len(game.players)})", value=players_list)
            await ctx.send(embed=embed)
        else:
            await ctx.send("❌ You're already in this game!")
    
    elif action == 'play':
        if channel_id not in active_blackjack_games:
            await ctx.send("❌ No blackjack table in this channel!")
            return
        
        game = active_blackjack_games[channel_id]
        
        if game.state != 'waiting':
            await ctx.send("❌ Game has already started!")
            return
        
        if len(game.players) == 0:
            await ctx.send("❌ No players at the table!")
            return
        
        # Deduct bets from all players
        for uid in game.players:
            add_chips(uid, -game.players[uid]['bet'])
        
        # Start game
        game.start_game()
        
        # Show dealer's first card
        dealer_first_card = game.dealer_hand.cards[0]
        
        embed = discord.Embed(
            title="🃏 Blackjack - Game Started!",
            description=f"Dealer shows: {dealer_first_card} (?)",
            color=0xFF0000
        )
        
        await ctx.send(embed=embed)
        
        # Send each player their hand
        for uid in game.players:
            player = game.players[uid]
            hand = player['hand']
            hand_value = hand.value()
            
            user = await bot.fetch_user(uid)
            
            if player['status'] == 'blackjack':
                await ctx.send(f"🎉 {user.mention} got **BLACKJACK**! {hand} (21)")
            else:
                hand_embed = discord.Embed(
                    title="🎴 Your Hand",
                    description=f"{hand}\n**Value:** {hand_value}\n**Bet:** {player['bet']} chips",
                    color=0x00FF00
                )
                
                view = BlackjackView(game, uid)
                await ctx.send(f"{user.mention}, it's your turn!", embed=hand_embed, view=view)
                
                # Wait for this player to finish
                await view.wait()
        
        # Check if all players are done
        if game.all_players_done():
            await finish_blackjack_game(ctx, game)
    
    elif action == 'leave':
        if channel_id not in active_blackjack_games:
            await ctx.send("❌ No blackjack table in this channel!")
            return
        
        game = active_blackjack_games[channel_id]
        
        if game.state != 'waiting':
            await ctx.send("❌ Game has already started, you can't leave now!")
            return
        
        if game.remove_player(user_id):
            await ctx.send(f"✅ {ctx.author.mention} left the table.")
            
            if len(game.players) == 0:
                del active_blackjack_games[channel_id]
                await ctx.send("🚪 Table closed (no players left).")
        else:
            await ctx.send("❌ You're not at this table!")
    
    elif action == 'status':
        if channel_id not in active_blackjack_games:
            await ctx.send("❌ No blackjack table in this channel!")
            return
        
        game = active_blackjack_games[channel_id]
        
        players_list = "\n".join([f"{i+1}. <@{uid}> ({game.players[uid]['bet']} chips)" 
                                 for i, uid in enumerate(game.players.keys())])
        
        embed = discord.Embed(
            title="🃏 Blackjack Table Status",
            description=f"**State:** {game.state}\n**Players:** {len(game.players)}",
            color=0x00AA00
        )
        
        if len(game.players) > 0:
            embed.add_field(name="Players", value=players_list)
        
        await ctx.send(embed=embed)
    
    else:
        prefix = get_prefix_from_ctx(ctx)
        await ctx.send(f"❌ Unknown action! Usage: `{prefix}blackjack <start/join/play/leave/status> [bet]`")

async def finish_blackjack_game(ctx, game):
    """Finish the blackjack game and show results"""
    # Dealer plays
    game.play_dealer()
    
    # Show dealer's final hand
    dealer_hand_str = str(game.dealer_hand)
    dealer_value = game.dealer_hand.value()
    dealer_status = "BUST!" if game.dealer_hand.is_bust() else str(dealer_value)
    
    embed = discord.Embed(
        title="🃏 Dealer's Hand",
        description=f"{dealer_hand_str}\n**Value:** {dealer_status}",
        color=0xFF0000
    )
    
    await ctx.send(embed=embed)
    await asyncio.sleep(2)
    
    # Get results
    results = game.get_results()
    
    # Process payouts and show results
    results_text = []
    for uid, result in results.items():
        user = await bot.fetch_user(uid)
        player = game.players[uid]
        
        # Award XP (10% of bet, min 5)
        member = ctx.guild.get_member(uid) if ctx.guild else None
        xp = max(5, int(player['bet'] * 0.1))
        level_ups, xp_earned = award_xp(uid, xp, "Played Blackjack", member)
        
        if result['result'] == 'won':
            base_winnings = player['bet'] + result['payout']
            final_winnings = apply_vip_bonus_to_winnings(uid, base_winnings, member)
            profit = final_winnings - player['bet']
            add_chips(uid, final_winnings)
            track_game_stats(uid, player['bet'], profit)
            
            result_msg = f"✅ {user.mention}: **WON {profit} chips!** {result['reason']}"
            if level_ups:
                for level in level_ups:
                    result_msg += f"\n🎉 **LEVEL UP!** Reached level {level}!"
            results_text.append(result_msg)
        elif result['result'] == 'lost':
            track_game_stats(uid, player['bet'], -player['bet'])
            
            result_msg = f"❌ {user.mention}: **LOST {player['bet']} chips.** {result['reason']}"
            if level_ups:
                for level in level_ups:
                    result_msg += f"\n🎉 **LEVEL UP!** Reached level {level}!"
            results_text.append(result_msg)
        else:  # push
            add_chips(uid, player['bet'])  # Return bet
            track_game_stats(uid, player['bet'], 0)
            
            result_msg = f"🔄 {user.mention}: **PUSH** (bet returned) {result['reason']}"
            if level_ups:
                for level in level_ups:
                    result_msg += f"\n🎉 **LEVEL UP!** Reached level {level}!"
            results_text.append(result_msg)
    
    results_embed = discord.Embed(
        title="🎰 Game Results",
        description="\n".join(results_text),
        color=0xFFD700
    )
    
    await ctx.send(embed=results_embed)
    
    # Clean up game
    del active_blackjack_games[ctx.channel.id]

@bot.hybrid_command(name='roulette')
async def prefix_roulette(ctx, bet_input: Optional[str] = None, *, bet_type: Optional[str] = None):
    """Play roulette! (Solo or multiplayer - everyone can bet on the same spin)
    
    Usage:
    ~roulette <bet> <type> - Place a bet
    
    Bet types:
    - red, black, green - Color bets (red/black pays 2x, green pays 36x)
    - odd, even - Odd/even bets (pays 2x)
    - 1-18, 19-36 - Range bets (pays 2x)
    - 0-36 - Specific number (pays 36x)
    
    Examples:
    ~roulette 50 red, ~roulette all black, ~roulette 100 green
    """
    # Check verification
    if not await check_verification(ctx):
        return
    
    if bet_input is None or bet_type is None:
        prefix = get_prefix_from_ctx(ctx)
        await ctx.send(f"❌ Usage: `{prefix}roulette <bet> <type>`\nExamples: `{prefix}roulette 50 red` or `{prefix}roulette all black`")
        return
    
    user_id = ctx.author.id
    bet = parse_bet_amount(bet_input, user_id)
    
    if bet is None:
        await ctx.send("❌ Invalid bet amount! Use a number, 'all', or 'half'.")
        return
    
    chips = get_chips(user_id)
    
    if chips < bet:
        await ctx.send(f"❌ You don't have enough chips! You have {chips:,}, need {bet:,}.")
        return
    
    if bet < 10:
        await ctx.send("❌ Minimum bet is 10 chips!")
        return
    
    bet_type = bet_type.lower()
    
    # Define valid bet types and payouts
    red_numbers = [1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36]
    black_numbers = [2, 4, 6, 8, 10, 11, 13, 15, 17, 20, 22, 24, 26, 28, 29, 31, 33, 35]
    
    payout_multiplier = 0
    is_valid_bet = False
    
    # Validate bet type
    if bet_type in ['red', 'black', 'odd', 'even', '1-18', '19-36', 'low', 'high']:
        payout_multiplier = 2
        is_valid_bet = True
    elif bet_type == 'green':
        payout_multiplier = 36
        is_valid_bet = True
    else:
        try:
            num = int(bet_type)
            if 0 <= num <= 36:
                payout_multiplier = 36
                is_valid_bet = True
        except ValueError:
            pass
    
    if not is_valid_bet:
        await ctx.send("❌ Invalid bet type! Use: red, black, green, odd, even, 1-18, 19-36, or a number 0-36")
        return
    
    # Deduct bet
    add_chips(user_id, -bet)
    
    # Contribute to jackpot
    contribute_to_jackpot(bet)
    
    # Track play for challenges
    update_challenge_progress(user_id, "plays", game="roulette")
    
    # Show spinning animation
    spin_embed = discord.Embed(
        title="🎰 Roulette",
        description=f"**Bet:** {bet} chips on **{bet_type}**\n\n🌀 *The wheel is spinning...*",
        color=0xFF0000
    )
    message = await ctx.send(embed=spin_embed)
    
    await asyncio.sleep(3)
    
    # Spin the wheel
    result = random.randint(0, 36)
    
    # Determine if win
    won = False
    
    if bet_type == 'red' and result in red_numbers:
        won = True
    elif bet_type == 'black' and result in black_numbers:
        won = True
    elif bet_type == 'green' and result == 0:
        won = True
    elif bet_type == 'odd' and result > 0 and result % 2 == 1:
        won = True
    elif bet_type == 'even' and result > 0 and result % 2 == 0:
        won = True
    elif bet_type in ['1-18', 'low'] and 1 <= result <= 18:
        won = True
    elif bet_type in ['19-36', 'high'] and 19 <= result <= 36:
        won = True
    else:
        try:
            if int(bet_type) == result:
                won = True
        except ValueError:
            pass
    
    # Determine color of result
    if result == 0:
        result_color_name = "🟢 green"
    elif result in red_numbers:
        result_color_name = "🔴 red"
    else:
        result_color_name = "⚫ black"
    
    # Award XP (10% of bet, min 5)
    member = ctx.guild.get_member(user_id) if ctx.guild else None
    xp = max(5, int(bet * 0.1))
    level_ups, xp_earned = award_xp(user_id, xp, "Played Roulette", member)
    
    # Calculate payout
    if won:
        base_winnings = bet * payout_multiplier
        winnings = apply_vip_bonus_to_winnings(user_id, base_winnings, member)
        profit = winnings - bet
        add_chips(user_id, winnings)
        
        # Track win for challenges
        update_challenge_progress(user_id, "wins", game="roulette")
        
        # Track game stats
        track_game_stats(user_id, bet, profit)
        
        result_text = f"**Result:** {result} ({result_color_name})\n**Your bet:** {bet} chips on **{bet_type}**\n\n✅ **YOU WIN!** +{profit} chips\n<:Casino_Chip:1437456315025719368> Total payout: {winnings} chips"
        
        if level_ups:
            for level in level_ups:
                result_text += f"\n🎉 **LEVEL UP!** Reached level {level}!"
        
        result_embed = discord.Embed(
            title="🎰 Roulette - You Win!",
            description=result_text,
            color=0x00FF00
        )
    else:
        # Track game stats
        track_game_stats(user_id, bet, -bet)
        
        result_text = f"**Result:** {result} ({result_color_name})\n**Your bet:** {bet} chips on **{bet_type}**\n\n❌ Better luck next time!\n-{bet} chips"
        
        if level_ups:
            for level in level_ups:
                result_text += f"\n🎉 **LEVEL UP!** Reached level {level}!"
        
        result_embed = discord.Embed(
            title="🎰 Roulette - Lost",
            description=result_text,
            color=0xFF0000
        )
    
    await message.edit(embed=result_embed)
    
    # Check for challenge completion
    await check_challenge_completion(ctx, user_id)

@bot.hybrid_command(name='hilo')
async def prefix_hilo(ctx, bet_input: Optional[str] = None):
    """Play Hi-Lo! Guess if the next card is higher or lower (Interactive with buttons)
    
    Usage:
    ~hilo <bet> - Start the game and choose with buttons
    
    Examples:
    ~hilo 50, ~hilo all, ~hilo half
    """
    # Check verification
    if not await check_verification(ctx):
        return
    
    if bet_input is None:
        prefix = get_prefix_from_ctx(ctx)
        await ctx.send(f"❌ Usage: `{prefix}hilo <bet>`\nExamples: `{prefix}hilo 50` or `{prefix}hilo all`")
        return
    
    user_id = ctx.author.id
    
    # Check if user already has an active game
    if user_id in active_games:
        await ctx.send("❌ You already have an active game! Please finish it before starting a new one.")
        return
    
    # Add to active games
    active_games.add(user_id)
    bet = parse_bet_amount(bet_input, user_id)
    
    if bet is None:
        active_games.discard(user_id)
        await ctx.send("❌ Invalid bet amount! Use a number, 'all', or 'half'.")
        return
    
    chips = get_chips(user_id)
    
    if chips < bet:
        active_games.discard(user_id)
        await ctx.send(f"❌ You don't have enough chips! You have {chips:,}, need {bet:,}.")
        return
    
    if bet < 10:
        active_games.discard(user_id)
        await ctx.send("❌ Minimum bet is 10 chips!")
        return
    
    # Deduct bet
    add_chips(user_id, -bet)
    
    # Contribute to jackpot
    contribute_to_jackpot(bet)
    
    # Track play for challenges
    update_challenge_progress(user_id, "plays", game="hilo")
    
    # Deal cards
    deck = Deck()
    first_card = deck.deal()
    second_card = deck.deal()
    
    # Create interactive view
    view = HiLoView(user_id, ctx.author.name, int(bet), first_card, second_card, ctx)
    
    # Show first card with buttons
    first_embed = discord.Embed(
        title="🎴 Hi-Lo Game",
        description=f"**Your bet:** {bet:,} chips\n\n**First card:** {first_card} (Value: {first_card.value()})\n\n🎯 Will the next card be **HIGHER** or **LOWER**?\n⬆️ Click a button to make your guess! ⬇️",
        color=0x9B59B6
    )
    
    await ctx.send(embed=first_embed, view=view)

class PokerGameView(discord.ui.View):
    """Interactive 5-Card Draw Poker with hold/discard buttons"""
    def __init__(self, user_id: int, username: str, bet: int, initial_hand: list, ctx):
        super().__init__(timeout=120)
        self.user_id = user_id
        self.username = username
        self.bet = bet
        self.hand = initial_hand
        self.held = [False] * 5  # Track which cards are held
        self.has_drawn = False
        self.deck = Deck()
        self.ctx = ctx
        
        # Add user to active games
        active_games.add(user_id)
        
        # Remove dealt cards from deck
        for card in initial_hand:
            try:
                self.deck.cards.remove(card)
            except ValueError:
                pass
        
        # Create 5 card buttons
        for i in range(5):
            button = discord.ui.Button(
                label=str(self.hand[i]),
                style=discord.ButtonStyle.secondary,
                row=i // 3,  # 3 cards per row
                custom_id=f"card_{i}"
            )
            button.callback = self.create_card_callback(i)
            self.add_item(button)
        
        # Add Draw button
        draw_btn = discord.ui.Button(
            label="🎴 Draw Cards",
            style=discord.ButtonStyle.primary,
            row=2,
            custom_id="draw"
        )
        draw_btn.callback = self.draw_callback
        self.add_item(draw_btn)
    
    def create_card_callback(self, card_index: int):
        async def card_callback(interaction: discord.Interaction):
            if interaction.user.id != self.user_id:
                await interaction.response.send_message("❌ This isn't your game!", ephemeral=True)
                return
            
            if self.has_drawn:
                await interaction.response.send_message("❌ You already drew cards!", ephemeral=True)
                return
            
            # Toggle hold status
            self.held[card_index] = not self.held[card_index]
            
            # Update button appearance
            for item in self.children:
                if isinstance(item, discord.ui.Button) and item.custom_id == f"card_{card_index}":
                    if self.held[card_index]:
                        item.style = discord.ButtonStyle.success
                        item.label = f"🔒 {str(self.hand[card_index])}"
                    else:
                        item.style = discord.ButtonStyle.secondary
                        item.label = str(self.hand[card_index])
                    break
            
            # Update embed
            held_text = "\n".join([
                f"{'🔒' if self.held[i] else '  '} **Card {i+1}:** {str(self.hand[i])}"
                for i in range(5)
            ])
            
            embed = discord.Embed(
                title="🃏 5-Card Draw Poker",
                description=f"**Bet:** {self.bet:,} chips\n\n**Your Hand:**\n{held_text}\n\n🎯 Click cards to hold/discard them\n🎴 Click 'Draw Cards' when ready!",
                color=0xFF6347
            )
            
            await interaction.response.edit_message(embed=embed, view=self)
        
        return card_callback
    
    async def draw_callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ This isn't your game!", ephemeral=True)
            return
        
        if self.has_drawn:
            await interaction.response.send_message("❌ You already drew cards!", ephemeral=True)
            return
        
        self.has_drawn = True
        
        # Replace non-held cards
        for i in range(5):
            if not self.held[i]:
                self.hand[i] = self.deck.deal()
        
        # Disable all buttons
        for item in self.children:
            if isinstance(item, discord.ui.Button):
                item.disabled = True
        
        # Evaluate final hand
        rank, score, hand_name = evaluate_poker_hand(self.hand)
        
        # Determine payout multiplier (rebalanced for 95% RTP)
        payouts = {
            9: 100,  # Royal Flush (was 250x)
            8: 25,   # Straight Flush (was 50x)
            7: 12,   # Four of a Kind (was 25x)
            6: 5,    # Full House (was 9x)
            5: 4,    # Flush (was 6x)
            4: 3,    # Straight (was 4x)
            3: 2,    # Three of a Kind (was 3x)
            2: 1,    # Two Pair (was 2x)
            1: 1,    # One Pair (Jacks+)
            0: 0     # High Card
        }
        
        # For One Pair, only pay if Jacks or better
        if rank == 1:
            pair_rank = score[0]
            if pair_rank < 11:
                multiplier = 0
                hand_name = "Pair (too low)"
            else:
                multiplier = payouts[rank]
        else:
            multiplier = payouts.get(rank, 0)
        
        # Calculate winnings
        base_winnings = int(self.bet * multiplier)
        won = base_winnings > 0
        
        # Track progress
        update_challenge_progress(self.user_id, "plays", game="poker")
        
        if won:
            update_challenge_progress(self.user_id, "wins", game="poker")
            member = self.ctx.guild.get_member(self.user_id) if self.ctx.guild else None
            winnings = apply_vip_bonus_to_winnings(self.user_id, base_winnings, member)
            profit = winnings - self.bet
            add_chips(self.user_id, winnings, self.username, f"Poker win: {hand_name} ({multiplier}x)")
            
            # Track game stats
            track_game_stats(self.user_id, self.bet, profit)
            
            # Show cards
            cards_display = "\n".join([f"**Card {i+1}:** {str(self.hand[i])}" for i in range(5)])
            
            embed = discord.Embed(
                title=f"🎉 {hand_name}!",
                description=f"**Your Final Hand:**\n{cards_display}\n\n✅ **Payout:** {multiplier}x\n<:Casino_Chip:1437456315025719368> **Winnings:** +{profit:,} chips",
                color=0x00FF00
            )
            embed.set_footer(text=f"Balance: {format_chips(self.user_id)} chips")
        else:
            # Track game stats
            track_game_stats(self.user_id, self.bet, -self.bet)
            
            # Show cards
            cards_display = "\n".join([f"**Card {i+1}:** {str(self.hand[i])}" for i in range(5)])
            
            embed = discord.Embed(
                title=f"🃏 {hand_name}",
                description=f"**Your Final Hand:**\n{cards_display}\n\n❌ No payout (need Jacks or better)\n💸 **Lost:** {self.bet:,} chips",
                color=0xFF0000
            )
            embed.set_footer(text=f"Balance: {format_chips(self.user_id)} chips")
        
        # Remove user from active games
        active_games.discard(self.user_id)
        
        await interaction.response.edit_message(embed=embed, view=self)
    
    async def on_timeout(self):
        """Called when the view times out"""
        active_games.discard(self.user_id)

@bot.hybrid_command(name='poker')
async def prefix_poker(ctx, bet_input: Optional[str] = None):
    """Play Interactive 5-Card Draw Poker!
    
    Usage: ~poker <bet>
    Example: ~poker 100, ~poker all, ~poker half
    
    Click cards to hold/discard them, then draw new cards!
    
    Payouts:
    - Royal Flush: 100x | Straight Flush: 25x | Four of a Kind: 12x
    - Full House: 5x | Flush: 4x | Straight: 3x
    - Three of a Kind: 2x | Two Pair: 1x | Pair (J+): 1x
    """
    # Check verification
    if not await check_verification(ctx):
        return
    
    # Check if user already has an active game
    if ctx.author.id in active_games:
        await ctx.send("❌ You already have an active game! Please finish it before starting a new one.")
        return
    
    if bet_input is None:
        prefix = get_prefix_from_ctx(ctx)
        await ctx.send(
            f"❌ Usage: `{prefix}poker <bet>`\n"
            f"Example: `{prefix}poker 100` or `{prefix}poker all`\n\n"
            f"**Payouts:**\n"
            f"Royal Flush: 100x | Straight Flush: 25x | Four of a Kind: 12x\n"
            f"Full House: 5x | Flush: 4x | Straight: 3x\n"
            f"Three of a Kind: 2x | Two Pair: 1x | Pair (J+): 1x"
        )
        return
    
    user_id = str(ctx.author.id)
    bet = parse_bet_amount(bet_input, int(user_id))
    
    if bet is None:
        await ctx.send("❌ Invalid bet amount! Use a number, 'all', or 'half'.")
        return
    
    chips = get_chips(ctx.author.id)
    
    if chips < bet:
        await ctx.send(f"❌ You don't have enough chips! You have {chips:,}, need {bet:,}.")
        return
    
    if bet < 10:
        await ctx.send("❌ Minimum bet is 10 chips!")
        return
    
    # Deduct bet
    remove_chips(ctx.author.id, int(bet), ctx.author.name, f"Poker bet ({bet} chips)")
    
    # Contribute to jackpot
    contribute_to_jackpot(int(bet))
    
    # Deal 5 cards
    deck = Deck()
    hand = [deck.deal() for _ in range(5)]
    
    # Create interactive view
    view = PokerGameView(ctx.author.id, ctx.author.name, int(bet), hand, ctx)
    
    # Show initial hand
    cards_display = "\n".join([f"  **Card {i+1}:** {str(hand[i])}" for i in range(5)])
    
    embed = discord.Embed(
        title="🃏 5-Card Draw Poker",
        description=f"**Bet:** {bet:,} chips\n\n**Your Hand:**\n{cards_display}\n\n🎯 Click cards to hold/discard them\n🎴 Click 'Draw Cards' when ready!",
        color=0xFF6347
    )
    
    await ctx.send(embed=embed, view=view)

@bot.hybrid_command(name='pokermp')
async def multiplayer_poker(ctx, action: Optional[str] = None, amount_input: Optional[str] = None):
    """Multiplayer Texas Hold'em Poker
    
    Commands:
    ~pokermp start <buy-in> - Start a poker table (supports 'all' and 'half')
    ~pokermp join - Join the table
    ~pokermp play - Start the game (needs 2+ players)
    ~pokermp leave - Leave the table
    ~pokermp status - Check table status
    """
    # Check verification
    if not await check_verification(ctx):
        return
    
    if not ctx.guild:
        await ctx.send("❌ Multiplayer poker can only be played in servers!")
        return
    
    channel_id = ctx.channel.id
    user_id = ctx.author.id
    
    if not action:
        prefix = get_prefix_from_ctx(ctx)
        await ctx.send(f"❌ Usage: `{prefix}pokermp <start/join/play/leave/status>`")
        return
    
    action = action.lower()
    
    if action == 'start':
        if not amount_input:
            await ctx.send("❌ Usage: `~pokermp start <buy-in>` (supports 'all' and 'half')")
            return
        
        amount = parse_bet_amount(amount_input, user_id)
        if amount is None or amount < 100:
            await ctx.send("❌ Minimum buy-in is 100 chips! Usage: `~pokermp start <buy-in>`")
            return
        
        if channel_id in active_poker_games:
            await ctx.send("❌ There's already a poker game in this channel!")
            return
        
        # Check if player has enough chips
        if get_chips(user_id) < amount:
            await ctx.send(f"❌ You don't have enough chips! You have {format_chips(user_id)}, need {amount:,}.")
            return
        
        # Create new game
        game = PokerGame(channel_id, amount)
        game.add_player(user_id, ctx.author.name)
        remove_chips(user_id, amount, ctx.author.name, "Poker table buy-in")
        game.players[user_id]['chips'] = amount
        active_poker_games[channel_id] = game
        
        embed = discord.Embed(
            title="🃏 Poker Table Started!",
            description=f"**Buy-in:** {amount:,} chips\n**Players:** 1/{6}\n\n{ctx.author.mention} joined the table!\n\nUse `~pokermp join` to join!",
            color=0x00FF00
        )
        await ctx.send(embed=embed)
    
    elif action == 'join':
        if channel_id not in active_poker_games:
            await ctx.send("❌ No poker game in this channel! Use `~pokermp start <buy-in>` to start one.")
            return
        
        game = active_poker_games[channel_id]
        
        if game.started:
            await ctx.send("❌ Game already started!")
            return
        
        if len(game.players) >= 6:
            await ctx.send("❌ Table is full! (Max 6 players)")
            return
        
        if user_id in game.players:
            await ctx.send("❌ You're already at the table!")
            return
        
        if get_chips(user_id) < game.buy_in:
            await ctx.send(f"❌ You don't have enough chips! You need {game.buy_in:,} chips.")
            return
        
        game.add_player(user_id, ctx.author.name)
        remove_chips(user_id, game.buy_in, ctx.author.name, "Poker table buy-in")
        game.players[user_id]['chips'] = game.buy_in
        
        player_list = "\n".join([f"• {game.players[pid]['name']} ({game.players[pid]['chips']:,} chips)" for pid in game.player_order])
        
        embed = discord.Embed(
            title="🃏 Player Joined!",
            description=f"{ctx.author.mention} joined the table!\n\n**Players ({len(game.players)}/6):**\n{player_list}",
            color=0x00FF00
        )
        await ctx.send(embed=embed)
    
    elif action == 'play':
        if channel_id not in active_poker_games:
            await ctx.send("❌ No poker game in this channel!")
            return
        
        game = active_poker_games[channel_id]
        
        if game.started:
            await ctx.send("❌ Game already started!")
            return
        
        if len(game.players) < 2:
            await ctx.send("❌ Need at least 2 players to start!")
            return
        
        # Start the game
        game.start_game()
        
        # Deal cards and show to each player
        for pid in game.player_order:
            player = game.players[pid]
            hand_str = ' '.join(str(card) for card in player['hand'])
            try:
                user = await ctx.bot.fetch_user(pid)
                dm_embed = discord.Embed(
                    title="🃏 Your Poker Hand",
                    description=f"**Your cards:** {hand_str}\n\nGame starting in {ctx.channel.mention}!",
                    color=0xFFD700
                )
                await user.send(embed=dm_embed)
            except Exception:
                pass
        
        # Deal flop (3 community cards)
        game.community_cards = [game.deck.pop(), game.deck.pop(), game.deck.pop()]
        community_str = ' '.join(str(card) for card in game.community_cards)
        
        embed = discord.Embed(
            title="🃏 Poker Game Started!",
            description=f"**Community Cards (Flop):**\n{community_str}\n\n**Pot:** {game.pot:,} chips\n\nCheck your DMs for your cards!\nUse `~pokermp status` to see the game state.",
            color=0x00FF00
        )
        await ctx.send(embed=embed)
        
        # Simplified: Auto-resolve after flop
        await asyncio.sleep(5)
        
        # Deal turn and river
        game.community_cards.append(game.deck.pop())  # Turn
        game.community_cards.append(game.deck.pop())  # River
        
        # Determine winner
        best_hands = {}
        for pid in game.player_order:
            if not game.players[pid]['folded']:
                player_hand = game.players[pid]['hand']
                all_cards = player_hand + game.community_cards
                # Evaluate best 5-card hand
                best_rank = -1
                best_score = []
                best_name = ""
                for i in range(len(all_cards) - 4):
                    for j in range(i+1, len(all_cards) - 3):
                        for k in range(j+1, len(all_cards) - 2):
                            for idx4 in range(k+1, len(all_cards) - 1):
                                for m in range(idx4+1, len(all_cards)):
                                    five_cards = [all_cards[i], all_cards[j], all_cards[k], all_cards[idx4], all_cards[m]]
                                    rank, score, name = evaluate_poker_hand(five_cards)
                                    if rank > best_rank or (rank == best_rank and score > best_score):
                                        best_rank = rank
                                        best_score = score
                                        best_name = name
                best_hands[pid] = (best_rank, best_score, best_name)
        
        # Find winner
        winner_id = max(best_hands.keys(), key=lambda x: (best_hands[x][0], best_hands[x][1]))
        winner = game.players[winner_id]
        winner_hand_name = best_hands[winner_id][2]
        
        # Award pot
        total_pot = sum(p['chips'] for p in game.players.values())
        member = ctx.guild.get_member(winner_id) if ctx.guild else None
        final_pot = apply_vip_bonus_to_winnings(winner_id, total_pot, member)
        add_chips(winner_id, final_pot, winner['name'], f"Won poker game with {winner_hand_name}")
        
        # Award XP and track game stats for all players
        for pid in game.player_order:
            # Award XP (10% of buy-in, min 5)
            player_member = ctx.guild.get_member(pid) if ctx.guild else None
            xp = max(5, int(game.buy_in * 0.1))
            award_xp(pid, xp, "Played Poker", player_member)
            
            if pid == winner_id:
                # Winner: profit = final_pot - buy_in
                profit = final_pot - game.buy_in
                track_game_stats(pid, game.buy_in, profit)
            else:
                # Losers: lost their buy-in
                track_game_stats(pid, game.buy_in, -game.buy_in)
        
        community_str = ' '.join(str(card) for card in game.community_cards)
        
        result_embed = discord.Embed(
            title="🃏 Poker Game Complete!",
            description=f"**Community Cards:**\n{community_str}\n\n**Winner:** {winner['name']} 🎉\n**Hand:** {winner_hand_name}\n**Prize:** {final_pot:,} chips",
            color=0xFFD700
        )
        await ctx.send(embed=result_embed)
        
        # Clean up
        del active_poker_games[channel_id]
    
    elif action == 'leave':
        if channel_id not in active_poker_games:
            await ctx.send("❌ No poker game in this channel!")
            return
        
        game = active_poker_games[channel_id]
        
        if user_id not in game.players:
            await ctx.send("❌ You're not at this table!")
            return
        
        if game.started:
            await ctx.send("❌ Can't leave after game started!")
            return
        
        # Refund chips
        refund = game.players[user_id]['chips']
        add_chips(user_id, refund, ctx.author.name, "Poker table refund")
        game.remove_player(user_id)
        
        if len(game.players) == 0:
            del active_poker_games[channel_id]
            await ctx.send("✅ You left the table. Table closed (no players left).")
        else:
            await ctx.send(f"✅ You left the table and received {refund:,} chips back.")
    
    elif action == 'status':
        if channel_id not in active_poker_games:
            await ctx.send("❌ No poker game in this channel!")
            return
        
        game = active_poker_games[channel_id]
        player_list = "\n".join([f"• {game.players[pid]['name']} ({game.players[pid]['chips']:,} chips)" for pid in game.player_order])
        
        status_str = "In Progress" if game.started else "Waiting for players"
        
        embed = discord.Embed(
            title="🃏 Poker Table Status",
            description=f"**Status:** {status_str}\n**Buy-in:** {game.buy_in:,} chips\n**Players ({len(game.players)}/6):**\n{player_list}",
            color=0x3498db
        )
        await ctx.send(embed=embed)

@bot.hybrid_command(name='roulettemp')
async def multiplayer_roulette(ctx, action: Optional[str] = None, bet_amount_input: Optional[str] = None, bet_type: Optional[str] = None):
    """Multiplayer Roulette - Multiple players bet on the same spin!
    
    Commands:
    ~roulettemp open - Open betting for a new spin
    ~roulettemp bet <amount> <type> - Place a bet (supports 'all' and 'half')
    ~roulettemp spin - Close betting and spin (anyone can spin)
    ~roulettemp status - Check current bets
    """
    # Check verification
    if not await check_verification(ctx):
        return
    
    if not ctx.guild:
        await ctx.send("❌ Multiplayer roulette can only be played in servers!")
        return
    
    channel_id = ctx.channel.id
    user_id = ctx.author.id
    
    if not action:
        prefix = get_prefix_from_ctx(ctx)
        await ctx.send(f"❌ Usage: `{prefix}roulettemp <open/bet/spin/status>`")
        return
    
    action = action.lower()
    
    if action == 'open':
        if channel_id in active_multiplayer_roulette:
            await ctx.send("❌ Betting is already open in this channel!")
            return
        
        game = MultiplayerRouletteGame(channel_id)
        active_multiplayer_roulette[channel_id] = game
        
        embed = discord.Embed(
            title="🎰 Multiplayer Roulette - Betting Open!",
            description="Place your bets!\n\n**Commands:**\n• `~roulettemp bet <amount> <type>`\n• Types: red, black, odd, even, or 1-36\n\nExample: `~roulettemp bet 100 red` or `~roulettemp bet all black`",
            color=0x00FF00
        )
        await ctx.send(embed=embed)
    
    elif action == 'bet':
        if channel_id not in active_multiplayer_roulette:
            await ctx.send("❌ No roulette game open! Use `~roulettemp open` to start.")
            return
        
        game = active_multiplayer_roulette[channel_id]
        
        if not game.betting_open:
            await ctx.send("❌ Betting is closed!")
            return
        
        if not bet_amount_input or not bet_type:
            await ctx.send("❌ Usage: `~roulettemp bet <amount> <type>`\nExample: `~roulettemp bet 100 red` or `~roulettemp bet all black`")
            return
        
        # Parse bet amount
        bet_amount = parse_bet_amount(bet_amount_input, user_id)
        if bet_amount is None:
            await ctx.send("❌ Invalid bet amount! Use a number, 'all', or 'half'.")
            return
        
        if bet_amount < 10:
            await ctx.send("❌ Minimum bet is 10 chips!")
            return
        
        if get_chips(user_id) < bet_amount:
            await ctx.send(f"❌ You don't have enough chips! You have {format_chips(user_id)}, need {bet_amount:,}.")
            return
        
        # Validate bet type
        bet_type = bet_type.lower()
        valid_bets = ['red', 'black', 'odd', 'even'] + [str(i) for i in range(1, 37)]
        
        if bet_type not in valid_bets:
            await ctx.send("❌ Invalid bet type! Use: red, black, odd, even, or 1-36")
            return
        
        # Place bet
        remove_chips(user_id, bet_amount, ctx.author.name, f"Roulette bet: {bet_type}")
        game.add_bet(user_id, ctx.author.name, bet_amount, bet_type, bet_type)
        
        await ctx.send(f"✅ {ctx.author.mention} bet **{bet_amount:,} chips** on **{bet_type}**!")
    
    elif action == 'spin':
        if channel_id not in active_multiplayer_roulette:
            await ctx.send("❌ No roulette game open!")
            return
        
        game = active_multiplayer_roulette[channel_id]
        
        if len(game.bets) == 0:
            await ctx.send("❌ No bets placed yet!")
            return
        
        game.close_betting()
        
        # Spin the wheel
        spin_embed = discord.Embed(
            title="🎰 Spinning the Wheel...",
            description=f"**Total Bets:** {game.get_player_count()} players\n**Total Pot:** {game.total_pot:,} chips",
            color=0xFFD700
        )
        message = await ctx.send(embed=spin_embed)
        await asyncio.sleep(3)
        
        # Generate result
        result = random.randint(0, 36)
        red_numbers = [1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36]
        
        is_red = result in red_numbers
        is_black = result != 0 and not is_red
        is_odd = result % 2 == 1 and result != 0
        is_even = result % 2 == 0 and result != 0
        
        # Determine winners and payouts
        winners = []
        total_winnings = {}
        
        for player_id, player_bets in game.bets.items():
            player_name = game.player_names[player_id]
            player_total_winnings = 0
            player_total_bet = 0
            
            for bet_amount, bet_type, bet_value in player_bets:
                player_total_bet += bet_amount
                won = False
                payout = 0
                
                if bet_value == str(result):
                    won = True
                    payout = bet_amount * 36
                elif bet_value == 'red' and is_red:
                    won = True
                    payout = bet_amount * 2
                elif bet_value == 'black' and is_black:
                    won = True
                    payout = bet_amount * 2
                elif bet_value == 'odd' and is_odd:
                    won = True
                    payout = bet_amount * 2
                elif bet_value == 'even' and is_even:
                    won = True
                    payout = bet_amount * 2
                
                if won:
                    player_total_winnings += payout
            
            # Award XP (10% of total bet, min 5)
            member = ctx.guild.get_member(player_id) if ctx.guild else None
            xp = max(5, int(player_total_bet * 0.1))
            award_xp(player_id, xp, "Played Roulette", member)
            
            if player_total_winnings > 0:
                final_winnings = apply_vip_bonus_to_winnings(player_id, player_total_winnings, member)
                add_chips(player_id, final_winnings, player_name, f"Roulette winnings on {result}")
                profit = final_winnings - player_total_bet
                track_game_stats(player_id, player_total_bet, profit)
                total_winnings[player_id] = final_winnings
                winners.append(f"• {player_name}: +{final_winnings:,} chips")
            else:
                track_game_stats(player_id, player_total_bet, -player_total_bet)
        
        # Show results
        color_name = "🔴 Red" if is_red else ("⚫ Black" if is_black else "🟢 Green")
        
        result_embed = discord.Embed(
            title="🎰 Roulette Result!",
            description=f"**Result:** {result} {color_name}",
            color=0x00FF00 if len(winners) > 0 else 0xFF0000
        )
        
        if winners:
            result_embed.add_field(name="Winners 🎉", value="\n".join(winners), inline=False)
        else:
            result_embed.add_field(name="Result", value="No winners this round!", inline=False)
        
        await message.edit(embed=result_embed)
        
        # Clean up
        del active_multiplayer_roulette[channel_id]
    
    elif action == 'status':
        if channel_id not in active_multiplayer_roulette:
            await ctx.send("❌ No roulette game open!")
            return
        
        game = active_multiplayer_roulette[channel_id]
        
        if len(game.bets) == 0:
            await ctx.send("No bets placed yet!")
            return
        
        bet_list = []
        for player_id, player_bets in game.bets.items():
            player_name = game.player_names[player_id]
            for bet_amount, bet_type, bet_value in player_bets:
                bet_list.append(f"• {player_name}: {bet_amount:,} chips on {bet_value}")
        
        embed = discord.Embed(
            title="🎰 Current Bets",
            description=f"**Players:** {game.get_player_count()}\n**Total Pot:** {game.total_pot:,} chips\n\n{chr(10).join(bet_list)}",
            color=0x3498db
        )
        await ctx.send(embed=embed)

@bot.hybrid_command(name='setprefix')
@commands.has_permissions(administrator=True)
async def prefix_setprefix(ctx, new_prefix: str):
    """Change the bot's prefix for this server (Admin only)"""
    if not ctx.guild:
        await ctx.send("❌ This command can only be used in a server!")
        return
    
    if len(new_prefix) > 5:
        await ctx.send("❌ Prefix must be 5 characters or less!")
        return
    
    prefixes[str(ctx.guild.id)] = new_prefix
    save_prefixes()
    
    await ctx.send(f"✅ Prefix changed to **{new_prefix}** for this server!")

@prefix_setprefix.error
async def setprefix_error(ctx, error):
    """Handle setprefix command errors"""
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ You need Administrator permissions to change the prefix!")
    elif isinstance(error, commands.MissingRequiredArgument):
        prefix = get_prefix_from_ctx(ctx)
        await ctx.send(f"❌ Usage: `{prefix}setprefix <new_prefix>`")

@bot.hybrid_command(name='bumpreminder', description="Setup DISBOARD bump reminders")
@commands.has_permissions(administrator=True)
@app_commands.describe(
    ping_type="Type of mention: 'user' or 'role'",
    target_user="User to ping for bump reminders",
    target_role="Role to ping for bump reminders"
)
async def setup_bump_reminder(ctx, ping_type: Optional[str] = None, target_user: Optional[discord.Member] = None, target_role: Optional[discord.Role] = None):
    """Setup DISBOARD bump reminders (Admin only)
    
    Usage:
    ~bumpreminder user @User - Ping a specific user
    ~bumpreminder role @Role - Ping a role
    /bumpreminder user target_user:@User - Slash command version
    /bumpreminder role target_role:@Role - Slash command version
    """
    if not ctx.guild:
        await ctx.send("❌ This command can only be used in a server!")
        return
    
    if not ping_type:
        await ctx.send("❌ Usage: `~bumpreminder user @User` or `~bumpreminder role @Role`")
        return
    
    ping_type = ping_type.lower()
    if ping_type not in ["user", "role"]:
        await ctx.send("❌ Ping type must be 'user' or 'role'!")
        return
    
    # Extract ID from mention - works for both prefix and slash commands
    if ping_type == "user":
        # For slash commands, use the target_user parameter
        if target_user:
            ping_target = target_user.id
            target_name = target_user.mention
        # For prefix commands, use ctx.message.mentions
        elif ctx.message and ctx.message.mentions:
            ping_target = ctx.message.mentions[0].id
            target_name = ctx.message.mentions[0].mention
        else:
            await ctx.send("❌ Please mention a user! Example: `~bumpreminder user @User`")
            return
    else:  # role
        # For slash commands, use the target_role parameter
        if target_role:
            ping_target = target_role.id
            target_name = target_role.mention
        # For prefix commands, use ctx.message.role_mentions
        elif ctx.message and ctx.message.role_mentions:
            ping_target = ctx.message.role_mentions[0].id
            target_name = ctx.message.role_mentions[0].mention
        else:
            await ctx.send("❌ Please mention a role! Example: `~bumpreminder role @Role`")
            return
    
    # Save configuration
    guild_id = str(ctx.guild.id)
    bump_config[guild_id] = {
        "channel_id": ctx.channel.id,
        "ping_target": ping_target,
        "ping_type": ping_type
    }
    save_bump_config()
    
    channel_mention = ctx.channel.mention if hasattr(ctx.channel, 'mention') else ctx.channel.name
    await ctx.send(
        f"✅ Bump reminders configured!\n"
        f"• Reminders will be sent in {channel_mention}\n"
        f"• Will ping: {target_name}\n\n"
        f"When someone bumps with `/bump`, I'll automatically remind you 2 hours later!"
    )

@bot.hybrid_command(name='bumpinfo')
async def bump_info(ctx):
    """View current bump reminder settings"""
    if not ctx.guild:
        await ctx.send("❌ This command can only be used in a server!")
        return
    
    guild_id = str(ctx.guild.id)
    
    if guild_id not in bump_config:
        await ctx.send("📭 Bump reminders are not configured for this server.\nUse `~bumpreminder` to set them up!")
        return
    
    config = bump_config[guild_id]
    channel = bot.get_channel(config["channel_id"])
    ping_type = config["ping_type"]
    ping_target = config["ping_target"]
    
    if ping_type == "role":
        target_mention = f"<@&{ping_target}>"
    else:
        target_mention = f"<@{ping_target}>"
    
    embed = discord.Embed(
        title="📢 Bump Reminder Settings",
        color=discord.Color.blue(),
        timestamp=datetime.now()
    )
    
    if channel:
        channel_name = getattr(channel, 'mention', f"#{getattr(channel, 'name', 'Unknown')}")
    else:
        channel_name = "Unknown"
    embed.add_field(name="Reminder Channel", value=channel_name, inline=False)
    embed.add_field(name="Ping Target", value=target_mention, inline=False)
    
    # Check for active bump reminder
    active_reminder = None
    for reminder in reminders:
        if (reminder.get("type") == "bump" and 
            reminder.get("guild_id") == ctx.guild.id and 
            not reminder.get("completed", False)):
            active_reminder = reminder
            break
    
    if active_reminder:
        # Calculate time remaining
        remind_at = datetime.fromisoformat(active_reminder["remind_at"])
        now = datetime.now()
        time_left = remind_at - now
        
        if time_left.total_seconds() > 0:
            # Calculate hours and minutes
            hours = int(time_left.total_seconds() // 3600)
            minutes = int((time_left.total_seconds() % 3600) // 60)
            
            if hours > 0:
                time_str = f"{hours}h {minutes}m"
            else:
                time_str = f"{minutes}m"
            
            status_value = f"⏳ Next bump available in: **{time_str}**"
            embed.color = discord.Color.orange()
        else:
            status_value = "✅ **Ready to bump!** Use `/bump` now!"
            embed.color = discord.Color.green()
    else:
        status_value = "✅ Active - No recent bumps detected yet"
        embed.color = discord.Color.blue()
    
    embed.add_field(name="Status", value=status_value, inline=False)
    
    await ctx.send(embed=embed)

@bot.hybrid_command(name='bumpdisable')
@commands.has_permissions(administrator=True)
async def disable_bump_reminder(ctx):
    """Disable bump reminders for this server (Admin only)"""
    if not ctx.guild:
        await ctx.send("❌ This command can only be used in a server!")
        return
    
    guild_id = str(ctx.guild.id)
    
    if guild_id not in bump_config:
        await ctx.send("📭 Bump reminders are not configured for this server.")
        return
    
    del bump_config[guild_id]
    save_bump_config()
    
    await ctx.send("✅ Bump reminders disabled for this server.")

@bot.hybrid_command(name='addchips')
@commands.is_owner()
async def add_chips_command(ctx, member: discord.Member, amount: int):
    """Manually add chips to a user's balance (Owner only)
    
    Usage: ~addchips @user 500
    """
    # Prevent modifying infinite users
    if is_infinite(member.id):
        await ctx.send("❌ Cannot modify the balance of users with infinite chips!")
        return
    
    if amount <= 0:
        await ctx.send("❌ Amount must be positive!")
        return
    
    # Get current balance
    old_balance = get_chips(member.id)
    
    # Add chips
    add_chips(member.id, amount, member.name, f"Owner gift from {ctx.author.name}")
    
    # Get new balance
    new_balance = get_chips(member.id)
    
    embed = discord.Embed(
        title="<:Casino_Chip:1437456315025719368> Chips Added",
        description=f"Added **{amount}** chips to {member.mention}",
        color=0x00FF00
    )
    embed.add_field(name="Previous Balance", value=f"{old_balance:,} chips", inline=True)
    embed.add_field(name="New Balance", value=f"{new_balance:,} chips", inline=True)
    
    await ctx.send(embed=embed)
    
    # Notify the user
    try:
        dm_embed = discord.Embed(
            title="<:Casino_Chip:1437456315025719368> Chips Received!",
            description=f"The bot owner added **{amount:,}** chips to your balance!\n\n**New balance:** {new_balance:,} chips",
            color=0x00FF00
        )
        await member.send(embed=dm_embed)
    except Exception:
        pass  # User has DMs disabled

@add_chips_command.error
async def addchips_error(ctx, error):
    """Handle addchips command errors"""
    if isinstance(error, commands.NotOwner):
        await ctx.send("❌ Only the bot owner can add chips!")
    elif isinstance(error, commands.MissingRequiredArgument):
        prefix = get_prefix_from_ctx(ctx)
        await ctx.send(f"❌ Usage: `{prefix}addchips @user <amount>`\nExample: `{prefix}addchips @John 500`")
    elif isinstance(error, commands.BadArgument):
        await ctx.send("❌ Invalid arguments! Make sure to mention a user and provide a valid number.")

@bot.hybrid_command(name='resetbalance')
@commands.is_owner()
async def reset_balance_command(ctx, member: discord.Member, amount: int = 1000):
    """Reset a user's chip balance (Owner only)
    
    Usage: ~resetbalance @user [amount]
    Example: ~resetbalance @John 5000
    Default: 1000 chips if no amount specified
    """
    # Prevent modifying infinite users
    if is_infinite(member.id):
        await ctx.send("❌ Cannot modify the balance of users with infinite chips!")
        return
    
    if amount < 0:
        await ctx.send("❌ Amount cannot be negative!")
        return
    
    # Get current balance
    old_balance = get_chips(member.id)
    
    # Set new balance
    player_chips[member.id] = amount
    save_chips()
    
    # Log the transaction
    log_chip_transaction(member.id, member.name, amount - old_balance, f"Balance reset by {ctx.author.name}", old_balance, amount)
    
    embed = discord.Embed(
        title="🔄 Balance Reset",
        description=f"Reset {member.mention}'s balance",
        color=0xFFA500
    )
    embed.add_field(name="Previous Balance", value=f"{old_balance:,} chips", inline=True)
    embed.add_field(name="New Balance", value=f"{amount:,} chips", inline=True)
    
    await ctx.send(embed=embed)
    
    # Notify the user
    try:
        dm_embed = discord.Embed(
            title="🔄 Balance Reset!",
            description=f"The bot owner reset your chip balance!\n\n**New balance:** {amount:,} chips",
            color=0xFFA500
        )
        await member.send(embed=dm_embed)
    except Exception:
        pass  # User has DMs disabled

@reset_balance_command.error
async def resetbalance_error(ctx, error):
    """Handle resetbalance command errors"""
    if isinstance(error, commands.NotOwner):
        await ctx.send("❌ Only the bot owner can reset balances!")
    elif isinstance(error, commands.MissingRequiredArgument):
        prefix = get_prefix_from_ctx(ctx)
        await ctx.send(f"❌ Usage: `{prefix}resetbalance @user [amount]`\nExample: `{prefix}resetbalance @John 5000`")
    elif isinstance(error, commands.BadArgument):
        await ctx.send("❌ Invalid arguments! Make sure to mention a user and provide a valid number.")

@bot.hybrid_command(name='infinite')
@commands.is_owner()
async def infinite_chips_command(ctx, member: Optional[discord.Member] = None, amount: int = 1000):
    """Toggle infinite chips for a user (Owner only)
    
    Usage: 
    - ~infinite [@user] - Give infinite chips to user (or yourself)
    - ~infinite [@user] [amount] - Remove infinite chips and set balance to amount
    
    If user already has infinite chips, this will remove it and restore regular balance.
    Default restored balance is 1000 chips (or specify custom amount).
    """
    target = member if member else ctx.author
    
    if is_infinite(target.id):
        # REMOVE infinite chips and restore regular balance
        infinite_users.remove(target.id)
        save_infinite_users()
        
        # Set their balance to the specified amount (default 1000)
        set_chips(target.id, amount, target.name, f"Infinite chips removed by {ctx.author.name}")
        
        embed = discord.Embed(
            title="♾️ Infinite Chips Removed",
            description=f"{target.mention}'s infinite chips have been removed!",
            color=0xFF6347
        )
        embed.add_field(name="New Balance", value=f"<:Casino_Chip:1437456315025719368> {amount:,} chips", inline=False)
        embed.set_footer(text="Regular chip economy restored")
        
        await ctx.send(embed=embed)
        
        # Notify the user
        if target.id != ctx.author.id:
            try:
                await target.send(f"♾️ Your infinite chips have been removed by {ctx.author.name}. You now have **{amount:,} chips**!")
            except Exception:
                pass
    else:
        # ADD infinite chips
        infinite_users.add(target.id)
        save_infinite_users()
        
        embed = discord.Embed(
            title="♾️ Infinite Chips Activated!",
            description=f"{target.mention} now has **infinite chips (∞)**!",
            color=0xFFD700
        )
        embed.add_field(name="Special Status", value="✨ Never runs out of chips\n🎰 Can play any game unlimited times\n<:Casino_Chip:1437456315025719368> Balance always shows ∞", inline=False)
        embed.set_footer(text="Use ~infinite again to remove this status")
        
        await ctx.send(embed=embed)
        
        # Notify the user
        if target.id != ctx.author.id:
            try:
                dm_embed = discord.Embed(
                    title="♾️ Infinite Chips!",
                    description="The bot owner granted you **infinite chips (∞)**!\n\n✨ You can now play unlimited games!",
                    color=0xFFD700
                )
                await target.send(embed=dm_embed)
            except Exception:
                pass  # User has DMs disabled

@infinite_chips_command.error
async def infinite_error(ctx, error):
    """Handle infinite command errors"""
    if isinstance(error, commands.NotOwner):
        await ctx.send("❌ Only the bot owner can grant infinite chips!")
    elif isinstance(error, commands.BadArgument):
        await ctx.send("❌ Invalid user! Make sure to mention a valid user.")


# ========================================
# SECRET CODES SYSTEM - 40 Total Codes
# ========================================

SECRET_CODES = {
    # GAMBLING THEME (13 codes)
    "lucky7": {"reward": 7777, "theme": "🎰 Gambling", "rarity": "Common", "title": "🍀 Lucky Seven!", "color": 0x00FF00},
    "double_down": {"reward": 10000, "theme": "🎰 Gambling", "rarity": "Common", "title": "🎲 Double Down!", "color": 0x3498db},
    "dealme": {"reward": 12000, "theme": "🎰 Gambling", "rarity": "Common", "title": "🃏 Deal Me In!", "color": 0x2ecc71},
    "chipstack": {"reward": 15000, "theme": "🎰 Gambling", "rarity": "Common", "title": "💵 Chip Stack!", "color": 0x1abc9c},
    
    "bonus": {"reward": 25000, "theme": "🎰 Gambling", "rarity": "Uncommon", "title": "🎉 Bonus Reward!", "color": 0x9b59b6},
    "royalflush": {"reward": 28000, "theme": "🎰 Gambling", "rarity": "Uncommon", "title": "👑 Royal Flush!", "color": 0xe91e63},
    "fullhouse": {"reward": 32000, "theme": "🎰 Gambling", "rarity": "Uncommon", "title": "🏠 Full House!", "color": 0xf39c12},
    "blackjack21": {"reward": 35000, "theme": "🎰 Gambling", "rarity": "Uncommon", "title": "🃏 Blackjack 21!", "color": 0xe67e22},
    
    "bigwin": {"reward": 50000, "theme": "🎰 Gambling", "rarity": "Rare", "title": "<:Casino_Chip:1437456315025719368> BIG WIN!", "color": 0xffd700},
    "highroller": {"reward": 60000, "theme": "🎰 Gambling", "rarity": "Rare", "title": "🎩 High Roller!", "color": 0xc0392b},
    "pokernights": {"reward": 65000, "theme": "🎰 Gambling", "rarity": "Rare", "title": "♠️ Poker Nights!", "color": 0x34495e},
    
    "67": {"reward": 67000, "theme": "🎰 Gambling", "rarity": "Mythic", "title": "🎁 Secret 67!", "color": 0xff1493},
    "allin777": {"reward": 77700, "theme": "🎰 Gambling", "rarity": "Mythic", "title": "🎰 All In 777!", "color": 0xff0000},
    "888": {"reward": 88888, "theme": "🎰 Gambling", "rarity": "Mythic", "title": "🎰 Triple Eight Fortune!", "color": 0xff6347},
    "casino": {"reward": 95000, "theme": "🎰 Gambling", "rarity": "Mythic", "title": "🏆 Casino Royale!", "color": 0xffd700},
    
    # ROCKET LEAGUE THEME (13 codes)
    "boost": {"reward": 8000, "theme": "🚗 Rocket League", "rarity": "Common", "title": "⚡ Boost Activated!", "color": 0x3498db},
    "demo": {"reward": 11000, "theme": "🚗 Rocket League", "rarity": "Common", "title": "💥 Demolition!", "color": 0xe74c3c},
    "octane": {"reward": 13000, "theme": "🚗 Rocket League", "rarity": "Common", "title": "🚙 Octane Legend!", "color": 0x2980b9},
    
    "fennec": {"reward": 22000, "theme": "🚗 Rocket League", "rarity": "Uncommon", "title": "🦊 Fennec Pro!", "color": 0xe67e22},
    "aerial": {"reward": 27000, "theme": "🚗 Rocket League", "rarity": "Uncommon", "title": "🎯 Aerial Master!", "color": 0x9b59b6},
    "musty": {"reward": 30000, "theme": "🚗 Rocket League", "rarity": "Uncommon", "title": "🌪️ Musty Flick!", "color": 0x16a085},
    "dominus": {"reward": 33000, "theme": "🚗 Rocket League", "rarity": "Uncommon", "title": "🏎️ Dominus!", "color": 0xc0392b},
    
    "flipreset": {"reward": 52000, "theme": "🚗 Rocket League", "rarity": "Rare", "title": "🔄 Flip Reset!", "color": 0x8e44ad},
    "ceiling_shot": {"reward": 58000, "theme": "🚗 Rocket League", "rarity": "Rare", "title": "⬆️ Ceiling Shot!", "color": 0x27ae60},
    "breezi": {"reward": 63000, "theme": "🚗 Rocket League", "rarity": "Rare", "title": "🎮 Breezi Flick!", "color": 0x2c3e50},
    
    "supersonic": {"reward": 85000, "theme": "🚗 Rocket League", "rarity": "Mythic", "title": "🚀 Supersonic Legend!", "color": 0xf39c12},
    "gc": {"reward": 92000, "theme": "🚗 Rocket League", "rarity": "Mythic", "title": "💎 Grand Champion!", "color": 0x9b59b6},
    "rlcs": {"reward": 99000, "theme": "🚗 Rocket League", "rarity": "Mythic", "title": "🏆 RLCS Champion!", "color": 0xffd700},
    
    # TOKYO GHOUL THEME (14 codes)
    "anteiku": {"reward": 9000, "theme": "☕ Tokyo Ghoul", "rarity": "Common", "title": "☕ Anteiku Cafe!", "color": 0x8b4513},
    "ccg": {"reward": 11500, "theme": "☕ Tokyo Ghoul", "rarity": "Common", "title": "🛡️ CCG Investigator!", "color": 0x7f8c8d},
    "quinque": {"reward": 14000, "theme": "☕ Tokyo Ghoul", "rarity": "Common", "title": "⚔️ Quinque Weapon!", "color": 0x95a5a6},
    
    "ukaku": {"reward": 24000, "theme": "☕ Tokyo Ghoul", "rarity": "Uncommon", "title": "🦅 Ukaku Kagune!", "color": 0xe74c3c},
    "kagune": {"reward": 26000, "theme": "☕ Tokyo Ghoul", "rarity": "Uncommon", "title": "👹 Kagune Power!", "color": 0xc0392b},
    "ghoul": {"reward": 29000, "theme": "☕ Tokyo Ghoul", "rarity": "Uncommon", "title": "😈 Ghoul Awakened!", "color": 0x8e44ad},
    "hinami": {"reward": 31000, "theme": "☕ Tokyo Ghoul", "rarity": "Uncommon", "title": "📚 Hinami's Books!", "color": 0x9b59b6},
    
    "touka": {"reward": 54000, "theme": "☕ Tokyo Ghoul", "rarity": "Rare", "title": "🐰 Touka Kirishima!", "color": 0x9b59b6},
    "rize": {"reward": 59000, "theme": "☕ Tokyo Ghoul", "rarity": "Rare", "title": "💜 Rize Kamishiro!", "color": 0x8e44ad},
    "eyepatch": {"reward": 64000, "theme": "☕ Tokyo Ghoul", "rarity": "Rare", "title": "👁️ Eyepatch Ghoul!", "color": 0x34495e},
    
    "kaneki": {"reward": 87000, "theme": "☕ Tokyo Ghoul", "rarity": "Mythic", "title": "⚡ Ken Kaneki!", "color": 0xecf0f1},
    "aogiri": {"reward": 93000, "theme": "☕ Tokyo Ghoul", "rarity": "Mythic", "title": "🌳 Aogiri Tree!", "color": 0x27ae60},
    "oneeyedking": {"reward": 98000, "theme": "☕ Tokyo Ghoul", "rarity": "Mythic", "title": "👑 One-Eyed King!", "color": 0xe74c3c},
    "vip": {"reward": 100000, "theme": "☕ Tokyo Ghoul", "rarity": "Mythic", "title": "✨ VIP Legend!", "color": 0xffd700},
}

async def claim_secret_code(ctx_or_interaction, code_name):
    """Unified secret code claim handler for both prefix and slash commands"""
    # Determine if it's a context or interaction
    is_interaction = hasattr(ctx_or_interaction, 'response')
    user = ctx_or_interaction.user if is_interaction else ctx_or_interaction.author
    user_id = str(user.id)
    
    # Normalize code name
    code_name = code_name.lower().strip()
    
    # Check if code exists
    if code_name not in SECRET_CODES:
        if is_interaction:
            await ctx_or_interaction.response.send_message("❌ Invalid secret code!", ephemeral=True)
        else:
            await ctx_or_interaction.send("❌ Invalid secret code!")
        return
    
    # Initialize user's secret claims if not exists
    if user_id not in secret_claims:
        secret_claims[user_id] = []
    
    # Check if already claimed
    if code_name in secret_claims[user_id]:
        if is_interaction:
            await ctx_or_interaction.response.send_message("❌ You've already claimed this secret code!", ephemeral=True)
        else:
            await ctx_or_interaction.send("❌ You've already claimed this secret code!")
        return
    
    # Get code details
    code = SECRET_CODES[code_name]
    
    # Grant chips
    add_chips(user.id, code["reward"], user.name, f"Secret code: {code_name}")
    secret_claims[user_id].append(code_name)
    save_secret_claims()
    
    # Create embed
    embed = discord.Embed(
        title=code["title"],
        description=f"**{code['theme']} • {code['rarity']}**\n\nYou found a secret code! **+{code['reward']:,} chips**\n\n<:Casino_Chip:1437456315025719368> New balance: **{format_chips(user.id)} chips**",
        color=code["color"]
    )
    embed.set_footer(text="🤫 This is a one-time claim! Share codes with your friends!")
    
    if is_interaction:
        await ctx_or_interaction.response.send_message(embed=embed)
    else:
        await ctx_or_interaction.send(embed=embed)

# Dynamic secret code command registration using factory function
def create_secret_command(code):
    """Factory function to create secret code commands with proper closure"""
    async def command_func(ctx):
        await claim_secret_code(ctx, code)
    command_func.__name__ = f'secret_{code}'
    return bot.command(name=code, help=f"Secret code - {SECRET_CODES[code]['reward']:,} chips (One-time claim)")(command_func)

# Register all 40 secret codes as individual commands
for code_name in SECRET_CODES.keys():
    create_secret_command(code_name)

@bot.hybrid_command(name='secret', description="Claim a secret code for bonus chips!")
@app_commands.describe(code="The secret code you discovered")
async def secret_command(ctx, code: str):
    """Claim a secret code for bonus chips
    
    Usage: ~secret <code> or /secret <code>
    Enter the secret code you discovered to claim bonus chips!
    """
    await claim_secret_code(ctx, code)

@bot.hybrid_command(name='secrets')
@commands.has_permissions(administrator=True)
async def secrets_list_command(ctx):
    """View all secret codes organized by theme and rarity (Admin only)
    
    Usage: ~secrets
    Shows all 40 secret codes with rewards, themes, and rarities
    """
    # Organize codes by theme
    themes = {
        "🎰 Gambling": [],
        "🚗 Rocket League": [],
        "☕ Tokyo Ghoul": []
    }
    
    # Group codes by theme
    for code_name, code_data in SECRET_CODES.items():
        themes[code_data["theme"]].append((code_name, code_data))
    
    # Sort each theme by reward amount
    for theme in themes:
        themes[theme].sort(key=lambda x: x[1]["reward"])
    
    # Create main embed
    main_embed = discord.Embed(
        title="🤫 Secret Codes Master List",
        description="**Total Codes:** 40\n**Total Possible Chips:** 1,872,077 <:Casino_Chip:1437456315025719368>\n\nAll codes are one-time claims per user.",
        color=0xffd700
    )
    
    # Add theme sections
    for theme_name, codes in themes.items():
        # Group by rarity within theme
        rarities = {"Common": [], "Uncommon": [], "Rare": [], "Mythic": []}
        for code_name, code_data in codes:
            rarities[code_data["rarity"]].append((code_name, code_data))
        
        # Build field text
        field_text = ""
        for rarity in ["Common", "Uncommon", "Rare", "Mythic"]:
            if rarities[rarity]:
                field_text += f"**{rarity}:**\n"
                for code_name, code_data in rarities[rarity]:
                    field_text += f"`~{code_name}` - {code_data['reward']:,} chips\n"
                field_text += "\n"
        
        main_embed.add_field(
            name=f"{theme_name} ({len(codes)} codes)",
            value=field_text.strip(),
            inline=False
        )
    
    main_embed.set_footer(text="💡 Players can use ~<code> or /secret <code> to claim • Share these with your community!")
    
    await ctx.send(embed=main_embed)
    
    # Send instructions for adding new codes
    info_embed = discord.Embed(
        title="📝 How to Add New Secret Codes",
        description="To add new secret codes, you need to edit the `SECRET_CODES` dictionary in `main.py`:",
        color=0x3498db
    )
    
    info_embed.add_field(
        name="1️⃣ Find the SECRET_CODES dictionary",
        value="Located around line 7504 in main.py",
        inline=False
    )
    
    info_embed.add_field(
        name="2️⃣ Add your new code",
        value='```python\n"yourcode": {\n    "reward": 50000,\n    "theme": "🎰 Gambling",\n    "rarity": "Rare",\n    "title": "🎉 Your Title!",\n    "color": 0xffd700\n}\n```',
        inline=False
    )
    
    info_embed.add_field(
        name="3️⃣ Theme Options",
        value="`🎰 Gambling` • `🚗 Rocket League` • `☕ Tokyo Ghoul`\nOr create a new theme!",
        inline=False
    )
    
    info_embed.add_field(
        name="4️⃣ Rarity Tiers",
        value="**Common:** 7k-15k chips\n**Uncommon:** 20k-35k chips\n**Rare:** 50k-70k chips\n**Mythic:** 70k-100k+ chips",
        inline=False
    )
    
    info_embed.add_field(
        name="5️⃣ Restart the bot",
        value="After adding codes, restart the bot for them to become active!",
        inline=False
    )
    
    info_embed.set_footer(text="The bot will automatically register new codes as commands!")
    
    await ctx.send(embed=info_embed)

@secrets_list_command.error
async def secrets_error(ctx, error):
    """Handle secrets command errors"""
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ You need Administrator permissions to view the secret codes list!")

@bot.hybrid_command(name='record')
@commands.has_permissions(administrator=True)
async def casino_record_command(ctx):
    """View casino profit/loss statistics (Admin only)
    
    Usage: ~record
    Shows total chips wagered, total chips won, and house profit margin
    """
    if not chips_log:
        await ctx.send("📭 No chip transactions recorded yet!")
        return
    
    # Categories for analysis
    total_wagered = 0  # All bets placed
    total_paid_out = 0  # All winnings paid
    total_claims = 0  # Daily/weekly/monthly claims
    total_admin_given = 0  # Admin-given chips
    total_secret_codes = 0  # Secret code claims
    total_jobs = 0  # Work command earnings
    
    # Keywords to identify transaction types
    bet_keywords = ["bet", "wager", "game"]
    win_keywords = ["win", "payout", "jackpot"]
    claim_keywords = ["daily", "weekly", "monthly", "yearly", "claim"]
    admin_keywords = ["admin", "owner", "added chips", "infinite"]
    secret_keywords = ["secret code"]
    job_keywords = ["work", "job"]
    
    # Analyze all transactions
    for trans in chips_log:
        amount = trans.get("amount", 0)
        reason = trans.get("reason", "").lower()
        
        # Categorize bets (negative amounts)
        if amount < 0:
            # Check if it's a game bet
            if any(keyword in reason for keyword in bet_keywords):
                total_wagered += abs(amount)
        
        # Categorize additions (positive amounts)
        elif amount > 0:
            # Game winnings
            if any(keyword in reason for keyword in win_keywords):
                total_paid_out += amount
            # Claims
            elif any(keyword in reason for keyword in claim_keywords):
                total_claims += amount
            # Secret codes
            elif any(keyword in reason for keyword in secret_keywords):
                total_secret_codes += amount
            # Jobs
            elif any(keyword in reason for keyword in job_keywords):
                total_jobs += amount
            # Admin/owner gifts
            elif any(keyword in reason for keyword in admin_keywords):
                total_admin_given += amount
    
    # Calculate profit
    house_profit = total_wagered - total_paid_out
    
    # Calculate profit margin (avoid division by zero)
    if total_wagered > 0:
        profit_margin = (house_profit / total_wagered) * 100
    else:
        profit_margin = 0
    
    # Determine color based on profit
    if house_profit > 0:
        color = 0x00FF00  # Green for profit
        status_emoji = "📈"
        status_text = "Profitable"
    elif house_profit < 0:
        color = 0xFF0000  # Red for loss
        status_emoji = "📉"
        status_text = "Operating at Loss"
    else:
        color = 0xFFFF00  # Yellow for break-even
        status_emoji = "➖"
        status_text = "Break Even"
    
    # Create main embed
    embed = discord.Embed(
        title="🏦 Casino Financial Records",
        description=f"**Status:** {status_emoji} {status_text}\n**Profit Margin:** {profit_margin:.2f}%",
        color=color
    )
    
    # Game Statistics
    embed.add_field(
        name="🎰 Game Operations",
        value=f"**Total Wagered:** {total_wagered:,} chips\n**Total Paid Out:** {total_paid_out:,} chips\n**House Profit:** {house_profit:,} chips",
        inline=False
    )
    
    # Other Sources
    embed.add_field(
        name="<:Casino_Chip:1437456315025719368> Other Chip Sources",
        value=f"**Daily/Weekly/Monthly Claims:** {total_claims:,} chips\n**Secret Codes:** {total_secret_codes:,} chips\n**Work/Jobs:** {total_jobs:,} chips\n**Admin Given:** {total_admin_given:,} chips",
        inline=False
    )
    
    # Total Overview
    total_chips_distributed = total_paid_out + total_claims + total_secret_codes + total_jobs + total_admin_given
    net_profit = total_wagered - total_chips_distributed
    
    embed.add_field(
        name="📊 Overall Summary",
        value=f"**Total Chips Distributed:** {total_chips_distributed:,} chips\n**Net Casino Profit:** {net_profit:,} chips",
        inline=False
    )
    
    # Analysis
    if total_wagered > 0:
        payout_percentage = (total_paid_out / total_wagered) * 100
        embed.add_field(
            name="📈 Analytics",
            value=f"**RTP (Return to Player):** {payout_percentage:.2f}%\n**House Edge:** {100 - payout_percentage:.2f}%\n**Transactions Analyzed:** {len(chips_log):,}",
            inline=False
        )
    
    embed.set_footer(text="💡 Based on the last 1,000 transactions in the chip log")
    embed.timestamp = datetime.now(timezone.utc)
    
    await ctx.send(embed=embed)

@casino_record_command.error
async def record_error(ctx, error):
    """Handle record command errors"""
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ You need Administrator permissions to view casino records!")

@bot.hybrid_command(name='chipslog')
@commands.has_permissions(administrator=True)
async def chips_log_command(ctx, lines: int = 20):
    """View recent chip transaction log (Admin only)
    
    Usage: ~chipslog [lines]
    Example: ~chipslog 50 (shows last 50 transactions)
    """
    if lines < 1:
        await ctx.send("❌ Number of lines must be at least 1!")
        return
    
    if lines > 100:
        lines = 100  # Cap at 100 to prevent spam
    
    if not chips_log:
        await ctx.send("📭 No chip transactions recorded yet!")
        return
    
    # Get the most recent transactions
    recent_logs = chips_log[-lines:]
    
    # Create embed with transaction log
    embed = discord.Embed(
        title="<:Casino_Chip:1437456315025719368> Chip Transaction Log",
        description=f"Showing last {len(recent_logs)} transaction(s)",
        color=0x5865F2
    )
    
    # Build transaction list
    log_text = ""
    for i, trans in enumerate(reversed(recent_logs), 1):
        timestamp = datetime.fromisoformat(trans["timestamp"])
        time_str = timestamp.strftime("%m/%d %H:%M")
        
        amount = trans["amount"]
        amount_str = f"+{amount}" if amount > 0 else str(amount)
        
        # Determine emoji based on transaction type
        if amount > 0:
            emoji = "📈"
        else:
            emoji = "📉"
        
        log_text += (
            f"`{time_str}` {emoji} **{trans['user_name']}** "
            f"`{amount_str}` chips\n"
            f"└ {trans['reason']} | Balance: {trans['balance_after']}\n"
        )
        
        # Split into multiple embeds if too long
        if len(log_text) > 3500 and i < len(recent_logs):
            embed.description = log_text
            await ctx.send(embed=embed)
            
            # Start new embed
            embed = discord.Embed(
                title="<:Casino_Chip:1437456315025719368> Chip Transaction Log (continued)",
                color=0x5865F2
            )
            log_text = ""
    
    # Send final embed
    if log_text:
        embed.description = log_text
        await ctx.send(embed=embed)
    
    # Add summary stats
    total_added = sum(t["amount"] for t in chips_log if t["amount"] > 0)
    total_removed = sum(abs(t["amount"]) for t in chips_log if t["amount"] < 0)
    
    stats_embed = discord.Embed(
        title="📊 Transaction Summary",
        color=0x00FF00
    )
    stats_embed.add_field(name="Total Chips Added", value=f"{total_added:,}", inline=True)
    stats_embed.add_field(name="Total Chips Removed", value=f"{total_removed:,}", inline=True)
    stats_embed.add_field(name="Total Transactions", value=f"{len(chips_log):,}", inline=True)
    
    await ctx.send(embed=stats_embed)

@chips_log_command.error
async def chipslog_error(ctx, error):
    """Handle chipslog command errors"""
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ You need Administrator permissions to view the chip log!")
    elif isinstance(error, commands.BadArgument):
        await ctx.send("❌ Invalid number! Usage: `~chipslog [lines]`")

@bot.hybrid_command(name='reset')
@commands.has_permissions(administrator=True)
async def reset_command(ctx, target: Optional[str] = None, claim_type: Optional[str] = None):
    """Unified reset command for claim timers (Admin only)
    
    Usage:
    ~reset @user <type> - Reset a user's claim timer (daily/weekly/monthly/yearly/all)
    ~reset alldaily - Reset EVERYONE's daily claim (Owner only)
    """
    prefix = get_prefix_from_ctx(ctx)
    
    if not target:
        embed = discord.Embed(
            title="🔄 Reset Commands",
            description="Reset claim timers for users",
            color=0xFF9900
        )
        embed.add_field(name="Reset User", value=f"`{prefix}reset @user <type>`\nTypes: daily, weekly, monthly, yearly, all", inline=False)
        embed.add_field(name="Reset All Daily", value=f"`{prefix}reset alldaily` - Reset everyone's daily (Owner only)", inline=False)
        return await ctx.send(embed=embed)
    
    # Check if it's the "alldaily" bulk reset (Owner only)
    if target.lower() == 'alldaily':
        if not await bot.is_owner(ctx.author):
            return await ctx.send("❌ Only the bot owner can reset everyone's daily claims!")
        
        reset_count = 0
        for user_id in list(claims.keys()):
            if 'daily' in claims[user_id]:
                del claims[user_id]['daily']
                reset_count += 1
        
        save_claims()
        
        embed = discord.Embed(
            title="✅ All Daily Claims Reset",
            description=f"Reset daily claims for **{reset_count}** users!",
            color=0x00FF00
        )
        return await ctx.send(embed=embed)
    
    # Otherwise, it's a user-specific reset
    # Try to get the member from the target string
    member = None
    if ctx.message and ctx.message.mentions:
        member = ctx.message.mentions[0]
    
    if not member:
        return await ctx.send(f"❌ Please mention a user: `{prefix}reset @user <type>`")
    
    if not claim_type:
        return await ctx.send(f"❌ Please specify a type: `{prefix}reset @user <type>`\nTypes: daily, weekly, monthly, yearly, all")
    
    claim_type = claim_type.lower()
    valid_types = ['daily', 'weekly', 'monthly', 'yearly', 'all']
    
    if claim_type not in valid_types:
        return await ctx.send(f"❌ Invalid type! Valid types: {', '.join(valid_types)}")
    
    user_id = str(member.id)
    
    if user_id not in claims:
        claims[user_id] = {}
    
    reset_types = ['daily', 'weekly', 'monthly', 'yearly'] if claim_type == 'all' else [claim_type]
    
    for claim in reset_types:
        if claim in claims[user_id]:
            del claims[user_id][claim]
    
    save_claims()
    
    embed = discord.Embed(
        title="🔄 Claim Timer Reset",
        description=f"Reset **{claim_type}** claim timer(s) for {member.mention}",
        color=0xFF9900
    )
    embed.set_footer(text=f"{member.name} can now claim their rewards again!")
    
    await ctx.send(embed=embed)
    
    try:
        dm_embed = discord.Embed(
            title="🔄 Claim Timer Reset",
            description=f"An admin reset your **{claim_type}** claim timer(s) in **{ctx.guild.name}**!",
            color=0xFF9900
        )
        await member.send(embed=dm_embed)
    except Exception:
        pass

@reset_command.error
async def reset_error(ctx, error):
    """Handle reset command errors"""
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ You need Administrator permissions to reset claim timers!")

@setup_bump_reminder.error
async def bump_reminder_error(ctx, error):
    """Handle bump reminder command errors"""
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ You need Administrator permissions to configure bump reminders!")
    elif isinstance(error, commands.MissingRequiredArgument):
        prefix = get_prefix_from_ctx(ctx)
        await ctx.send(
            f"❌ Usage:\n"
            f"`{prefix}bumpreminder user @User` - Ping a specific user\n"
            f"`{prefix}bumpreminder role @Role` - Ping a role"
        )

@tasks.loop(seconds=10)
async def check_reminders():
    """Check for reminders that need to be sent"""
    now = datetime.now()
    
    for reminder in reminders:
        if reminder["completed"]:
            continue
        
        remind_at = datetime.fromisoformat(reminder["remind_at"])
        
        if now >= remind_at:
            try:
                # Check if this is a bump reminder or regular reminder
                if reminder.get("type") == "bump":
                    # Handle bump reminder - use CURRENT config (not stored values)
                    guild_id = str(reminder.get("guild_id"))
                    
                    # Get current config (in case user changed channel/target)
                    if guild_id in bump_config:
                        current_config = bump_config[guild_id]
                        channel = bot.get_channel(current_config["channel_id"])
                        ping_type = current_config.get("ping_type", "user")
                        ping_target = current_config.get("ping_target")
                    else:
                        # Fallback to stored values if config was removed
                        channel = bot.get_channel(reminder["channel_id"])
                        ping_type = reminder.get("ping_type", "user")
                        ping_target = reminder.get("ping_target")
                    
                    if channel and isinstance(channel, discord.abc.Messageable):
                        
                        if ping_type == "role":
                            mention = f"<@&{ping_target}>"
                        else:
                            mention = f"<@{ping_target}>"
                        
                        embed = discord.Embed(
                            title="📢 Time to Bump!",
                            description="It's been 2 hours since the last bump. You can bump the server again!",
                            color=discord.Color.blue(),
                            timestamp=datetime.now()
                        )
                        embed.add_field(name="How to bump", value="Use `/bump` to bump your server on DISBOARD!", inline=False)
                        
                        try:
                            await channel.send(mention, embed=embed)
                            reminder["completed"] = True
                            save_reminders()
                        except Exception as e:
                            print(f"Failed to send bump reminder: {e}")
                
                else:
                    # Handle regular reminder
                    channel = bot.get_channel(reminder["channel_id"])
                    user = await bot.fetch_user(reminder["user_id"])
                    
                    embed = discord.Embed(
                        title="⏰ Reminder",
                        description=reminder["message"],
                        color=discord.Color.gold(),
                        timestamp=datetime.now()
                    )
                    embed.set_footer(text=f"Set {datetime.fromisoformat(reminder['created_at']).strftime('%Y-%m-%d %H:%M:%S')}")
                    
                    # Try to send to channel, fallback to DM
                    sent = False
                    if channel and isinstance(channel, discord.abc.Messageable):
                        try:
                            await channel.send(f"{user.mention}", embed=embed)
                            sent = True
                        except Exception:
                            pass
                    
                    # If channel send failed, try DM
                    if not sent:
                        try:
                            await user.send(embed=embed)
                            sent = True
                        except Exception:
                            pass
                    
                    # Only mark as completed if successfully sent
                    if sent:
                        reminder["completed"] = True
                        save_reminders()
                    else:
                        print(f"Failed to deliver reminder to user {reminder['user_id']}")
                
            except Exception as e:
                print(f"Error processing reminder: {e}")

@check_reminders.before_loop
async def before_check_reminders():
    """Wait for bot to be ready before starting the loop"""
    await bot.wait_until_ready()

@tasks.loop(minutes=5)
async def check_claim_reminders():
    """Check for ready claims and send DM reminders"""
    now = datetime.now()
    
    for user_id, user_claims in claims.items():
        try:
            # Initialize reminder tracking for this user if needed
            if user_id not in claim_reminders_sent:
                claim_reminders_sent[user_id] = {}
            
            # Check daily claim
            if 'daily' in user_claims:
                last_claim = datetime.fromisoformat(user_claims['daily'])
                time_diff = now - last_claim
                cooldown = timedelta(hours=12)
                
                # If cooldown has passed and we haven't sent a reminder yet
                if time_diff >= cooldown and not claim_reminders_sent[user_id].get('daily', False):
                    try:
                        user = await bot.fetch_user(int(user_id))
                        embed = discord.Embed(
                            title="<:Casino_Chip:1437456315025719368> Daily Claim Ready!",
                            description=f"Your daily claim of **{DAILY_REWARD}** chips is now available!",
                            color=0x00FF00
                        )
                        embed.add_field(
                            name="How to claim",
                            value="Use `/daily` or `~daily` to claim your reward!",
                            inline=False
                        )
                        embed.set_footer(text="Claim cooldown: 12 hours")
                        
                        await user.send(embed=embed)
                        claim_reminders_sent[user_id]['daily'] = True
                        save_claim_reminders()
                    except Exception as e:
                        print(f"Failed to send daily claim reminder to user {user_id}: {e}")
            
            # Check weekly claim
            if 'weekly' in user_claims:
                last_claim = datetime.fromisoformat(user_claims['weekly'])
                time_diff = now - last_claim
                cooldown = timedelta(hours=168)
                
                # If cooldown has passed and we haven't sent a reminder yet
                if time_diff >= cooldown and not claim_reminders_sent[user_id].get('weekly', False):
                    try:
                        user = await bot.fetch_user(int(user_id))
                        embed = discord.Embed(
                            title="💎 Weekly Claim Ready!",
                            description=f"Your weekly claim of **{WEEKLY_REWARD}** chips is now available!",
                            color=0x0099FF
                        )
                        embed.add_field(
                            name="How to claim",
                            value="Use `/weekly` or `~weekly` to claim your reward!",
                            inline=False
                        )
                        embed.set_footer(text="Claim cooldown: 168 hours (7 days)")
                        
                        await user.send(embed=embed)
                        claim_reminders_sent[user_id]['weekly'] = True
                        save_claim_reminders()
                    except Exception as e:
                        print(f"Failed to send weekly claim reminder to user {user_id}: {e}")
            
            # Check monthly claim
            if 'monthly' in user_claims:
                last_claim = datetime.fromisoformat(user_claims['monthly'])
                
                # Check if it's a new month
                if now.month != last_claim.month or now.year != last_claim.year:
                    # If we haven't sent a reminder for this month yet
                    if not claim_reminders_sent[user_id].get('monthly', False):
                        try:
                            user = await bot.fetch_user(int(user_id))
                            embed = discord.Embed(
                                title="🌟 Monthly Claim Ready!",
                                description=f"Your monthly claim of **{MONTHLY_REWARD}** chips is now available!",
                                color=0xFFD700
                            )
                            embed.add_field(
                                name="How to claim",
                                value="Use `/monthly` or `~monthly` to claim your reward!",
                                inline=False
                            )
                            embed.set_footer(text="Claim cooldown: Once per calendar month")
                            
                            await user.send(embed=embed)
                            claim_reminders_sent[user_id]['monthly'] = True
                            save_claim_reminders()
                        except Exception as e:
                            print(f"Failed to send monthly claim reminder to user {user_id}: {e}")
            
            # Check yearly claim
            if 'yearly' in user_claims:
                last_claim = datetime.fromisoformat(user_claims['yearly'])
                time_diff = now - last_claim
                cooldown = timedelta(days=365)
                
                # If cooldown has passed and we haven't sent a reminder yet
                if time_diff >= cooldown and not claim_reminders_sent[user_id].get('yearly', False):
                    try:
                        user = await bot.fetch_user(int(user_id))
                        embed = discord.Embed(
                            title="🎊 Yearly Claim Ready!",
                            description=f"Your yearly claim of **{YEARLY_REWARD:,}** chips is now available!",
                            color=0xFF1493
                        )
                        embed.add_field(
                            name="How to claim",
                            value="Use `/yearly` or `~yearly` to claim your reward!",
                            inline=False
                        )
                        embed.set_footer(text="Claim cooldown: 365 days")
                        
                        await user.send(embed=embed)
                        claim_reminders_sent[user_id]['yearly'] = True
                        save_claim_reminders()
                    except Exception as e:
                        print(f"Failed to send yearly claim reminder to user {user_id}: {e}")
        
        except Exception as e:
            print(f"Error checking claim reminders for user {user_id}: {e}")

@check_claim_reminders.before_loop
async def before_check_claim_reminders():
    """Wait for bot to be ready before starting the loop"""
    await bot.wait_until_ready()

@tasks.loop(hours=1)
async def check_shop_rotation():
    """Check if it's time to rotate the shop (2pm PST daily)"""
    import pytz
    
    # Get current time in PST
    pst = pytz.timezone('America/Los_Angeles')
    now = datetime.now(pst)
    
    # Check if it's 2pm PST (14:00)
    if now.hour == 14 and now.minute < 60:
        # Check if we've already rotated today
        if os.path.exists(SHOP_ITEMS_FILE):
            try:
                last_modified = datetime.fromtimestamp(os.path.getmtime(SHOP_ITEMS_FILE), tz=pst)
                
                # Only rotate if we haven't rotated yet today
                if last_modified.date() < now.date():
                    rotate_shop_daily()
                    print(f"[SHOP] Daily rotation completed at {now.strftime('%Y-%m-%d %H:%M:%S %Z')}")
            except Exception as e:
                print(f"[SHOP] Error checking rotation status: {e}")
                rotate_shop_daily()
        else:
            # No shop file exists, rotate now
            rotate_shop_daily()

@check_shop_rotation.before_loop
async def before_check_shop_rotation():
    """Wait for bot to be ready before starting the loop"""
    await bot.wait_until_ready()

# Twitch API integration variables
twitch_access_token = None
twitch_token_expiry = None

async def get_twitch_access_token():
    """Get Twitch OAuth access token using Client Credentials"""
    global twitch_access_token, twitch_token_expiry
    
    client_id = os.getenv('CLIENT_ID')
    client_secret = os.getenv('CLIENT_SECRET')
    
    if not client_id or not client_secret:
        print("[TWITCH] Missing CLIENT_ID or CLIENT_SECRET")
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
                    print(f"[TWITCH] Got new access token, expires at {twitch_token_expiry}")
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
    
    client_id = os.getenv('CLIENT_ID')
    
    # Get fresh token if needed
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
            # Get user ID first
            async with session.get(f'https://api.twitch.tv/helix/users?login={username}', headers=headers, timeout=aiohttp.ClientTimeout(total=5)) as resp:
                if resp.status != 200:
                    return None
                
                users = await resp.json()
                if not users.get('data'):
                    return None
                
                user_id = users['data'][0]['id']
            
            # Get stream data
            async with session.get(f'https://api.twitch.tv/helix/streams?user_id={user_id}', headers=headers, timeout=aiohttp.ClientTimeout(total=5)) as resp:
                if resp.status == 200:
                    streams = await resp.json()
                    if streams.get('data') and len(streams['data']) > 0:
                        stream = streams['data'][0]
                        return {
                            'is_live': True,
                            'title': stream.get('title', 'No title'),
                            'game_name': stream.get('game_name', 'Unknown game'),
                            'viewer_count': stream.get('viewer_count', 0)
                        }
                    else:
                        return {'is_live': False}
                else:
                    return None
    except Exception as e:
        print(f"[TWITCH] Error fetching stream data for {username}: {e}")
        return None

def load_streams_config():
    """Load streams configuration from file"""
    global streams_config
    if os.path.exists(STREAMS_CONFIG_FILE):
        try:
            with open(STREAMS_CONFIG_FILE, "r") as f:
                streams_config = json.load(f)
        except Exception as e:
            print(f"Error loading streams config: {e}")
            streams_config = {}

def save_streams_config():
    """Save streams configuration to file"""
    try:
        with open(STREAMS_CONFIG_FILE, "w") as f:
            json.dump(streams_config, f, indent=2)
    except Exception as e:
        print(f"Error saving streams config: {e}")

@tasks.loop(minutes=5)
async def check_streams():
    """Check if streamers are live on Twitch/YouTube"""
    
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
                
                # Check if currently live
                is_live = False
                stream_url = ""
                stream_data = {}
                
                try:
                    if platform == 'twitch':
                        # Use Twitch API to get live data
                        stream_data = await get_twitch_stream_data(username)
                        if stream_data:
                            is_live = stream_data.get('is_live', False)
                            stream_url = f"https://twitch.tv/{username}"
                            print(f"[STREAMS] {username} - API result: is_live={is_live}")
                        else:
                            # Fallback to page scraping if API fails
                            print(f"[STREAMS] {username} - API returned None, falling back to page scraping")
                            async with aiohttp.ClientSession() as session:
                                async with session.get(f'https://www.twitch.tv/{username}', timeout=aiohttp.ClientTimeout(total=5)) as resp:
                                    if resp.status == 200:
                                        text = await resp.text()
                                        is_live = '"isLiveBroadcast":true' in text or '"type":"live"' in text
                                        if is_live:
                                            stream_url = f"https://twitch.tv/{username}"
                                        print(f"[STREAMS] {username} - Page scraping result: is_live={is_live}")
                    
                    elif platform == 'youtube':
                        # YouTube uses page scraping (no API)
                        async with aiohttp.ClientSession() as session:
                            async with session.get(f'https://www.youtube.com/@{username}', timeout=aiohttp.ClientTimeout(total=5)) as resp:
                                if resp.status == 200:
                                    text = await resp.text()
                                    is_live = '"isLiveContent":true' in text or '"isUpcoming":false' in text and 'live' in text.lower()
                                    if is_live:
                                        stream_url = f"https://youtube.com/@{username}/live"
                except Exception as e:
                    print(f"Error checking stream {username} on {platform}: {e}")
                    continue
                
                # If live status changed to true and wasn't live before, send notification
                if is_live and not streamer.get('live'):
                    print(f"[STREAMS] {username} just went live! Sending notification to {guild.name}")
                    try:
                        # Create fancy formatted notification
                        if platform == 'twitch':
                            title = stream_data.get('title', 'No title')
                            game = stream_data.get('game_name', 'Unknown game')
                            viewers = stream_data.get('viewer_count', 0)
                            
                            if viewers > 0:
                                viewer_text = f"Viewers : **{viewers:,}**"
                            else:
                                viewer_text = "Viewers : Just went live!"
                            
                            message = f"""━━━━━━━━━━━━━━━━━━━━━━━━━━
[ LIVE ] TWITCH STREAM ALERT
━━━━━━━━━━━━━━━━━━━━━━━━━━

Streamer: **{username}**
Title   : {title}
Game    : **{game}**
{viewer_text}

Watch Here:
{stream_url}

━━━━━━━━━━━━━━━━━━━━━━━━━━
Click the link to join the stream.
━━━━━━━━━━━━━━━━━━━━━━━━━━"""
                        elif platform == 'youtube':
                            message = f"""━━━━━━━━━━━━━━━━━━━━━━━━━━
[ LIVE ] YOUTUBE STREAM ALERT
━━━━━━━━━━━━━━━━━━━━━━━━━━

Creator: **{username}**
Status : Now Live on YouTube

Watch Here:
{stream_url}

━━━━━━━━━━━━━━━━━━━━━━━━━━
Click the link to join the stream.
━━━━━━━━━━━━━━━━━━━━━━━━━━"""
                        
                        if isinstance(channel, discord.TextChannel):
                            await channel.send(
                                content=f"{role.mention}\n{message}"
                            )
                        
                        # Update live status
                        streamer['live'] = True
                        streamer['last_check'] = datetime.now(timezone.utc).isoformat()
                        save_streams_config()
                        print(f"[STREAMS] Notified {guild.name} that {username} is live on {platform}")
                    except Exception as e:
                        print(f"Error sending stream notification: {e}")
                
                # If was live but now offline, update status
                elif not is_live and streamer.get('live'):
                    streamer['live'] = False
                    streamer['last_check'] = datetime.now(timezone.utc).isoformat()
                    save_streams_config()
        
        except Exception as e:
            print(f"Error checking streams for guild {guild_id}: {e}")

@check_streams.before_loop
async def before_check_streams():
    """Wait for bot to be ready before starting the loop"""
    await bot.wait_until_ready()

# Error handling and logging
async def send_error_to_channel(error_title: str, error_details: str, context: Optional[str] = None):
    """Send error message to the designated error channel"""
    try:
        channel = bot.get_channel(ERROR_CHANNEL_ID)
        if channel and isinstance(channel, discord.TextChannel):
            embed = discord.Embed(
                title=f"🚨 {error_title}",
                description=error_details[:4000],  # Discord embed description limit
                color=0xFF0000,
                timestamp=datetime.now(timezone.utc)
            )
            if context:
                embed.add_field(name="Context", value=context[:1024], inline=False)
            await channel.send(embed=embed)
    except Exception as e:
        print(f"Failed to send error to channel: {e}")

@bot.hybrid_command(name='streamnotify', description="Manage stream notifications")
@commands.has_permissions(manage_guild=True)
@app_commands.describe(
    action="Action: setup/add/remove/list/test",
    arg1="For setup: #channel. For add/remove: platform (twitch/youtube)",
    arg2="For setup: @role. For add/remove: username"
)
async def stream_notify_command(ctx, action: Optional[str] = None, arg1: Optional[str] = None, arg2: Optional[str] = None):
    """Unified stream notification management
    
    Usage:
    ~streamnotify setup <#channel> @role - Configure notification channel and role
    ~streamnotify add <twitch/youtube> <username> - Add a streamer to monitor
    ~streamnotify remove <twitch/youtube> <username> - Remove a streamer
    ~streamnotify list - View all monitored streamers
    ~streamnotify test - Send a test notification
    """
    prefix = get_prefix_from_ctx(ctx)
    guild_id = str(ctx.guild.id)
    
    if not action:
        embed = discord.Embed(
            title="📺 Stream Notifications",
            description="Manage stream notifications for your server",
            color=0x9146FF
        )
        embed.add_field(name="Setup", value=f"`{prefix}streamnotify setup #channel @role`", inline=False)
        embed.add_field(name="Add Streamer", value=f"`{prefix}streamnotify add twitch <username>`\n`{prefix}streamnotify add youtube <username>`", inline=False)
        embed.add_field(name="Remove Streamer", value=f"`{prefix}streamnotify remove twitch <username>`\n`{prefix}streamnotify remove youtube <username>`", inline=False)
        embed.add_field(name="List", value=f"`{prefix}streamnotify list` - View all monitored streamers", inline=False)
        embed.add_field(name="Test", value=f"`{prefix}streamnotify test` - Send a test notification", inline=False)
        return await ctx.send(embed=embed)
    
    action = action.lower()
    
    # SETUP: Configure channel and role
    if action == 'setup':
        channel = None
        role = None
        
        # For prefix commands, try to find channel/role in message
        if ctx.message and ctx.message.channel_mentions:
            channel = ctx.message.channel_mentions[0]
        if ctx.message and ctx.message.role_mentions:
            role = ctx.message.role_mentions[0]
        
        if not channel or not role:
            return await ctx.send(f"❌ Please use: `{prefix}streamnotify setup #channel @role`")
        
        if guild_id not in streams_config:
            streams_config[guild_id] = {}
        
        streams_config[guild_id]['channel_id'] = channel.id
        streams_config[guild_id]['role_id'] = role.id
        streams_config[guild_id]['streamers'] = streams_config[guild_id].get('streamers', [])
        
        save_streams_config()
        
        embed = discord.Embed(
            title="✅ Stream Notifications Setup",
            description=f"Notifications will be sent to {channel.mention} with {role.mention} pinged",
            color=0x00FF00
        )
        return await ctx.send(embed=embed)
    
    # ADD: Add a streamer
    elif action == 'add':
        if not arg1 or not arg2:
            return await ctx.send(f"❌ Please use: `{prefix}streamnotify add <twitch/youtube> <username>`")
        
        platform = arg1.lower()
        username = arg2
        
        if platform not in ['twitch', 'youtube']:
            return await ctx.send("❌ Platform must be `twitch` or `youtube`")
        
        if guild_id not in streams_config:
            streams_config[guild_id] = {'streamers': []}
        
        if 'streamers' not in streams_config[guild_id]:
            streams_config[guild_id]['streamers'] = []
        
        # Check if already added
        for streamer in streams_config[guild_id]['streamers']:
            if streamer['username'].lower() == username.lower() and streamer['platform'] == platform:
                return await ctx.send(f"⚠️ **{username}** is already being monitored on {platform.capitalize()}")
        
        streams_config[guild_id]['streamers'].append({
            'username': username,
            'platform': platform,
            'live': False,
            'last_check': datetime.now(timezone.utc).isoformat()
        })
        
        save_streams_config()
        
        color = 0x9146FF if platform == 'twitch' else 0xFF0000
        embed = discord.Embed(
            title=f"✅ {platform.capitalize()} Streamer Added",
            description=f"Now monitoring **{username}** on {platform.capitalize()}",
            color=color
        )
        return await ctx.send(embed=embed)
    
    # REMOVE: Remove a streamer
    elif action == 'remove':
        if not arg1 or not arg2:
            return await ctx.send(f"❌ Please use: `{prefix}streamnotify remove <twitch/youtube> <username>`")
        
        platform = arg1.lower()
        username = arg2
        
        if platform not in ['twitch', 'youtube']:
            return await ctx.send("❌ Platform must be `twitch` or `youtube`")
        
        if guild_id not in streams_config or not streams_config[guild_id].get('streamers'):
            return await ctx.send("❌ No streamers to remove")
        
        original_count = len(streams_config[guild_id]['streamers'])
        streams_config[guild_id]['streamers'] = [
            s for s in streams_config[guild_id]['streamers']
            if not (s['username'].lower() == username.lower() and s['platform'] == platform)
        ]
        
        if len(streams_config[guild_id]['streamers']) == original_count:
            return await ctx.send(f"❌ {platform.capitalize()} streamer `{username}` not found")
        
        save_streams_config()
        
        color = 0x9146FF if platform == 'twitch' else 0xFF0000
        embed = discord.Embed(
            title=f"✅ {platform.capitalize()} Streamer Removed",
            description=f"Stopped monitoring **{username}** on {platform.capitalize()}",
            color=color
        )
        return await ctx.send(embed=embed)
    
    # LIST: Show all monitored streamers
    elif action == 'list':
        if guild_id not in streams_config or not streams_config[guild_id].get('streamers'):
            return await ctx.send("❌ No streamers being monitored")
        
        embed = discord.Embed(
            title="📺 Monitored Streamers",
            color=0x9146FF
        )
        
        twitch_streamers = [s for s in streams_config[guild_id]['streamers'] if s['platform'] == 'twitch']
        youtube_streamers = [s for s in streams_config[guild_id]['streamers'] if s['platform'] == 'youtube']
        
        if twitch_streamers:
            twitch_list = ""
            for s in twitch_streamers:
                status = "🟢" if s.get('live') else "⚫"
                twitch_list += f"{status} [{s['username']}](https://twitch.tv/{s['username']})\n"
            embed.add_field(name="📺 Twitch", value=twitch_list, inline=False)
        
        if youtube_streamers:
            youtube_list = ""
            for s in youtube_streamers:
                status = "🟢" if s.get('live') else "⚫"
                youtube_list += f"{status} {s['username']}\n"
            embed.add_field(name="▶️ YouTube", value=youtube_list, inline=False)
        
        if not twitch_streamers and not youtube_streamers:
            return await ctx.send("❌ No streamers being monitored")
        
        return await ctx.send(embed=embed)
    
    # TEST: Send a test notification
    elif action == 'test':
        if guild_id not in streams_config or 'channel_id' not in streams_config[guild_id]:
            return await ctx.send(f"❌ Stream notifications not set up! Use `{prefix}streamnotify setup #channel @role` first.")
        
        channel = bot.get_channel(streams_config[guild_id]['channel_id'])
        if not channel:
            return await ctx.send("❌ Could not find the notification channel. Please run setup again.")
        
        embed = discord.Embed(
            title="✅ Test Notification",
            description="Stream notifications are working correctly!",
            color=0x00FF00
        )
        embed.set_footer(text="This is a test message")
        
        try:
            await channel.send(embed=embed)
            await ctx.send(f"✅ Test notification sent to {channel.mention}!")
        except Exception as e:
            await ctx.send(f"❌ Failed to send test notification: {e}")
    
    else:
        return await ctx.send(f"❌ Unknown action. Use `{prefix}streamnotify` for help")

# ============= NEW SYSTEMS: QUESTS, PRESTIGE, MYSTATS, BIRTHDAY, REFER =============

@bot.hybrid_command(name='quests')
async def quests_command(ctx):
    """View daily quests and track progress"""
    user_id = str(ctx.author.id)
    today = datetime.now().date().isoformat()
    
    init_player_stats(user_id)
    
    if user_id not in daily_quests:
        daily_quests[user_id] = {
            'quests': [],
            'last_reset': today,
            'completed_today': 0
        }
    
    quest_data = daily_quests[user_id]
    
    # Reset quests if it's a new day
    if quest_data.get('last_reset') != today:
        quest_types = ['slots_wins', 'blackjack_wins', 'total_wagered', 'xp_earned']
        daily_quests[user_id]['quests'] = [
            {
                'type': random.choice(quest_types),
                'target': random.randint(5, 20) if 'wins' in quest_types else random.randint(50000, 200000),
                'progress': 0,
                'reward': random.randint(500, 2000)
            } for _ in range(3)
        ]
        daily_quests[user_id]['last_reset'] = today
        daily_quests[user_id]['completed_today'] = 0
        save_daily_quests()
    
    embed = discord.Embed(
        title="📋 Daily Quests",
        description="Complete quests for bonus chips!",
        color=0xFFD700
    )
    
    if not daily_quests[user_id]['quests']:
        embed.add_field(name="No Quests", value="Come back tomorrow!", inline=False)
    else:
        for i, quest in enumerate(daily_quests[user_id]['quests'], 1):
            progress = f"{quest['progress']}/{quest['target']}"
            reward_text = f"💰 **{quest['reward']}** chips"
            embed.add_field(
                name=f"Quest {i}: {quest['type'].replace('_', ' ').title()}",
                value=f"Progress: {progress}\nReward: {reward_text}",
                inline=False
            )
    
    embed.set_footer(text=f"Completed today: {quest_data.get('completed_today', 0)}/3")
    await ctx.send(embed=embed)

@bot.hybrid_command(name='prestige')
async def prestige_command(ctx):
    """Reset your progress for permanent multipliers"""
    user_id = str(ctx.author.id)
    
    init_player_stats(user_id)
    
    if user_id not in prestige_data:
        prestige_data[user_id] = {'prestige_tier': 0, 'total_resets': 0, 'multiplier': 1.0}
    
    prestige = prestige_data[user_id]
    current_level = player_stats[user_id].get('level', 1)
    
    embed = discord.Embed(
        title="✨ Prestige System",
        description="Reset your progress to gain permanent multipliers!",
        color=0x9900FF
    )
    
    embed.add_field(name="Current Level", value=str(current_level), inline=True)
    embed.add_field(name="Prestige Tier", value=str(prestige['prestige_tier']), inline=True)
    embed.add_field(name="Multiplier", value=f"{prestige['multiplier']}x", inline=True)
    
    next_multiplier = 1.0 + (prestige['total_resets'] + 1) * 0.05
    embed.add_field(
        name="Next Prestige",
        value=f"Reach Level 100+ to prestige\nNew Multiplier: {next_multiplier}x",
        inline=False
    )
    
    if current_level >= 100:
        embed.add_field(
            name="Ready to Prestige!",
            value="Use `~prestige confirm` to reset (You'll keep your multiplier!)",
            inline=False
        )
    
    await ctx.send(embed=embed)

@bot.hybrid_command(name='mystats')
async def mystats_command(ctx):
    """View your personal game statistics"""
    user_id = str(ctx.author.id)
    
    init_player_stats(user_id)
    
    stats = player_stats[user_id]
    history = game_history.get(user_id, [])
    
    if not history:
        return await ctx.send("❌ You haven't played any games yet!")
    
    total_games = len(history)
    wins = len([g for g in history if g.get('result') == 'win'])
    losses = len([g for g in history if g.get('result') == 'loss'])
    win_rate = (wins / total_games * 100) if total_games > 0 else 0
    
    total_wagered = sum(g.get('wager', 0) for g in history)
    total_won = sum(g.get('amount', 0) for g in history if g.get('result') == 'win')
    roi = ((total_won - total_wagered) / total_wagered * 100) if total_wagered > 0 else 0
    
    game_counts = {}
    for game in history:
        game_name = game.get('game', 'unknown')
        game_counts[game_name] = game_counts.get(game_name, 0) + 1
    
    favorite_game: Union[str, None] = "N/A"
    if game_counts:
        favorite_game = max(game_counts, key=lambda g: game_counts[g])
    
    embed = discord.Embed(
        title="📊 My Statistics",
        description=f"Game stats for {ctx.author.name}",
        color=0x00FFFF
    )
    
    embed.add_field(name="Total Games", value=str(total_games), inline=True)
    embed.add_field(name="Wins", value=f"{wins} ({win_rate:.1f}%)", inline=True)
    embed.add_field(name="Losses", value=str(losses), inline=True)
    
    embed.add_field(name="Total Wagered", value=f"💰 {total_wagered:,}", inline=True)
    embed.add_field(name="ROI", value=f"{roi:.2f}%", inline=True)
    embed.add_field(name="Favorite Game", value=favorite_game.title(), inline=True)
    
    embed.add_field(name="Level", value=str(stats.get('level', 1)), inline=True)
    embed.add_field(name="XP", value=str(stats.get('xp', 0)), inline=True)
    embed.add_field(name="VIP Tier", value=stats.get('vip_tier', 'None'), inline=True)
    
    await ctx.send(embed=embed)

@bot.hybrid_command(name='birthday')
async def birthday_command(ctx, date=None):
    """Set your birthday for annual bonus chips"""
    user_id = str(ctx.author.id)
    
    if not date:
        if user_id in user_birthdays:
            return await ctx.send(f"🎂 Your birthday is set to: **{user_birthdays[user_id]}**")
        return await ctx.send("❌ Use `~birthday MM-DD` to set your birthday (e.g., `~birthday 03-15`)")
    
    try:
        month, day = date.split('-')
        month, day = int(month), int(day)
        if not (1 <= month <= 12 and 1 <= day <= 31):
            raise ValueError
        
        user_birthdays[user_id] = f"{month:02d}-{day:02d}"
        save_birthdays()
        
        embed = discord.Embed(
            title="🎂 Birthday Set!",
            description=f"Your birthday is now set to **{user_birthdays[user_id]}**\nYou'll get bonus chips on your special day!",
            color=0xFF69B4
        )
        await ctx.send(embed=embed)
    except (ValueError, IndexError):
        await ctx.send("❌ Invalid format. Use `~birthday MM-DD` (e.g., `~birthday 03-15`)")

@bot.hybrid_command(name='refer')
async def refer_command(ctx, action: Optional[str] = None, user: Optional[discord.User] = None):
    """Referral system - invite friends and earn bonuses"""
    user_id = str(ctx.author.id)
    
    init_player_stats(user_id)
    
    if user_id not in referral_data:
        referral_data[user_id] = {'referrer_id': None, 'referred_users': [], 'bonus_earned': 0}
    
    if action == 'link':
        embed = discord.Embed(
            title="🔗 Your Referral Link",
            description=f"Share this code with friends!\n\n**Referral Code:** `{user_id}`\n\nFriends who verify with your code get **500 bonus chips** and you get **250 chips**!",
            color=0x00FF00
        )
        await ctx.send(embed=embed)
    
    elif action == 'use' and user:
        referrer_id = str(user.id)
        
        if referrer_id not in referral_data:
            referral_data[referrer_id] = {'referrer_id': None, 'referred_users': [], 'bonus_earned': 0}
        
        if user_id not in referral_data[referrer_id]['referred_users']:
            referral_data[referrer_id]['referred_users'].append(user_id)
            referral_data[user_id]['referrer_id'] = int(referrer_id)
            
            add_chips(user_id, 500)
            add_chips(referrer_id, 250)
            referral_data[referrer_id]['bonus_earned'] += 250
            
            save_referrals()
            save_player_stats()
            
            embed = discord.Embed(
                title="✅ Referral Bonus!",
                description=f"You were referred by <@{referrer_id}>!\n\n**You got:** 💰 500 chips\n**They got:** 💰 250 chips",
                color=0x00FF00
            )
            await ctx.send(embed=embed)
        else:
            await ctx.send("❌ Already referred by this user!")
    
    else:
        ref_data = referral_data[user_id]
        embed = discord.Embed(
            title="🔗 Referral Stats",
            description="Your referral information",
            color=0x00FF00
        )
        
        embed.add_field(name="Referred Friends", value=str(len(ref_data['referred_users'])), inline=True)
        embed.add_field(name="Bonus Earned", value=f"💰 {ref_data['bonus_earned']:,}", inline=True)
        
        if ref_data['referrer_id']:
            embed.add_field(name="Your Referrer", value=f"<@{ref_data['referrer_id']}>", inline=False)
        
        embed.add_field(name="Get Started", value="`~refer link` - Get your referral code\n`~refer use @user` - Use someone's referral code", inline=False)
        
        await ctx.send(embed=embed)

@bot.event
async def on_command_error(ctx, error):
    """Handle command errors"""
    error_msg = str(error)
    
    # Ignore certain errors
    if isinstance(error, commands.CommandNotFound):
        return
    
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"❌ Missing required argument: `{error.param.name}`")
        return
    
    if isinstance(error, commands.BadArgument):
        await ctx.send("❌ Invalid argument provided.")
        return
    
    if isinstance(error, commands.CommandOnCooldown):
        await ctx.send(f"⏰ This command is on cooldown. Try again in {error.retry_after:.1f}s")
        return
    
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ You don't have permission to use this command.")
        return
    
    # For all other errors, send to user and log to channel
    await ctx.send("❌ An error occurred while executing this command. The error has been logged.")
    
    context_info = f"**Command:** {ctx.command}\n**User:** {ctx.author} ({ctx.author.id})\n**Guild:** {ctx.guild.name if ctx.guild else 'DM'} ({ctx.guild.id if ctx.guild else 'N/A'})\n**Channel:** {ctx.channel.name if hasattr(ctx.channel, 'name') else 'DM'}"
    
    await send_error_to_channel(
        "Command Error",
        f"```py\n{type(error).__name__}: {error_msg}\n```",
        context_info
    )
    
    print(f"Command error in {ctx.command}: {error}")

@bot.event
async def on_error(event, *args, **kwargs):
    """Handle general errors"""
    import traceback
    
    error_msg = traceback.format_exc()
    
    await send_error_to_channel(
        f"Bot Error in {event}",
        f"```py\n{error_msg[:3900]}\n```",
        f"**Event:** {event}"
    )
    
    print(f"Error in {event}:")
    print(error_msg)

# Run the bot
if __name__ == "__main__":
    token = os.getenv("DISCORD_BOT_TOKEN")
    if not token:
        print("Error: DISCORD_BOT_TOKEN not found in environment variables!")
        print("Please set your Discord bot token in the Secrets tab.")
        exit(1)
    
    bot.run(token)
