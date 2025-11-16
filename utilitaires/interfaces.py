# utilitaires/interfaces.py
import discord
from discord.ext import commands
from datetime import datetime
from typing import Optional

# NOTE: on importe les fonctions de résumé / génération depuis les autres modules.
# Ces imports doivent exister (fichiers compo.py, artefacts.py, parties.py)
# Ils sont placés en bas pour éviter les imports circulaires lors du chargement.
# from utilitaires.compo import generate_compo_summary
# from utilitaires.artefacts import generate_artefact_summary, generate_artefact_perso_summary
# from utilitaires.parties import generate_augment_stats

# ------------------------------
# Modals (Formulaires)
# ------------------------------

class CompoModal(discord.ui.Modal, title='Ajouter/Modifier une Compo'):
    """Modal pour entrer les stats d'une compo"""
    nom = discord.ui.TextInput(
        label='Nom de la compo',
        placeholder='Ex: SG, Frost, etc.',
        required=True,
        max_length=20
    )
    placement = discord.ui.TextInput(
        label='Placement moyen',
        placeholder='Ex: 4.12',
        required=True,
        max_length=10
    )
    winrate = discord.ui.TextInput(
        label='Win Rate',
        placeholder='Ex: 15.5%',
        required=True,
        max_length=10
    )
    top4rate = discord.ui.TextInput(
        label='Top 4 Rate',
        placeholder='Ex: 58%',
        required=True,
        max_length=10
    )
    patch = discord.ui.TextInput(
        label='Patch',
        placeholder='Ex: 15.22',
        required=True,
        max_length=10
    )

    async def on_submit(self, interaction: discord.Interaction):
        # Convertir la virgule en point
        placement_value = self.placement.value.replace(',', '.')
        
        # Trouver ou créer la catégorie
        category = discord.utils.get(interaction.guild.categories, name="compo")
        if not category:
            category = await interaction.guild.create_category("compo")
        
        # Trouver ou créer le salon
        channel_name = self.nom.value.lower()
        channel = discord.utils.get(category.channels, name=channel_name)
        if not channel:
            channel = await category.create_text_channel(channel_name)
        
        # Chercher le dernier message du bot
        last_message = None
        async for message in channel.history(limit=10):
            if message.author == interaction.client.user:
                last_message = message
                break
        
        # Créer l'embed
        embed = discord.Embed(
            title=f"📊 Compo {self.nom.value.upper()}",
            color=0x00D9FF,
            timestamp=datetime.now()
        )
        embed.add_field(name="Placement moyen", value=placement_value, inline=True)
        embed.add_field(name="WinRate", value=self.winrate.value, inline=True)
        embed.add_field(name="Top4 Rate", value=self.top4rate.value, inline=True)
        embed.add_field(name="Patch", value=self.patch.value, inline=True)
        embed.set_footer(text=f"Mis à jour par {interaction.user.name}")
        
        # Modifier ou créer
        if last_message:
            await last_message.edit(embed=embed)
            await interaction.response.send_message(
                f"✅ Stats de {self.nom.value.upper()} mises à jour dans {channel.mention} !",
                ephemeral=True
            )
        else:
            await channel.send(embed=embed)
            await interaction.response.send_message(
                f"✅ Stats de {self.nom.value.upper()} créées dans {channel.mention} !",
                ephemeral=True
            )


class ArtefactModal(discord.ui.Modal, title='Ajouter un Artefact'):
    """Modal pour entrer les stats d'un artefact"""
    nom = discord.ui.TextInput(
        label='Nom de l\'artefact',
        placeholder='Ex: RadiantSword',
        required=True,
        max_length=30
    )
    personnage = discord.ui.TextInput(
        label='Personnage',
        placeholder='Ex: Sett',
        required=True,
        max_length=20
    )
    avg = discord.ui.TextInput(
        label='AVG (Placement moyen)',
        placeholder='Ex: 3.95',
        required=True,
        max_length=10
    )
    delta = discord.ui.TextInput(
        label='Delta',
        placeholder='Ex: 0.12',
        required=True,
        max_length=10
    )
    patch = discord.ui.TextInput(
        label='Patch',
        placeholder='Ex: 15.22',
        required=True,
        max_length=10
    )

    async def on_submit(self, interaction: discord.Interaction):
        # Trouver ou créer la catégorie
        category = discord.utils.get(interaction.guild.categories, name="artefact")
        if not category:
            category = await interaction.guild.create_category("artefact")
        
        # Trouver ou créer le salon
        channel_name = self.nom.value.lower()
        channel = discord.utils.get(category.channels, name=channel_name)
        if not channel:
            channel = await category.create_text_channel(channel_name)
        
        # Supprimer l'ancien message du même personnage
        async for message in channel.history(limit=50):
            if message.author == interaction.client.user and message.embeds:
                embed = message.embeds[0]
                if any(field.name == "Personnage" and field.value.lower() == self.personnage.value.lower() for field in embed.fields):
                    await message.delete()
                    break
        
        # Créer un nouvel embed
        embed = discord.Embed(
            title=f"🪄 Artefact {self.nom.value.upper()}",
            color=0x8A2BE2,
            timestamp=datetime.now()
        )
        embed.add_field(name="Personnage", value=self.personnage.value, inline=True)
        embed.add_field(name="AVG", value=self.avg.value, inline=True)
        embed.add_field(name="Delta", value=self.delta.value, inline=True)
        embed.add_field(name="Patch", value=self.patch.value, inline=True)
        embed.set_footer(text=f"Mis à jour par {interaction.user.name}")
        
        await channel.send(embed=embed)
        await interaction.response.send_message(
            f"✅ Artefact **{self.nom.value.upper()}** mis à jour dans {channel.mention} !",
            ephemeral=True
        )


class GameModal(discord.ui.Modal, title="Enregistrer une Partie"):

    # -------------------------
    #   CONSTRUCTEUR
    # -------------------------
    def __init__(self, who):
        super().__init__()
        self.who = who

        # Champs du formulaire
        self.compo_placement = discord.ui.TextInput(
            label="Compo et Placement",
            placeholder="Ex : SG 3",
            required=True
        )
        self.augment1 = discord.ui.TextInput(label="Augment 1", required=True)
        self.augment2 = discord.ui.TextInput(label="Augment 2", required=True)
        self.augment3 = discord.ui.TextInput(label="Augment 3", required=True)
        self.patch = discord.ui.TextInput(label="Patch", required=True)

        # Ajouter les champs au modal
        self.add_item(self.compo_placement)
        self.add_item(self.augment1)
        self.add_item(self.augment2)
        self.add_item(self.augment3)
        self.add_item(self.patch)

    # -------------------------
    #   on_submit
    # -------------------------
    async def on_submit(self, interaction: discord.Interaction):
        # ----- 1. PARSING DE "COMPO + PLACEMENT" -----
        parts = self.compo_placement.value.strip().split()
        
        if len(parts) < 2:
            await interaction.response.send_message(
                "⚠️ Format invalide. Ex : `SG 3` ou `Frost 5`",
                ephemeral=True
            )
            return

        # On considère que la dernière partie est le placement
        compo_value = " ".join(parts[:-1])
        placement_value = parts[-1]

        # ----- 2. CONVERSION DU PLACEMENT EN INT -----
        try:
            placement_int = int(placement_value)
        except ValueError:
            placement_int = 9  # Défaut si non numérique

        guild = interaction.guild

        # ----- 3. CATÉGORIE + CHANNEL : "Parties" -----
        category = discord.utils.get(guild.categories, name="Parties")
        if not category:
            category = await guild.create_category("Parties")

        # ----- 4. CHANNEL "mesgames" -----
        mesgames = discord.utils.get(category.channels, name="mesgames")
        if not mesgames:
            mesgames = await category.create_text_channel("mesgames")

        # ----- 5. CHANNEL "autresgames" -----
        autresgames = discord.utils.get(category.channels, name="autregames")
        if not autresgames:
            autresgames = await category.create_text_channel("autregames")

        # ----- 6. COMPTER LES PARTIES -----
        count = 0
        async for _ in autresgames.history(limit=2000):
            count += 1

        # ----- 6. CRÉATION DE L'EMBED -----
        embed = discord.Embed(
            title=f"🎮 Game #{count + 1}",
            color=0x00FF00 if placement_int <= 4 else 0xFF0000,
            timestamp=datetime.now()
        )
        embed.add_field(name="Compo", value=compo_value.upper(), inline=True)
        embed.add_field(name="Placement", value=placement_value, inline=True)
        embed.add_field(name="Patch", value=self.patch.value, inline=True)
        embed.add_field(name="Augment 1", value=self.augment1.value, inline=False)
        embed.add_field(name="Augment 2", value=self.augment2.value, inline=False)
        embed.add_field(name="Augment 3", value=self.augment3.value, inline=False)

        if placement_int == 1:
            embed.set_footer(text=f"🏆 Victoire ! • {interaction.user.name}")
        elif placement_int <= 4:
            embed.set_footer(text=f"🎯 Top 4 ! • {interaction.user.name}")
        else:
            embed.set_footer(text=f"Joueur : {interaction.user.name}")

        # ----- 7. ENREGISTREMENT SELON LE TYPE -----
        if self.who == "moi":
            # → Le joueur veut enregistrer dans les deux salons
            await mesgames.send(embed=embed)
            await autresgames.send(embed=embed)
            await interaction.followup.send(
                f"🎮 Partie enregistrée dans {mesgames.mention} **et** {autresgames.mention} !",
                ephemeral=True
            )

        elif self.who == "autres":
            # → N'enregistre que dans AUTRES GAMES
            await autresgames.send(embed=embed)
            await interaction.followup.send(
                f"🎲 Partie enregistrée dans {autresgames.mention} !",
                ephemeral=True
            )

        else:
            await interaction.followup.send(
                "⚠️ Erreur interne : type de game inconnu.",
                ephemeral=True
            )


class ConditionModal(discord.ui.Modal, title='Ajouter une Condition'):
    """Modal pour ajouter une condition à une compo"""
    compo = discord.ui.TextInput(
        label='Nom de la compo',
        placeholder='Ex: Akali',
        required=True,
        max_length=20
    )
    condition_name = discord.ui.TextInput(
        label='Nom de la condition',
        placeholder='Ex: Nashor Radiant, Dawncore, 4 Supreme',
        required=True,
        max_length=50
    )
    placement = discord.ui.TextInput(
        label='Placement avec condition',
        placeholder='Ex: 4.11',
        required=True,
        max_length=10
    )

    async def on_submit(self, interaction: discord.Interaction):
        # Importer la fonction
        from utilitaires.conditions import get_compo_base_stats, create_conditions_channel, add_condition
        
        guild = interaction.guild
        
        # Récupérer les stats de base
        base_stats = await get_compo_base_stats(guild, self.compo.value)
        
        if not base_stats:
            await interaction.response.send_message(
                f"❌ Compo **{self.compo.value}** introuvable. Ajoutez d'abord la compo !",
                ephemeral=True
            )
            return
        
        # Créer/récupérer le channel conditions
        channel = await create_conditions_channel(guild, self.compo.value, base_stats)
        
        # Ajouter la condition
        success = await add_condition(
            channel,
            self.condition_name.value,
            self.placement.value,
            base_stats['placement']
        )
        
        if success:
            await interaction.response.send_message(
                f"✅ Condition **{self.condition_name.value}** ajoutée pour {self.compo.value} dans {channel.mention}",
                ephemeral=True
            )
        else:
            await interaction.response.send_message(
                "❌ Erreur lors de l'ajout de la condition.",
                ephemeral=True
            )


# ------------------------------
# Views (Buttons / Selects)
# ------------------------------

class MainMenu(discord.ui.View):
    """Menu principal avec tous les boutons"""
    def __init__(self):
        super().__init__(timeout=None)  # Pas de timeout
    
    @discord.ui.button(label='📊 Ajouter Compo', style=discord.ButtonStyle.primary, row=0, custom_id='tft_add_compo')
    async def add_compo(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = CompoModal()
        await interaction.response.send_modal(modal)
    
    @discord.ui.button(label='🪄 Ajouter Artefact', style=discord.ButtonStyle.primary, row=0, custom_id='tft_add_artefact')
    async def add_artefact(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = ArtefactModal()
        await interaction.response.send_modal(modal)
    
    @discord.ui.button(label='🔧 Ajouter Condition', style=discord.ButtonStyle.primary, row=0, custom_id='tft_add_condition')
    async def add_condition(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = ConditionModal()
        await interaction.response.send_modal(modal)
    
    @discord.ui.button(label="🎮 Enregistrer Ma Partie", style=discord.ButtonStyle.success, row=1)
    async def addmy_game(self, interaction, button):
        modal = GameModal(who="moi")
        await interaction.response.send_modal(modal)


    @discord.ui.button(label="🎲 Enregistrer Une Partie", style=discord.ButtonStyle.success, row=1)
    async def add_game(self, interaction, button):
        modal = GameModal(who="autres")
        await interaction.response.send_modal(modal)

    
    @discord.ui.button(label='📈 Générer Résumés', style=discord.ButtonStyle.secondary, row=2, custom_id='tft_summaries')
    async def generate_summaries(self, interaction: discord.Interaction, button: discord.ui.Button):
        view = SummaryMenu()
        await interaction.response.send_message(
            "Quel résumé voulez-vous générer ?",
            view=view,
            ephemeral=True
        )
    
    @discord.ui.button(label='🔍 Stats Augments', style=discord.ButtonStyle.secondary, row=2, custom_id='tft_stats')
    async def stats_augments(self, interaction: discord.Interaction, button: discord.ui.Button):
        view = AugmentStatsView()
        await interaction.response.send_message(
            "Configurez les filtres pour les stats d'augments :",
            view=view,
            ephemeral=True
        )
    
    @discord.ui.button(label='❓ Aide', style=discord.ButtonStyle.gray, row=2, custom_id='tft_help')
    async def help_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = create_help_embed(interaction.user)
        await interaction.response.send_message(embed=embed, ephemeral=True)


class SummaryMenu(discord.ui.View):
    """Menu pour choisir quel résumé générer"""
    def __init__(self):
        super().__init__(timeout=60)
    
    @discord.ui.select(
        placeholder='Choisissez un type de résumé...',
        options=[
            discord.SelectOption(label='Résumé Compos', description='Génère un résumé par tiers', emoji='📊'),
            discord.SelectOption(label='Résumé Artefacts', description='Liste tous les artefacts triés par AVG', emoji='🪄'),
            discord.SelectOption(label='Résumé Artefacts par Perso', description='Groupe les artefacts par personnage', emoji='👥'),
            discord.SelectOption(label='Résumé Conditions', description='Résumé des conditions d\'une compo', emoji='🔧'),
        ]
    )
    async def summary_select(self, interaction: discord.Interaction, select: discord.ui.Select):
        await interaction.response.send_message("Quel patch voulez-vous analyser ?", view=PatchInputView(select.values[0]), ephemeral=True)


class PatchInputView(discord.ui.View):
    """Vue pour entrer le patch"""
    def __init__(self, summary_type):
        super().__init__(timeout=60)
        self.summary_type = summary_type
    
    @discord.ui.button(label='Entrer le patch', style=discord.ButtonStyle.primary)
    async def patch_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = PatchModal(self.summary_type)
        await interaction.response.send_modal(modal)


class PatchModal(discord.ui.Modal, title='Entrer le Patch'):
    """Modal pour entrer le patch"""
    patch = discord.ui.TextInput(
        label='Patch',
        placeholder='Ex: 15.22',
        required=True,
        max_length=10
    )
    
    def __init__(self, summary_type):
        super().__init__()
        self.summary_type = summary_type
    
    async def on_submit(self, interaction: discord.Interaction):
        # Appelle la bonne fonction en fonction du choix
        if self.summary_type == 'Résumé Compos':
            # generate_compo_summary importé dynamiquement (voir bas)
            await generate_compo_summary(interaction, self.patch.value)
        elif self.summary_type == 'Résumé Artefacts':
            await generate_artefact_summary(interaction, self.patch.value)
        elif self.summary_type == 'Résumé Artefacts par Perso':
            await generate_artefact_perso_summary(interaction, self.patch.value)
        elif self.summary_type == 'Résumé Conditions':
            await generate_conditions_summary(interaction, self.patch.value)


class AugmentStatsView(discord.ui.View):
    """Vue pour configurer les stats d'augments"""
    def __init__(self):
        super().__init__(timeout=60)
        self.patch = "0"
        self.ordre = "0"
        self.compo = "0"
    
    @discord.ui.select(
        placeholder='Filtrer par patch...',
        options=[
            discord.SelectOption(label='Tous les patchs', value='0', default=True),
            discord.SelectOption(label='15.22', value='15.22'),
            discord.SelectOption(label='15.21', value='15.21'),
            discord.SelectOption(label='14.1', value='14.1'),
        ],
        row=0
    )
    async def patch_select(self, interaction: discord.Interaction, select: discord.ui.Select):
        self.patch = select.values[0]
        await interaction.response.edit_message(content=f"Patch: {self.patch} | Ordre: {self.ordre} | Compo: {self.compo}", view=self)
    
    @discord.ui.select(
        placeholder='Filtrer par ordre d\'augment...',
        options=[
            discord.SelectOption(label='Tous les augments', value='0', default=True),
            discord.SelectOption(label='Augment 1 seulement', value='1'),
            discord.SelectOption(label='Augment 2 seulement', value='2'),
            discord.SelectOption(label='Augment 3 seulement', value='3'),
        ],
        row=1
    )
    async def ordre_select(self, interaction: discord.Interaction, select: discord.ui.Select):
        self.ordre = select.values[0]
        await interaction.response.edit_message(content=f"Patch: {self.patch} | Ordre: {self.ordre} | Compo: {self.compo}", view=self)
    
    @discord.ui.button(label='Filtrer par compo', style=discord.ButtonStyle.secondary, row=2)
    async def compo_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = CompoFilterModal(self)
        await interaction.response.send_modal(modal)
    
    @discord.ui.button(label='Générer les stats', style=discord.ButtonStyle.success, row=3)
    async def generate_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await generate_augment_stats(interaction, self.patch, self.ordre, self.compo)


class CompoFilterModal(discord.ui.Modal, title='Filtrer par Compo'):
    """Modal pour entrer le nom de la compo"""
    compo = discord.ui.TextInput(
        label='Nom de la compo (0 pour toutes)',
        placeholder='Ex: SG ou 0',
        required=True,
        max_length=20,
        default='0'
    )
    
    def __init__(self, parent_view):
        super().__init__()
        self.parent_view = parent_view
    
    async def on_submit(self, interaction: discord.Interaction):
        self.parent_view.compo = self.compo.value
        await interaction.response.edit_message(
            content=f"Patch: {self.parent_view.patch} | Ordre: {self.parent_view.ordre} | Compo: {self.parent_view.compo}",
            view=self.parent_view
        )

# ------------------------------
# Aide (embed)
# ------------------------------

def create_help_embed(user: Optional[discord.User]):
    """Crée l'embed d'aide"""
    embed = discord.Embed(
        title="📖 Guide d'utilisation du TFT Bot",
        description="Interface graphique pour gérer vos stats TFT facilement !",
        color=0x00D9FF,
        timestamp=datetime.now()
    )
    
    embed.add_field(
        name="🎯 Comment utiliser le bot",
        value=(
            "1. Utilisez `/menu` pour afficher le menu principal\n"
            "2. Cliquez sur les boutons pour accéder aux fonctions\n"
            "3. Remplissez les formulaires qui apparaissent\n"
            "4. Vos données sont automatiquement organisées !"
        ),
        inline=False
    )
    
    embed.add_field(
        name="📊 Fonctionnalités principales",
        value=(
            "• **Ajouter Compo** : Enregistrez les stats d'une composition\n"
            "• **Ajouter Artefact** : Ajoutez un artefact et ses performances\n"
            "• **Ajouter Condition** : Ajoutez des conditions à une compo\n"
            "• **Enregistrer Partie** : Sauvegardez vos games avec augments\n"
            "• **Générer Résumés** : Créez des analyses par patch\n"
            "• **Stats Augments** : Analysez la performance des augments"
        ),
        inline=False
    )
    
    embed.add_field(
        name="💡 Astuces",
        value=(
            "• Pas besoin de créer les channels, le bot s'en charge\n"
            "• Les messages sont mis à jour automatiquement\n"
            "• Utilisez des virgules ou des points pour les nombres\n"
            "• Les résumés sont générés dans `#Résumé`"
        ),
        inline=False
    )
    
    embed.set_footer(text=f"Demandé par {user.name if user else 'Utilisateur'}")
    return embed

# ------------------------------
# Imports dynamiques pour éviter les cycles
# ------------------------------
# Ces fonctions sont définies dans les autres modules (compo.py, artefacts.py, parties.py, conditions.py).
# On les importe ici à la fin du fichier (import local) pour éviter les problèmes d'import circulaire.
try:
    from utilitaires.compo import generate_compo_summary
except Exception:
    async def generate_compo_summary(interaction, patch):
        await interaction.response.send_message("❌ Fonction generate_compo_summary non disponible (module compo non chargé).", ephemeral=True)

try:
    from utilitaires.artefacts import generate_artefact_summary, generate_artefact_perso_summary
except Exception:
    async def generate_artefact_summary(interaction, patch):
        await interaction.response.send_message("❌ Fonction generate_artefact_summary non disponible (module artefacts non chargé).", ephemeral=True)
    async def generate_artefact_perso_summary(interaction, patch):
        await interaction.response.send_message("❌ Fonction generate_artefact_perso_summary non disponible (module artefacts non chargé).", ephemeral=True)

try:
    from utilitaires.parties import generate_augment_stats
except Exception:
    async def generate_augment_stats(interaction, patch, ordre, compo):
        await interaction.response.send_message("❌ Fonction generate_augment_stats non disponible (module parties non chargé).", ephemeral=True)

try:
    from utilitaires.conditions import generate_conditions_summary
except Exception:
    async def generate_conditions_summary(interaction, compo):
        await interaction.response.send_message("❌ Fonction generate_conditions_summary non disponible (module conditions non chargé).", ephemeral=True)