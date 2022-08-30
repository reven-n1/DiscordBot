class NonOwnedCharacter(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class NonExistentCharacter(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)
