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

    async def on_ready(self):
        print("Logged in as {}".format(self.user))
