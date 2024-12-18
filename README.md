# Ezzer's Counting Bot

Ezzer's Counting Bot is a user-friendly bot for managing counting activities in Discord servers. Follow this guide to set it up and host it on your PC easily.

---

## Getting Started

### 1. Install Python
1. Download and install Python (version 3.8 or higher) from [python.org](https://www.python.org/).
2. During installation, **check the box that says "Add Python to PATH"**.
3. After installation, open a terminal or command prompt and type:
`python --version`
If Python is installed correctly, it will show the Python version.

---

### 2. Download the Bot Files
1. Go to the [CountingBot GitHub Repository](https://github.com/ezzer0307/CountingBot).
2. Click the green **"Code"** button and select **"Download ZIP"**.
3. Extract the ZIP file to a folder on your computer.

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
`json
{
    "token": "YOUR_BOT_TOKEN_HERE"
}`
3. Save your file

---

### 7. Restart The Bot
1. Restart the bot by running the file again.
2. The bot is now ready to use in your Discord server!

---

## How to Use the Bot
### Accessing the Dashboard
1. Use the `/dashboard` command in your Discord server to open the bot's control panel.
2. From the dropdown menu, you can:
- **Modules**: Toggle and configure the bot's features.
- **Settings**: Manage counting roles, channels, and values.
- **Debug**: Get troubleshooting information.

---

### Troubleshooting
If you encounter issues:

1. Ensure Python and discord.py are installed correctly.
2. Check that your bot token is pasted correctly in config.json.
3. Verify the bot has permissions in your server (e.g., Manage Messages).
4. Use `/debug` if your bot isn't working properly.

---

## Source Code
Ezzer's Counting Bot is open-source! Feel free to explore and contribute: [GitHub Repository](https://github.com/ezzer0307/CountingBot)

---

Enjoy using CountingBot! 🚀

---

### Links
[Patreon](https://patreon.com/ezzer0307)
[Discord Server](https://discord.gg/SSxwePn9)
