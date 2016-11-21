import asyncio

from dcbot.config import Config
from dcbot.jsonhelper import JSONHelper
from dcbot.constants import *

import discord

import traceback


class DestinyChildBot(discord.Client):
    def __init__(self, config_file='Config/config.ini'):
        self.config = Config(config_file)
        self.json = JSONHelper("resources/children.json")
        super().__init__()

    def run(self):
        super().run(self.config.token)

    async def on_error(self, event, *args, **kwargs):
        traceback.print_exc()

    async def on_ready(self):
        print("Successfully connected!")

    async def on_message(self, message):
        print("[{}]@{}:{}".format(message.server, message.channel, message.content))
        if message.author == self.user:
            return

        content = message.content.strip()  # type: str

        if content.startswith(self.config.command_trigger):  # command parser
            command, *args = content.split()
            command = command[len(self.config.command_trigger):].lower().strip()

            cmd_func = getattr(self, 'c_{}'.format(command))

            await cmd_func()

        tindex = content.find(self.config.trigger)
        if tindex == -1:
            return
        lex = tindex+len(self.config.trigger)
        if content[lex] == self.config.lextender:
            rex = content.find(self.config.rextender, lex+1)
            word = content[lex+1: rex]
        else:
            end = content.find(' ', tindex)
            word = content[tindex+1: None if end == -1 else end]
        print("Found a trigger;", word)
        try:  # check if it's the id as keyword
            as_int = int(word)
            await self.send_childinfo(message.channel, as_int)
        except ValueError:
            await self.send_childinfo(message.channel, word)

    async def send_childinfo(self, dest, identifier):
        c = self.json.get_child_by_identifier(identifier)
        ele_color = {Attribute.fire.value: 0xFF331C, Attribute.dark.value: 0x7C4E98, Attribute.light.value: 0xFFFFFF,
                     Attribute.forest.value: 0x00FF00, Attribute.water.value: 0x2691E4}
        if c is not None:
            if not self.config.debug:
                emb = discord.Embed(type='rich', colour=ele_color[c[JSON_ATTRIBUTE_ID]])
                emb.set_author(name="{} - {}[{}⭐]".format(c[JSON_NAME], c[JSON_EN_NAME], c[JSON_RARITY]))
                emb.description = "Role: {} | Element: {}".format(Role(c[JSON_ROLE_ID]).name.capitalize()
                                                                  , Attribute(c[JSON_ATTRIBUTE_ID]).name.capitalize())
                emb.add_field(name='HP', value=c[JSON_STAT_HP], inline=False)
                emb.add_field(name='Attack', value=c[JSON_STAT_ATK], inline=False)
                emb.add_field(name='Agility', value=c[JSON_STAT_AGI], inline=False)
                emb.add_field(name='Defense', value=c[JSON_STAT_DEF], inline=False)
                emb.add_field(name='Critical', value=c[JSON_STAT_CRIT], inline=False)
                emb.set_thumbnail(url="{}{}_i.png".format(INVEN_IMAGE_URL, c[JSON_INVEN_ID]))
                return await self.send_message(dest, embed=emb)
            return await self.send_message(dest, c)

    async def c_create_child_entry(self, **kwargs):
        self.json.add_entry(kwargs)

    async def c_reload_json(self):
        self.json = JSONHelper("resources/children.json")

    async def c_debug(self):
        self.config.debug = not self.config.debug
        print("Debug toggled to", self.config.debug)

    async def c_logout(self):
        self.logout()
