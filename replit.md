# Discord Kursein Bot - Tokyo Ghoul + Rocket League + JJK Theme

## Overview
Kursein is a streamlined Discord bot with a Tokyo Ghoul, Rocket League, and Jujutsu Kaisen theme. The bot features Rocket League integration, DISBOARD bump reminders, stream notifications, moderation tools, and a full JJK-themed idle RPG economy game.

## Recent Changes (January 2026)
- **Mission Board System**: Choice-based missions with difficulty tiers, risk/reward tradeoffs
- **Dispatch System**: Send sorcerers on idle missions (30min-12hr), claim rewards later
- **Injury System**: High-risk missions can cause injuries that block actions until healed
- **Item Shop & Inventory**: Healing items, XP boosts, protection wards, success boosters
- **Recovery Actions**: ~eat (6h cd) and ~rest (12h cd) for healing and XP
- **Rare Loot Collections**: 12 rare items across 8 collections with set bonuses
- **JJK Economy System**: Full Jujutsu Kaisen themed economy game (55+ commands)

## Features

### JJK Idle RPG System
Run your own Jujutsu School, exorcise curses, and become a Special Grade sorcerer!

**Getting Started:**
- `~jjkstart` - Begin your sorcerer journey
- `~school` - View your school stats
- `~balance` - Check yen balance
- `~jjkguide` - Full command list

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
- `~sorcerers` / `~hire <name>` - Hire sorcerers (Yuji, Megumi, Nobara, Gojo, etc.)
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
- `~jjklb` - Top sorcerers by yen

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
- `jjk_players` - JJK economy player data (includes inventory, injuries, missions, collections)
- `jjk_clans` - JJK clan data

### JJK Game Data
**Sorcerers (9):** Yuji, Megumi, Nobara, Maki, Panda, Inumaki, Todo, Yuta, Gojo
**Techniques (7):** Divergent Fist, Black Flash, Ten Shadows, Cursed Speech, Boogie Woogie, Reverse Cursed, Domain Amplification
**Tools (5):** Slaughter Demon, Playful Cloud, Inverted Spear, Split Soul Katana, Prison Realm
**Domains (5):** No Domain, Incomplete, Chimera Shadow Garden, Malevolent Shrine, Infinite Void
**Grades:** Grade 4 -> Grade 3 -> Grade 2 -> Grade 1 -> Semi-1st -> Special Grade

**Mission Difficulties:** Easy (1-2 min), Medium (3-5 min), Hard (6-10 min), Extreme (12-30 min)
**Dispatch Durations:** 30 min to 12 hours
**Items (8):** Bandage, Cursed Salve, Reverse Technique Scroll, XP Charm, Luck Talisman, Protection Ward, Energy Drink, Salmon Onigiri
**Injuries (5):** Minor Bruise, Cursed Wound, Broken Arm, Cursed Poison, Domain Backlash
**Rare Loot (12):** Sukuna's Finger, Death Painting Fragment, Infinity Cloth, Todo's Idol Photo, etc.
**Collections (8):** King of Curses, Death Paintings, Limitless Legacy, Jujutsu Memories, Technique Archive, Zenin Legacy, Cursed Bonds, Disaster Curses

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
├── main.py              # Main bot code (~3100 lines)
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
