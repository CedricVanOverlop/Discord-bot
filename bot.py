import discord
from discord.ext import commands
from discord import app_commands
import os
from dotenv import load_dotenv
from datetime import datetime

# Importation des modules internes
from utilitaires.interfaces import MainMenu, create_help_embed
from utilitaires.compo import compo_cmd, resume_compo_cmd
from utilitaires.artefacts import artefact_cmd, resume_artefact_cmd, resume_artefact_perso_cmd
from utilitaires.parties import mesgames_cmd,autresgames_cmd, statsaugment_cmd
from utilitaires.conditions import condition_cmd, resume_conditions_cmd
from utilitaires.events_manager import EventManager



load_dotenv()

class TFTBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.all()
        super().__init__(command_prefix='!', intents=intents)
    
    async def on_ready(self):
        print(f'{self.user} est connecté!')
        try:
            synced = await self.tree.sync()
            print(f'Synchronisé {len(synced)} commande(s)')
        except Exception as e:
            print(f'Erreur de synchronisation : {e}')


bot = TFTBot()

# ----- Slash Command Menu -----
@bot.tree.command(name='menu', description='Affiche le menu principal du TFT Bot')
async def menu(interaction: discord.Interaction):
    embed = discord.Embed(
        title="🎮 TFT Stats Manager",
        description="Utilisez les boutons ci-dessous pour gérer vos statistiques TFT",
        color=0x00D9FF
    )
    embed.set_footer(text="Bot créé pour le suivi TFT high-level")
    
    view = MainMenu()
    await interaction.response.send_message(embed=embed, view=view)


# ===== COMMANDES TEXTES RÉIMPORTÉES =====

bot.command(name="compo")(compo_cmd)
bot.command(name="resume_compo")(resume_compo_cmd)

bot.command(name="artefact")(artefact_cmd)
bot.command(name="resume_artefact")(resume_artefact_cmd)
bot.command(name="resume_artefact_perso")(resume_artefact_perso_cmd)

bot.command(name="mesgames")(mesgames_cmd)
bot.command(name="autresgames")(autresgames_cmd)
bot.command(name="statsaugment")(statsaugment_cmd)

bot.command(name="condition")(condition_cmd)
bot.command(name="resume_conditions")(resume_conditions_cmd)


# ----- Commande HELP -----
@bot.command(name='help_tft')
async def help_command(ctx):
    embed = create_help_embed(ctx.author)
    await ctx.send(embed=embed)

@bot.command(name="fullresume")
async def fullresume(ctx):
    guild = ctx.guild

    # ==========================
    #      SALON RÉSUMÉ GLOBAL
    # ==========================
    category_resume = discord.utils.get(guild.categories, name="Résumé")
    if not category_resume:
        category_resume = await guild.create_category("Résumé")

    summary_channel = discord.utils.get(category_resume.channels, name="résumé-global")
    if not summary_channel:
        summary_channel = await category_resume.create_text_channel("résumé-global")

    # ==========================
    #      TABLEAUX
    # ==========================
    compos_rows = []      # [Nom, Avg, WinRate, Top4, Patch]
    artefacts_rows = []   # [Nom, Perso, Avg, Delta, Patch]
    conditions_rows = []  # [Compo, Condition, Avg, Delta]

    # ==========================
    #      COMPOS
    # ==========================
    compo_cat = discord.utils.get(guild.categories, name="compo")
    if compo_cat:
        for chan in compo_cat.channels:
            async for msg in chan.history(limit=50):
                if msg.author != ctx.bot.user or not msg.embeds:
                    continue

                embed = msg.embeds[0]
                fields = {f.name.lower(): f.value for f in embed.fields}

                nom = embed.title.replace("📊 Compo ", "").upper()
                avg = fields.get("placement moyen", "?")
                winrate = fields.get("winrate", fields.get("win rate", "?"))
                top4 = fields.get("top4 rate", fields.get("top 4 rate", "?"))
                patch = fields.get("patch", "?")

                compos_rows.append([nom, avg, winrate, top4, patch])
                break  # un seul embed par compo

    # ==========================
    #      ARTEFACTS
    # ==========================
    arte_cat = discord.utils.get(guild.categories, name="artefact")
    if arte_cat:
        for chan in arte_cat.channels:
            async for msg in chan.history(limit=50):
                if msg.author != ctx.bot.user or not msg.embeds:
                    continue

                embed = msg.embeds[0]
                fields = {f.name.lower(): f.value for f in embed.fields}

                nom = embed.title.replace("🪄 Artefact ", "").upper()
                perso = fields.get("personnage", "?")
                avg = fields.get("avg", "?")
                delta = fields.get("delta", "?")
                patch = fields.get("patch", "?")

                artefacts_rows.append([nom, perso, avg, delta, patch])
                break  # un embed par artefact

    # ==========================
    #      CONDITIONS
    # ==========================
    cond_cat = discord.utils.get(guild.categories, name="Conditions")  # <<< majuscule ici
    if cond_cat:
        for chan in cond_cat.channels:
            # on attend des noms du type "conditions-akali"
            compo_name = chan.name
            if compo_name.startswith("conditions-"):
                compo_name = compo_name.replace("conditions-", "", 1)
            compo_name_display = compo_name.upper()

            async for msg in chan.history(limit=100):
                if msg.author != ctx.bot.user or not msg.embeds:
                    continue

                embed = msg.embeds[0]
                title_lower = embed.title.lower()

                # on ignore le premier message "Stats de base - ..."
                if "stats de base" in title_lower:
                    continue

                fields = {f.name.lower(): f.value for f in embed.fields}
                placement_str = fields.get("placement avec condition", None)
                diff_str = fields.get("différence", None)

                if not placement_str or not diff_str:
                    continue

                # Nettoyage des nombres
                def to_float(s: str):
                    s = s.replace("**", "").replace(",", ".").strip()
                    try:
                        return float(s)
                    except ValueError:
                        return None

                placement_val = to_float(placement_str)
                diff_val = to_float(diff_str)

                if placement_val is not None:
                    avg_display = f"{placement_val:.2f}"
                else:
                    avg_display = placement_str

                if diff_val is not None:
                    delta_display = f"{diff_val:+.2f}"
                else:
                    delta_display = diff_str

                conditions_rows.append([
                    compo_name_display,
                    embed.title,   # le titre contient l'emoji + nom de condition
                    avg_display,
                    delta_display
                ])

    # ==========================
    #      FONCTION TABLE TEXTE
    # ==========================
    def make_table(headers, rows):
        if not rows:
            return "_Aucune donnée trouvée._\n"

        # largeurs de colonne
        col_widths = [len(h) for h in headers]
        for row in rows:
            for i, cell in enumerate(row):
                col_widths[i] = max(col_widths[i], len(str(cell)))

        # ligne header
        header_line = "| " + " | ".join(
            str(headers[i]).ljust(col_widths[i]) for i in range(len(headers))
        ) + " |"

        # ligne de séparation
        sep_line = "| " + " | ".join("-" * col_widths[i] for i in range(len(headers))) + " |"

        # lignes de données
        row_lines = []
        for row in rows:
            row_lines.append(
                "| " + " | ".join(str(row[i]).ljust(col_widths[i]) for i in range(len(headers))) + " |"
            )

        table_text = "\n".join([header_line, sep_line] + row_lines)
        return f"```\n{table_text}\n```\n"

    # ==========================
    #      GÉNÉRATION TEXTES
    # ==========================
    compos_rows.sort(key=lambda r: safe_float(r[1]))       # r[1] = Avg
    artefacts_rows.sort(key=lambda r: safe_float(r[2]))    # r[2] = Avg
    conditions_rows.sort(key=lambda r: safe_float(r[2]))   # r[2] = Avg

    table_compos = make_table(["Nom", "Avg", "WinRate", "Top4", "Patch"], compos_rows)
    table_artefacts = make_table(["Nom", "Perso", "Avg", "Delta", "Patch"], artefacts_rows)
    table_conditions = make_table(["Compo", "Condition", "Avg", "Delta"], conditions_rows)

    # ==========================
    #      MESSAGE FINAL
    # ==========================
    final_text = (
        "**📊 RÉSUMÉ GLOBAL**\n\n"
        "===== COMPOS =====\n"
        f"{table_compos}"
        "===== ARTEFACTS =====\n"
        f"{table_artefacts}"
        "===== CONDITIONS =====\n"
        f"{table_conditions}"
    )

    await summary_channel.send(final_text)
    await ctx.send(f"✅ Résumé global généré dans {summary_channel.mention}")

def safe_float(x):
    try:
        return float(str(x).replace(",", ".").replace("**", ""))
    except:
        return 9999  # très grand pour envoyer les erreurs en bas
    
event_manager = EventManager(bot)

@bot.command()
async def addevent(ctx, name: str, date: str, repeat: str = "none"):
    await event_manager.add_event(ctx, name, date, repeat)

@bot.command()
async def listevents(ctx):
    await event_manager.list_events_cmd(ctx)

@bot.command()
async def deleteevent(ctx, name: str):
    await event_manager.delete_event(ctx, name)

@bot.event
async def on_ready():
    print("Bot lancé 🎉")
    event_manager.setup_scheduler(bot)

@bot.command()
async def checklist_now(ctx):
    await event_manager.send_checklist_now(ctx)

@bot.command()
async def edit_event(ctx, old_name: str, new_name: str = None, new_date: str = None, new_repeat: str = None):
    await event_manager.edit_event(ctx, old_name, new_name, new_date, new_repeat)

@bot.command()
async def report_unfinished(ctx):
    await event_manager.report_unfinished()
    await ctx.send("🔁 Tâches non faites reportées à demain !")

@bot.command(name="helpevent")
async def helpevent(ctx):
    embed = discord.Embed(
        title="📅 Guide des commandes d'événements",
        description="Voici toutes les commandes disponibles pour gérer tes événements, tâches et checklists.",
        color=0x00D9FF
    )

    embed.add_field(
        name="➕ Ajouter un événement",
        value=(
            "**Commande :** `!addevent <nom> <date> [repeat]`\n"
            "**Date format :** `YYYY-MM-DDTHH:MM`\n"
            "**Repeat :** `none` (défaut) ou `weekly`\n"
            "**Exemple :**\n"
            "`!addevent Sport 2025-01-25T18:00 weekly`"
        ),
        inline=False
    )

    embed.add_field(
        name="📜 Lister les événements",
        value=(
            "**Commande :** `!listevents`\n"
            "Affiche tous les événements enregistrés avec leur date et répétition."
        ),
        inline=False
    )

    embed.add_field(
        name="❌ Supprimer un événement",
        value=(
            "**Commande :** `!deleteevent <nom>`\n"
            "**Exemple :** `!deleteevent Sport`"
        ),
        inline=False
    )

    embed.add_field(
        name="✏️ Modifier un événement",
        value=(
            "**Commande :** `!edit_event <ancien_nom> [nouveau_nom] [nouvelle_date] [nouveau_repeat]`\n"
            "Les paramètres sont optionnels : tu peux changer ce que tu veux.\n"
            "**Exemples :**\n"
            "`!edit_event Sport new_date=2025-01-30T19:00`\n"
            "`!edit_event Révision new_repeat=weekly`\n"
            "`!edit_event Lessive new_name=Machine`"
        ),
        inline=False
    )

    embed.add_field(
        name="📋 Forcer l’envoi immédiat d’une checklist",
        value=(
            "**Commande :** `!checklist_now`\n"
            "Envoie la checklist du jour immédiatement dans ton canal #discipline."
        ),
        inline=False
    )

    embed.add_field(
        name="🔁 Reporter les tâches non terminées à demain",
        value=(
            "**Commande :** `!report_unfinished`\n"
            "Prend toutes les tâches datées d’hier et les décale à demain."
        ),
        inline=False
    )

    embed.add_field(
        name="⏰ Checklist automatique chaque matin",
        value=(
            "La checklist du matin est gérée automatiquement par EventManager.\n"
            "L’heure est configurable dans ton fichier config si besoin."
        ),
        inline=False
    )

    embed.set_footer(text="Bot Event Manager — créé sur mesure pour toi.")

    await ctx.send(embed=embed)

bot.run(os.getenv("DISCORD_TOKEN"))