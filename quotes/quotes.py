from redbot.core import commands, Config
from redbot.core.bot import Red
import discord


class Quotes(commands.Cog):
    """Quotes cog"""

    def __init__(self, bot: Red):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=8707089453709)
        default_guild = {"quotes": []}
        self.config.register_guild(**default_guild)

    async def generate_cache(self):
        self.quotes = await self.config.all_guilds()

    @commands.command()
    async def quote(self, ctx: commands.Context, *, author_or_num=None):
        """Say a quote.
        No arguments: Random quote
        Author: Random quote from author
        ID: Quote with given ID"""

        quote_list = self.quotes.get(ctx.guild.id)["quotes"]

        if len(quote_list) == 0:
            ctx.send("No quotes in guild.")
            return

        print(type(author_or_num))

        if type(author_or_num) is discord.Member:
            quote = self.get_quote_by_author(ctx, author_or_num)
        else:
            try:
                quoteid = int(author_or_num)
                quote = self.get_quote_by_id(ctx, quoteid)
            except ValueError:
                quote = self.get_quote_by_name(ctx, author_or_num)

    def get_quote_by_author(self, ctx: commands.Context, author: discord.Member):
        quotes = [(i, q) for i, q in enumerate(self.quotes.get(
            ctx.guild.id)["quotes"]) if q['author_id'] == author.id]
        print(quotes)
