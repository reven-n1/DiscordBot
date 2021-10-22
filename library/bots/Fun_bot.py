from library.__init__ import data
from random import randint, choice
import discord


class Fun_bot:
    def __init__(self):
        self.__ger_self_chance = data.get_self_ger_chanse
        self.__ger_self_phrases = data.get_ger_self_phrases
        self.__ger_phrases = data.get_ger_phrases
        

    def ger_function(self, message_author:discord.member.Member, random_member:discord.member.Member) -> str:
        """
        Farts on random server member or whoever called it

        Args:
            message_author (message.author.id): requestor id
            random_member (guild.member): random guild member

        Returns:
            str: string with fart phrase
        """
        
        if randint(0, 101) >= self.__ger_self_chance:  # Chance to обосраться

            return (f"{message_author.mention} "
                    f"{choice(self.__ger_phrases)} {random_member.mention}")
        else:
            return f"{message_author.mention} {choice(self.__ger_self_phrases)}"  # Самообсер