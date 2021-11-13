from library.__init__ import data
from random import randint, choice
from library.__init__ import db, bot
import discord


class Fun_bot:
    def __init__(self):
        self.__ger_self_chance = data.get_self_ger_chanse
        self.__ger_self_phrases = data.get_ger_self_phrases
        self.__ger_phrases = data.get_ger_phrases
        self.__db = db
        

    def ger_function(self, message_author:discord.member.Member, random_member:discord.member.Member) -> str:
        """
        Farts on random server member or whoever called it

        Args:
            message_author (message.author.id): requestor id
            random_member (guild.member): random guild member

        Returns:
            str: string with fart phrase
        """
        if random_member.bot:
            self.__db.statistic_increment('ger_bot')
        if random_member.id == bot.user.id:
            self.__db.statistic_increment('ger_me')
        if randint(0, 101) >= self.__ger_self_chance:  # Chance to обосраться
            self.__db.statistic_increment('ger')
            return (f"{message_author.mention} "
                    f"{choice(self.__ger_phrases)} {random_member.mention}")
        else:
            self.__db.statistic_increment('self_ger')
            return f"{message_author.mention} {choice(self.__ger_self_phrases)}"  # Самообсер