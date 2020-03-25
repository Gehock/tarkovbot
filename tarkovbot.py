from discord.ext.commands import Bot

extensions = [
    'commands',
    'dmsnitch',
]


class Tarkovbot(Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.owner = None
        self.comand_names = []

        self.load_extension('reload')
        for extension in extensions:
            self.load_extension(extension)

    def fetch_data(self) -> None:
        if self.owner_id is None:
            if len(self.owner_ids) > 0:
                self.owner = self.get_user(self.owner_ids[0])
            else:
                from secret import ADMIN
                self.owner_id = ADMIN
        self.owner = self.get_user(self.owner_id)
        self.command_names = [command.name for command in self.commands]

    async def on_ready(self):
        print("Logged in as {}".format(self.user))
        await self.wait_until_ready()
        self.fetch_data()
