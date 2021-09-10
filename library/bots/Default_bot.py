class Default_bot:
    def __init__(self):
        self.name = "Amia(bot)"
        self.delete_quantity = 100       
       

    def get_info(self):
        """
        Returns info list
        """
        info_list = []
        count = 0
        for line in self.bot_info["commands"].keys():
            info_list.append(f'{line} - ')
        for line in self.bot_info["commands"].values():
            info_list[count] += line
            count += 1

        return info_list


    @property
    async def server_delete_quantity(self):
        """
        Default message delete quantity getter 

        Returns:
            int: quantity
        """
        return self.delete_quantity


      