from itertools import groupby, zip_longest
from math import ceil
from typing import List, Tuple, Union
from sqlalchemy import select
from library.exceptions.validator import NonOwnedCharacter, NonExistentCharacter
from discord.ext.commands.core import is_nsfw
from discord import guild_only
from discord.ext.commands import cooldown
from library import user_guild_cooldown
from discord.commands import slash_command, Option
from discord import User, ApplicationContext
from discord import Bot
from discord.embeds import Embed
from discord import Cog
from library.data.db.database import Database, Statistic, StatisticParameter, UsersArkCollection
from discord.errors import NotFound
from random import choice, randrange
from collections import namedtuple
from library.data.data_loader import DataHandler
from json import loads
from re import sub
import discord
import logging

data = DataHandler()


class Ark(Cog):
    qualified_name = 'Ark'
    description = 'Рулетка с дефками'
    __stars_0_5 = "<:star:801095671720968203>"
    __stars_6 = "<:star2:801105195958140928>"

    class SkinSelector(discord.ui.View):
        user_id: int

        def __init__(self, embed: discord.Embed, skins: list, user_id: int, timeout=180):
            super().__init__(timeout=timeout)
            self.user_id = user_id
            self.skin_select.options = []
            self.embed = embed
            for skin in skins:
                self.skin_select.options.append(
                    discord.SelectOption(label=skin.name, description=skin.desc, value=skin.id))

        async def respond(self, context: ApplicationContext, **kwargs) -> None:
            message = await context.respond(embed=self.embed, view=self, **kwargs)
            self.message = await message.original_message()

        async def on_timeout(self) -> None:
            try:
                await self.message.edit(view=None)
            except NotFound as e:
                logging.warning(e)
            return await super().on_timeout()

        @discord.ui.select(placeholder='Choose skin', min_values=1, max_values=1, options=[])
        async def skin_select(self, _: discord.ui.Select, ctx: ApplicationContext):
            if ctx.user.id != self.user_id:
                await ctx.respond('Не трожь. Не твоя девочка, вот ты и бесишся!', ephemeral=True)
                return
            new_image_url = ctx.data.get('values', [''])[0].replace('#', '%23')
            new_embed = ctx.message.embeds[0].set_image(
                url=f"https://raw.githubusercontent.com/Aceship/Arknight-Images/main/characters/{new_image_url}.png")
            await ctx.response.edit_message(embed=new_embed)

    def __init__(self, bot: Bot):
        self.bot = bot

        self.__six_star_chance, self.__five_star_chance, \
        self.__four_star_chance, self.__three_star_chance = data.get_ark_chances

        with open("library/config/character_table.json", "rb") as character_json:
            self.characters_data = loads(character_json.read())

        with open("library/config/skin_table.json", "rb") as skin_json:
            self.skin_data = loads(skin_json.read())['charSkins']

    # cog commands ----------------------------------------------------------------------------------------------

    async def myark_autocomplete(self, ctx: discord.AutocompleteContext):
        collection = await self.get_ark_collection(ctx.interaction.user.id)
        return list(sorted([char.operator_name for rar in collection.values() for char in rar if
                            str(char.operator_name).lower().startswith(ctx.value.lower())]))

    @slash_command(name="myark",
                   description='Вывести твою коллекцию сочных аниме девочек(и кунчиков ^-^). ')
    @is_nsfw()
    async def myark_slash(self, ctx: ApplicationContext,
                          char_name: Option(str, 'Имя персонажа', autocomplete=myark_autocomplete, default=None),
                          public: Option(bool, 'Похвастаться?', default=False)):
        result = await self.myark(char_name, ctx.user)
        if isinstance(result, Embed):
            await ctx.respond(embed=result, ephemeral=not public)
        elif isinstance(result, self.SkinSelector):
            await result.respond(ctx, ephemeral=not public)

    @slash_command(name="barter",
                   brief='Обменять много хуевых персов на мало пиздатых')
    @is_nsfw()
    @guild_only()
    async def barter_slash(self, ctx: ApplicationContext):
        """
        Serves to exchange 5 characters for 1 rank higher\n
        if possible else returns 'Нет операторов на обмен'
        """
        barter_list = await self.get_barter_list(ctx.user.id)
        if barter_list:
            await ctx.defer()
            barter = self.ark_barter(barter_list, ctx.user.id)
            async for new_char in barter:
                selector = self.ark_embed_and_view(new_char, ctx.user)
                await selector.respond(ctx)
            await ctx.followup.send(content="Готово! Наслаждайся!")
        else:
            await ctx.respond("***Нет операторов на обмен***", ephemeral=15)

    @slash_command(name="ark",
                   description='Кидает рандомную девочку (но это не точно, там и трапики есть, ня) и сохраняет её')
    @is_nsfw()
    @guild_only()
    @cooldown(1, data.get_ark_cooldown, user_guild_cooldown)
    async def ark_slash(self, ctx: ApplicationContext):
        """
        Return a random arknigts character (from character_table.json)
        """
        character_data = await self.roll_random_character(ctx.user.id)
        selector = self.ark_embed_and_view(character_data, ctx.user)
        await selector.respond(ctx)

    def ark_embed_and_view(self, character_data: list, author: discord.Member):
        """
        Generates embed form recieved ark data

        Args:
            character_data (list): random character data from character_table.json
            message (discord.message): message
        """
        embed = discord.Embed(color=data.get_embed_color, title=character_data.name,
                              description=str(character_data.stars) * character_data.rarity,
                              url=f"https://aceship.github.io/AN-EN-Tags/akhrchars.html?opname={character_data.name}")
        embed.add_field(name="Description",
                        value=f"{character_data.description_first_part}\n{character_data.description_sec_part}",
                        inline=False)
        embed.add_field(name="Position", value=character_data.position)
        embed.add_field(name="Tags", value=str(character_data.tags), inline=True)
        line = sub("[<@.>/]", "", character_data.traits)  # Delete all tags in line
        embed.add_field(name="Traits", value=line.replace("bakw", ""), inline=False)
        embed.set_thumbnail(url=character_data.profession)
        embed.set_image(url=f"https://raw.githubusercontent.com/Aceship/Arknight-Images/main/characters/{character_data.character_id}_1.png")
        embed.set_footer(text=f"Requested by {author.display_name}")
        return Ark.SkinSelector(embed, self.get_skin_list(character_data.character_id), author.id,
                                data.get_chat_misc_cooldown_sec)

    # functions --------------------------------------------------------------------------------------------------------------------

    async def myark(self, char_name: str, user: User) -> Union[SkinSelector, Embed]:
        ark_collection = await self.get_ark_collection(user.id)
        if not char_name:
            all_character_count = self.get_ark_count()
            user_chara_count = sum([len(characters) for characters in ark_collection.values()])
            collection_message = discord.Embed(
                title=f"{user.display_name}'s collection {user_chara_count}/{all_character_count} \
                                              ({round((user_chara_count / all_character_count) * 100, 2)}%)",
                color=data.get_embed_color)
            for rarity, characters in ark_collection.items():
                characters_list = [f"{character.operator_name} x {character.operator_count}" for character in characters]
                chunk_size = ceil(len(characters_list) / ceil(len('\n'.join(characters_list)) / 1024))
                for idx, chunk in enumerate(zip_longest(*[iter(characters_list)]*chunk_size, fillvalue='')):
                    collection_message.add_field(name=(":star:" * rarity if rarity < 6 else ":star2:" * rarity) if idx == 0 else f"Продолжение {rarity}*",
                                                 value='\n'.join(chunk), inline=False
                                                 )
            if len(ark_collection) == 0:
                collection_message.add_field(name="Ти бомж", value="иди покрути девочек!")
            collection_message.set_footer(text="Используй команду /myark <имя> чтоб посмотреть на персонажа.")
            return (collection_message, None)
        try:
            return self.ark_embed_and_view(await self.show_character(char_name, user.id), user)
        except NonOwnedCharacter:
            return discord.Embed(title="***Лох, у тебя нет такой дивочки***")
        except NonExistentCharacter:
            return discord.Embed(title="***Лошара, даже имя своей вайфу не запомнил((***")

    def get_skin_list(self, character_id) -> namedtuple:
        skinTyple = namedtuple('skin', ['id', 'name', 'desc'])
        skin_list = []
        for skin in filter(lambda x: x['charId'] == character_id, self.skin_data.values()):
            skin_list.append(skinTyple._make((skin['portraitId'],
                                              f"{skin['displaySkin']['skinName']}" if skin['displaySkin'][
                                                  'skinName'] else f"{skin['displaySkin']['modelName']}#{skin['portraitId'].split('_')[-1]}",
                                              skin['displaySkin']['skinGroupName'])))
        return skin_list

    async def get_ark_collection(self, collection_owner_id: int) -> List[UsersArkCollection]:
        """
        This function returns all ark collection

        Args:
            collection_owner_id (message.autthor.id): requestor id

        Returns:
            dict: requestor characters collection
        """
        async with await Database.get_class_session() as session:
            requestor_collection = (await session.execute(
                select(UsersArkCollection).where(UsersArkCollection.user_id == collection_owner_id).order_by(
                    UsersArkCollection.rarity))).scalars().all()
        out_dict = {k: list(v) for k, v in groupby(requestor_collection, lambda x: int(x.rarity))}
        return out_dict

    async def get_barter_list(self, author_id: int) -> list:
        """
        Creates list of characters for barter

        Args:
            author_id (message.author.id): requestor id

        Returns:
            list: list that contains quantity and character stars
        """
        async with await Database.get_class_session() as session:
            res = (await session.execute(select(UsersArkCollection).where(UsersArkCollection.user_id == author_id,
                                                                          UsersArkCollection.operator_count >= 6,
                                                                          UsersArkCollection.rarity < 6).order_by(
                UsersArkCollection.rarity))).scalars().all()

            barter_list = []
            for item in res:
                if item.rarity < 6 and item.operator_count > 5:
                    if item.operator_count % 5 != 0:
                        new_char_quantity = item.operator_count % 5
                    else:
                        new_char_quantity = (item.operator_count // 5) - 1

                    barter_list.append([item.rarity + 1, new_char_quantity])

                    item.operator_count = new_char_quantity
                    session.add(item)

            await session.commit()

        return barter_list

    async def ark_barter(self, barter_list: list, author_id: int) -> tuple:
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
                await self.__add_ark_to_db(author_id, character.name, character.rarity)
                yield character

    def get_ark_count(self) -> int:
        """
        Returns counter of all possible characters

        Returns:
            int: count of all possible characters
        """
        return len([val for val in self.characters_data.values() if val["rarity"] >= 2 and val["itemDesc"] is not None])

    async def roll_random_character(self, author_id: int) -> tuple:
        """
        Calls function that adds character to db

        Args:
            author_id (message.author.id): requestor id

        Returns:
            list: random character data
        """
        new_character = self.__return_new_character(await self.__get_ark_rarity(author_id))

        await self.__add_ark_to_db(author_id, new_character.name, new_character.rarity)
        return new_character

    async def __get_ark_rarity(self, author_id: int) -> int:
        """
        Returns random character rarity
        """
        db: Database = await Database()
        chance_increase = (await db.get_user_statistic(author_id, StatisticParameter.Parameter.SIX_MISS)).count
        rarity = randrange(0, 100000)
        if rarity <= (self.__six_star_chance + (chance_increase * 2 - 50 if chance_increase >= 50 else 0)) * 1000:
            await db.reset_user_statistic(author_id, StatisticParameter.Parameter.SIX_MISS)
            return 6
        else:
            await db.increment_user_statistic(author_id, StatisticParameter.Parameter.SIX_MISS)
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
            if rarity == character_rarity and char[
                "itemDesc"] is not None:  # to ignore summoners items and other rarities
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
        character = character_data_tuple(character_id, name, description_first_part, description_sec_part, position,
                                         tags,
                                         traits, profession, stars, rarity)

        return character

    async def __add_ark_to_db(self, author_id: int, character_name: str, character_rarity: int) -> None:
        """
        Adds record to db

        Args:
            author_id (message.author.id): requestor id
            character_name (str): received character name
            character_rarity (int): received chaaracter rarity
        """
        db: Database = await Database()
        async with db.get_session() as session:
            char = await db.insert_if_not_exsits(UsersArkCollection, UsersArkCollection.user_id == author_id,
                                                 UsersArkCollection.operator_name == character_name,
                                                 UsersArkCollection.rarity == character_rarity
                                                 )
            char.operator_count += 1
            session.add(char)
            await db.increment_statistic(Statistic.Parameter.ARK)
            await session.commit()

    async def show_character(self, character_name: str, requestor_id: int) -> namedtuple:
        """
        Interlayer between validator function and show func

        Args:
            character_name (str): character name
            requestor_id ([type]): message author id

        Returns:
            namedtuple: list with character description
        """
        return await self.__show_character_validator(character_name, requestor_id)

    async def __show_character_validator(self, character_name: str, requestor_id: int) -> namedtuple:
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

        character_name = character_name.replace(' ', '_').replace('\'', '')
        for char_id, char in self.characters_data.items():

            name = char["name"].replace(' ', '_').replace('\'', '')
            character_id = char_id

            if character_name == name:
                break
        else:
            raise NonExistentCharacter
        async with await Database.get_class_session() as session:
            res = (await session.execute(select(UsersArkCollection).where(UsersArkCollection.user_id == requestor_id,
                                                                          UsersArkCollection.operator_name == character_name
                                                                          ))).scalars().first()

        if not res:
            raise NonOwnedCharacter

        return self.__parse_character_json(character_id, self.characters_data[character_id])


def setup(bot):
    """
    Adds cogs
    """
    bot.add_cog(Ark(bot))
