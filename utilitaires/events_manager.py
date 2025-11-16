import json
import discord
from discord.ext import tasks
from datetime import datetime, timedelta
import pytz

TIMEZONE = pytz.timezone("Europe/Brussels")

class EventManager:
    def __init__(self, bot):
        self.bot = bot
        self.file = "events.json"
        self.load()

    # -----------------------------
    #       GESTION JSON
    # -----------------------------
    def load(self):
        try:
            with open(self.file, "r") as f:
                self.events = json.load(f)
        except:
            self.events = []

    def save(self):
        with open(self.file, "w") as f:
            json.dump(self.events, f, indent=4)

    # -----------------------------
    #   AJOUTER UN EVENT
    # -----------------------------
    async def add_event(self, ctx, name, date, repeat="none"):
        self.events.append({"name": name, "date": date, "repeat": repeat})
        self.save()
        await ctx.send(f"📌 Événement **{name}** ajouté !")

    # -----------------------------
    #   LISTE DES EVENTS
    # -----------------------------
    def list_events(self):
        return self.events

    async def list_events_cmd(self, ctx):
        if not self.events:
            return await ctx.send("Aucun événement enregistré.")
        msg = "**📅 Événements :**\n"
        for e in self.events:
            msg += f"- {e['name']} → {e['date']} ({e['repeat']})\n"
        await ctx.send(msg)

    # -----------------------------
    #   SUPPRIMER EVENT
    # -----------------------------
    async def delete_event(self, ctx, name):
        self.events = [e for e in self.events if e["name"] != name]
        self.save()
        await ctx.send(f"🗑️ Événement **{name}** supprimé.")

    # -----------------------------
    #   MODIFIER EVENT
    # -----------------------------
    async def edit_event(self, ctx, old_name, new_name=None, new_date=None, new_repeat=None):
        for e in self.events:
            if e["name"] == old_name:
                if new_name:
                    e["name"] = new_name
                if new_date:
                    e["date"] = new_date
                if new_repeat:
                    e["repeat"] = new_repeat
                self.save()
                return await ctx.send(f"✏️ Événement **{old_name}** modifié !")
        await ctx.send("❌ Aucun événement trouvé avec ce nom.")

    # -----------------------------
    #     CHECKLIST DU JOUR
    # -----------------------------
    async def send_checklist(self):
        guild = self.bot.guilds[0]

        # Catégorie Informations
        category_info = discord.utils.get(guild.categories, name="Informations")
        if not category_info:
            category_info = await guild.create_category("Informations")

        # Salon discipline
        channel = discord.utils.get(category_info.text_channels, name="discipline")
        if not channel:
            channel = await guild.create_text_channel("discipline", category=category_info)

        now = datetime.now(TIMEZONE)
        today = now.date()

        embed = discord.Embed(
            title="📋 Checklist du jour",
            description="Voici les tâches prévues aujourd’hui :",
            color=discord.Color.blurple()
        )

        buttons = []
        remaining_events = []

        for e in self.events:
            dt = datetime.fromisoformat(e["date"])
            dt = TIMEZONE.localize(dt)

            if dt.date() == today:
                embed.add_field(name=e["name"], value=f"🕒 {dt.time()}", inline=False)

                b = discord.ui.Button(
                    label=f"✔️ {e['name']}",
                    style=discord.ButtonStyle.green,
                    custom_id=f"done_{e['name']}"
                )
                buttons.append(b)
            else:
                remaining_events.append(e)

        view = discord.ui.View(timeout=None)

        for b in buttons:
            async def done_callback(interaction, event_name=b.custom_id.replace("done_", "")):
                self.events = [ev for ev in self.events if ev["name"] != event_name]
                self.save()
                await interaction.response.send_message(f"✔️ **{event_name}** fait !", ephemeral=True)

            b.callback = done_callback
            view.add_item(b)

        await channel.send(embed=embed, view=view)

        # Répétition hebdo
        new_events = []
        for e in self.events:
            dt = datetime.fromisoformat(e["date"])
            dt = TIMEZONE.localize(dt)

            if e["repeat"] == "weekly" and dt.date() == today:
                next_week = dt + timedelta(days=7)
                new_events.append({"name": e["name"], "date": next_week.isoformat(), "repeat": "weekly"})

        self.events = remaining_events + new_events
        self.save()

    # -----------------------------
    #   REPORTER LES NON-FAITS
    # -----------------------------
    async def report_unfinished(self):
        now = datetime.now(TIMEZONE)
        today = now.date()

        new_events = []

        for e in self.events:
            dt = datetime.fromisoformat(e["date"])
            dt = TIMEZONE.localize(dt)

            if dt.date() < today:  # non fait hier
                new_date = datetime.combine(today + timedelta(days=1), dt.time())
                new_date = TIMEZONE.localize(new_date)

                new_events.append({
                    "name": e["name"],
                    "date": new_date.isoformat(),
                    "repeat": e["repeat"]
                })
            else:
                new_events.append(e)

        self.events = new_events
        self.save()

    # -----------------------------
    #   TASK AUTOMATIQUE 08:00
    # -----------------------------
    def setup_scheduler(self, bot):
        @tasks.loop(minutes=1)
        async def scheduler():
            now = datetime.now(TIMEZONE)
            if now.hour == 8 and now.minute == 0:
                await self.send_checklist()
                await self.report_unfinished()

        @scheduler.before_loop
        async def before():
            await self.bot.wait_until_ready()

        scheduler.start()

    # -----------------------------
    # COMMANDES POUR TESTER
    # -----------------------------
    async def send_checklist_now(self, ctx):
        await self.send_checklist()
        await ctx.send("📨 Checklist envoyée !")
