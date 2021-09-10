from library.data.json_data import ger_phrases, \
ger_self_chance, ger_self_phrases
from random import randint, choice


class Fun_bot:
    def __init__(self):
        self.ger_self_chance = ger_self_chance
        self.ger_self_phrases = ger_self_phrases
        self.ger_phrases = ger_phrases
        

    def ger_function(self, message_author, random_member):
        """
        Farts on random server member or whoever called it

        Args:
            message_author (message.author.id): requestor id
            random_member (guild.member): random guild member

        Returns:
            str: string with fart phrase
        """
        
        if randint(0, 101) >= self.ger_self_chance:  # Chance to обосраться

            return (f"{message_author.mention} "
                    f"{choice(self.ger_phrases)} {random_member.mention}")
        else:
            return f"{message_author.mention} {choice(self.ger_self_phrases)}"  # Самообсер