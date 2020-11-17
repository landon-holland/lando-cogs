from .boconomicon import Boconomicon


async def setup(bot):
    cog = Boconomicon(bot)
    await cog.generate_cache()
    bot.add_cog(cog)
