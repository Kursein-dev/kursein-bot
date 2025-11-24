# Discord DISBOARD Bump Assistant & Casino Bot

## Overview
This project is a Discord bot designed to boost server engagement through two core features: a DISBOARD bump reminder system and an extensive casino game suite. The bump assistant automates the detection of DISBOARD server bumps and notifies users after the 2-hour cooldown, ensuring consistent server visibility. The casino module provides a diverse range of gambling experiences, from quick games like slots and coinflip to intricate table games such as blackjack, roulette, hi-lo, poker, crash, mines, wheel, and craps. It incorporates a persistent chip economy, daily rewards, a robust challenge system, XP & leveling, VIP tiers, achievements, a progressive jackpot, a loan system, a shop, tournaments, and a pet collection system to foster active and long-term community participation. The bot aims to deliver both entertainment and practical utility, cultivating a more vibrant and interactive Discord community.

## User Preferences
- The bot supports both prefix commands (default: `~`) and slash commands (`/`).
- Admins can customize the bot's prefix using `~setprefix`.
- The user expects persistent storage for all game-related data, bump configurations, and user progress.
- The bot should provide clear and organized help interfaces, grouping commands by category.
- The user prefers interactive elements where appropriate, such as buttons for game actions.
- All chip transactions should be logged for transparency and monitoring.

## System Architecture
The bot is built using Python 3.11 and the discord.py 2.6.4 library, supporting both traditional prefix and native Discord slash commands. All configurations, user data (bump reminders, custom prefixes, chip balances, ticket balances, claims, challenges, XP, VIP status, achievements, loans, shop inventory, tournament data, transaction logs, rob success rate, monthly claim tracking, bounties, guild player tracking, verified users, and pet collections) are stored persistently using JSON files. The bot includes background tasks for bump reminders (10-second interval), claim reminders (5-minute interval), and daily shop rotation (checks at 2pm PST using pytz timezone handling).

**Slash Commands:** The bot currently supports 5 slash commands (`/bump`, `/secret`, `/coinflip`, `/roll`, `/8ball`). The `/help` slash command was removed in favor of the more comprehensive `~guide` prefix command, which provides better organization and detailed information across 7 interactive pages.

**Error Logging:**
- All bot errors and command errors are automatically logged to Discord channel ID: `1435009092782522449`
- Error logs include full stack traces, context (command, user, guild, channel), and timestamps
- Comprehensive error handling for both command errors and general bot events

**Server-Specific Features:**
- **Leaderboards**: Each Discord server has its own separate leaderboard showing only verified users who are members of that server. Players must verify using `~verify` to appear on the leaderboard. This ensures fair competition and prevents cross-server leaderboard pollution.

**Key Features and Implementations:**
- **Verification System**: Users must verify once using `~verify` before playing casino games.
- **DISBOARD Bump Assistant**: Detects `/bump` commands and manages 2-hour cooldown reminders.
- **Dual Currency Economy**: 
    - **Chips**: Users start with 1000 chips. Includes daily, weekly, monthly, and yearly chip claims with cooldowns and DM reminders. Owners can grant/revoke infinite chips.
    - **Tickets**: Premium currency purchased in shop or traded from chips at 100,000 chips = 1 ticket. Tickets unlock pet rolls and special features. Use `~buytickets` to convert chips to tickets, or buy ticket bundles in the rotating shop for better value.
    - **Daily Transfer Limits**: 100k chips/day base limit (150k for Gold/Platinum/Elite VIP, 250k hard cap). Prevents chip funneling and maintains economy integrity.
    - **Bank System**: Secure chip storage protected from robberies. Commands: `~bank` (view balance), `~deposit` (store chips), `~withdraw` (retrieve chips). Bank balances are separate from wallet and cannot be stolen.
    - **Clan/Mafia System**: Players can form groups with shared vaults. Create clans for 50k chips using `~createclan`, manage members with `~claninvite`/`~clanjoin`/`~clanleave`/`~clankick`, pool resources with `~clandeposit`/`~clanwithdraw`, and compete on `~clanleaderboard`. Each clan has a leader, optional officers, and a shared vault for team cooperation.
    - **House Profit Tracking**: Admins can view detailed casino statistics using `~record` showing total wagered, payouts, profit margins, RTP%, and house edge analytics.
    - **Economy Balancing (Nov 2025)**: Comprehensive rebalancing to achieve ~95% RTP and prevent extreme wins:
        - **Maximum Bet Limits**: Enforced per-game limits (Slots/Coinflip/Hi-Lo/Wheel/Craps/Poker: 100k chips, Blackjack: 250k chips, Crash: 500k chips, Mines: 250k chips)
        - **Rebalanced Payouts**: Slots reduced (Triple Diamonds 100x→50x, Triple Sevens 50x→25x), Poker reduced (Royal Flush 250x→100x, Straight Flush 50x→25x, Four of a Kind 25x→12x, Full House 9x→5x, Flush 6x→4x, Straight 4x→3x, Three of a Kind 3x→2x, Two Pair 2x→1x)
        - **VIP Bonus Cap**: Maximum 1M chips bonus per game to prevent extreme multiplier stacking
        - **Centralized Validation**: All games use consistent bet validation with clear error messages
- **Enhanced Job System**: Comprehensive career progression with 30 unique jobs unlocked through leveling. Players earn 700-19,250 chips every 2 hours. Jobs unlock at specific levels (1, 5, 10, 15, 20, 25, 30, 40, 50, 60, 75) with higher-level jobs paying significantly more. Commands: `~jobs` (view all 30 jobs with unlock status), `~selectjob <job name>` (choose your career), `~work` (work your selected job or random unlocked job). Features level-based progression, persistent job selection, and visual indicators (⭐ selected, ✅ unlocked, 🔒 locked).
- **Secret Codes System**: 40 themed secret codes for bonus chips (7.7k-100k chips). Themes: Gambling (13 codes), Rocket League (13 codes), Tokyo Ghoul (14 codes). Rarity tiers: Common, Uncommon, Rare, Mythic. One-time claims per user. Use `/secret <code>` or `~<code>` directly.
- **Gaming Suite**:
    - **Quick Games**: Slots, Coinflip, Dice rolling, Magic 8-Ball.
    - **Table Games**: Blackjack (solo/multiplayer), Roulette (multiplayer with red/black/green betting), Hi-Lo, Poker (5-Card Draw, Texas Hold'em multiplayer).
    - **Advanced Games**: Crash (heavily rigged 1.00x-5.00x range with 90% instant crash rate), Mines, Wheel, Craps.
    - **Multiplayer**: PvP Coinflip, Multiplayer Poker, Multiplayer Roulette, Sports Betting.
    - **All games feature anti-spam protection** - players can only have 1 active game at a time.
- **Progression System**: 
    - **XP & Leveling**: Players earn XP (10% of bet amount) from all casino games with instant level-up notifications and chip rewards.
    - **VIP Tiers (6 Total)**: 
        - **Booster** 🚀 (Server Boosters): +25% chips, +40% XP, +25k daily bonus
        - **Bronze** 🥉 (50M wagered): +10% chips, +15% XP, +2.5k daily bonus
        - **Silver** 🥈 (250M wagered): +20% chips, +30% XP, +10k daily bonus
        - **Gold** 🥇 (1B wagered): +35% chips, +50% XP, +50k daily bonus
        - **Platinum** 💎 (5B wagered): +60% chips, +80% XP, +250k daily bonus
        - **Elite** 👑 (25B wagered): +100% chips (DOUBLE!), +150% XP, +1.5M daily bonus
        - Booster VIP is exclusive to server boosters regardless of wagered amount. Requirements increased 20-50x (Nov 2025) to make tiers extremely exclusive and prestigious. View all tiers with `~viptiers`.
    - **Achievements**: Unlock achievements for various milestones.
    - **Progressive Jackpot**: 0.1% chance to win the jackpot pool on any game.
    - **Loan System**: Borrow chips when broke (with interest).
    - **Shop System**: Daily rotating shop featuring 6 random items from a pool of 52 items (31 regular + 21 seasonal). Rotates at 2pm PST daily. Button-based interactive interface with pagination (2 items/page). Categories include basic boosts (XP, chips, luck), advanced boosts (jackpot multipliers, god mode, high roller rush), ultimate protection (diamond insurance, bankruptcy shield, streak saver), elite combo packs (whale bundle, legend's arsenal), VIP passes (gold/platinum/elite tiers), special items (instant levels, double daily claims, lucky 7), and premium ticket bundles. Holiday items automatically appear during their respective seasons (Christmas, Halloween, New Year, Valentine's, Easter, Summer, Thanksgiving). Items can be purchased via buy buttons or activated using `~use <item_id>`.
    - **Tournament System**: Compete in weekly tournaments.
- **Challenge System**: 18 challenges tracking plays, wins, jackpots, streaks, and claims across all games (slots, poker, blackjack, roulette, hilo, wheel, crash, mines, craps, coinflip). Rewards range from 250-3,000 chips.
- **Owner Tools**: `~addchips`, `~resetbalance`, `~infinite` (toggle infinite chips).
- **Admin Tools**: `~verifyuser`, `~unverify`, `~chipslog`, `~resetclaim`, `~bumpreminder`, `~bumpdisable`, `~secrets` (view all 40 secret codes), `~record` (view casino profit/loss statistics and RTP analytics).
- **Pets Collection System**: Roll for collectible pets with different rarity tiers. 20 unique pets across 6 rarity levels (Common 50%, Uncommon 30%, Rare 12%, Epic 5%, Legendary 2.5%, Mythic 0.5%). Roll cost: 1 ticket per roll. Track unique pets and duplicates. Commands: `~rollpet` (roll for random pet), `~pets` (view collection).
- **Tickets System**: Premium currency system where players can purchase tickets in the daily rotating shop or trade chips for tickets. Conversion rate: 100,000 chips = 1 ticket. Ticket bundles available in shop offer better value. Tickets used for pet rolls. Commands: `~buytickets [amount]` (convert chips to tickets), `~balance` (view chips and tickets).
- **Rocket League Integration**: Full RL rank system and Tracker.gg API integration for gaming community.
    - **Rank System**: 23 ranks from Unranked to Supersonic Legend (Bronze I-III, Silver I-III, Gold I-III, Platinum I-III, Diamond I-III, Champion I-III, Grand Champion I-III, Supersonic Legend)
    - **Live Stats Fetching**: Uses Tracker.gg API to fetch real-time player stats including career stats (wins, goals, assists, saves, shots, MVPs) and ranked playlist data (1v1, 2v2, 3v3 with ranks and MMR). Handles URL encoding for usernames with spaces/special characters.
    - **Commands**: `~setrank <rank>` (manually set RL rank), `~rllb [limit]` (RL rank leaderboard), `~setrlprofile <platform> <username>` (link Tracker.gg profile), `~rlstats [@user]` (fetch live stats from Tracker.gg API)
    - **Platforms Supported**: Epic Games, Steam, PlayStation, Xbox, Nintendo Switch
    - **Data Storage**: Persistent rank and profile data stored in rl_ranks.json and rl_profiles.json
    - **API Configuration**: Uses TRACKER_API_KEY environment secret for Tracker.gg API authentication with aiohttp for async requests
- **Social/Utility**: `~guide` (interactive paginated command guide with Previous/Next buttons - 7 pages covering Getting Started, Banking & Clans, Casino Games, Multiplayer & Social, Rocket League Integration, Progression & Codes, plus Admin Commands for administrators), `~gameinfo` / `~games` (comprehensive 4-page casino games guide with detailed payouts and strategies), `~profile`, `~setbanner` (set custom profile banner image), `~removebanner` (remove profile banner), `~setidol` (set pet as profile idol displayed in trades), `~inventory` (view items and active boosts), `~use` (activate purchased items from inventory), `~leaderboard`, `~mt` (multi-trade system with automatic chip amount detection), `~rob` (dynamic robbery system), `~bounty` (place bounties on players), `~bounties` (view active bounties), `~claim` (dynamic success rate: 10% at 500 chips down to 0.01% at 100k+ chips - higher bounties much harder to claim).
- **Banking Commands**: `~bank` (view wallet and bank balance), `~deposit <amount>` (deposit chips to safe storage), `~withdraw <amount>` (withdraw from bank to wallet). Bank balances are protected from `~rob` attempts.
- **Clan/Mafia Commands**: `~createclan <name>` (create clan for 50k chips), `~clan` (view clan info), `~claninvite @user` (invite members), `~clanjoin <clan name>` (join a clan), `~clanleave` (leave clan), `~clankick @user` (remove member - leader only), `~clandeposit <amount>` (add chips to vault), `~clanwithdraw <amount>` (withdraw from vault - leader/officers only), `~clans` (list all clans), `~clanleaderboard` (top clans by vault).
- **UI/UX**: Clear, organized, and categorized help interfaces with pagination. Interactive buttons for game actions and navigation. Color-coded embeds for clarity.

## Development Configuration
- **Type Checking**: Pyright configuration added to `pyproject.toml` to suppress false-positive warnings from emoji Unicode characters while maintaining type safety
- **Code Quality**: All code passes Python compilation, AST parsing, and syntax validation - 0 actual errors
- **Note**: IDE may show Pyright warnings about emojis (🎰, 🃏, etc.) - these are false positives and can be safely ignored

## External Dependencies
- **Discord API**: Core integration for bot functionality, message handling, slash commands, and interactive components.
- **DISBOARD**: The bot interacts with the DISBOARD service by detecting its `/bump` command to manage reminders.