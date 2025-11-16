# utilitaires/parties.py
import discord
from datetime import datetime


# ============================================================
#       CALCUL DES AUGMENTS (UI BUTTON : “Stats Augments”)
# ============================================================

async def generate_augment_stats(interaction, patch, ordre, compo):
    guild = interaction.guild

    # Catégorie Résumé
    category = discord.utils.get(guild.categories, name="Résumé")
    if not category:
        category = await guild.create_category("Résumé")

    # Channel mesgames
    games_channel = discord.utils.get(category.channels, name="autregames")
    if not games_channel:
        await interaction.response.send_message(
            "❌ Aucune game trouvée. Ajoute d'abord des games avec le bouton.",
            ephemeral=True
        )
        return

    # Channel stats_augments
    stats_channel = discord.utils.get(category.channels, name="stats_augments")
    if not stats_channel:
        stats_channel = await category.create_text_channel("stats_augments")

    data = []

    # Lire les games
    async for message in games_channel.history(limit=2000):
        if message.author == interaction.client.user and message.embeds:
            embed = message.embeds[0]
            fields = {f.name.lower(): f.value for f in embed.fields}

            # Filtres
            if patch != "0" and fields["patch"].lower() != patch.lower():
                continue
            if compo != "0" and fields["compo"].lower() != compo.lower():
                continue

            try:
                placement = float(fields["placement"].replace(',', '.'))
            except ValueError:
                continue

            data.append({
                "placement": placement,
                "aug1": fields["augment 1"],
                "aug2": fields["augment 2"],
                "aug3": fields["augment 3"],
            })

    if not data:
        await interaction.response.send_message("❌ Aucune game trouvée avec ces filtres.", ephemeral=True)
        return

    # Ordre choisi
    if ordre == "1":
        keys = ["aug1"]
    elif ordre == "2":
        keys = ["aug2"]
    elif ordre == "3":
        keys = ["aug3"]
    else:
        keys = ["aug1", "aug2", "aug3"]

    stats = {}

    for game in data:
        for key in keys:
            aug = game[key]
            if aug not in stats:
                stats[aug] = {"total": 0, "count": 0}
            stats[aug]["total"] += game["placement"]
            stats[aug]["count"] += 1

    # Calcul des moyennes
    results = []
    for aug, s in stats.items():
        avg = s["total"] / s["count"]
        results.append((aug, avg, s["count"]))

    results.sort(key=lambda x: x[1])

    # Création du résumé
    summary = (
        f"📊 **Stats Augments**\n"
        f"Patch `{patch}` | Ordre `{ordre}` | Compo `{compo}`\n\n"
    )
    for aug, avg, count in results[:25]:
        summary += f"**{aug}** — Moyenne **{avg:.2f}** ({count} games)\n"

    embed = discord.Embed(description=summary, color=0x00D9FF, timestamp=datetime.now())
    embed.set_footer(text=f"Demandé par {interaction.user.name}")

    await stats_channel.send(embed=embed)
    await interaction.response.send_message(
        f"📌 Stats générées dans {stats_channel.mention}",
        ephemeral=True
    )


# ============================================================
#       COMMANDE TEXTE : MES GAMES
# ============================================================

async def games_cmd(ctx, compo: str, placement: str, augment1: str, augment2: str, augment3: str, patch: str, who: str):
    
    # Convertir placement
    try:
        placement_int = int(placement)
    except ValueError:
        placement_int = 9

    guild = ctx.guild

    # Catégorie Parties
    category = discord.utils.get(guild.categories, name="Parties")
    if not category:
        category = await guild.create_category("Parties")

    # Salon mesgames
    channel1 = discord.utils.get(category.channels, name="mesgames")
    if not channel1:
        channel1 = await category.create_text_channel("mesgames")

    # Salon autregames
    channel = discord.utils.get(category.channels, name="autregames")
    if not channel:
        channel = await category.create_text_channel("autregames")

    # Compter les games (FIX)
    count = 0
    async for _ in channel.history(limit=2000):
        count += 1

    embed = discord.Embed(
        title=f"🎮 Game #{count + 1}",
        color=0x00FF00 if placement_int <= 4 else 0xFF0000,
        timestamp=datetime.now()
    )

    embed.add_field(name="Compo", value=compo.upper(), inline=True)
    embed.add_field(name="Placement", value=placement, inline=True)
    embed.add_field(name="Patch", value=patch, inline=True)
    embed.add_field(name="Augment 1", value=augment1, inline=False)
    embed.add_field(name="Augment 2", value=augment2, inline=False)
    embed.add_field(name="Augment 3", value=augment3, inline=False)

    user = ctx.author if hasattr(ctx, "author") else ctx.user

    if placement_int == 1:
        embed.set_footer(text=f"🏆 Victoire ! • {user.name}")
    elif placement_int <= 4:
        embed.set_footer(text=f"🎯 Top 4 ! • {user.name}")
    else:
        embed.set_footer(text=f"Joueur : {user.name}")

    # Enregistrer
    await channel.send(embed=embed)

    if who == "moi":
        await channel1.send(embed=embed)


async def mesgames_cmd(ctx, compo: str, placement: str, augment1: str, augment2: str, augment3: str, patch: str):
    await games_cmd(ctx, compo, placement, augment1, augment2, augment3, patch,"moi")

async def autresgames_cmd(ctx, compo: str, placement: str, augment1: str, augment2: str, augment3: str, patch: str):
    await games_cmd(ctx, compo, placement, augment1, augment2, augment3,patch,"x")


# ============================================================
#     COMMANDE TEXTE : CALCUL STAT AUGMENT
# ============================================================

async def statsaugment_cmd(ctx, patch: str, ordre: str, compo: str):
    guild = ctx.guild

    category = discord.utils.get(guild.categories, name="Résumé")
    if not category:
        category = await guild.create_category("Résumé")

    # Channel mesgames
    games_channel = discord.utils.get(category.channels, name="autregames")
    if not games_channel:
        await ctx.send("❌ Aucune game enregistrée.")
        return

    # Channel stats_augments
    stats_channel = discord.utils.get(category.channels, name="stats_augments")
    if not stats_channel:
        stats_channel = await category.create_text_channel("stats_augments")

    data = []

    # Lire les parties
    async for message in games_channel.history(limit=2000):
        if message.author == ctx.bot.user and message.embeds:
            embed = message.embeds[0]
            fields = {f.name.lower(): f.value for f in embed.fields}

            # Filtrage
            if patch != "0" and fields["patch"].lower() != patch.lower():
                continue
            if compo != "0" and fields["compo"].lower() != compo.lower():
                continue

            try:
                placement = float(fields["placement"])
            except ValueError:
                continue

            data.append({
                "placement": placement,
                "aug1": fields["augment 1"],
                "aug2": fields["augment 2"],
                "aug3": fields["augment 3"],
            })

    if not data:
        await ctx.send("❌ Aucune donnée trouvée avec ces filtres.")
        return

    # Ordre des augments
    if ordre == "1":
        keys = ["aug1"]
    elif ordre == "2":
        keys = ["aug2"]
    elif ordre == "3":
        keys = ["aug3"]
    else:
        keys = ["aug1", "aug2", "aug3"]

    counts = {}
    for game in data:
        for key in keys:
            aug = game[key]
            if aug not in counts:
                counts[aug] = {"total": 0, "count": 0}
            counts[aug]["total"] += game["placement"]
            counts[aug]["count"] += 1

    results = [(aug, v["total"] / v["count"], v["count"]) for aug, v in counts.items()]
    results.sort(key=lambda x: x[1])

    # Texte final
    text = (
        f"📊 **Stats Augments**\n"
        f"Patch `{patch}` | Ordre `{ordre}` | Compo `{compo}`\n\n"
    )

    for aug, avg, count in results[:25]:
        text += f"**{aug}** — Moyenne **{avg:.2f}** ({count} games)\n"

    embed = discord.Embed(description=text, color=0x00D9FF, timestamp=datetime.now())
    embed.set_footer(text=f"Demandé par {ctx.author.name}")

    await stats_channel.send(embed=embed)
    await ctx.send(f"📌 Stats envoyées dans {stats_channel.mention}")
