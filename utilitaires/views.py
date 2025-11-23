import discord
from discord.ui import View, Button
from modals import CompoModal, BuildModal, ArtefactModal, RadiantModal, ConditionsModal


class MenuView(View):
    def __init__(self, tft_sheets):
        super().__init__(timeout=180)
        self.tft = tft_sheets
    
    @discord.ui.button(label="📊 Compo", style=discord.ButtonStyle.primary, row=0)
    async def button_compo(self, interaction: discord.Interaction, button: Button):
        await interaction.response.send_modal(CompoModal(self.tft))
    
    @discord.ui.button(label="🎒 Build", style=discord.ButtonStyle.success, row=0)
    async def button_build(self, interaction: discord.Interaction, button: Button):
        await interaction.response.send_modal(BuildModal(self.tft))
    
    @discord.ui.button(label="✨ Artefact", style=discord.ButtonStyle.secondary, row=0)
    async def button_artefact(self, interaction: discord.Interaction, button: Button):
        await interaction.response.send_modal(ArtefactModal(self.tft))
    
    @discord.ui.button(label="💎 Radiant", style=discord.ButtonStyle.secondary, row=1)
    async def button_radiant(self, interaction: discord.Interaction, button: Button):
        await interaction.response.send_modal(RadiantModal(self.tft))
    
    @discord.ui.button(label="📋 Conditions", style=discord.ButtonStyle.danger, row=1)
    async def button_conditions(self, interaction: discord.Interaction, button: Button):
        await interaction.response.send_modal(ConditionsModal(self.tft))