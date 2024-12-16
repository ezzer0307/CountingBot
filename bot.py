import discord
from discord.ext import commands
from discord import app_commands
from discord.ui import View, Select, Button, Modal, TextInput
import json
import os
import asyncio
import aiohttp
import sys
import time
import threading

CONFIG_FILE = "config.json"

# Default configuration
config = {
    "token": None,
    "current_count": 1,
    "counting_channel_id": None,
    "correct_counter_role_id": None,
    "last_counter_id": None,
    "bot_nickname": "Ezzer's Counting",
    "countingrole": "False",
    "spam": "False",
    "embed": "False",
    "nodelete": "False",
    "reposting": "False",
    "webhook": "False",
    "dm": "False",
    "updatenickname": "False",
    "numberformat": "False",
    "typing": "False"
}

if not os.path.isfile(CONFIG_FILE):
    print(f"{CONFIG_FILE} not found. Creating one...")
    with open(CONFIG_FILE, "w") as file:
        json.dump(config, file, indent=4)  # Write JSON with indentation
    print(f"{CONFIG_FILE} created.")


# Load configuration
def load_config():
    global config
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as file:
            config.update(json.load(file))


# Save configuration
def save_config():
    with open(CONFIG_FILE, "w") as file:
        json.dump(config, file, indent=4)


# Initialize configuration
load_config()

# Intents and bot setup
intents = discord.Intents.default()
intents.message_content = True
intents.messages = True
intents.members = True
intents.guilds = True
bot = commands.Bot(command_prefix="!", intents=intents)


# Function to format numbers with commas
def format_number(number):
    return f"{number:,}".replace(",", ",") if config["numberformat"].lower() == "true" else f"{number:,}".replace(",",
                                                                                                                  "")


def emoji(status):
    return "🔘" if status.lower() == "true" else "⚫"


def replaceWord(value, old, new):
    return value.replace(old, new)


def get_menu():
    MODULES = {
        "embed": "Repost messages in an embed.",
        "nodelete": "Don't delete incorrect counts.",
        "reposting": "Repost the message.",
        "spam": "Allow multiple counts in a row.",
        "webhook": "Repost messages using a webhook.",
        "dm": "DM users if they count incorrectly or multiple times.",
        "updatenickname": "Update the bot's nickname with the next count.",
        "countingrole": "Apply a role to the correct counters.",
        "numberformat": "Format numbers with commas (e.g., 1234 → 1,234).",
        "typing": "Make the bot typing in the counting channel when failed to count."
    }
    menu = "**Available Modules:**\n"
    for module, description in MODULES.items():
        menu += f"{emoji(config[module])} **{module.capitalize()}** - {description}\n"
    return menu

async def typing_with_timeout(channel, timeout=4):
    """Show typing indicator for a set timeout in the background."""
    async with channel.typing():  # Starts typing indicator
        await asyncio.sleep(timeout)  # Keep typing indicator active for the specified duration


class SettingsDropdown(Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Set Counting Channel", description="Set the channel for counting."),
            discord.SelectOption(label="Set Current Count", description="Set the current count value."),
            discord.SelectOption(label="Set Counting Role", description="Set the role for correct counters."),
            discord.SelectOption(label="Set Bot Nickname", description="Set the bot's nickname."),
        ]
        super().__init__(placeholder="Select a setting to configure...", options=options)

    async def callback(self, interaction: discord.Interaction):
        selection = self.values[0]
        if selection == "Set Counting Channel":
            view = SetChannelDropdownView(interaction.guild)
            await interaction.response.send_message("Select a counting channel:", view=view, ephemeral=True)
        elif selection == "Set Current Count":
            modal = SetCountModal()
            await interaction.response.send_modal(modal)
        elif selection == "Set Counting Role":
            view = SetRoleDropdownView(interaction.guild)
            await interaction.response.send_message("Select a counting role:", view=view, ephemeral=True)
        elif selection == "Set Bot Nickname":
            modal = SetNicknameModal()
            await interaction.response.send_modal(modal)
        else:
            await interaction.response.send_message("Invalid selection.", ephemeral=True)


class SettingsView(View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(SettingsDropdown())


class SetChannelDropdown(Select):
    def __init__(self, guild):
        # Fetch text channels and ensure they are valid
        channels = [channel for channel in guild.text_channels if channel.permissions_for(guild.me).send_messages]

        # Truncate to a maximum of 25 options as required by Discord
        truncated_channels = channels[:25]

        options = [
            discord.SelectOption(label=channel.name, value=str(channel.id))
            for channel in truncated_channels
        ]

        # Add a fallback option if no valid channels are available
        if not options:
            options = [discord.SelectOption(label="No text channels available", value="none", default=True)]

        super().__init__(placeholder="Choose a channel...", options=options)

    async def callback(self, interaction: discord.Interaction):
        if self.values[0] == "none":
            await interaction.response.send_message(
                "No valid text channels are available to select.", ephemeral=True
            )
            return

        selected_channel_id = int(self.values[0])
        config["counting_channel_id"] = selected_channel_id
        save_config()

        selected_channel = interaction.guild.get_channel(selected_channel_id)
        if selected_channel:
            await interaction.response.send_message(
                f"Counting channel set to {selected_channel.mention}.", ephemeral=True
            )
        else:
            await interaction.response.send_message("An error occurred while setting the channel.", ephemeral=True)

class SetChannelDropdownView(View):
    def __init__(self, guild):
        super().__init__(timeout=None)
        self.add_item(SetChannelDropdown(guild))

class SetRoleDropdown(Select):
    def __init__(self, guild):
        # Fetch roles and truncate to 25 if necessary
        roles = guild.roles[:25]  # Limit to 25 roles
        options = [
            discord.SelectOption(label=role.name, value=str(role.id))
            for role in roles
        ]

        # Add a fallback option if no roles are available
        if not options:
            options = [discord.SelectOption(label="No roles available", value="none", default=True)]

        super().__init__(placeholder="Choose a role...", options=options)

    async def callback(self, interaction: discord.Interaction):
        if self.values[0] == "none":
            await interaction.response.send_message(
                "No roles are available to select.", ephemeral=True
            )
            return

        selected_role_id = int(self.values[0])
        role = interaction.guild.get_role(selected_role_id)
        if not role:
            await interaction.response.send_message("Invalid channel selection.", ephemeral=True)
            return

        config["correct_counter_role_id"] = selected_role_id
        save_config()
        await interaction.response.send_message(
            f"Counting channel set to {role.mention}.", ephemeral=True
        )


class SetRoleDropdownView(View):
    def __init__(self, guild):
        super().__init__(timeout=None)
        self.add_item(SetRoleDropdown(guild))


class SetCountModal(Modal, title="Set Current Count"):
    count = TextInput(label="Current Count", placeholder="Enter the current count", required=True)

    async def on_submit(self, interaction: discord.Interaction):
        try:
            config["current_count"] = int(self.count.value)
            save_config()

            await interaction.response.send_message(
                f"Current count updated to {self.count.value}.", ephemeral=True
            )
        except ValueError:
            await interaction.response.send_message("Invalid input. Please enter a valid number.", ephemeral=True)


class SetNicknameModal(Modal, title="Set Bot Nickname"):
    nickname = TextInput(label="Nickname", placeholder="Enter the new nickname", required=True)

    async def on_submit(self, interaction: discord.Interaction):
        config["bot_nickname"] = self.nickname.value
        save_config()

        try:
            bot_member = interaction.guild.get_member(bot.user.id)
            if bot_member:
                for guild in bot.guilds:
                    update_bot_nickname(guild, config["current_count"] + 1)
                await interaction.response.send_message(
                    f"Bot nickname updated to {config['bot_nickname']}.", ephemeral=True
                )
        except discord.Forbidden:
            await interaction.response.send_message("I lack permissions to change my nickname.", ephemeral=True)

class ModuleMenu(View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(ModuleDropdown())

    async def send_status(self, interaction):
        description = "\n".join(
            f"{emoji(config.get(module, 'False'))} {module.capitalize()} - {details['description']}"
            for module, details in MODULES.items()
        )
        embed = discord.Embed(
            title="Available Modules",
            description=description,
            colour=discord.Color.dark_embed()
        )
        await interaction.response.edit_message(embed=embed, view=self)


class ModuleDropdown(Select):
    def __init__(self):
        options = [
            discord.SelectOption(label=module.capitalize(), description=details["description"])
            for module, details in MODULES.items()
        ]
        super().__init__(placeholder="Choose a module to configure...", options=options)

    async def callback(self, interaction: discord.Interaction):
        module_name = self.values[0].lower()
        incompatible = MODULES[module_name]["incompatible_with"]
        active_incompatible = [mod for mod in incompatible if config.get(mod, "False").lower() == "true"]
        current_status = config.get(module_name, "False").lower() == "true"

        embed = discord.Embed(
            content="",
            title=f"Module: {module_name.capitalize()}",
            description=(
                f"**Description:** {MODULES[module_name]['description']}\n"
                f"**Current Status:** {'Enabled' if current_status else 'Disabled'}\n\n"
                f"**Incompatible Modules:** {', '.join(incompatible) if incompatible else 'None'}\n"
                f"**Active Incompatibilities:** {', '.join(active_incompatible) if active_incompatible else 'None'}"
            ),
            colour=discord.Color.dark_embed()
        )
        view = ModuleToggleView(module_name)
        await interaction.response.edit_message(embed=embed, view=view)


class ModuleToggleView(View):
    def __init__(self, module_name):
        super().__init__(timeout=None)
        self.module_name = module_name
        self.add_item(ModuleToggleButton(module_name))
        self.add_item(GoBackButton())


class ModuleToggleButton(Button):
    def __init__(self, module_name):
        current_status = config.get(module_name, "False").lower() == "true"
        label = "Module is enabled (click to disable)" if current_status else "Module is disabled (click to enable)"
        super().__init__(label=label, style=discord.ButtonStyle.green if current_status else discord.ButtonStyle.red)
        self.module_name = module_name

    async def callback(self, interaction: discord.Interaction):
        current_status = config.get(self.module_name, "False").lower() == "true"
        incompatible = MODULES[self.module_name]["incompatible_with"]
        active_incompatible = [mod for mod in incompatible if config.get(mod, "False").lower() == "true"]

        if not current_status and active_incompatible:
            await interaction.response.send_message(
                f"Cannot enable **{self.module_name.capitalize()}** because the following incompatible modules are active:\n"
                f"{', '.join(active_incompatible)}",
                ephemeral=True
            )
            return

        config[self.module_name] = "True" if not current_status else "False"
        save_config(config)
        await interaction.message.edit(view=ModuleToggleView(self.module_name))


class GoBackButton(Button):
    def __init__(self):
        super().__init__(label="Go Back", style=discord.ButtonStyle.secondary)

    async def callback(self, interaction: discord.Interaction):
        await ModuleMenu().send_status(interaction)


class ModulesView(View):
    def __init__(self):
        super().__init__(timeout=None)
        options = [
            discord.SelectOption(
                label=module.capitalize(),
                description=description[:100]  # Truncate description if necessary
            )
            for module, description in {
                "Embed": "Repost messages in an embed.",
                "Nodelete": "Don't delete incorrect counts.",
                "Reposting": "Repost the message.",
                "Spam": "Allow multiple counts in a row.",
                "Webhook": "Repost messages using a webhook.",
                "DM": "DM users if they count incorrectly or multiple times.",
                "Update Nickname": "Update the bot's nickname with the next count.",
                "Counting Role": "Apply a role to the correct counters.",
                "Number Format": "Format numbers with commas (e.g., 1234 → 1,234).",
                "Typing": "Make the bot typing in the counting channel when failed to count."
            }.items()
        ]
        self.add_item(Select(
            placeholder="Choose a module to configure...",
            options=options,
            custom_id="modules_dropdown"
        ))


class ModuleDetailsView(View):
    def __init__(self, module_name, is_enabled, incompatible_modules):
        super().__init__(timeout=None)
        toggle_label = f"Module is {'enabled' if is_enabled else 'disabled'} (click to {'disable' if is_enabled else 'enable'})"
        toggle_style = discord.ButtonStyle.green if is_enabled else discord.ButtonStyle.red

        # Add buttons
        self.add_item(Button(label=toggle_label, custom_id=f"toggle_{module_name.lower()}", style=toggle_style))
        self.add_item(Button(label="Go Back", custom_id="go_back", style=discord.ButtonStyle.grey))

        self.module_name = module_name
        self.is_enabled = is_enabled
        self.incompatible_modules = incompatible_modules


# Function to update the bot's nickname in the guild
async def update_bot_nickname(guild, next_count):
    if config["updatenickname"].lower() == "true":
        try:
            bot_member = guild.get_member(bot.user.id)
            if bot_member:
                formatted_number = format_number(next_count)
                new_nickname = (f"[{formatted_number if config["numberformat"].lower() == "true" else next_count}] " + config["bot_nickname"]) if config[
                    "counting_channel_id"] else f"[NO CHANNEL] {config["bot_nickname"]}"
                await bot_member.edit(nick=new_nickname)
        except discord.Forbidden:
            print("Bot lacks permissions to change its nickname.")
        except discord.HTTPException as e:
            print(f"Failed to update bot nickname: {e}")


@bot.event
async def on_ready():
    try:
        print("Syncing commands...")
        synced = await bot.tree.sync()
        print(f"\n{len(synced)} commands synced!")
    except Exception as e:
        print(f"Error syncing commands: {e}")
    print(f"Bot is ready. Logged in as {bot.user}")
    for guild in bot.guilds:
        if config["current_count"] is not None:
            await update_bot_nickname(guild, config["current_count"] + 1)


@bot.event
async def on_message(message):
    if message.author.bot:
        return

    if config["counting_channel_id"]:
        pass
    else:
        for guild in bot.guilds:
            await update_bot_nickname(guild, config["current_count"] + 1)

    if config["counting_channel_id"] and message.channel.id == config["counting_channel_id"]:
        if config["spam"].lower() == "false":  # Prevent double counting if enabled
            if message.author.id == config["last_counter_id"]:
                await message.delete()
                if config["dm"].lower() == "true":
                    await message.author.send(
                        f"You have already counted in <#{config["counting_channel_id"]}>! Wait for someone else to count before you count again..")
                return

        current_count = config["current_count"]
        next_count = current_count + 1
        formatted_number = format_number(next_count)
        repost_message = formatted_number if config['numberformat'].lower() == "true" else next_count
        if message.content in {str(next_count), formatted_number}:
            if config["webhook"].lower() == "true":
                await message.delete()

                # Create or fetch the webhook
                webhook = None
                webhooks = await message.channel.webhooks()
                for hook in webhooks:
                    if hook.name == "CountingBot":
                        webhook = hook
                        break

                if not webhook:
                    webhook = await message.channel.create_webhook(name="CountingBot")

                await webhook.send(
                    repost_message,
                    username=message.author.display_name,
                    avatar_url=message.author.avatar.url if message.author.avatar else None,
                )
            elif config["reposting"].lower() == "true":
                await message.delete()
                await message.channel.send(f"<@{message.author.id}>: {repost_message}")

            elif config["embed"].lower() == "true":
                await message.delete()
                embed = discord.Embed(description=f"<@{message.author.id}>: {repost_message}")
                await message.channel.send(embed=embed)

            if config["countingrole"].lower() == "true":  # Check if counting role is enabled
                if config["correct_counter_role_id"]:
                    role = message.guild.get_role(config["correct_counter_role_id"])
                    if role:
                        for member in role.members:
                            await member.remove_roles(role)
                        await message.author.add_roles(role)

            config["last_counter_id"] = message.author.id
            config["current_count"] = next_count
            save_config()

            # Update bot's nickname with the next count
            await update_bot_nickname(message.guild, config["current_count"] + 1)
        elif config["nodelete"].lower() == "false":
            if config["typing"].lower() == "true":
                asyncio.create_task(typing_with_timeout(message.channel, timeout=4))
            await message.delete()
            if config["dm"].lower() == "true":
                await message.author.send(f"That was not the correct number! The next count is **{formatted_number}**.")
            await message.channel.trigger_typing()
    else:
        await bot.process_commands(message)


@bot.event
async def on_message_delete(message):
    # Ensure the deletion is from the counting channel
    if config["counting_channel_id"] and message.channel.id == config["counting_channel_id"]:
        # Check if the deleted message matches the last valid count
        current_count = config["current_count"]
        formatted_number = format_number(current_count)

        if message.content in {str(current_count), formatted_number}:
            # Notify the channel about the deletion
            await message.channel.send(
                f"<@{config["last_counter_id"]}>: {formatted_number}"
            )
            # Optional: Prevent further counting by adding a cooldown or reset logic
            # Uncomment the line below if you'd like to enforce a reset
            # config["current_count"] -= 1  # Step back the count if needed
            save_config()


@bot.event
async def on_interaction(interaction: discord.Interaction):
    if "custom_id" not in interaction.data:
        return

    custom_id = interaction.data["custom_id"]

    if custom_id == "modules_dropdown":
        selected_module = replaceWord(interaction.data["values"][0], " ", "")

        # Define module data
        modules_data = {
            "embed": {"enabled": config["embed"].lower() == "true", "incompatible": ["Reposting", "Webhook"],
                      "description": "Repost messages in an embed", "name": "Embed"},
            "nodelete": {"enabled": config["nodelete"].lower() == "true", "incompatible": ["DM", "Typing"],
                         "description": "No messages get deleted, even if you fail to count.", "name": "No Delete"},
            "reposting": {"enabled": config["reposting"].lower() == "true", "incompatible": ["Embed", "Webhook"],
                          "description": "Repost the message", "name": "Repost"},
            "spam": {"enabled": config["spam"].lower() == "true", "incompatible": [],
                     "description": "Allow people to count multiple times in a row.", "name": "Spam"},
            "webhook": {"enabled": config["webhook"].lower() == "true", "incompatible": ["Embed", "Reposting"],
                        "description": "Repost the message in a webhook", "name": "Webhook"},
            "dm": {"enabled": config["dm"].lower() == "true", "incompatible": ["Nodelete"],
                   "description": "DM the user if they counted incorrectly or counted multiple times.", "name": "DM"},
            "updatenickname": {"enabled": config["updatenickname"].lower() == "true", "incompatible": [],
                               "description": "Update the bot's nickname with the next count",
                               "name": "Update Nickname"},
            "countingrole": {"enabled": config["countingrole"].lower() == "true", "incompatible": [],
                             "description": "Apply a role to the correct counters", "name": "Counting Role"},
            "numberformat": {"enabled": config["numberformat"].lower() == "true", "incompatible": [],
                             "description": "Apply comas when reposting, webhooks or embed is enabled. If enabled, 1234 will be formatted to 1,234",
                             "name": "Number Format"},
            "typing": {"enabled": config["typing"].lower() == "true", "incompatible": ["Nodelete"],
                       "description": "Make the bot typing in the counting channel when failed to count.",
                       "name": "Typing"},
        }

        module_info = modules_data[selected_module.lower()]
        module_name = module_info["name"]
        is_enabled = module_info["enabled"]
        incompatible_modules = module_info["incompatible"]
        description = module_info["description"]

        # Edit message to show module details
        embed = discord.Embed(title=f"Module Information • {module_name}",
                              description=f"{description}\nIncompatible modules: `{', '.join(incompatible_modules) if incompatible_modules else 'None'}`")
        await interaction.response.edit_message(
            content="",
            embed=embed,
            view=ModuleDetailsView(selected_module, is_enabled, incompatible_modules),
        )

    elif custom_id.startswith("toggle_"):
        module_name = custom_id.replace("toggle_", "").capitalize()

        # Check incompatible modules
        modules_data = {
            "embed": {"enabled": config["embed"].lower() == "true", "incompatible": ["Reposting", "Webhook"]},
            "nodelete": {"enabled": config["nodelete"].lower() == "true", "incompatible": ["DM", "Typing"]},
            "reposting": {"enabled": config["reposting"].lower() == "true", "incompatible": ["Embed", "Webhook"]},
            "spam": {"enabled": config["spam"].lower() == "true", "incompatible": []},
            "webhook": {"enabled": config["webhook"].lower() == "true", "incompatible": ["Embed", "Reposting"]},
            "dm": {"enabled": config["dm"].lower() == "true", "incompatible": ["Nodelete"]},
            "updatenickname": {"enabled": config["updatenickname"].lower() == "true", "incompatible": []},
            "countingrole": {"enabled": config["countingrole"].lower() == "true", "incompatible": []},
            "numberformat": {"enabled": config["numberformat"].lower() == "true", "incompatible": []},
            "typing": {"enabled": config["typing"].lower() == "true", "incompatible": ["Nodelete"]}
        }
        incompatible = [mod for mod in modules_data[module_name.lower()]["incompatible"] if
                        modules_data[mod.lower()]["enabled"]]

        if incompatible:
            await interaction.response.send_message(
                content=(
                    f"Cannot enable **{module_name}** because the following incompatible modules are active:\n"
                    f"**{', '.join(incompatible)}**."
                ),
                ephemeral=True
            )
            return

        # Toggle module state and save
        config[module_name.lower()] = "false" if config[module_name.lower()] == "true" else "true"
        save_config()

        # Refresh module details
        is_enabled = config[module_name.lower()] == "true"
        await interaction.response.edit_message(
            content="",
            view=ModuleDetailsView(module_name, is_enabled, modules_data[module_name.lower()]["incompatible"]),
        )

    elif custom_id == "go_back":
        desc = get_menu()
        embed = discord.Embed(description=desc)
        await interaction.response.edit_message(
            content="",
            embed=embed,
            view=ModulesView(),
        )

# Slash command: Help Command
@bot.tree.command(name="help", description="Gets all the available help commands.")
async def help(interaction: discord.Interaction):
    embed = discord.Embed(
        title="",
        description=(
            "## List of commands\n"
            "### `>` </debug:1311451017379844116> - Debug your bot"
            "### `>` </modules:1309811694557462571> - Gets a list of available modules"
            "### `>` </settings:1318221863939211346> - Manage your bot's settings."
            "### `>` </help:1307533852264239136> - Gets a list of available help commands."
        ),
        colour=discord.Color.dark_embed()
    )
    await interaction.response.send_message(
        embed=embed, ephemeral=True  # Correct usage: embed is passed as a keyword argument
    )


# Slash command: Debug Command
@bot.tree.command(name="debug", description="Debug your bot")
@app_commands.checks.has_permissions(administrator=True)
async def debug(interaction: discord.Interaction):
    embed = discord.Embed(
        title="",
        description=(
            "# Debug\n"
            "\n"
            "## Modules\n"
            f"### {emoji(config['embed'])} **Embed**\n"
            f"### {emoji(config['nodelete'])} **Nodelete**\n"
            f"### {emoji(config['reposting'])} **Reposting**\n"
            f"### {emoji(config['spam'])} **Spam**\n"
            f"### {emoji(config['webhook'])} **Webhook**\n"
            f"### {emoji(config['dm'])} **DM**\n"
            f"### {emoji(config['updatenickname'])} **Update Nickname**\n"
            f"### {emoji(config['countingrole'])} **Counting Role**\n"
            f"### {emoji(config['numberformat'])} **Number Format**\n"
            f"### {emoji(config['typing'])} **Typing**\n"
            "### ⚫ = Disabled, 🔘 = Enabled\n"
            "\n"
            "## Settings\n"
            "### `>` Counting Channel: " + f"<#{config["counting_channel_id"]}>\n" if config["counting_channel_id"] else "None\n"
            f"### `>` Current Count: {config["current_count"]}\n"
            "### `>` Counting Role: " + f"<@&{config["correct_counter_role_id"]}>\n" if config["correct_counter_role_id"] else "None\n"
            f"### `>` Bot Nickname: **{config["bot_nickname"]}**\n"
            f"### `>` Last Counter: " + f"<@{config["last_counter_id"]}>\n" if config["last_counter_id"] else "None\n"
        ),
        colour=discord.Color.dark_embed()
    )
    await interaction.response.send_message(
        embed=embed, ephemeral=True  # Correct usage: embed is passed as a keyword argument
    )

@bot.tree.command(name="modules", description="Configures all of your modules.")
async def modules(interaction: discord.Interaction):
    embed = discord.Embed(
        title="Modules Configuration",
        description=get_menu(),
        colour=discord.Color.dark_embed()
    )
    await interaction.response.send_message(
        embed=embed,
        view=ModulesView(),
        ephemeral=True
    )

@bot.tree.command(name="settings", description="Manage bot settings.")
@app_commands.checks.has_permissions(administrator=True)
async def settings(interaction: discord.Interaction):
    """Command to open the settings menu."""
    view = SettingsView()
    await interaction.response.send_message("Select a setting to configure:", view=view, ephemeral=True)

async def command_error(interaction: discord.Interaction, error):
    if isinstance(error, app_commands.MissingPermissions):
        await interaction.response.send_message(
            "You do not have permission to use this command.", ephemeral=True
        )
    else:
        await interaction.response.send_message(
            "An error occurred while executing the command.", ephemeral=True
        )


# Run the bot with the token from config.json
if config["token"]:
    bot.run(config["token"])
else:
    print("Error: No token found in config.json.")
