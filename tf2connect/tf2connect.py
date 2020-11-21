from redbot.core import commands, Config, checks
import discord


class TF2Connect(commands.Cog):
    """TF2 Connect Info"""

    def __init__(self):
        self.config = Config.get_conf(self, identifier=111111111)

        default_guild = {
            "channels": []
        }

        self.config.register_guild(**default_guild)

    @commands.command()
    @commands.guild_only()
    @checks.admin()
    async def tf2connect(self, ctx):
        """Enables or disables TF2Connect in current channel"""

        config = self.config.guild(ctx.guild)
        channels = await self.config.guild(ctx.guild).channels()
        msg = ""
        if ctx.channel.id in channels:
            msg = "Disabled in `#{0}`".format(ctx.channel.name)
            async with config.channels() as channels:
                channels.remove(ctx.channel.id)
        else:
            msg = "Enabled in `#{0}`".format(ctx.channel.name)
            async with config.channels() as channels:
                channels.append(ctx.channel.id)
        embed = discord.Embed(color=await ctx.embed_color(), title="TF2Connect")
        embed.description = msg
        await ctx.send(embed=embed)

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        channels = await self.config.guild(message.guild).channels()
        if message.channel.id not in channels:
            return
        msg = message.content.strip()
        if msg.startswith("connect"):
            ip = msg[8:msg.index(';')]
            password = msg[msg.index('password') + 9:]
            embed = discord.Embed(color=0xcf7336, title="TF2Connect")
            embed.description = "steam://connect/{0};password/{1}".format(
                ip, password)
            await message.channel.send(embed=embed)
