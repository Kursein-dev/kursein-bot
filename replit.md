# Discord Kursein Bot - Tokyo Ghoul + Rocket League Theme

## Overview
Kursein is a streamlined Discord bot with a Tokyo Ghoul and Rocket League theme. The bot focuses on community engagement through Rocket League integration, DISBOARD bump reminders, stream notifications, and moderation tools.

## Recent Changes (January 2026)
- **Complete Rebuild**: Removed all casino system (50+ commands) and Karuta features
- **Ultra-Streamlined**: Reduced to core commands only
- **Twitch API Update**: Now uses TWITCH_CLIENT_ID and TWITCH_CLIENT_SECRET for proper authentication
- **Season 21 Update**: Added `~resetranks` command, setrank now requires linked tracker for admin verification
- **Rank Verification Queue**: Ranks now go to pending queue for admin approval
- **Auto Rank Roles**: Automatically assigns roles when ranks are approved
- **AFK System**: Users can set AFK status with auto-clear on message
- **Server Stats**: View server member count, growth, and activity
- **Mod Logging**: Ban/unban events and warn command logged to updates channel
- **Member Logging**: Join/leave with new account detection (< 7 days pings admin)

## Features

### Rocket League Integration
- `~setrlprofile <platform> <username>` - Link Tracker.gg profile (required before setting rank)
- `~setrank <rank>` - Submit rank for admin verification (supports "Diamond 1" or "Diamond I")
- `~rllb` - View server rank leaderboard
- `~stats [@user]` - Fetch live RL stats from Tracker.gg
- `~profile [@user]` - View user profile with RL rank and tracker link

### Rank Admin Commands
- `~pendingranks` - View pending rank verifications
- `~approverank <@user>` - Approve rank (auto-assigns role)
- `~denyrank <@user> [reason]` - Deny rank with reason
- `~adminsetprofile <@user/ID> <rank> <url>` - Set rank directly without verification
- `~setrankrole <tier> @role` - Configure auto-assign roles (bronze, silver, gold, etc.)
- `~rankroles` - View configured rank roles
- `~resetranks` - Reset all ranks for new season

### AFK System
- `~afk [reason]` - Set AFK status
- Auto-clears when you send a message
- Notifies others when they ping an AFK user

### Server Stats
- `~serverstats` - View member count, online users, channels, age, owner

### Moderation
- `~warn <@user> [reason]` - Warn a user (logs to updates channel, DMs user)
- Auto-logs ban/unban events to updates channel

### Member Logging
- Join/leave messages with member count
- New accounts (< 7 days) ping admin role with red warning
- Semi-new accounts (< 30 days) show orange warning

### DISBOARD Bump Reminders
- `~bumpinfo` - View bump reminder status
- Automatically detects `/bump` command and reminds after 2-hour cooldown
- Hardcoded to ping designated role in bump channel

### Stream Notifications
- `~list` - View monitored streamers
- Hardcoded streamers: kursein, hikarai_, warinspanish209, loafylmaoo
- Checks every 2 minutes and pings when streamers go live

### Utility Commands
- `~guide` - View all commands
- `~botinfo` - Bot stats (servers, members, commands)

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
- `rl_profiles` - Linked Tracker.gg profiles (with URL)
- `streams_config` - Stream notification settings
- `afk_users` - AFK status with reason and timestamp
- `pending_ranks` - Pending rank verifications
- `rank_roles` - Tier to role ID mapping

### Hardcoded IDs
- LOG_CHANNEL_ID: 1435009184285589554 (updates/logs)
- ADMIN_ROLE_ID: 1410509859685662781 (pinged for new accounts)
- BUMP_CHANNEL_ID: 1418819741471997982
- BUMP_ROLE_ID: 1436421726727700542
- STREAM_CHANNEL_ID: 1442613254546526298

### Background Tasks
- **Reminder Checker** (1 min) - Sends bump reminders
- **Stream Checker** (2 min) - Monitors Twitch

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

## File Structure
```
├── main.py              # Main bot code (~1400 lines)
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
- Ranks accept both "1" and "I" format (Diamond 1 = Diamond I)
