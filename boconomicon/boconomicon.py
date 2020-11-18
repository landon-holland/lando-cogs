from redbot.core import commands, checks, Config
from redbot.core.bot import Red
import discord
from random import random


class Boconomicon(commands.Cog):
    """Boconomicon"""

    def __init__(self, bot: Red):
        self.bot = bot
        # Default config for all guilds with random identifier
        self.config = Config.get_conf(self, identifier=9988776655)
        default_guild = {
            "enabled": False,
            "chance": 20,
            "length": 5,
            "triggers": [
                "ca",
                "ce",
                "ci",
                "co",
                "cu",
                "cho",
                "cha",
                "chi"
            ],
            "overrides": {
                "necronomicon": "boconomicon",
                "economy": "boconomy",
                "vocabulary": "bocabulary",
                "algorithm": "boalgorithm",
            }
        }
        self.config.register_guild(**default_guild)

    async def generate_cache(self):
        self.boconomicon_cache = await self.config.all_guilds()

    def cog_unload(self):
        if self.boconomicon_cache is not None:
            self.boconomicon_cache.clear()

    @commands.command()
    @commands.guild_only()
    @checks.mod()
    async def boconomicon(self, ctx: commands.Context):
        """Toggles Boconomicon"""
        msg = ""
        if await self.config.guild(ctx.guild).enabled() == False:
            await self.config.guild(ctx.guild).enabled.set(True)
            msg = "You reach out and open the Boconomicon, releasing an unspeakable horror into the world."
        else:
            await self.config.guild(ctx.guild).enabled.set(False)
            msg = "You quickly shut the Boconomicon, sealing away the lingering, dark spirits inside."
        embed = discord.Embed(color=await ctx.embed_color(), title="Boconomicon")
        embed.description = msg
        embed.set_thumbnail(
            url="https://media.discordapp.net/attachments/169189973805891584/778386157633404938/boconomicon.png?width=460&height=460")
        await ctx.send(embed=embed)
        await self.generate_cache()

    @commands.group(aliases=["bset"])
    @commands.guild_only()
    @checks.mod()
    async def boconomiconset(self, ctx: commands.Context):
        """Adjust Boconomicon settings"""
        pass

    @boconomiconset.command(name="chance")
    async def boconomiconset_chance(self, ctx: commands.Context, chance: int):
        """Sets the chance of Boconomicon replacing a word. The chance will be 1/`chance`."""
        if (chance <= 0):
            await ctx.send("Chance must be a positive.")
        else:
            await self.config.guild(ctx.guild).chance.set(chance)
            await ctx.send("Chance now set to 1/{0}".format(chance))
        await self.generate_cache()

    @boconomiconset.command(name="length")
    async def boconomiconset_length(self, ctx: commands.Context, length: int):
        """Sets the minimum length required for Boconomicon to replace a word."""
        if (length < 2):
            await ctx.send("Length must be greater than 2.")
        else:
            await self.config.guild(ctx.guild).length.set(length)
            await ctx.send("Minimum length now set to {0}".format(length))
        await self.generate_cache()

    @boconomiconset.group(name="trigger", alias=["triggers"])
    async def boconomiconset_trigger(self, ctx: commands.Context):
        """Add or remove triggers for Boconomicon"""
        if not ctx.invoked_subcommand:
            embed = discord.Embed(color=await ctx.embed_color(), title="Current triggers")
            msg = ""
            triggers = await self.config.guild(ctx.guild).triggers()
            for trigger in triggers:
                msg += trigger + "\n"
            embed.description = msg
            await ctx.send(embed=embed)

    @boconomiconset_trigger.command(name="add")
    async def boconomiconset_trigger_add(self, ctx: commands.Context, trigger: str):
        """Add trigger to Boconomicon"""
        async with self.config.guild(ctx.guild).triggers() as trigger_list:
            trigger_list.append(trigger)
        await ctx.send("Trigger `{0}` successfully added.".format(trigger))
        await self.generate_cache()

    @boconomiconset_trigger.command(name="remove")
    async def boconomiconset_trigger_remove(self, ctx: commands.Context, trigger: str):
        """Remove trigger from Boconomicon"""
        async with self.config.guild(ctx.guild).triggers() as trigger_list:
            try:
                trigger_list.remove(trigger)
                await ctx.send("Trigger `{0}` successfully removed.".format(trigger))
            except ValueError:
                await ctx.send("Trigger `{0}` is already not a trigger.".format(trigger))
        await self.generate_cache()

    @boconomiconset.group(name="override", alias=["overrides"])
    async def boconomiconset_override(self, ctx: commands.Context):
        """Add or remove overrides for Boconomicon"""
        if not ctx.invoked_subcommand:
            embed = discord.Embed(color=await ctx.embed_color(), title="Current overrides")
            msg = ""
            overrides = await self.config.guild(ctx.guild).overrides()
            for word, override in overrides.items():
                msg += "`{0}`: `{1}`\n".format(word, override)
            embed.description = msg
            await ctx.send(embed=embed)

    @boconomiconset_override.command(name="add", alias=["edit"])
    async def boconomiconset_override_add(self, ctx: commands.Context, keyword: str, replacement: str):
        """Add or edit override to Boconomicon"""
        async with self.config.guild(ctx.guild).overrides() as override_list:
            override_list[keyword] = replacement
        await ctx.send("`{0}` will now be replaced by `{1}`.".format(keyword, replacement))
        await self.generate_cache()

    @boconomiconset_override.command(name="remove")
    async def boconomiconset_override_remove(self, ctx: commands.Context, keyword: str):
        """Remove override from Boconomicon"""
        async with self.config.guild(ctx.guild).overrides() as override_list:
            try:
                del override_list[keyword]
                await ctx.send("Override `{0}` successfully removed.".format(keyword))
            except KeyError:
                await ctx.send("Override `{0}` is already not an override.".format(keyword))
        await self.generate_cache()

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        data = self.boconomicon_cache.get(message.guild.id)
        if not data["enabled"]:
            return
        if message.author.bot:
            return
        if message.content.startswith(tuple(await self.bot.get_valid_prefixes())):
            return
        if (random() >= 1 / data["chance"]):
            return
        words = message.content.split()
        msg = ""
        changes = False
        for word in words:
            if word in data["overrides"]:
                msg += data["overrides"][word]
                changes = True
            elif word.lower().startswith(tuple(data["triggers"])):
                msg += "bo" + word
                changes = True
            else:
                msg += word
            msg += " "
        if changes:
            await message.channel.send(msg)
