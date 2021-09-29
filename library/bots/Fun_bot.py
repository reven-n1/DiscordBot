import discord
from library.data.json_data import ger_phrases, \
ger_self_chance, ger_self_phrases
from random import randint, choice


class Fun_bot:
    def __init__(self):
        self.__ger_self_chance = ger_self_chance
        self.__ger_self_phrases = ger_self_phrases
        self.__ger_phrases = ger_phrases
        

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