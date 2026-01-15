# Discord Kursein Bot - Tokyo Ghoul + Rocket League + JJK Theme

## Overview
Kursein is a streamlined Discord bot with a Tokyo Ghoul, Rocket League, and Jujutsu Kaisen theme. The bot features Rocket League integration, DISBOARD bump reminders, stream notifications, moderation tools, and a full JJK-themed idle RPG economy game with cross-series collaborations.

## Recent Changes (January 2026)
- **PvP Battle System**: Challenge other players with ~pvp @user, ELO-based ranked matchmaking (Bronze to Special Grade)
- **Side Missions**: 10 side objectives with tracking and rewards (~sidemissions, ~claimside)
- **Enhanced Leaderboards**: Multiple leaderboard categories (~jjklb, ~lvllb, ~huntlb, ~pvplb, ~storylb)
- **Cooldown Timer**: View all cooldowns at once with ~cooldowns
- **21 Collab Characters**: Attack on Titan, Demon Slayer, Chainsaw Man, One Piece, Dandadan, SAO, Love and Deepspace
- **Facilities System**: Build 5 facilities (Dormitory, Training Grounds, Cursed Archives, Barrier Ward, Curse Workshop) for passive bonuses
- **Holiday Events**: Bot Launch event (Jan 14-21) and Birthday event (Jan 17-18) with income/XP multipliers and claimable rewards
- **Give Command**: Transfer yen between players with ~give
- **Paginated Leaderboard**: Button-based navigation for jjklb
- **Button-Based Navigation**: ~guide and ~jjkguide now use Discord buttons for category navigation
- **Mission Board System**: Choice-based missions with difficulty tiers, risk/reward tradeoffs
- **Dispatch System**: Send sorcerers on idle missions (30min-12hr), claim rewards later
- **Injury System**: High-risk missions can cause injuries that block actions until healed
- **Item Shop & Inventory**: Healing items, XP boosts, protection wards, success boosters
- **Recovery Actions**: ~eat (6h cd) and ~rest (12h cd) for healing and XP
- **Rare Loot Collections**: 12 rare items across 8 collections with set bonuses
- **Story Mode**: 6 story arcs with 22 chapters following the JJK storyline

## Features

### JJK Idle RPG System
Run your own Jujutsu School, exorcise curses, and become a Special Grade sorcerer!

**Getting Started:**
- `~jjkstart` - Begin your sorcerer journey
- `~school` - View your school stats
- `~balance` - Check yen balance
- `~cooldowns` - View all cooldown timers
- `~jjkguide` - Full command list

**PvP Battle System (NEW!):**
- `~pvp @user` - Challenge another sorcerer to battle
- `~pvpstats` - View your PvP stats and rank
- `~pvplb` - PvP leaderboard
- ELO-based ranking: Unranked -> Bronze -> Silver -> Gold -> Platinum -> Diamond -> Special Grade
- Combat power based on level, sorcerers, techniques, tools, and domain
- 5 minute cooldown between battles

**Side Missions (NEW!):**
- `~sidemissions` - View available side objectives
- `~claimside <mission_id>` - Claim completed mission rewards
- 10 missions: Training, Curse Hunting, Wealth, Squad Building, PvP achievements
- Repeatable missions with cooldowns
- Progress tracked automatically for hunt/train activities

**Story Mode:**
- `~story` - View your story progress
- `~chapter` - Start your current story chapter
- `~storyclaim` - Claim completed chapter rewards
- `~arcs` - View all story arcs and their rewards
- 6 Story Arcs: Fearsome Womb, Cursed Training, Kyoto Exchange, Origin of Obedience, Shibuya Incident, Culling Game
- Complete arcs to unlock techniques and characters!

**Mission Board (Choice-Based Gameplay):**
- `~missions` - View 4 available missions (Easy/Medium/Hard/Extreme)
- `~accept <#>` - Accept a mission by number
- `~missionclaim` - Claim rewards when mission completes
- Missions have different durations, rewards, and injury risks
- Board refreshes every 30 minutes

**Dispatch System (Idle Missions):**
- `~dispatchlist` - View dispatch mission options
- `~dispatch <sorcerer> <mission_id>` - Send a sorcerer on a long mission
- `~dispatchstatus` - Check progress of dispatched sorcerers
- `~dispatchclaim` - Claim all completed dispatch rewards
- Missions range from 30 minutes to 12 hours
- Higher risk = better rewards + rare loot chances

**Injury & Recovery:**
- Injuries can block hunting/training until healed
- `~rest` - Rest to heal injuries (12h cooldown)
- `~eat` - Eat for small XP and minor healing (6h cooldown)
- Use healing items to speed recovery

**Item Shop & Inventory:**
- `~inventory` - View your items
- `~shopitems` - Browse the item shop
- `~buyitem <name>` - Purchase an item
- `~use <name>` - Use an item
- Items: Bandages, Cursed Salve, XP Charms, Luck Talismans, Protection Wards, etc.

**Rare Loot & Collections:**
- `~collections` - View your rare loot progress
- 12 rare items across 8 collections
- Complete collections for permanent bonuses and titles
- Collections: King of Curses, Disaster Curses, Limitless Legacy, etc.

**Quick Earning (Legacy):**
- `~hunt` - Exorcise curses for yen/XP (30s cooldown)
- `~train` - Train to gain XP (60s cooldown)
- `~daily` - Daily reward with streak bonus
- `~collect` - Collect hourly income from sorcerers

**Upgrades:**
- `~sorcerers` / `~hire <name>` - Hire sorcerers (52 total including collabs!)
- `~techniques` / `~learntechnique <name>` - Learn cursed techniques
- `~tools` / `~buytool <name>` - Buy cursed tools
- `~domain` / `~upgradedomain` - Upgrade domain expansion

**Clans:**
- `~clancreate <name>` - Create a clan (50,000 yen)
- `~clanjoin <name>` - Join an existing clan
- `~clanleave` - Leave your clan
- `~claninfo` - View clan details
- `~clanlb` - Clan leaderboard

**Leaderboards:**
- `~leaderboards` - View all leaderboard categories
- `~jjklb` - Top sorcerers by yen
- `~lvllb` - Top sorcerers by level
- `~huntlb` - Top curse hunters
- `~pvplb` - Top PvP players by ELO
- `~storylb` - Story progress leaderboard
- `~clanlb` - Clan leaderboard

**Facilities:**
- `~facilities` - View your facilities and bonuses
- `~build <facility>` - Build a facility
- 5 Facilities: Dormitory (income +20%), Training Grounds (XP +20%), Cursed Archives (passive 500 yen/hr), Barrier Ward (injury -10%), Curse Workshop (loot +10%)

**Events:**
- `~events` - View active holiday events
- `~eventclaim` - Claim event rewards
- Bot Launch Event (Jan 14-21): +50% income/XP, claimable reward
- Birthday Event (Jan 17-18): +100% income/XP, claimable reward

**Give/Trade:**
- `~give <@user> <amount>` - Transfer yen to another player

### Rocket League Integration
- `~setrlprofile <platform> <username>` - Link Tracker.gg profile
- `~setrank <rank>` - Submit rank for admin verification
- `~rllb` - View server rank leaderboard
- `~stats [@user]` - Fetch live RL stats
- `~profile [@user]` - View user profile

### Rank Admin Commands
- `~pendingranks` - View pending rank verifications
- `~approverank <@user>` - Approve rank (auto-assigns role)
- `~denyrank <@user> [reason]` - Deny rank with reason
- `~adminsetprofile <@user/ID> <rank> <url>` - Set rank directly
- `~setrankrole <tier> @role` - Configure auto-assign roles
- `~rankroles` - View configured rank roles
- `~resetranks` - Reset all ranks for new season

### AFK System
- `~afk [reason]` - Set AFK status
- Auto-clears when you send a message
- Notifies others when they ping an AFK user

### Server Stats
- `~serverstats` - View member count, online users, channels, age, owner

### Moderation
- `~warn <@user> [reason]` - Warn a user (logs to updates channel)
- Auto-logs ban/unban events to updates channel

### DISBOARD Bump Reminders
- `~bumpinfo` - View bump reminder status
- Automatically detects `/bump` and reminds after 2-hour cooldown

### Stream Notifications
- `~list` - View monitored streamers
- Hardcoded: kursein, hikarai_, warinspanish209, loafylmaoo

### Utility Commands
- `~guide` - View all commands
- `~botinfo` - Bot stats

## System Architecture

### Technology Stack
- **Python 3.11** with discord.py 2.6.4
- **PostgreSQL** (Neon-backed) for persistent storage
- **JSON files** as automatic backups
- **Tracker.gg API** for Rocket League stats
- **Twitch Helix API** for stream detection

### Data Storage
Primary storage in PostgreSQL with JSONB columns:
- `reminders` - Bump reminders
- `prefixes` - Server prefixes
- `rl_ranks` - Rocket League ranks
- `rl_profiles` - Linked Tracker.gg profiles
- `afk_users` - AFK status
- `pending_ranks` - Pending rank verifications
- `rank_roles` - Tier to role ID mapping
- `jjk_players` - JJK economy player data (includes inventory, injuries, missions, collections, story progress, PvP stats, side mission progress)
- `jjk_clans` - JJK clan data

### JJK Game Data
**Sorcerers (52 total):**
- JJK Core (21): Yuji, Megumi, Nobara, Maki, Panda, Inumaki, Todo, Yuta, Gojo, Nanami, Mei Mei, Kusakabe, Miwa, Momo, Mechamaru, Kamo, Mai, Naoya, Choso, Toji, Sukuna
- Exclusive (1): Saya (Noctflare technique)
- Solo Leveling (3): Sung Jinwoo, Cha Hae-In, Goto Ryuji
- Persona (3): Joker, Makoto, Yu Narukami
- Tokyo Ghoul (3): Kaneki, Touka, Arima
- Attack on Titan (3): Eren, Mikasa, Levi
- Demon Slayer (3): Tanjiro, Nezuko, Zenitsu
- Chainsaw Man (3): Denji, Power, Makima
- One Piece (3): Luffy, Zoro, Sanji
- Dandadan (2): Okarun, Momo
- SAO (2): Kirito, Asuna
- Love and Deepspace (3): Zayne, Rafayel, Xavier

**Techniques (8):** Divergent Fist, Black Flash, Ten Shadows, Cursed Speech, Boogie Woogie, Reverse Cursed, Domain Amplification, Noctflare (exclusive)
**Tools (5):** Slaughter Demon, Playful Cloud, Inverted Spear, Split Soul Katana, Prison Realm
**Domains (5):** No Domain, Incomplete, Chimera Shadow Garden, Malevolent Shrine, Infinite Void
**Grades:** Grade 4 -> Grade 3 -> Grade 2 -> Grade 1 -> Semi-1st -> Special Grade

**PvP Ranks:** Unranked -> Bronze (800 ELO) -> Silver (1000) -> Gold (1200) -> Platinum (1400) -> Diamond (1600) -> Special Grade (1800)

**Story Arcs (6):** Fearsome Womb, Cursed Training, Kyoto Goodwill Event, Origin of Obedience, Shibuya Incident, Culling Game
**Story Chapters:** 22 total chapters across all arcs
**Mission Difficulties:** Easy (1-2 min), Medium (3-5 min), Hard (6-10 min), Extreme (12-30 min)
**Dispatch Durations:** 30 min to 12 hours
**Items (8):** Bandage, Cursed Salve, Reverse Technique Scroll, XP Charm, Luck Talisman, Protection Ward, Energy Drink, Salmon Onigiri
**Injuries (5):** Minor Bruise, Cursed Wound, Broken Arm, Cursed Poison, Domain Backlash
**Rare Loot (12):** Sukuna's Finger, Death Painting Fragment, Infinity Cloth, Todo's Idol Photo, etc.
**Collections (8):** King of Curses, Death Paintings, Limitless Legacy, Jujutsu Memories, Technique Archive, Zenin Legacy, Cursed Bonds, Disaster Curses
**Side Missions (10):** Training Dummy, Curse Collector, Training Montage, Wealthy Sorcerer, Squad Builder, Technique Student, Domain Initiate, Dedication, First Blood, PvP Veteran

### Hardcoded IDs
- LOG_CHANNEL_ID: 1435009184285589554
- ADMIN_ROLE_ID: 1410509859685662781
- BUMP_CHANNEL_ID: 1418819741471997982
- BUMP_ROLE_ID: 1436421726727700542
- STREAM_CHANNEL_ID: 1442613254546526298

### Background Tasks
- **Reminder Checker** (1 min) - Sends bump reminders
- **Stream Checker** (2 min) - Monitors Twitch

## Required Environment Variables

### Secrets (Required)
- `DISCORD_BOT_TOKEN` - Discord bot token
- `TRACKER_API_KEY` - Tracker.gg API key

### Secrets (Optional)
- `TWITCH_CLIENT_ID` - Twitch Developer App Client ID
- `TWITCH_CLIENT_SECRET` - Twitch Developer App Client Secret

## File Structure
```
├── main.py              # Main bot code (~5200 lines)
├── db.py                # Database operations
├── replit.md            # This documentation
├── jjk_data.json        # JJK player data backup
├── jjk_clans.json       # JJK clan data backup
└── *.json               # Other backup data files
```

## User Preferences
- Bot supports both prefix commands (`~`) and slash commands (`/`)
- Default prefix: `~`
- Tokyo Ghoul + Rocket League + JJK theme
- Ranks accept both "1" and "I" format (Diamond 1 = Diamond I)
- NO gambling/casino mechanics - focus on choice-based idle RPG gameplay
