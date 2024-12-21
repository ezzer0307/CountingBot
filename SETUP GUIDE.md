# Ezzer's Counting Bot

Ezzer's Counting Bot is a user-friendly bot for managing counting activities in Discord servers. Follow this guide to set it up and host it on your PC easily.

---

## Directories
### Getting Started
- [Install Python](https://github.com/ezzer0307/CountingBot/blob/main/README.md#1-install-python)
- [Download The Bot Files](https://github.com/ezzer0307/CountingBot/blob/main/README.md#2-download-the-bot-files)
- [Install Required Libraries](https://github.com/ezzer0307/CountingBot/blob/main/README.md#3-install-required-libraries)
- [Create a Discord Bot](https://github.com/ezzer0307/CountingBot/blob/main/README.md#4-create-a-discord-bot)
- [Run the Bot for the First Time](https://github.com/ezzer0307/CountingBot/blob/main/README.md#5-run-the-bot-for-the-first-time)
- [Add Your Bot Token](https://github.com/ezzer0307/CountingBot/blob/main/README.md#6-add-your-bot-token)
- [Restart The Bot](https://github.com/ezzer0307/CountingBot/blob/main/README.md#7-restart-the-bot)
---

## Getting Started

### 1. Install Python
1. Download and install Python (version 3.8 or higher) from [python.org](https://www.python.org/).
2. During installation, **check the box that says "Add Python to PATH"**.
3. After installation, open a terminal or command prompt and type:
`python --version`
4. If Python is installed correctly, it will show the Python version.

---

### 2. Download the Bot Files
1. Go to the [releases](https://github.com/ezzer0307/CountingBot/releases/latest) tab.
2. Click the **Download** link.
3. Place it on your computer.
4. **Warning**: Do not place it inside **Desktop** or **Downloads**. Put it inside a folder in **Documents**.

---

### 3. Install Required Libraries
1. Open a terminal or command prompt in the folder where you extracted the bot files.
- On Windows: Right-click in the folder and select **"Open in Terminal"** or **"Open Command Prompt"**.
2. Install the required library by typing:
`pip install discord.py`
3. Wait for the installation to complete.

---

### 4. Create a Discord Bot
1. Go to the [Discord Developer Portal](https://discord.com/developers/applications).
2. Click **"New Application"** and give your bot a name.
3. Navigate to the **Bot** tab and click **"Add Bot"**.
4. Under the bot settings, copy the **token** (you'll need this in the next step).

---

### 5. Run the Bot for the First Time
1. Go back to the folder where you extracted the bot files.
2. Run the python file
3. A `config.json` file will be created in the same folder.

---

### 6. Add Your Bot Token
1. Open the `config.json` file using a text editor (like Notepad).
2. Paste your bot token in the `token` field:
`"token": "YOUR_BOT_TOKEN_HERE"`
3. Save your file

---

### 7. Restart The Bot
1. Restart the bot by running the file again.
2. The bot is now ready to use in your Discord server!
---
