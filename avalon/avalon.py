from redbot.core import commands, checks
import discord


class Avalon(commands.Cog):
    """Avalon"""

    def __init__(self):
        self.players = []
        self.readyPlayers = []
        self.minPlayers = 5
        self.maxPlayers = 10
        self.playerRoles = {}
        self.questNum = 1
        self.gameStatus = 0  # 0: No Game. 1: Intermission. 2: In game

    def makeEmbed(self, title, color, name, value):
        embed = discord.Embed(title=title, color=color)
        embed.add_field(name=name,
                        value=value,
                        inline=False)

        return embed

    async def checkPM(self, message):
        # TODO fix this
        # Checks if we're talking in PM, and if not - outputs an error
        if isinstance(message.channel, discord.abc.PrivateChannel):
            # PM
            return True
        else:
            # Not in PM
            await message.channel.send(embed=self.makeEmbed('Avalon', 0xff4055, 'Error', 'This command must be used in PMs.'))
            return False

    # Guild commands
    @commands.group()
    @commands.guild_only()
    async def avalon(self, ctx):
        """Main Avalon command"""
        pass

    @avalon.command()
    @commands.guild_only()
    async def start(self, ctx):
        """Start game of Avalon"""
        self.players = [ctx.message.author.id]
        self.readyPlayers = []
        self.playerRoles = {}
        self.questNum = 1
        self.gameStatus = 1
        await ctx.send(embed=self.makeEmbed('Avalon', 0x77dd77, 'Starting...', 'Starting game of Avalon in PMs...'))
        # TODO PM

    @avalon.command()
    @commands.guild_only()
    async def join(self, ctx):
        """Join existing game of Avalon"""
        if len(self.players) > self.maxPlayers:
            await ctx.send(embed=self.makeEmbed('Avalon', 0xff4055, 'Error', 'Already 10 players in game.'))
            return
        if self.gameStatus == 0:
            await ctx.send(embed=self.makeEmbed('Avalon', 0xff4055, 'Error', 'You must start a game first.'))
            return
        elif self.gameStatus == 2:
            await ctx.send(embed=self.makeEmbed('Avalon', 0xff4055, 'Error', 'Game is already in progress.'))
            return
        if ctx.message.author.id in self.players:
            await ctx.send(embed=self.makeEmbed('Avalon', 0xff4055, 'Error', 'You are already in the game.'))
            return

        self.players.append(ctx.message.author.id)
        # TODO PM
        # TODO PM everyone who is already in the game
        await ctx.send(embed=self.makeEmbed('Avalon', 0x77dd77, 'Joined', 'You have joined the game. Check PMs!'))

    @avalon.command()
    @commands.guild_only()
    @checks.mod()
    async def stop(self, ctx):
        """Stop game of Avalon"""
        if self.gameStatus == 0:
            await ctx.send(embed=self.makeEmbed('Avalon', 0xff4055, 'Error', 'No game in progress.'))
            return
        self.gameStatus = 0
        await ctx.send(embed=self.makeEmbed('Avalon', 0x77dd77, 'Stopped', 'Current game of Avalon stopped'))

    # PM commands
    @avalon.command()
    async def leave(self, ctx):
        """Leave game of Avalon during intermission"""
        if not await self.checkPM(ctx.message):
            return
        if ctx.message.author.id not in self.players:
            await ctx.send(embed=self.makeEmbed('Avalon', 0xff4055, 'Error', 'You are not in a game..'))
            return
        if self.gameStatus == 0:
            await ctx.send(embed=self.makeEmbed('Avalon', 0xff4055, 'Error', 'No game in progress.'))
            return
        elif self.gameStatus == 2:
            await ctx.send(embed=self.makeEmbed('Avalon', 0xff4055, 'Error', 'You can not leave an in progress game.'))
            return
        self.players.remove(ctx.author.id)
        await ctx.send(embed=self.makeEmbed('Avalon', 0x77dd77, 'Avalon', 'You have successfully left the game.'))

    @avalon.command()
    async def ready(self, ctx):
        """Ready up for Avalon game"""
        if not await self.checkPM(ctx.message):
            return
        if ctx.author.id in self.readyPlayers:
            await ctx.send(embed=self.makeEmbed('Avalon', 0xff4055, 'Error', 'You are already ready.'))
            return
        self.readyPlayers.append(ctx.message.author.id)
        await ctx.send(embed=self.makeEmbed('Avalon', 0x77dd77, 'Joined', 'You have readied up!'))

        # TODO PM everyone that you readied up

    @avalon.command()
    async def unready(self, ctx):
        """Unready for Avalon game"""
        if not await self.checkPM(ctx.message):
            return
        if ctx.author.id not in self.readyPlayers:
            await ctx.send(embed=self.makeEmbed('Avalon', 0xff4055, 'Error', 'You aren\'t ready.'))
            return
        self.readyPlayers.remove(ctx.author.id)
        await ctx.send(embed=self.makeEmbed('Avalon', 0x77dd77, 'Avalon', 'You have unreadied.'))
