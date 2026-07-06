# God Bot — Telegram Group Guardian

A self-hosted Telegram moderation bot. Runs 100% on your own VPS — no third-party
API calls for content scanning (NSFW detection runs locally via NudeNet).

## Current features (v1)

- 🚫 **NSFW auto-delete** — scans photos/stickers with a local ML model (NudeNet)
  and deletes anything flagged as nudity. No image ever leaves your server.
- 🔗 **Link filter** — detects and deletes messages containing URLs, `t.me/`
  links, or `@username` mentions.
- 🕒 **Auto-delete timer** — automatically deletes media messages N seconds/
  minutes/hours/days after they're posted, fully configurable per group.
- 🔨 **Moderation** — `/ban`, `/unban`, `/kick`, `/mute`, `/unmute`.
- ⚠️ **Warns** — `/warn`, `/warns`, `/resetwarn`, with an auto-ban/mute at a
  configurable warn limit.
- 🔒 **Locks** — lock specific message types (`links`, `media`, `stickers`,
  `forwards`) so only admins can post them.
- ⚙️ Every feature above is configurable **per group** and stored in SQLite.

Admins are always exempt from all filters/locks so they can't accidentally
lock themselves out.

The code is structured (`bot/handlers/...`) so you can keep adding more
modules later (Notes, Filters-by-keyword, Greetings, Federations, CAPTCHA,
Antiflood, etc.) without touching existing files.

## 1. Create your bot

1. Message [@BotFather](https://t.me/BotFather) on Telegram, send `/newbot`,
   follow the prompts, and copy the token it gives you.
2. In your group, add the bot and promote it to **admin** with at least:
   - Delete messages
   - Ban users
   - Restrict members

## 2. Local setup / test

```bash
git clone <your-repo-url> god_bot
cd god_bot
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
nano .env   # paste your BOT_TOKEN, set OWNER_IDS, etc.

python run.py
```

First run will download the NudeNet ONNX model automatically (a few MB) —
this only happens once, everything after is fully offline.

## 3. Deploy on a VPS (Ubuntu example)

```bash
sudo apt update && sudo apt install -y python3 python3-venv python3-pip git

git clone <your-repo-url> /home/ubuntu/god_bot
cd /home/ubuntu/god_bot
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
nano .env   # fill in BOT_TOKEN etc.
deactivate
```

### Keep it running 24/7 with systemd

```bash
sudo cp god-bot.service.example /etc/systemd/system/god-bot.service
sudo nano /etc/systemd/system/god-bot.service   # fix the User/paths if needed
sudo systemctl daemon-reload
sudo systemctl enable god-bot
sudo systemctl start god-bot

# check logs
sudo journalctl -u god-bot -f
```

## 4. Push to GitHub

```bash
git init
git add .
git commit -m "Initial commit: God Bot v1"
git branch -M main
git remote add origin <your-repo-url>
git push -u origin main
```

`.env` and `data/` (the SQLite DB) are already in `.gitignore` so your bot
token and group data never get pushed.

## Commands reference

| Command | Who | Description |
|---|---|---|
| `/start`, `/help` | anyone | Show help |
| `/settings` | anyone | Show current group config |
| `/nsfwfilter on\|off` | admin | Toggle NSFW auto-delete |
| `/linkfilter on\|off` | admin | Toggle link auto-delete |
| `/setdeletetimer 30s\|10m\|2h\|1d\|off` | admin | Auto-delete media after N time |
| `/warnlimit <n>` | admin | Warns before auto-action |
| `/warnaction ban\|mute` | admin | Action at warn limit |
| `/lock <type>` / `/unlock <type>` | admin | Lock `links`/`media`/`stickers`/`forwards` |
| `/locks` | anyone | List active locks |
| `/ban` `/unban` `/kick` `/mute` `/unmute` | admin | Reply to a user's message |
| `/warn` `/warns` `/resetwarn` | admin (warn/resetwarn) | Reply to a user's message |

## Notes / limitations (be upfront about these)

- NudeNet checks **static images** (photos, static stickers). Videos and
  animated GIFs are not scanned frame-by-frame yet — that needs extracting
  frames with OpenCV, which you can add in `bot/utils/nsfw_detector.py`.
- NudeNet runs on CPU by default; on a very small VPS (512MB–1GB RAM) it may
  be slow. 2GB RAM+ is recommended if NSFW filtering is heavily used.
- This bot only acts in **groups it's an admin in** with the right
  permissions — it will silently skip deleting if it lacks rights.
- SQLite is fine for dozens–hundreds of groups. If you scale to a very large
  number of groups, consider moving to Postgres.

## Roadmap (matches the feature list you screenshotted)

Not yet built, but the modular structure makes each of these a self-contained
addition in `bot/handlers/`: Antiflood, AntiRaid, Approval, Blocklists,
CAPTCHA, Clean Commands/Service, Connections, Federations, Filters (custom
keyword replies), Formatting, Greetings, Import/Export, Languages, Log
Channels, Misc, Notes, Pin, Privacy, Purges, Reports, Rules, Topics, Custom
Instances. Ask and these can be added one module at a time.
