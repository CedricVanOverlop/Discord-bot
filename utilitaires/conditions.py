# utilitaires/conditions.py
import discord
from datetime import datetime


# ============================================================
#   RÉCUPÉRATION DES STATS DE BASE D'UNE COMPO
# ============================================================

async def get_compo_base_stats(guild, compo_name):
    """Récupère les stats de base d'une compo depuis son channel"""
    category = discord.utils.get(guild.categories, name="compo")
    if not category:
        return None
    
    # Trouver le channel de la compo
    channel_name = compo_name.lower()
    channel = discord.utils.get(category.channels, name=channel_name)
    if not channel:
        return None
    
    # Chercher le dernier message avec les stats
    async for message in channel.history(limit=10):
        if message.embeds:
            embed = message.embeds[0]
            
            # Extraire les stats
            fields = {f.name.lower(): f.value for f in embed.fields}
            
            try:
                placement = float(fields.get("placement moyen", "0").replace(',', '.'))
                winrate = fields.get("winrate", "N/A")
                top4rate = fields.get("top4 rate", "N/A")
                patch = fields.get("patch", "N/A")
                
                return {
                    "name": compo_name,
                    "placement": placement,
                    "winrate": winrate,
                    "top4rate": top4rate,
                    "patch": patch,
                    "message_id": message.id
                }
            except (ValueError, KeyError):
                continue
    
    return None


# ============================================================
#   CRÉATION DU CHANNEL CONDITIONS
# ============================================================

async def create_conditions_channel(guild, compo_name, base_stats):
    """Crée ou récupère le channel conditions pour une compo"""
    # Catégorie Conditions
    category = discord.utils.get(guild.categories, name="Conditions")
    if not category:
        category = await guild.create_category("Conditions")
    
    # Channel spécifique à la compo
    channel_name = f"conditions-{compo_name.lower()}"
    channel = discord.utils.get(category.channels, name=channel_name)
    
    if not channel:
        channel = await category.create_text_channel(channel_name)
        
        # Message de bienvenue avec les stats de base
        embed = discord.Embed(
            title=f"📊 Stats de base - {compo_name.upper()}",
            description="Voici les statistiques de base de cette composition",
            color=0x3498db,
            timestamp=datetime.now()
        )
        embed.add_field(name="Placement Moyen", value=f"**{base_stats['placement']:.2f}**", inline=True)
        embed.add_field(name="Win Rate", value=base_stats['winrate'], inline=True)
        embed.add_field(name="Top 4 Rate", value=base_stats['top4rate'], inline=True)
        embed.add_field(name="Patch", value=base_stats['patch'], inline=True)
        embed.set_footer(text="Stats de référence pour les conditions")
        
        await channel.send(embed=embed)
    
    return channel


# ============================================================
#   AJOUT D'UNE CONDITION
# ============================================================

async def add_condition(channel, condition_name, placement, base_placement):
    """Ajoute une condition dans le channel"""
    try:
        placement_float = float(placement.replace(',', '.'))
    except ValueError:
        return False
    
    # Calculer la différence
    difference = placement_float - base_placement
    
    # Déterminer la couleur et l'emoji
    if difference < -0.15:
        color = 0x2ecc71  # Vert foncé - Excellent
        emoji = "🌟"
        tier = "S-Tier"
    elif difference < 0:
        color = 0x27ae60  # Vert clair - Bon
        emoji = "📈"
        tier = "A-Tier"
    elif difference < 0.1:
        color = 0xf39c12  # Orange - Neutre
        emoji = "➡️"
        tier = "B-Tier"
    else:
        color = 0xe74c3c  # Rouge - Mauvais
        emoji = "📉"
        tier = "C-Tier"
    
    # Créer l'embed
    embed = discord.Embed(
        title=f"{emoji} {condition_name}",
        color=color,
        timestamp=datetime.now()
    )
    
    embed.add_field(
        name="Placement avec condition",
        value=f"**{placement_float:.2f}**",
        inline=True
    )
    embed.add_field(
        name="Base",
        value=f"**{base_placement:.2f}**",
        inline=True
    )
    embed.add_field(
        name="Différence",
        value=f"**{difference:+.2f}**",
        inline=True
    )
    embed.add_field(
        name="Tier",
        value=f"**{tier}**",
        inline=False
    )
    
    await channel.send(embed=embed)
    return True


# ============================================================
#   RÉSUMÉ DES CONDITIONS
# ============================================================

async def generate_conditions_summary(interaction, compo_name):
    """Génère un résumé des conditions pour une compo"""
    guild = interaction.guild
    
    # Trouver le channel conditions
    category = discord.utils.get(guild.categories, name="Conditions")
    if not category:
        await interaction.response.send_message("❌ Aucune condition trouvée.", ephemeral=True)
        return
    
    channel_name = f"conditions-{compo_name.lower()}"
    channel = discord.utils.get(category.channels, name=channel_name)
    
    if not channel:
        await interaction.response.send_message(
            f"❌ Aucune condition pour {compo_name}.",
            ephemeral=True
        )
        return
    
    # Récupérer les stats de base
    base_stats = None
    conditions = []
    
    async for message in channel.history(limit=100):
        if message.embeds:
            embed = message.embeds[0]
            
            # Premier message = stats de base
            if "Stats de base" in embed.title:
                fields = {f.name.lower(): f.value for f in embed.fields}
                base_stats = float(fields.get("placement moyen", "0").replace('**', '').replace(',', '.'))
            else:
                # C'est une condition
                fields = {f.name.lower(): f.value for f in embed.fields}
                try:
                    placement = float(fields.get("placement avec condition", "0").replace('**', '').replace(',', '.'))
                    conditions.append({
                        "name": embed.title,
                        "placement": placement
                    })
                except ValueError:
                    continue
    
    if not base_stats or not conditions:
        await interaction.response.send_message(
            "❌ Pas assez de données pour générer un résumé.",
            ephemeral=True
        )
        return
    
    # Trier par placement
    conditions.sort(key=lambda x: x["placement"])
    
    # Créer le résumé
    summary = f"**📊 Résumé Conditions - {compo_name.upper()}**\n\n"
    summary += f"**Base:** {base_stats:.2f}\n\n"
    
    for cond in conditions:
        diff = cond["placement"] - base_stats
        emoji = "📈" if diff < 0 else "📉"
        summary += f"{emoji} {cond['name']} → **{cond['placement']:.2f}** ({diff:+.2f})\n"
    
    embed = discord.Embed(
        description=summary,
        color=0x9b59b6,
        timestamp=datetime.now()
    )
    embed.set_footer(text=f"Généré par {interaction.user.name}")
    
    await channel.send(embed=embed)
    await interaction.response.send_message(
        f"✅ Résumé généré dans {channel.mention}",
        ephemeral=True
    )


# ============================================================
#   COMMANDE TEXTE
# ============================================================

async def condition_cmd(ctx, compo: str, condition_name: str, placement: str):
    """Commande texte : !condition"""
    guild = ctx.guild
    
    # Récupérer les stats de base
    base_stats = await get_compo_base_stats(guild, compo)
    
    if not base_stats:
        await ctx.send(f"❌ Compo **{compo}** introuvable. Ajoutez d'abord la compo avec !compo")
        return
    
    # Créer/récupérer le channel conditions
    channel = await create_conditions_channel(guild, compo, base_stats)
    
    # Ajouter la condition
    success = await add_condition(channel, condition_name, placement, base_stats['placement'])
    
    if success:
        await ctx.send(f"✅ Condition **{condition_name}** ajoutée pour {compo} dans {channel.mention}")
    else:
        await ctx.send("❌ Erreur lors de l'ajout de la condition.")


async def resume_conditions_cmd(ctx, compo: str):
    """Commande texte : !resume_conditions"""
    await generate_conditions_summary(ctx, compo)