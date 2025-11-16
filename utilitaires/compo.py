# utilitaires/compo.py
import discord
from datetime import datetime

# ============================================================
#   RÉSUMÉ COMPOS (UTILISÉ PAR L’UI & PAR LES COMMANDES TEXTE)
# ============================================================

async def generate_compo_summary(interaction, patch):
    """Génère le résumé des compos (UI version)"""
    guild = interaction.guild

    # Catégorie compo
    categoryComp = discord.utils.get(guild.categories, name="compo")
    if not categoryComp:
        await interaction.response.send_message("❌ Aucune compo trouvée.", ephemeral=True)
        return

    # Catégorie Résumé
    category = discord.utils.get(guild.categories, name="Résumé")
    if not category:
        category = await guild.create_category("Résumé")

    # Salon résumé-compo
    channel_name = "résumé-compo"
    channel = discord.utils.get(category.channels, name=channel_name)
    if not channel:
        channel = await category.create_text_channel(channel_name)

    # Lire toutes les compos
    stats = []
    for chan in categoryComp.channels:
        async for message in chan.history(limit=10):
            if message.author == interaction.client.user and message.embeds:
                embed = message.embeds[0]

                patch_field = next((f.value for f in embed.fields if f.name.lower() == "patch"), None)
                if not patch_field or patch_field.lower() != patch.lower():
                    continue

                placement_str = embed.fields[0].value.replace(',', '.')
                try:
                    placement = float(placement_str)
                except ValueError:
                    continue

                stats.append({
                    "nom": embed.title.replace("📊 Compo ", "").upper(),
                    "placement": placement
                })
                break

    if not stats:
        await interaction.response.send_message(f"❌ Aucune stat trouvée pour le patch {patch}.", ephemeral=True)
        return

    # Trier les compos
    stats.sort(key=lambda s: s["placement"])

    tiers = {"G": [], "A": [], "B": [], "C": [], "F": []}
    for s in stats:
        p = s["placement"]
        if p < 4.1: tiers["G"].append(s)
        elif p < 4.25: tiers["A"].append(s)
        elif p < 4.4: tiers["B"].append(s)
        elif p < 4.6: tiers["C"].append(s)
        else: tiers["F"].append(s)

    resume_text = f"**🏆 Résumé des Compos (Patch {patch})**\n\n"
    for tier, comps in tiers.items():
        if comps:
            resume_text += f"**Tier {tier}**\n"
            for compo in comps:
                resume_text += f"📊{compo['nom']} — Avg : **{compo['placement']:.2f}**\n"
            resume_text += "\n"

    embed = discord.Embed(description=resume_text, color=0xFFD700, timestamp=datetime.now())
    embed.set_footer(text=f"Généré par {interaction.user.name}")

    await channel.send(embed=embed)
    await interaction.response.send_message(
        f"✅ Résumé du patch **{patch}** envoyé dans {channel.mention} !",
        ephemeral=True
    )


# ============================================================
#   COMMANDES TEXTE
# ============================================================

async def compo_cmd(ctx, nom: str, placement: str, WinRate: str, Top4Rate: str, Patch: str):
    """Commande texte : !compo"""
    placement = placement.replace(',', '.')

    category = discord.utils.get(ctx.guild.categories, name="compo")
    if not category:
        category = await ctx.guild.create_category("compo")

    channel_name = nom.lower()
    channel = discord.utils.get(category.channels, name=channel_name)
    if not channel:
        channel = await category.create_text_channel(channel_name)

    # Chercher dernier message
    last_message = None
    async for message in channel.history(limit=10):
        if message.author == ctx.bot.user:
            last_message = message
            break

    embed = discord.Embed(
        title=f"📊 Compo {nom.upper()}",
        color=0x00D9FF,
        timestamp=datetime.now()
    )
    embed.add_field(name="Placement moyen", value=placement, inline=True)
    embed.add_field(name="WinRate", value=WinRate, inline=True)
    embed.add_field(name="Top4 Rate", value=Top4Rate, inline=True)
    embed.add_field(name="Patch", value=Patch, inline=True)
    embed.set_footer(text=f"Mis à jour par {ctx.author.name}")

    if last_message:
        await last_message.edit(embed=embed)
        await ctx.message.add_reaction('✅')
    else:
        await channel.send(embed=embed)
        await ctx.send(f"✅ Stats de {nom.upper()} créées dans {channel.mention} !")


async def resume_compo_cmd(ctx, patch: str):
    """Commande texte : !resume_compo"""
    guild = ctx.guild

    categoryComp = discord.utils.get(guild.categories, name="compo")
    if not categoryComp:
        await ctx.send("❌ Aucune compo trouvée.")
        return

    category = discord.utils.get(guild.categories, name="Résumé")
    if not category:
        category = await guild.create_category("Résumé")

    channel_name = "résumé-compo"
    channel = discord.utils.get(category.channels, name=channel_name)
    if not channel:
        channel = await category.create_text_channel(channel_name)

    stats = []
    for chan in categoryComp.channels:
        async for message in chan.history(limit=10):
            if message.author == ctx.bot.user and message.embeds:
                embed = message.embeds[0]

                patch_field = next((f.value for f in embed.fields if f.name.lower() == "patch"), None)
                if not patch_field or patch_field.lower() != patch.lower():
                    continue

                placement_str = embed.fields[0].value.replace(',', '.')
                try:
                    placement = float(placement_str)
                except ValueError:
                    continue

                stats.append({
                    "nom": embed.title.replace("📊 Compo ", "").upper(),
                    "placement": placement
                })
                break

    if not stats:
        await ctx.send(f"❌ Aucune stat trouvée pour le patch {patch}.")
        return

    # Tri
    stats.sort(key=lambda s: s["placement"])
    tiers = {"G": [], "A": [], "B": [], "C": [], "F": []}

    for s in stats:
        p = s["placement"]
        if p < 4.1: tiers["G"].append(s)
        elif p < 4.25: tiers["A"].append(s)
        elif p < 4.4: tiers["B"].append(s)
        elif p < 4.6: tiers["C"].append(s)
        else: tiers["F"].append(s)

    resume_text = f"**🏆 Résumé des Compos (Patch {patch})**\n\n"
    for tier, comps in tiers.items():
        if comps:
            resume_text += f"**Tier {tier}**\n"
            for compo in comps:
                resume_text += f"📊{compo['nom']} — Avg : **{compo['placement']:.2f}**\n"
            resume_text += "\n"

    embed = discord.Embed(description=resume_text, color=0xFFD700, timestamp=datetime.now())
    embed.set_footer(text=f"Généré par {ctx.author.name}")

    await channel.send(embed=embed)
    await ctx.send(f"✅ Résumé du patch **{patch}** envoyé dans {channel.mention} !")

