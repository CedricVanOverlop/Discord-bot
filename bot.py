import discord
from discord.ext import commands
from discord import app_commands
import os
from dotenv import load_dotenv

from utilitaires.Sheet_TFT import TFTSheets
from utilitaires.views import MenuView

load_dotenv()

class TFTBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.all()
        super().__init__(command_prefix='!', intents=intents)
        
        # Instance de TFTSheets
        self.tft = TFTSheets()
    
    async def setup_hook(self):
        """Appelé automatiquement avant on_ready"""
        # Synchronise les commandes slash
        try:
            synced = await self.tree.sync()
            print(f'✅ Synchronisé {len(synced)} commande(s) slash')
        except Exception as e:
            print(f'❌ Erreur de synchronisation : {e}')
    
    async def on_ready(self):
        print(f'✅ {self.user} est connecté!')
        print(f'📋 Compos chargées : {", ".join(self.tft.get_all_compos())}')


# Initialise le bot
bot = TFTBot()


# ========== COMMANDES SLASH ==========

@bot.tree.command(name="tft", description="Menu principal TFT")
async def tft_menu(interaction: discord.Interaction):
    """Affiche le menu principal avec les boutons"""
    view = MenuView(bot.tft)
    
    embed = discord.Embed(
        title="🎮 Menu TFT",
        description="Clique sur un bouton pour accéder aux informations",
        color=discord.Color.blue()
    )
    embed.set_footer(text="Les formulaires s'ouvriront automatiquement")
    
    await interaction.response.send_message(embed=embed, view=view)


@bot.tree.command(name="liste", description="Liste toutes les compos disponibles")
async def liste(interaction: discord.Interaction):
    """Affiche la liste de toutes les compos"""
    compos = bot.tft.get_all_compos()
    
    if not compos:
        await interaction.response.send_message(
            "❌ Aucune compo chargée. Vérifie ton fichier `compos.json`",
            ephemeral=True
        )
        return
    
    compos_text = "\n".join([f"• **{c}**" for c in compos])
    
    embed = discord.Embed(
        title="📋 Compos disponibles",
        description=compos_text,
        color=discord.Color.green()
    )
    embed.set_footer(text=f"{len(compos)} compo(s) disponible(s)")
    
    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="help_tft", description="Affiche l'aide du bot")
async def help_tft(interaction: discord.Interaction):
    """Affiche l'aide avec toutes les commandes"""
    embed = discord.Embed(
        title="🤖 Aide - TFT Bot",
        description="Voici toutes les commandes disponibles :",
        color=discord.Color.blue()
    )
    
    embed.add_field(
        name="/tft",
        value="Ouvre le menu principal avec les boutons interactifs",
        inline=False
    )
    embed.add_field(
        name="/liste",
        value="Affiche toutes les compos disponibles",
        inline=False
    )
    embed.add_field(
        name="/help_tft",
        value="Affiche cette aide",
        inline=False
    )
    
    embed.add_field(
        name="📊 Fonctionnalités",
        value=(
            "• **Compo** : Stats générales d'une compo\n"
            "• **Build** : Items pour un carry\n"
            "• **Artefact** : Artefacts pour un carry\n"
            "• **Radiant** : Items radiants pour un carry\n"
            "• **Conditions** : Toutes les conditions d'une compo"
        ),
        inline=False
    )
    
    embed.set_footer(text="Utilise /tft pour commencer !")
    
    await interaction.response.send_message(embed=embed)

# ========== LANCEMENT DU BOT ==========

if __name__ == "__main__":
    bot.run(os.getenv("DISCORD_TOKEN"))