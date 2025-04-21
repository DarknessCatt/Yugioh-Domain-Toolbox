from array import array

from classes.card import Card

from classes.databases.cardsDB import CardsDB
from classes.databases.databaseExceptions import CardIdNotFoundError, CardNameNotFoundError

# Handles simple name lists
class NameList:

    # Reads a list of names, returning a 3 lists of passcodes: main, extra and side.
    # If name can't be processed, skip it.
    @staticmethod
    def Decode(nameList : str) -> list[array]:
        main = []
        extra = []

        lines = nameList.split("\n")
        for line in lines:
            line = line.strip()

            if not line: #empty line
                continue

            try:
                data = CardsDB.Instance().GetCardByName(line.strip())
                card = Card(data)

                if card.IsExtraDeckMonster():
                    extra.append(card)
                else:
                    main.append(card)

            except CardNameNotFoundError as error:
                print(f"Couldn't process card with name [{error.args[0]}]. Keep in mind pre-release cards are not supported.")
                continue
        
        return [main, extra, []]
    
    # Encodes a deck (3 arrays of Cards) into a simple list of names
    @staticmethod
    def Encode(decks : list[array]) -> str:
        text = []

        for deck in decks:
            for card in deck:
                text.append(card.name)

        return "\n".join(text)