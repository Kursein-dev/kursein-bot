# Discord Kursein Bot - JJK Idle RPG

## Overview
Kursein v4.0 is a JJK-focused Discord bot featuring a full idle RPG economy game with cross-series collaborations (Solo Leveling, Persona, Tokyo Ghoul, Attack on Titan, Demon Slayer, Chainsaw Man, One Piece, Dandadan, SAO, Love and Deepspace, Seven Deadly Sins, My Hero Academia, Bleach, Naruto, Hunter x Hunter). The bot now focuses purely on the JJK RPG experience with server utilities.

## Recent Changes (January 2026)
- **v4.0 Refactor**: Removed Rocket League, Twitch stream, bump reminders, and moderation features to focus purely on JJK RPG
- **Unified Guide**: Single `~guide` command with interactive button navigation for all features
- **Unified Leaderboard**: Single `~lb` command with tabbed navigation (Yen, Level, Hunt, PvP, Story, Clan)
- **PvP Battle System**: Challenge other players with ~pvp @user, ELO-based ranked matchmaking (Bronze to Special Grade)
- **Side Missions**: 10 side objectives with tracking and rewards (~sidemissions, ~claimside)
- **Cooldown Timer**: View all cooldowns at once with ~cooldowns
- **122 Sorcerers**: 34 JJK core + 1 exclusive (Saya) + 87 collab characters from 14 series
- **Facilities System**: Build 5 facilities for passive bonuses
- **Holiday Events**: Bot Launch event (Jan 14-21) and Birthday event (Jan 17-18)
- **Mission Board System**: Choice-based missions with difficulty tiers, risk/reward tradeoffs
- **Dispatch System**: Send sorcerers on idle missions (30min-12hr), claim rewards later
- **Item Shop & Inventory**: Healing items, XP boosts, protection wards, success boosters
- **Rare Loot Collections**: 12 rare items across 8 collections with set bonuses
- **Story Mode**: 6 story arcs with 22 chapters following the JJK storyline
- **Gates System**: Solo Leveling-inspired dungeon gates (E/D/C/B/A/S ranks) with gate tokens and rare loot
- **100-Floor Dungeon**: SAO Tower-style progressive climbing with boss floors, checkpoints, and milestone rewards
- **Team Dispatch**: Send squads of 2-4 sorcerers with synergy bonuses based on series composition

## Features

### JJK Idle RPG System
Run your own Jujutsu School, exorcise curses, and become a Special Grade sorcerer!

**Getting Started:**
- `~jjkstart` - Begin your sorcerer journey
- `~school` - View your school stats
- `~balance` - Check yen balance
- `~cooldowns` - View all cooldown timers
- `~guide` - Full interactive command guide with button navigation

**PvP Battle System (NEW!):**
- `~pvp @user` - Challenge another sorcerer to battle
- `~pvpstats` - View your PvP stats and rank
- `~lb` then click PvP tab - PvP leaderboard (or use legacy alias `~pvplb`)
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

**Leaderboards (Unified with Tabs):**
- `~lb` / `~leaderboard` - View all leaderboards with interactive tab buttons
- Tabs: Yen, Level, Hunt, PvP, Story, Clan
- Player names are now pingable mentions!

**Facilities:**
- `~facilities` - View your facilities and bonuses
- `~build <facility>` - Build a facility
- 5 Facilities: Dormitory (income +20%), Training Grounds (XP +20%), Cursed Archives (passive 500 yen/hr), Barrier Ward (injury -10%), Curse Workshop (loot +10%)

**Events:**
- `~events` - View active holiday events
- `~eventclaim` - Claim event rewards
- Bot Launch Event (Jan 14-21): +50% income/XP, claimable reward
- Birthday Event (Jan 17-18): +100% income/XP, claimable reward

**Gates System (Solo Leveling):**
- `~gates` - View available gates
- `~entergate <rank>` - Enter a gate (E/D/C/B/A/S)
- `~gateclaim` - Claim gate rewards
- 6 gate ranks with level requirements (E: Lv1, D: Lv10, C: Lv25, B: Lv50, A: Lv100, S: Lv200)
- Earn Gate Tokens, yen, XP, and rare loot

**100-Floor Dungeon (SAO Tower):**
- `~dungeon` - View dungeon progress
- `~climbfloor` - Attempt the next floor
- `~dungeonclaim` - Claim floor rewards
- Boss floors every 10 floors (better rewards)
- Checkpoints every 10 floors (failure returns to last checkpoint)
- Milestones: Floor 10 (25K), Floor 25 (Technique), Floor 50 (250K), Floor 75 (Sorcerer), Floor 100 (1M)

**Team Dispatch:**
- `~teamdispatch` - View team missions
- `~sendteam <mission_id> <sorcerers>` - Send a squad (2-4 sorcerers)
- `~teamstatus` - Check team progress
- `~teamclaim` - Claim completed missions
- 5 team missions with varying difficulty and team size requirements
- Synergy bonuses for same-series or diverse teams

**Give/Trade:**
- `~give <@user> <amount>` - Transfer yen to another player

### AFK System
- `~afk [reason]` - Set AFK status
- Auto-clears when you send a message
- Notifies others when they ping an AFK user

### Server Stats
- `~serverstats` - View member count, online users, channels, age, owner

### Utility Commands
- `~guide` - View all commands
- `~botinfo` - Bot stats

## System Architecture

### Technology Stack
- **Python 3.11** with discord.py 2.6.4
- **PostgreSQL** (Neon-backed) for persistent storage
- **JSON files** as automatic backups

### Data Storage
Primary storage in PostgreSQL with JSONB columns:
- `prefixes` - Server prefixes
- `afk_users` - AFK status
- `jjk_players` - JJK economy player data (includes inventory, injuries, missions, collections, story progress, PvP stats, side mission progress)
- `jjk_clans` - JJK clan data

### JJK Game Data
**Sorcerers (122 total):**
- JJK Core (34): Yuji, Megumi, Nobara, Maki, Panda, Inumaki, Todo, Yuta, Gojo, Nanami, Mei Mei, Kusakabe, Miwa, Momo, Mechamaru, Kamo, Mai, Naoya, Choso, Toji, Sukuna, Kenjaku, Mahito, Jogo, Hanami, Dagon, Kashimo, Hakari, Higuruma, Ryu, Uro, Uraume, Yorozu, Charles
- Exclusive (1): Saya (Noctflare technique)
- Solo Leveling (6): Sung Jinwoo, Cha Hae-In, Goto Ryuji, Beru, Iron, Thomas Andre
- Persona (5): Joker, Makoto, Yu Narukami, Ann, Ryuji
- Tokyo Ghoul (6): Kaneki, Touka, Arima, Tsukiyama, Ayato, Eto
- Attack on Titan (6): Eren, Mikasa, Levi, Erwin, Hange, Annie
- Demon Slayer (8): Tanjiro, Nezuko, Zenitsu, Inosuke, Rengoku, Mitsuri, Muichiro, Shinobu
- Chainsaw Man (6): Denji, Power, Makima, Aki, Kobeni, Angel Devil
- One Piece (8): Luffy, Zoro, Sanji, Nami, Robin, Law, Shanks, Ace
- Dandadan (4): Okarun, Momo, Aira, Turbo Granny
- SAO (5): Kirito, Asuna, Sinon, Leafa, Eugeo
- Love and Deepspace (6): Zayne, Rafayel, Xavier, Sylus, Caleb, MC (Deepspace Hunter)
- Seven Deadly Sins (7): Meliodas, Ban, King, Diane, Gowther, Escanor, Merlin
- My Hero Academia (10): Deku, Bakugo, Todoroki, All Might, Uraraka, Iida, Tokoyami, Kirishima, Endeavor, Hawks
- Bleach (7): Ichigo, Rukia, Byakuya, Kenpachi, Aizen, Toshiro, Urahara
- Naruto (7): Naruto, Sasuke, Kakashi, Itachi, Minato, Jiraiya, Madara
- Hunter x Hunter (5): Gon, Killua, Kurapika, Hisoka, Netero

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

## Required Environment Variables

### Secrets (Required)
- `DISCORD_BOT_TOKEN` - Discord bot token

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
- Tokyo Ghoul + JJK theme
- NO gambling/casino mechanics - focus on choice-based idle RPG gameplay
