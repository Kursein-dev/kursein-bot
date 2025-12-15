# Discord DISBOARD Bump Assistant & Casino Bot

## Overview
This project is a Discord bot designed to boost server engagement through two core features: a DISBOARD bump reminder system and an extensive casino game suite. The bump assistant automates the detection of DISBOARD server bumps and notifies users after the 2-hour cooldown, ensuring consistent server visibility. The casino module provides a diverse range of gambling experiences with a persistent chip economy, daily rewards, challenges, XP & leveling, VIP tiers, achievements, a progressive jackpot, a loan system, a shop, and a pet collection system. The bot aims to deliver both entertainment and practical utility, cultivating a more vibrant and interactive Discord community.

## Recent Changes (December 2025)
- **Complete Database Migration**: Moved ALL runtime data from JSON files to PostgreSQL database
  - Data persists across deployments (no more data loss when pushing to Render)
  - Migrated ALL 20+ data types: streams_config, claims, chips, player_stats, claim_reminders, tickets, pets, jobs, loans, banks, clans, jackpot, bounties, rl_ranks, rl_profiles, verified_users, infinite_users, secret_claims, monthly_claims, daily_transfers, guild_players, profile_banners, staff_data, login_streaks
  - JSON files kept as automatic backups but database is now primary storage
  - Automatic migration on first startup - detects JSON files and imports to database
- **Stream Notifications Fixed**: Improved detection and faster checks (2 min instead of 5 min)
- **Daily Reminders Fixed**: Now checks every 1 minute instead of 5 minutes for faster notifications
- **Casino Odds Rebalanced**: Made games fair like real casinos with proper house edges
  - Crash: ~4% house edge at safe cash-outs (was 90% instant loss)
  - Wheel: 87.5% RTP, 12.5% house edge (realistic casino wheel)
  - Bet limits adjusted per game (skill games have higher limits)
- **Shop Emoji Fix**: Fixed broken custom emoji in buy button labels
- **Command Cleanup**: Reduced from 98 to 90 commands for cleaner organization
- **Removed Commands**: tournament/tourney, monthlyrewards, mt (multi-trade), testchannel, claim (bounty claim)
- **Unified Reset Command**: Merged `resetdailyclaims` and `resetclaim` into single `~reset` command with user-specific and bulk options
- **Unified Stream Command**: Merged `twitch` and `youtube` into `~streamnotify` with add/remove/list/test subcommands
- **Deployment Fix**: Added `.python-version` file (3.11.10) for Render compatibility

## User Preferences
- The bot supports both prefix commands (default: `~`) and slash commands (`/`).
- Admins can customize the bot's prefix using `~setprefix`.
- The user expects persistent storage for all game-related data, bump configurations, and user progress.
- The bot should provide clear and organized help interfaces, grouping commands by category.
- The user prefers interactive elements where appropriate, such as buttons for game actions.
- All chip transactions should be logged for transparency and monitoring.
- User is considering removing casino features and seeking community input for new direction.

## System Architecture
The bot is built using Python 3.11 and the discord.py 2.6.4 library, supporting both traditional prefix and native Discord slash commands (all commands use `@bot.hybrid_command`). All configurations and user data are stored persistently in PostgreSQL database (JSONB columns for flexible data storage), with JSON files as automatic backups. The bot includes background tasks for bump reminders, claim reminders, daily shop rotation (checks at 2pm PST using pytz timezone handling), and stream checking every 2 minutes.

**UI/UX Decisions:**
- Clear, organized, and categorized help interfaces with pagination.
- Interactive buttons for game actions and navigation.
- Color-coded embeds for clarity.

**Technical Implementations & Feature Specifications:**
- **95 Total Commands**: All supporting both prefix (~) and slash (/) formats
- **Persistent Data Storage**: Primary storage in PostgreSQL database with JSONB columns; JSON files as automatic backups. Database module (`db.py`) handles all data operations.
- **Error Logging**: All bot and command errors are logged to a specific Discord channel with full stack traces, context, and timestamps.
- **DISBOARD Bump Assistant**: Detects `/bump` commands and manages 2-hour cooldown reminders.
- **Dual Currency Economy**: Chips (primary) and Tickets (premium). Includes daily/weekly/monthly/yearly claims, a bank system, a clan/mafia system with shared vaults, and economy balancing with max bet limits and rebalanced payouts.
- **Enhanced Job System**: 30 unique jobs unlocked through leveling, offering chip rewards every 2 hours.
- **Secret Codes System**: 40 themed codes for bonus chips with varying rarity.
- **Gaming Suite**:
    - Quick Games: Slots, Coinflip, Dice rolling, Magic 8-Ball.
    - Table Games: Blackjack (solo/multiplayer), Roulette, Hi-Lo, Poker (5-Card Draw, Texas Hold'em multiplayer).
    - Advanced Games: Crash, Mines, Wheel, Craps.
    - Multiplayer: PvP Coinflip, Multiplayer Poker, Multiplayer Roulette, Sports Betting.
    - Anti-spam protection ensures only one active game per player.
- **Progression System**: XP & Leveling (earn XP from games, level-up rewards), 6 VIP Tiers (based on wagered amount, offering chip/XP bonuses), Achievements, Progressive Jackpot, Loan System.
- **Shop System**: Daily rotating shop with 6 random items from a pool of 52, including boosts, protection, combo packs, VIP passes, special items, and premium ticket bundles. Seasonal items appear automatically.
- **Challenge System**: 18 challenges across various games with chip rewards.
- **Owner/Admin Tools**: Commands for managing chips, user verification, bump reminders, viewing secret codes, unified reset command, and casino statistics (`~record`).
- **Pets Collection System**: Roll for 20 unique pets across 6 rarity levels using tickets.
- **Tickets System**: Premium currency for pet rolls, purchasable in the shop or convertible from chips.
- **Rocket League Integration**: Full RL rank system and Tracker.gg API integration for live player stats, leaderboards, and profile linking. Supports all major platforms.
- **Stream Notification System**: Unified `~streamnotify` command with add/remove/list/test subcommands. Monitors Twitch and YouTube streams every 5 minutes, sending notifications with stream titles, game categories, viewer counts, and role pings when streamers go live.
- **Interactive Staff Directory**: `~staff` command displays paginated staff member profiles with Name, Position, Description, and Fun Facts.
- **Karuta Integration**: Full integration with the Karuta card game bot:
    - `~kwish add/remove/list/clear` - Manage personal wishlist of characters (up to 50)
    - `~kwish channel` - Route wishlist pings to a specific channel
    - `~kwish reminders on/off` - Toggle DM reminders for cooldowns
    - `~kcd` - View tracked Karuta cooldowns
    - Automatic drop scanning: Detects Karuta drops and pings users when wishlist characters appear
    - Cooldown tracking: Automatically tracks when users run k!drop, k!daily, k!vote and sends DM reminders when ready

## Deployment
- **Replit (Development)**: Uses `python main.py` workflow with built-in PostgreSQL
- **Render (Production)**: 
  - Requires `.python-version` file (3.11.10) - NOT `runtime.txt`
  - Must provision PostgreSQL database and set DATABASE_URL environment variable
  - Database migration is automatic on first startup
- **Important**: Only run ONE bot instance at a time (Replit OR Render, not both)

## External Dependencies
- **Discord API**: Core for bot functionality, message handling, slash commands, and interactive components.
- **DISBOARD**: Interaction for detecting `/bump` commands to manage reminders.
- **Tracker.gg API**: Used for fetching real-time Rocket League player statistics.
- **Twitch/YouTube**: Direct web requests are used to check stream status for live notifications (no API keys required for these platforms).
- **Karuta Bot**: Monitors Karuta (ID: 646937666251915264) messages to detect card drops and scan for wishlist matches.