from library.my_Exceptions.validator import NonOwnedCharacter, NonExistentCharacter
from nextcord.ext.commands.core import guild_only, is_nsfw
from nextcord.ext.commands import command, cooldown
from library import user_guild_cooldown
from nextcord.ext.commands import Cog
from nextcord.channel import DMChannel
from nextcord.errors import NotFound
from random import choice, randrange
from collections import namedtuple
from library import data
from library import db
from json import loads
from re import sub
import nextcord
import logging


class Ark(Cog):
    qualified_name = 'Ark'
    description = 'Рулетка с дефками'

    def __init__(self, bot):
        self.bot = bot
        self.__db = db

        self.__six_star_chance, self.__five_star_chance, \
            self.__four_star_chance, self.__three_star_chance = data.get_ark_chances

        self.__stars_0_5 = "<:star:801095671720968203>"
        self.__stars_6 = "<:star2:801105195958140928>"

        with open("library/config/character_table.json", "rb") as character_json:
            self.characters_data = loads(character_json.read())

        with open("library/config/skin_table.json", "rb") as skin_json:
            self.skin_data = loads(skin_json.read())['charSkins']

    # cog commands --------------------------------------------------------------------------------------------------------------

    @command(name="myark", aliases=["моидевочки", "майарк"],
             brief='Вывести твою коллекцию сочных аниме девочек(и кунчиков ^-^)',
             description='Вывести твою коллекцию сочных аниме девочек(и кунчиков ^-^). '
             'Отправлю этот списочек прямой посылочкой в твои ЛС, братик. А если ты укажешь имя песонажа я покажу его карточку')
    async def myark(self, ctx, *char_name):
        """
        This command sends ark collection to private messages.\n
        If collection empty -> returns 'Empty collection'
        """
        char_name = " ".join(char_name)
        ark_collection = self.get_ark_collection(ctx.message.author.id)

        if char_name == "":
            all_character_count = self.get_ark_count()
            user_chara_count = sum([len(characters) for characters in ark_collection.values()])
            collection_message = nextcord.Embed(title=f"{ctx.author.display_name}'s collection {user_chara_count}/{all_character_count} \
                                              ({round((user_chara_count/all_character_count)*100,2)}%)", color=data.get_embed_color)
            for rarity, characters in ark_collection.items():
                characters_list = "\n".join([f"{character[1]} x {character[2]}" for character in characters])
                collection_message.add_field(name=":star:"*rarity if rarity < 6 else ":star2:"*rarity, value=characters_list, inline=False)
            if len(ark_collection) == 0:
                collection_message.add_field(name="Ти бомж", value="иди покрути девочек!")
            collection_message.set_footer(text="Используй команду !майарк <имя> чтоб посмотреть на персонажа.")
            await ctx.message.author.send(embed=collection_message)
        else:
            try:
                embed, selector = self.ark_embed_and_view(self.show_character(char_name, ctx.message.author.id), ctx.message)
                selector.message = await ctx.message.author.send(embed=embed, view=selector)
            except NonOwnedCharacter:
                await ctx.message.author.send("***Лох, у тебя нет такой дивочки***")
            except NonExistentCharacter:
                await ctx.message.author.send("***Лошара, даже имя своей вайфу не запомнил((***")
        if not isinstance(ctx.message.channel, DMChannel):
            await ctx.message.delete()

    @is_nsfw()
    @guild_only()
    @command(name="barter", aliases=["обмен"],
             brief='Обменять много хуевых персов на мало пиздатых',
             description='Обменять 5 дубликатов персонажей на 1 персонажа с более высоким уровнем редкости, йо.')
    async def barter(self, ctx):
        """
        Serves to exchange 5 characters for 1 rank higher\n
        if possible else returns 'Нет операторов на обмен'
        """
        barter_list = self.get_barter_list(ctx.message.author.id)
        if barter_list:
            barter = self.ark_barter(barter_list, ctx.message.author.id)
            try:
                new_char = next(barter)

                while new_char:
                    embed, selector = self.ark_embed_and_view(new_char, ctx.message)
                    selector.message = await ctx.message.channel.send(embed=embed, view=selector)
                    new_char = next(barter)
            except StopIteration:
                pass
        else:
            await ctx.send("***Нет операторов на обмен***", delete_after=15)
            await ctx.message.delete(delay=15)

    @is_nsfw()
    @guild_only()
    @cooldown(1, data.get_ark_cooldown, user_guild_cooldown)
    @command(name="ark", aliases=["арк"],
             brief='Твоя любимая команда',
             description='Кидает рандомную девочку (но это не точно, там и трапики есть, ня) и сохраняет её'
             ', чтобы ты потом мог ее посмотреть при помощи команды myark, ну или обменять если ты её не любишь(')
    async def ark(self, ctx):
        """
        Return a random arknigts character (from character_table.json)
        """
        character_data = self.roll_random_character(ctx.message.author.id)
        embed, selector = self.ark_embed_and_view(character_data, ctx.message)
        selector.message = await ctx.message.channel.send(embed=embed, view=selector)

    def ark_embed_and_view(self, character_data, message):
        """
        Generates embed form recieved ark data

        Args:
            character_data (list): random character data from character_table.json
            message (nextcord.message): message
        """
        embed = nextcord.Embed(color=data.get_embed_color, title=character_data.name,
                               description=str(character_data.stars) * character_data.rarity,
                               url=f"https://aceship.github.io/AN-EN-Tags/akhrchars.html?opname={character_data.name}")
        embed.add_field(name="Description", value=f"{character_data.description_first_part}\n{character_data.description_sec_part}",
                        inline=False)
        embed.add_field(name="Position", value=character_data.position)
        embed.add_field(name="Tags", value=str(character_data.tags), inline=True)
        line = sub("[<@.>/]", "", character_data.traits)  # Delete all tags in line
        embed.add_field(name="Traits", value=line.replace("bakw", ""), inline=False)
        embed.set_thumbnail(url=character_data.profession)
        embed.set_image(url=f"https://aceship.github.io/AN-EN-Tags/img/characters/{character_data.character_id}_1.png")
        embed.set_footer(text=f"Requested by {message.author.display_name}")
        return embed, Ark.SkinSelector(self.get_skin_list(character_data.character_id), data.get_chat_misc_cooldown_sec)

    class SkinSelector(nextcord.ui.View):
        message: nextcord.Message

        def __init__(self, skins: list, timeout=180):
            super().__init__(timeout=timeout)
            self.skin_select.options = []
            for skin in skins:
                self.skin_select.options.append(nextcord.SelectOption(label=skin.name, description=skin.desc, value=skin.id))

        async def on_timeout(self) -> None:
            try:
                await self.message.edit(view=None)
            except NotFound as e:
                logging.warning(e)
            return await super().on_timeout()

        @nextcord.ui.select(placeholder='Choose skin', min_values=1, max_values=1, options=[])
        async def skin_select(self, select: nextcord.ui.Select, interaction: nextcord.Interaction):
            assert interaction.message.embeds
            new_image_url = interaction.data.get('values', [''])[0].replace('#', '%23')
            new_embed = interaction.message.embeds[0].set_image(
                url=f"https://aceship.github.io/AN-EN-Tags/img/characters/{new_image_url}.png")
            await interaction.response.edit_message(embed=new_embed)

    # functions --------------------------------------------------------------------------------------------------------------------

    def get_skin_list(self, character_id) -> namedtuple:
        skinTyple = namedtuple('skin', ['id', 'name', 'desc'])
        skin_list = []
        for skin in self.skin_data.values():
            if skin['charId'] == character_id:
                skin_list.append(skinTyple._make((skin['portraitId'],
                                                  f"{skin['displaySkin']['skinName']}" if skin['displaySkin'][
                                                      'skinName'] else f"{skin['displaySkin']['modelName']}#{skin['portraitId'].split('_')[-1]}",
                                                  skin['displaySkin']['skinGroupName'])))
        return skin_list

    def get_ark_collection(self, collection_owner_id: int) -> dict:
        """
        This function returns all ark collection

        Args:
            collection_owner_id (message.autthor.id): requestor id

        Returns:
            dict: requestor characters collection
        """
        requestor_collection = sorted(self.__db.extract(
            f"""SELECT rarity, operator_name, operator_count FROM users_ark_collection
                WHERE user_id == '{collection_owner_id}'"""))

        out_list = {}
        if requestor_collection is None:
            return {}
        for character in requestor_collection:
            if character[0] not in out_list.keys():  # filling  the out_list with rarity lists
                out_list[character[0]] = list()
            out_list[character[0]].append(character)

        return out_list

    def get_barter_list(self, author_id: int) -> list:
        """
        Creates list of characters for barter

        Args:
            author_id (message.author.id): requestor id

        Returns:
            list: list that contains quantity and character stars
        """
        res = sorted(self.__db.extract(f"""SELECT rarity, operator_count, operator_name FROM users_ark_collection
                                         WHERE user_id == '{author_id}' AND operator_count >= 6 """))

        barter_list = []
        for rarity, count, _ in res:
            if rarity < 6 and count > 5:
                if count % 5 != 0:
                    new_char_quantity = count % 5
                elif count % 5 == 0:
                    new_char_quantity = (count // 5) - 1
                else:
                    pass

                barter_list.append([rarity + 1, new_char_quantity])

                self.__db.alter(f"""UPDATE users_ark_collection SET operator_count =
                                CASE
                                    WHEN operator_count % 5 != 0  THEN operator_count % 5
                                    WHEN operator_count  % 5 == 0 THEN 5
                                    ELSE operator_count
                                END
                                WHERE rarity < 6 AND operator_count > 5 AND user_id ='{author_id}'""")

        return barter_list

    def ark_barter(self, barter_list: list, author_id: int) -> tuple:
        """
        Exchanges characters and calls function to add them to db

        Args:
            barter_list (list): list that contains quantity and character stars
            author_id (int): requestor id

        Yields:
            str: random character
        """
        for operators in barter_list:
            for _ in range(0, operators[1]):
                character = self.__return_new_character(operators[0])
                self.__add_ark_to_db(author_id, character.name, character.rarity)
                yield character

    def get_ark_count(self) -> int:
        """
        Returns counter of all possible characters

        Returns:
            int: count of all possible characters
        """
        count = 0
        json_data = self.characters_data
        for line in json_data.values():
            if line["rarity"] >= 2 and line["itemDesc"] is not None:
                count += 1
        return count

    def roll_random_character(self, author_id: int) -> tuple:
        """
        Calls function that adds character to db

        Args:
            author_id (message.author.id): requestor id

        Returns:
            list: random character data
        """
        new_character = self.__return_new_character(self.__get_ark_rarity())

        self.__add_ark_to_db(author_id, new_character.name, new_character.rarity)
        return new_character

    def __get_ark_rarity(self) -> int:
        """
        Returns random character rarity
        """
        rarity = randrange(0, 100000)
        if rarity <= self.__six_star_chance * 1000:
            return 6
        if rarity <= self.__five_star_chance * 1000:
            return 5
        if rarity <= self.__four_star_chance * 1000:
            return 4
        if rarity <= self.__three_star_chance * 1000:
            return 3

    def __return_new_character(self, rarity: int) -> tuple:
        """
        Creates list of characters

        Args:
            rarity (int): character rarity

        Returns:
            list: list that contains characters
        """
        choice_list = []

        for character_id, char in self.characters_data.items():
            character_rarity = int(char["rarity"]) + 1
            if rarity == character_rarity and char["itemDesc"] is not None:  # to ignore summoners items and other rarities
                choice_list.append(character_id)

        random_character = choice(choice_list)

        return self.__parse_character_json(random_character, self.characters_data[str(random_character)])

    def __parse_character_json(self, character_id: str, character_data: dict) -> tuple:
        """
        Creates namedtuple that contains character description

        Args:
            character_id (int): character id
            character_data (dict): full data about character

        Returns:
            namedtuple: list with character description
        """
        rarity = int(character_data["rarity"]) + 1
        profession = data.get_ark_profession(character_data["profession"])
        name = character_data["name"].replace(" ", "_").replace("'", "")
        description_first_part = character_data["itemUsage"]
        description_sec_part = character_data["itemDesc"]
        position = character_data["position"]
        tags = ", ".join(character_data["tagList"])
        traits = character_data["description"]
        if rarity == 6:
            stars = self.__stars_6
        else:
            stars = self.__stars_0_5

        character_data_tuple = namedtuple('character', 'character_id name description_first_part description_sec_part position tags \
                traits profession stars rarity')
        character = character_data_tuple(character_id, name, description_first_part, description_sec_part, position, tags,
                                         traits, profession, stars, rarity)

        return character

    def __add_ark_to_db(self, author_id: int, character_name: str, character_rarity: int) -> None:
        """
        Adds record to db

        Args:
            author_id (message.author.id): requestor id
            character_name (str): received character name
            character_rarity (int): received chaaracter rarity
        """
        res = self.__db.extract(f"""SELECT operator_count FROM users_ark_collection WHERE user_id == '{author_id}'
                                  AND operator_name == '{character_name}'""")

        if res == []:
            self.__db.alter(
                "INSERT INTO users_ark_collection (user_id, operator_name, rarity, operator_count)"
                f" VALUES ('{author_id}', '{character_name}', '{character_rarity}', '1')")
        else:
            self.__db.alter(f"""UPDATE users_ark_collection SET operator_count = '{res[0][0] + 1}'
                              WHERE user_id ='{author_id}'AND operator_name == '{character_name}'""")
        self.__db.statistic_increment('ark')

    def show_character(self, character_name: str, requestor_id: int) -> namedtuple:
        """
        Interlayer between validator function and show func

        Args:
            character_name (str): character name
            requestor_id ([type]): message author id

        Returns:
            namedtuple: list with character description
        """
        return self.__show_character_validator(character_name, requestor_id)

    def __show_character_validator(self, character_name: str, requestor_id: int) -> namedtuple:
        """
        Validates input data and either raise exceptions or returns character data

        Args:
            character_name (str): character name
            requestor_id ([type]): message author id

        Raises:
            NonExistentCharacter: raises when there is an error in the character name
            NonOwnedCharacter: raises when you don't have this character

        Returns:
            namedtuple: list with character description
        """

        character_name = character_name.replace(' ', '_').replace('\'', '').lower()
        for char_id, char in self.characters_data.items():

            name = char["name"].replace(' ', '_').replace('\'', '').lower()
            character_id = char_id

            if character_name == name:
                break
        else:
            raise NonExistentCharacter
        res = self.__db.extract(f"SELECT operator_name FROM users_ark_collection WHERE user_id == '{requestor_id}'"
                                f"and lower(operator_name)='{character_name}'")

        if not res:
            raise NonOwnedCharacter

        return self.__parse_character_json(character_id, self.characters_data[character_id])


def setup(bot):
    """
    Adds cogs
    """
    bot.add_cog(Ark(bot))
