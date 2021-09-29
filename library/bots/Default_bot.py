class Default_bot:
    def __init__(self):
        self.name = "Amia(bot)"
        self.__delete_quantity = 100       
       

    def get_info(self):
        """
        Returns info list
        """
        info_list = []
        for command_name, command_desc in self.bot_info["commands"].values():
            info_list.append(f"{command_name} - {command_desc}")

        return info_list


    @property
    async def server_delete_quantity(self):
        """
        Default message delete quantity getter 

        Returns:
            int: quantity
        """
        return self.__delete_quantity


      