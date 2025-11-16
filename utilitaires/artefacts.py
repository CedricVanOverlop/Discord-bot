# utilitaires/artefacts.py
import discord
from datetime import datetime


# ============================================================
#    RÉSUMÉ ARTEFACTS PAR ARTEFACT (UI ET TEXTE)
# ============================================================

async def generate_artefact_summary(interaction, patch):
    """Résumé par artefact (UI version)"""
    guild = interaction.guild

    # Catégorie artefact
    category = discord.utils.get(guild.categories, name="artefact")
    if not category:
        await interaction.response.send_message("❌ Aucune donnée d'artefact trouvée.", ephemeral=True)
        return

    # Catégorie Résumé
    category_resume = discord.utils.get(guild.categories, name="Résumé")
    if not category_resume:
        category_resume = await guild.create_category("Résumé")

    # Salon résumé-artefacts
    channel_name = "résumé-artefacts"
    channel = discord.utils.get(category_resume.channels, name=channel_name)
    if not channel:
        channel = await category_resume.create_text_channel(channel_name)

    stats = []

    for chan in category.channels:
        async for message in chan.history(limit=50):
            if message.author == interaction.client.user and message.embeds:
                embed = message.embeds[0]

                # Vérifier le patch
                patch_field = next((f.value for f in embed.fields if f.name.lower() == "patch"), None)
                if not patch_field or patch_field != patch:
                    continue

                # Extraire AVG et Delta
                avg_field = next((f.value for f in embed.fields if f.name.lower() == "avg"), None)
                delta_field = next((f.value for f in embed.fields if f.name.lower() == "delta"), None)
                perso_field = next((f.value for f in embed.fields if f.name.lower() == "personnage"), None)

                if not avg_field or not delta_field or not perso_field:
                    continue

                # Convertir AVG
                try:
                    avg = float(avg_field.replace(',', '.'))
                except ValueError:
                    continue

                artefact_name = embed.title.replace("🪄 Artefact ", "").upper()

                stats.append({
                    "artefact": artefact_name,
                    "avg": avg,
                    "delta": delta_field,
                    "perso": perso_field
                })

    if not stats:
        await interaction.response.send_message(f"❌ Aucun artefact trouvé pour le patch {patch}.", ephemeral=True)
        return

    stats.sort(key=lambda s: s["avg"])

    # Résumé formaté
    resume = f"**🪄 Résumé des Artefacts (Patch {patch})**\n\n"
    for s in stats:
        resume += f"**{s['artefact']}** — Perso: **{s['perso']}** — AVG: **{s['avg']:.2f}** — Δ {s['delta']}\n"

    embed = discord.Embed(description=resume, color=0x8A2BE2, timestamp=datetime.now())
    embed.set_footer(text=f"Généré par {interaction.user.name}")

    await channel.send(embed=embed)
    await interaction.response.send_message(
        f"✅ Résumé Artefacts patch {patch} généré dans {channel.mention} !",
        ephemeral=True
    )


# ============================================================
#    RÉSUMÉ ARTEFACTS PAR PERSONNAGE (UI ET TEXTE)
# ============================================================

async def generate_artefact_perso_summary(interaction, patch):
    """Résumé par personnage (UI version)"""
    guild = interaction.guild

    category = discord.utils.get(guild.categories, name="artefact")
    if not category:
        await interaction.response.send_message("❌ Aucune donnée d'artefact trouvée.", ephemeral=True)
        return

    category_resume = discord.utils.get(guild.categories, name="Résumé")
    if not category_resume:
        category_resume = await guild.create_category("Résumé")

    channel_name = "résumé-artefacts-perso"
    channel = discord.utils.get(category_resume.channels, name=channel_name)
    if not channel:
        channel = await category_resume.create_text_channel(channel_name)

    stats = {}

    for chan in category.channels:
        async for message in chan.history(limit=50):
            if message.author == interaction.client.user and message.embeds:
                embed = message.embeds[0]

                patch_field = next((f.value for f in embed.fields if f.name.lower() == "patch"), None)
                if not patch_field or patch_field != patch:
                    continue

                # Extraire infos
                artefact_name = embed.title.replace("🪄 Artefact ", "")
                perso_field = next((f.value for f in embed.fields if f.name.lower() == "personnage"), None)
                avg_field = next((f.value for f in embed.fields if f.name.lower() == "avg"), None)

                if not perso_field or not avg_field:
                    continue

                try:
                    avg = float(avg_field.replace(',', '.'))
                except ValueError:
                    continue

                if perso_field not in stats:
                    stats[perso_field] = []

                stats[perso_field].append({
                    "artefact": artefact_name,
                    "avg": avg
                })

    if not stats:
        await interaction.response.send_message(f"❌ Aucun artefact trouvé pour le patch {patch}.", ephemeral=True)
        return

    # Construction du résumé
    resume = f"**👥 Résumé des Artefacts par Personnage (Patch {patch})**\n\n"

    for perso, lst in stats.items():
        resume += f"### **{perso}**\n"
        lst.sort(key=lambda x: x["avg"])
        for entry in lst:
            resume += f"🪄 {entry['artefact']} — AVG: **{entry['avg']:.2f}**\n"
        resume += "\n"

    embed = discord.Embed(description=resume, color=0x00A9FF, timestamp=datetime.now())
    embed.set_footer(text=f"Généré par {interaction.user.name}")

    await channel.send(embed=embed)
    await interaction.response.send_message(
        f"📌 Résumé par personnage généré dans {channel.mention}",
        ephemeral=True
    )


# ============================================================
#    COMMANDES TEXTE
# ============================================================

async def artefact_cmd(ctx, Nom: str, Personnage: str, AVG: str, Delta: str, Patch: str):
    """Commande texte : !artefact"""
    AVG = AVG.replace(',', '.')

    category = discord.utils.get(ctx.guild.categories, name="artefact")
    if not category:
        category = await ctx.guild.create_category("artefact")

    channel_name = Nom.lower()
    channel = discord.utils.get(category.channels, name=channel_name)
    if not channel:
        channel = await category.create_text_channel(channel_name)

    # Supprimer l'ancien message pour le même personnage
    async for message in channel.history(limit=50):
        if message.author == ctx.bot.user and message.embeds:
            embed = message.embeds[0]
            if any(field.name == "Personnage" and field.value.lower() == Personnage.lower() for field in embed.fields):
                await message.delete()
                break

    embed = discord.Embed(
        title=f"🪄 Artefact {Nom.upper()}",
        color=0x8A2BE2,
        timestamp=datetime.now()
    )
    embed.add_field(name="Personnage", value=Personnage, inline=True)
    embed.add_field(name="AVG", value=AVG, inline=True)
    embed.add_field(name="Delta", value=Delta, inline=True)
    embed.add_field(name="Patch", value=Patch, inline=True)
    embed.set_footer(text=f"Ajouté par {ctx.author.name}")

    await channel.send(embed=embed)
    await ctx.send(f"🪄 Artefact **{Nom.upper()}** ajouté/MAJ dans {channel.mention} !")


async def resume_artefact_cmd(ctx, patch: str):
    """Commande texte : !resume_artefact"""
    await generate_artefact_summary(ctx, patch)


async def resume_artefact_perso_cmd(ctx, patch: str):
    """Commande texte : !resume_artefact_perso"""
    await generate_artefact_perso_summary(ctx, patch)
