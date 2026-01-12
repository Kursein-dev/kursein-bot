# Discord Kursein Bot - Tokyo Ghoul + Rocket League Theme

## Overview
Kursein is a streamlined Discord bot with a Tokyo Ghoul and Rocket League theme. The bot focuses on community engagement through Rocket League integration, DISBOARD bump reminders, and stream notifications.

## Recent Changes (January 2026)
- **Complete Rebuild**: Removed all casino system (50+ commands) and Karuta features
- **Ultra-Streamlined**: Reduced to 11 core commands only
- **Twitch API Update**: Now uses TWITCH_CLIENT_ID and TWITCH_CLIENT_SECRET for proper authentication

## Features

### Rocket League Integration
- `~setrank <rank>` - Set your RL rank (Bronze I through Supersonic Legend)
- `~rllb` - View server rank leaderboard
- `~setrlprofile <platform> <username>` - Link Tracker.gg profile
- `~rlstats [@user]` - Fetch live RL stats from Tracker.gg

### DISBOARD Bump Reminders
- `~bumpreminder user @User` or `~bumpreminder role @Role` - Setup reminders
- `~bumpinfo` - View current bump configuration
- `~bumpdisable` - Disable reminders
- Automatically detects `/bump` command and reminds after 2-hour cooldown

### Stream Notifications
- `~streamnotify setup #channel @role` - Configure notifications
- `~streamnotify add twitch/youtube <username>` - Add streamer
- `~streamnotify remove <username>` - Remove streamer
- `~streamnotify list` - View monitored streamers
- Checks every 2 minutes and pings when streamers go live

### Utility Commands
- `~profile [@user]` - View user profile with RL rank
- `~guide` - View all commands

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
- `bump_config` - Bump reminder configuration
- `rl_ranks` - Rocket League ranks
- `rl_profiles` - Linked Tracker.gg profiles
- `streams_config` - Stream notification settings

### Background Tasks
- **Reminder Checker** (1 min) - Sends bump reminders
- **Stream Checker** (2 min) - Monitors Twitch/YouTube

## Required Environment Variables

### Secrets (Required)
- `DISCORD_BOT_TOKEN` - Discord bot token
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
├── main.py              # Main bot code (~700 lines)
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
- No Karuta features
