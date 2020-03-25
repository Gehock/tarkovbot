from discord import Message
from discord.ext.commands import Cog

from tarkovbot import Tarkovbot


class DMSnitch(Cog):

    def __init__(self, bot: Tarkovbot):
        self.bot = bot

    @Cog.listener()
    async def on_message(self, message: Message):
        if message.author == self.bot.user:
            return
        if message.guild is None:
            if message.content[0] == self.bot.command_prefix:
                if message.content[1:].split(' ')[0] in self.bot.command_names:
                    return
            owner = self.bot.owner
            await owner.send("DM: [{}]: {}".format(
                message.author, message.content))


def setup(bot: Tarkovbot):
    bot.add_cog(DMSnitch(bot))
