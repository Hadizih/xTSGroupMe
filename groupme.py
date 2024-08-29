import discord
from discord import ui, app_commands
from discord.ext import commands
from dotenv import load_dotenv
from datetime import datetime
import csv
import os

load_dotenv()
character_data = {}
registration_open = False
CHANNEL_ID = os.getenv("CHANNEL_ID")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Bot ist eingeloggt als {bot.user}")
    # Synchronize slash commands
    try:
        synced = await bot.tree.sync()
        print(f"Slash-Commands synchronisiert: {len(synced)} Commands")
    except Exception as e:
        print(f"Fehler bei der Synchronisation der Slash-Commands: {e}")

# Modal for class selection
class CharacterClassView(ui.View):
    def __init__(self):
        super().__init__()
        

    @ui.select(placeholder="Wähle deine Klasse...", options=[
        discord.SelectOption(label="Nekromant", emoji="🧟", value="Nekromant"),
        discord.SelectOption(label="Barbar", emoji="⚔️", value="Barbar"),
        discord.SelectOption(label="Zauberer", emoji="🔮", value="Zauberer"),
        discord.SelectOption(label="Jäger", emoji="🏹", value="Jäger"),
        discord.SelectOption(label="Druide", emoji="🐺", value="Druide")
    ])
    async def class_select_callback(self, interaction: discord.Interaction, select: ui.Select):
        selected_class = select.values[0]
        await interaction.response.send_message("Bist du ein Bosskiller?", view=BosskillerView(selected_class), ephemeral=True)

# Modal for bosskiller selection
class BosskillerView(ui.View):
    def __init__(self, selected_class):
        super().__init__()
        self.selected_class = selected_class

    @ui.select(placeholder="Bist du ein Bosskiller?", options=[
        discord.SelectOption(label="Ja", emoji="✅", value="Ja"),
        discord.SelectOption(label="Nein", emoji="❌", value="Nein")
    ])
    async def bosskiller_select_callback(self, interaction: discord.Interaction, select: ui.Select):
        bosskiller = select.values[0]
        await interaction.response.send_modal(CharacterRegistration(self.selected_class, bosskiller))

# Modal for character registration
class CharacterRegistration(ui.Modal, title="Community Run Anmeldung"):
    def __init__(self, selected_class, bosskiller, twitch_name="", level="", favorite_boss="egal"):
        super().__init__()
        self.selected_class = selected_class
        self.bosskiller = bosskiller

        self.twitch_name = ui.TextInput(label="Twitch Name", default=twitch_name, placeholder="Twitch Name")
        self.level = ui.TextInput(label="Level (*muss zwischen 1 und 100 liegen)", default=level, placeholder="Zwischen 1 und 100")
        self.favorite_boss = ui.TextInput(label="Welchen Boss möchtest du am liebsten farmen?", default=favorite_boss, required=False, placeholder="UberHadi")

        self.add_item(self.twitch_name)
        self.add_item(self.level)
        self.add_item(self.favorite_boss)

    async def on_submit(self, interaction: discord.Interaction):

        # Check if level is between 1 and 100
        try:
            if not 1 <= int(self.level.value) <= 100:
                await interaction.response.send_modal(CharacterRegistration(self.selected_class, self.bosskiller, self.twitch_name.value, self.level.value, self.favorite_boss.value))
                await interaction.followup.send_message("Das Level muss zwischen 1 und 100 liegen. Bitte korrigiere deine Eingabe.", ephemeral=True)
                return
        except ValueError:
            await interaction.response.send_modal(CharacterRegistration(self.selected_class, self.bosskiller, self.twitch_name.value, self.level.value, self.favorite_boss.value))
            await interaction.followup.send_message("Das Level muss zwischen 1 und 100 liegen. Bitte korrigiere deine Eingabe.", ephemeral=True)
            return
        
        # Save data to character_data
        character_data[interaction.user.id] = {
            "twitch_name": self.twitch_name.value,
            "character_class": self.selected_class,  
            "level": self.level.value,
            "bosskiller": self.bosskiller, 
            "favorite_boss": self.favorite_boss.value
        }
        await interaction.response.send_message("Anmeldung erfolgreich!", ephemeral=True)

# Modal for unregister confirmation
class ConfirmUnregister(ui.Modal, title="Bestätige deine Abmeldung"):
   
    def __init__(self, user_data):
        super().__init__()
        self.user_data = user_data
        self.confirmation = ui.TextInput(label="Gib 'JA' ein, um dich abzumelden.", placeholder="JA", custom_id="confirmation")
        self.add_item(self.confirmation)

    async def on_submit(self, interaction: discord.Interaction):
        if self.confirmation.value.lower() == "ja":
            user_id = interaction.user.id
            if user_id in character_data:
                del character_data[user_id]
                await interaction.response.send_message("Du hast dich erfolgreich abgemeldet.", ephemeral=True)
            else:
                await interaction.response.send_message("Du hast keine Anmeldung, die gelöscht werden könnte.", ephemeral=True)
        else:
            await interaction.response.send_message("Du hast dich NICHT abgemeldet.", ephemeral=True)

    async def on_interaction_check(self, interaction: discord.Interaction) -> bool:
        # Show data
        response_message = (
            f"Twitch Name: {self.user_data['twitch_name']}\n"
            f"Klasse: {self.user_data['character_class']}\n"
            f"Level: {self.user_data['level']}\n"
            f"Bosskiller: {self.user_data['bosskiller']}\n"
            f"Lieblingsboss: {self.user_data['favorite_boss']}\n\n"
            f"Bist du sicher, dass du dich abmelden möchtest?"
        )
        await interaction.response.send_message(response_message, ephemeral=True)
        return False  # Prevents the modal from closing

def save_character_data_to_csv(file_name=""):
    with open(file_name, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        # header
        writer.writerow(["twitch_name", "character_class", "level", "bosskiller", "favorite_boss"])
        
        # save data for each user
        for user_id, user_data in character_data.items():
            writer.writerow([user_data["twitch_name"], user_data["character_class"], 
                             user_data["level"], user_data["bosskiller"], user_data["favorite_boss"]])

# Commands
@bot.command(name="hallo")
async def hello(ctx):
    await ctx.send(f"Hallo, {ctx.author.name}!")

@bot.command(name="groupme")
async def help(ctx):
    response_message = (
        "Slash Commands:\n"
        "/anmelden - Anmeldung für Community Run\n"
        "/abmelden - Melde dich vom Community Run ab\n"
    )
    await ctx.send(response_message)

# Slash commands
@bot.tree.command(name="anmelden", description="Anmeldung für Community Run")
async def register(interaction: discord.Interaction):
    if registration_open == True:
        user_id = interaction.user.id
        if user_id in character_data:
            user_data = character_data[user_id]
            response_message = (
                f"Du bist bereits angemeldet!\n"
                f"Twitch Name: {user_data['twitch_name']}\n"
                f"Klasse: {user_data['character_class']}\n"
                f"Level: {user_data['level']}\n"
                f"Bosskiller: {user_data['bosskiller']}\n"
                f"Lieblingsboss: {user_data['favorite_boss']}"
            )
            await interaction.response.send_message(response_message, ephemeral=True)
        else:
            await interaction.response.send_message("Wähle deine Klasse:", view=CharacterClassView(), ephemeral=True)
    else:
        await interaction.response.send_message("Es ist aktuell keine Community Run Anmeldung geöffnet.", ephemeral=True)
    

@bot.tree.command(name="abmelden", description="Melde dich vom Community Run ab")
async def unregister(interaction: discord.Interaction):
    user_id = interaction.user.id
    if user_id in character_data:
        user_data = character_data[user_id]
        await interaction.response.send_modal(ConfirmUnregister(user_data))
    else:
        await interaction.response.send_message("Du hast keine Anmeldung, die gelöscht werden könnte.", ephemeral=True)

@app_commands.default_permissions(administrator=True)
@bot.tree.command(name="open_registration", description="Öffnet die Anmeldung für den Community Run")
async def open_registration(interaction: discord.Interaction):
    global registration_open
    if registration_open == True:
        await interaction.response.send_message("Es ist bereits eine Anmeldung für die xTheShouter-Community Runs ist geöffnet. Schließe diese zuerst.", ephemeral=True)
        return
    else:
        registration_open = True
        id = int(CHANNEL_ID)
        channel = bot.get_channel(id)
        if channel is None:
            await interaction.response.send_message(f"Fehler: Der Kanal konnte nicht gefunden werden. Bitte überprüfe die Kanal-ID. ID={id}", ephemeral=True)
            return
        user = interaction.user.name
        await channel.send(f"{user} hat die Anmeldung für die xTheShouter-Community Boss Runs geöffnet.")
        await interaction.response.send_message("Die Anmeldung für die xTheShouter-Community Runs ist jetzt geöffnet.", ephemeral=True)

@app_commands.default_permissions(administrator=True)
@bot.tree.command(name="close_registration", description="Schließt die Anmeldung für den Community Run")
async def close_registration(interaction: discord.Interaction):
    global registration_open
    if registration_open == False:
        await interaction.response.send_message("Es sind aktuell keine xTheShouter-Community Runs geöffnet", ephemeral=True)
        return
    else:
        registration_open = False
        file_name = "community-runs-" + datetime.today().strftime("%Y-%m-%d") + ".csv"
        save_character_data_to_csv(file_name=file_name)
        character_data.clear() 
        id = int(CHANNEL_ID)
        user = interaction.user.name
        channel = bot.get_channel(id)
        if channel is None:
            await interaction.response.send_message(f"Fehler: Der Kanal konnte nicht gefunden werden. Bitte überprüfe die Kanal-ID. ID={id}", ephemeral=True)
            return
        await channel.send(f"{user} hat die Anmeldung für die xTheShouter-Community Boss Runs geschlossen.")
        await interaction.response.send_message("Anmeldung geschlossen", file=discord.File(file_name), ephemeral=True)
        os.remove(file_name)

@app_commands.default_permissions(administrator=True)
@bot.tree.command(name="show_registrations", description="Zeigt alle Anmeldungen für den Community Run")
async def show_registration(interaction: discord.Interaction):
    response_message = ""
    if not character_data:
        response_message = "Es sind aktuell keine Anmeldungen vorhanden."  
    else:
        for user_id, user_data in character_data.items():
            response_message += (
                f"Twitch Name: {user_data['twitch_name']}\n"
                f"Klasse: {user_data['character_class']}\n"
                f"Level: {user_data['level']}\n"
                f"Bosskiller: {user_data['bosskiller']}\n"
                f"Bevorzugter Boss: {user_data['favorite_boss']}\n\n"
            )
    await interaction.response.send_message(response_message, ephemeral=True)

@app_commands.default_permissions(administrator=True)
@bot.tree.command(name="save_registrations", description="Speichert die Anmeldungen in einer CSV-Datei")
async def save_registration(interaction: discord.Interaction):
    file_name = "community-runs" + datetime.today().strftime("%Y-%m-%d")+".csv"
    save_character_data_to_csv(file_name=file_name)
    await interaction.response.send_message("Die Anmeldungen wurden erfguitolgreich exportiert", file=discord.File(file_name), ephemeral=True)
    os.remove(file_name)



bot.run(os.getenv("DC_BOT_TOKEN"))