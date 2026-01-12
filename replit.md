# Discord Kursein Bot - Tokyo Ghoul + Rocket League Theme

## Overview
Kursein is a Discord bot rebuilt from the ground up with a Tokyo Ghoul and Rocket League theme. The bot focuses on community engagement through Rocket League integration, Karuta card game companion features, DISBOARD bump reminders, and stream notifications.

## Recent Changes (January 2026)
- **Complete Rebuild**: Removed entire casino system (50+ commands), starting fresh
- **Streamlined Codebase**: Reduced from 15,000+ lines to ~1,200 lines
- **22 Core Commands**: Focused on utility, Rocket League, Karuta, and notifications
- **Twitch API Update**: Now uses TWITCH_CLIENT_ID and TWITCH_CLIENT_SECRET for proper authentication

## Features

### Rocket League Integration
- `~setrank <rank>` - Set your RL rank (Bronze I through Supersonic Legend)
- `~rllb` - View server rank leaderboard
- `~setrlprofile <platform> <username>` - Link Tracker.gg profile
- `~rlstats [@user]` - Fetch live RL stats from Tracker.gg

### Karuta Companion
- `~kwish` - Manage character wishlist (up to 50 characters)
- `~kcd` - View tracked Karuta cooldowns
- **Drop Analysis**: Uses Gemini Vision AI to analyze card drops and show wishlist counts
- **Cooldown Tracking**: DM reminders when drop/daily/vote cooldowns are ready

### DISBOARD Bump Reminders
- `~bumpreminder user @User` or `~bumpreminder role @Role` - Setup reminders
- `~bumpdisable` - Disable reminders
- Automatically detects `/bump` command and reminds after 2-hour cooldown

### Stream Notifications
- `~streamnotify setup #channel @role` - Configure notifications
- `~streamnotify add twitch/youtube <username>` - Add streamer
- `~streamnotify remove <username>` - Remove streamer
- `~streamnotify list` - View monitored streamers
- Checks every 2 minutes and pings when streamers go live

### Utility Commands
- `~ping` - Check bot latency
- `~id <emoji>` - Get custom emoji info
- `~roll <dice>` - Roll dice (e.g., 1d6, 2d20)
- `~8ball <question>` - Magic 8-ball
- `~profile [@user]` - View user profile
- `~setbanner <url>` - Set profile banner
- `~verify` - Verify yourself
- `~guide` - View all commands

### Admin Commands
- `~setprefix <prefix>` - Change bot prefix
- `~staff` - View staff directory
- `~staffedit <field> <value>` - Edit staff profile
- `~update <message>` - Post bot update (Owner only)

## System Architecture

### Technology Stack
- **Python 3.11** with discord.py 2.6.4
- **PostgreSQL** (Neon-backed) for persistent storage
- **JSON files** as automatic backups
- **Gemini 2.0 Flash** for Karuta drop OCR
- **Tracker.gg API** for Rocket League stats
- **Twitch Helix API** for stream detection

### Data Storage
Primary storage in PostgreSQL with JSONB columns:
- `reminders` - Bump reminders
- `prefixes` - Server prefixes
- `bump_config` - Bump reminder configuration
- `verified_users` - Verified user list
- `rl_ranks` - Rocket League ranks
- `rl_profiles` - Linked Tracker.gg profiles
- `streams_config` - Stream notification settings
- `staff_data` - Staff directory profiles
- `karuta_wishlists` - User wishlists
- `karuta_cooldowns` - Cooldown tracking
- `karuta_settings` - User settings
- `profile_banners` - Custom banners

### Background Tasks
- **Reminder Checker** (1 min) - Sends bump reminders
- **Stream Checker** (2 min) - Monitors Twitch/YouTube
- **Karuta Cooldown Checker** (1 min) - Sends DM reminders

## Required Environment Variables

### Secrets (Required)
- `DISCORD_BOT_TOKEN` - Discord bot token
- `GEMINI_API_KEY` - Google AI API key for Karuta drop analysis
- `TRACKER_API_KEY` - Tracker.gg API key for RL stats

### Secrets (Optional - for Stream Notifications)
- `TWITCH_CLIENT_ID` - Twitch Developer App Client ID
- `TWITCH_CLIENT_SECRET` - Twitch Developer App Client Secret

To get Twitch credentials:
1. Go to https://dev.twitch.tv/console/apps
2. Create a new application
3. Copy the Client ID and generate a Client Secret

## Deployment

### Replit (Development)
- Uses `python main.py` workflow
- Built-in PostgreSQL database
- All environment variables in Secrets tab

### Render (Production)
- Requires `.python-version` file (3.11.10)
- Provision PostgreSQL and set DATABASE_URL
- Set all required environment variables

## File Structure
```
├── main.py              # Main bot code (~1,200 lines)
├── db.py                # Database operations
├── main_backup_casino.py # Backup of casino version
├── replit.md            # This documentation
├── .python-version      # Python version for Render
└── *.json               # Backup data files
```

## User Preferences
- Bot supports both prefix commands (`~`) and slash commands (`/`)
- Default prefix: `~` (customizable per server)
- Tokyo Ghoul + Rocket League theme
- No casino/gambling features
