import discord
from discord.ui import Modal, TextInput


# ========== FONCTION UTILITAIRE ==========

async def get_or_create_compo_channel(guild: discord.Guild, compo_name: str) -> discord.TextChannel:
    """
    Trouve ou crée un channel pour une compo dans la catégorie 'compo'
    
    Args:
        guild: Le serveur Discord
        compo_name: Nom de la compo (ex: "Noxus")
    
    Returns:
        Le channel Discord (existant ou nouvellement créé)
    """
    # Normalise le nom du channel (minuscules, espaces -> tirets)
    channel_name = compo_name.lower().replace(" ", "-")
    
    # 1. Trouve la catégorie "compo"
    category = discord.utils.get(guild.categories, name="compo")
    
    if not category:
        raise ValueError("❌ La catégorie 'compo' n'existe pas sur ce serveur")
    
    # 2. Cherche si le channel existe déjà dans cette catégorie
    existing_channel = discord.utils.get(category.channels, name=channel_name)
    
    if existing_channel:
        # Channel existe déjà
        return existing_channel
    
    # 3. Crée le channel s'il n'existe pas
    new_channel = await guild.create_text_channel(
        name=channel_name,
        category=category,
        topic=f"Discussion et stats pour la compo {compo_name}"
    )
    
    return new_channel


# ========== MODALS ==========

class CompoModal(Modal):
    def __init__(self, tft_sheets):
        super().__init__(title="📊 Stats Compo")
        self.tft = tft_sheets
        
        self.compo = TextInput(
            label="Nom de la compo",
            placeholder="Ex: Noxus",
            required=True,
            max_length=50
        )
        self.add_item(self.compo)
    
    async def on_submit(self, interaction: discord.Interaction):
        compo = self.compo.value
        info = self.tft.get_compo_info(compo)
        
        if not info:
            await interaction.response.send_message(
                f"❌ Compo `{compo}` non trouvée.",
                ephemeral=True
            )
            return
        
        # Trouve ou crée le channel
        try:
            channel = await get_or_create_compo_channel(interaction.guild, compo)
        except ValueError as e:
            await interaction.response.send_message(str(e), ephemeral=True)
            return
        
        # Crée l'embed
        embed = discord.Embed(
            title=f"📊 {info['nom']}",
            color=discord.Color.blue()
        )
        embed.add_field(name="Avg Place", value=info['avg'], inline=True)
        embed.add_field(name="Win Rate", value=info['winrate'], inline=True)
        embed.add_field(name="Top 4 Rate", value=info['top4rate'], inline=True)
        embed.set_footer(text=f"Demandé par {interaction.user.display_name}")
        
        # Répond à l'interaction (obligatoire dans les 3 secondes)
        await interaction.response.send_message(
            f"✅ Stats de **{compo}** envoyées dans {channel.mention}",
            ephemeral=True
        )
        
        # Envoie dans le channel de la compo
        await channel.send(embed=embed)


class BuildModal(Modal):
    def __init__(self, tft_sheets):
        super().__init__(title="🎒 Builds")
        self.tft = tft_sheets
        
        self.compo = TextInput(
            label="Nom de la compo",
            placeholder="Ex: Noxus",
            required=True
        )
        self.carry = TextInput(
            label="Nom du carry",
            placeholder="Ex: Darius",
            required=True
        )
        
        self.add_item(self.compo)
        self.add_item(self.carry)
    
    async def on_submit(self, interaction: discord.Interaction):
        compo = self.compo.value
        carry = self.carry.value
        
        builds = self.tft.get_build_info(compo, carry)
        
        if not builds:
            await interaction.response.send_message(
                f"❌ Aucun build trouvé pour `{carry}` dans `{compo}`",
                ephemeral=True
            )
            return
        
        # Trouve ou crée le channel
        try:
            channel = await get_or_create_compo_channel(interaction.guild, compo)
        except ValueError as e:
            await interaction.response.send_message(str(e), ephemeral=True)
            return
        
        # Crée l'embed
        embed = discord.Embed(
            title=f"🎒 Builds - {carry} ({compo})",
            color=discord.Color.gold()
        )
        
        for idx, build in enumerate(builds, 1):
            items_text = f"**Items:** {build['item1']} | {build['item2']} | {build['item3']}\n"
            items_text += f"**Avg:** {build['avg']}"
            embed.add_field(name=f"Build #{idx}", value=items_text, inline=False)
        
        embed.set_footer(text=f"Demandé par {interaction.user.display_name}")
        
        # Répond à l'interaction
        await interaction.response.send_message(
            f"✅ Builds de **{carry}** ({compo}) envoyés dans {channel.mention}",
            ephemeral=True
        )
        
        # Envoie dans le channel
        await channel.send(embed=embed)


class ArtefactModal(Modal):
    def __init__(self, tft_sheets):
        super().__init__(title="✨ Artefacts")
        self.tft = tft_sheets
        
        self.compo = TextInput(
            label="Nom de la compo",
            placeholder="Ex: Noxus",
            required=True
        )
        self.carry = TextInput(
            label="Nom du carry",
            placeholder="Ex: Darius",
            required=True
        )
        
        self.add_item(self.compo)
        self.add_item(self.carry)
    
    async def on_submit(self, interaction: discord.Interaction):
        compo = self.compo.value
        carry = self.carry.value
        
        artifacts = self.tft.get_artifact_info(compo, carry)
        
        if not artifacts:
            await interaction.response.send_message(
                f"❌ Aucun artefact trouvé pour `{carry}` dans `{compo}`",
                ephemeral=True
            )
            return
        
        # Trouve ou crée le channel
        try:
            channel = await get_or_create_compo_channel(interaction.guild, compo)
        except ValueError as e:
            await interaction.response.send_message(str(e), ephemeral=True)
            return
        
        # Crée l'embed
        embed = discord.Embed(
            title=f"✨ Artefacts - {carry} ({compo})",
            color=discord.Color.purple()
        )
        
        for idx, art in enumerate(artifacts, 1):
            art_text = f"**Artefact:** {art['artefact']}\n"
            art_text += f"**Avg:** {art['avg']}"
            embed.add_field(name=f"Option #{idx}", value=art_text, inline=False)
        
        embed.set_footer(text=f"Demandé par {interaction.user.display_name}")
        
        # Répond à l'interaction
        await interaction.response.send_message(
            f"✅ Artefacts de **{carry}** ({compo}) envoyés dans {channel.mention}",
            ephemeral=True
        )
        
        # Envoie dans le channel
        await channel.send(embed=embed)


class RadiantModal(Modal):
    def __init__(self, tft_sheets):
        super().__init__(title="💎 Radiants")
        self.tft = tft_sheets
        
        self.compo = TextInput(
            label="Nom de la compo",
            placeholder="Ex: Noxus",
            required=True
        )
        self.carry = TextInput(
            label="Nom du carry",
            placeholder="Ex: Darius",
            required=True
        )
        
        self.add_item(self.compo)
        self.add_item(self.carry)
    
    async def on_submit(self, interaction: discord.Interaction):
        compo = self.compo.value
        carry = self.carry.value
        
        radiants = self.tft.get_radiant_info(compo, carry)
        
        if not radiants:
            await interaction.response.send_message(
                f"❌ Aucun radiant trouvé pour `{carry}` dans `{compo}`",
                ephemeral=True
            )
            return
        
        # Trouve ou crée le channel
        try:
            channel = await get_or_create_compo_channel(interaction.guild, compo)
        except ValueError as e:
            await interaction.response.send_message(str(e), ephemeral=True)
            return
        
        # Crée l'embed
        embed = discord.Embed(
            title=f"💎 Radiants - {carry} ({compo})",
            color=discord.Color.from_rgb(255, 215, 0)
        )
        
        for idx, rad in enumerate(radiants, 1):
            rad_text = f"**Radiant:** {rad['radiant']}\n"
            rad_text += f"**Avg:** {rad['avg']}"
            embed.add_field(name=f"Option #{idx}", value=rad_text, inline=False)
        
        embed.set_footer(text=f"Demandé par {interaction.user.display_name}")
        
        # Répond à l'interaction
        await interaction.response.send_message(
            f"✅ Radiants de **{carry}** ({compo}) envoyés dans {channel.mention}",
            ephemeral=True
        )
        
        # Envoie dans le channel
        await channel.send(embed=embed)


class ConditionsModal(Modal):
    def __init__(self, tft_sheets):
        super().__init__(title="📋 Conditions")
        self.tft = tft_sheets
        
        self.compo = TextInput(
            label="Nom de la compo",
            placeholder="Ex: Noxus",
            required=True
        )
        self.add_item(self.compo)
    
    async def on_submit(self, interaction: discord.Interaction):
        compo = self.compo.value
        conditions = self.tft.get_conditions_info(compo)
        
        if not conditions:
            await interaction.response.send_message(
                f"❌ Aucune condition trouvée pour `{compo}`",
                ephemeral=True
            )
            return
        
        # Trouve ou crée le channel
        try:
            channel = await get_or_create_compo_channel(interaction.guild, compo)
        except ValueError as e:
            await interaction.response.send_message(str(e), ephemeral=True)
            return
        
        # Crée l'embed
        embed = discord.Embed(
            title=f"📋 Conditions - {compo}",
            color=discord.Color.green()
        )
        
        for idx, cond in enumerate(conditions, 1):
            cond_text = f"**Condition:** {cond['condition']}\n"
            cond_text += f"**Avg:** {cond['avg']} | "
            cond_text += f"**WR:** {cond['winrate']} | "
            cond_text += f"**Top4:** {cond['top4rate']}\n"
            if cond['remarques']:
                cond_text += f"**Remarques:** {cond['remarques']}"
            
            embed.add_field(name=f"#{idx}", value=cond_text, inline=False)
        
        embed.set_footer(text=f"Demandé par {interaction.user.display_name}")
        
        # Répond à l'interaction
        await interaction.response.send_message(
            f"✅ Conditions de **{compo}** envoyées dans {channel.mention}",
            ephemeral=True
        )
        
        # Envoie dans le channel
        await channel.send(embed=embed)