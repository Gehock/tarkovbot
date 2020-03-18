from discord.ext.commands import Bot

extensions = [
    'commands',
]


class Tarkovbot(Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.load_extension('reload')
        for extension in extensions:
            self.load_extension(extension)

        @self.check
        async def globally_block_dms(ctx):
            return ctx.guild is not None

    async def on_ready(self):
        print("Logged in as {}".format(self.user))
