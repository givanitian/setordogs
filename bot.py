import discord
from discord import app_commands
from discord.ext import commands
import json
import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")
GUILD_ID = int(os.getenv("GUILD_ID"))
DATA_FILE = "data.json"

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

def load_data():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

@bot.event
async def on_ready():
    guild = discord.Object(id=GUILD_ID)
    await bot.tree.sync(guild=guild)
    print(f"Bot online sebagai {bot.user}")

# ===== /send =====
@bot.tree.command(name="send", description="Kirim ID dan Password", guild=discord.Object(id=GUILD_ID))
async def send(interaction: discord.Interaction):
    await interaction.response.send_message("Masukan ID:", ephemeral=True)

    def check(m):
        return m.author == interaction.user and m.channel == interaction.channel

    id_msg = await bot.wait_for("message", check=check)
    user_id = id_msg.content

    await interaction.followup.send("Masukan Password:", ephemeral=True)
    pass_msg = await bot.wait_for("message", check=check)
    password = pass_msg.content

    data = load_data()
    data.append({"id": user_id, "password": password})
    save_data(data)

    await interaction.followup.send("✅ ID & Password berhasil disimpan", ephemeral=True)

# ===== /id =====
@bot.tree.command(name="id", description="Lihat semua ID & Password", guild=discord.Object(id=GUILD_ID))
async def show_id(interaction: discord.Interaction):
    data = load_data()
    if not data:
        await interaction.response.send_message("Data kosong", ephemeral=True)
        return

    text = ""
    for i, d in enumerate(data, 1):
        text += f"{i}. ID: {d['id']} | Password: {d['password']}\n"

    await interaction.response.send_message(text, ephemeral=True)

# ===== /config =====
@bot.tree.command(name="config", description="Edit atau hapus ID", guild=discord.Object(id=GUILD_ID))
@app_commands.describe(
    action="edit / delete",
    user_id="ID yang ingin diubah",
    new_password="Password baru (jika edit)"
)
async def config(
    interaction: discord.Interaction,
    action: str,
    user_id: str,
    new_password: str = None
):
    data = load_data()
    index = next((i for i, d in enumerate(data) if d["id"] == user_id), None)

    if index is None:
        await interaction.response.send_message("❌ ID tidak ditemukan", ephemeral=True)
        return

    if action.lower() == "delete":
        data.pop(index)
        save_data(data)
        await interaction.response.send_message("🗑️ ID berhasil dihapus", ephemeral=True)

    elif action.lower() == "edit":
        if not new_password:
            await interaction.response.send_message("Password baru wajib diisi", ephemeral=True)
            return
        data[index]["password"] = new_password
        save_data(data)
        await interaction.response.send_message("✏️ Password berhasil diubah", ephemeral=True)

    else:
        await interaction.response.send_message("Action harus edit atau delete", ephemeral=True)

bot.run(TOKEN)
