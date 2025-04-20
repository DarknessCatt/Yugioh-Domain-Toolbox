from array import array

from classes.card import Card

from classes.databases.cardsDB import CardsDB
from classes.databases.databaseExceptions import CardIdNotFoundError, CardNameNotFoundError

# Handles YDK lists
class YDK:
    COMMENT = "#"
    SIDE_DECK = "!side"

    # Decodes an YDK, returning a 3 lists of passcodes: main, extra and side.
    # If a line can't be processed, skip it.
    @staticmethod
    def Decode(decklist : str) -> list[array]:
        decks = [[],[]] # [main/extra], [side]
        curr_deck = decks[0]

        lines = decklist.split("\n")
        for line in lines:
            line = line.strip()
            
            if line.startswith(YDK.COMMENT):
                continue

            if line.startswith(YDK.SIDE_DECK):
                curr_deck = decks[1]
                continue
            
            if not line.isdigit():
                print(f"Couldn't process line [{line}]. Skipping.")
                continue
            
            curr_deck.append(int(line))

        main = []
        extra = []
        side = []

        for id in decks[0]:
            try:
                data = CardsDB.Instance().GetCardById(id)
                card = Card(data)

                if card.IsExtraDeckMonster():
                    extra.append(card)
                else:
                    main.append(card)

            except CardIdNotFoundError as error:
                print(f"Couldn't process card with id [{error.args[0]}]. Keep in mind pre-release cards are not supported.")
                continue

        for id in decks[1]:
            try:
                data = CardsDB.Instance().GetCardById(id)
                card = Card(data)
                side.append(card)

            except CardIdNotFoundError as error:
                print(f"Couldn't process card with id [{error.args[0]}]. Keep in mind pre-release cards are not supported.")
                continue
        
        return [main, extra, side]
    
    # Encodes a deck (3 arrays of Cards) into a ydk file
    @staticmethod
    def Encode(decks : list[array]) -> str:
        text = [
            f"{YDK.COMMENT}Created by Domain Toolbox",
            f"{YDK.COMMENT}main"
            ]

        for card in decks[0]:
            text.append(str(card.id))
        
        text.append(f"{YDK.COMMENT}extra")

        for card in decks[1]:
            text.append(str(card.id))
        
        text.append(YDK.SIDE_DECK)

        for card in decks[2]:
            text.append(str(card.id))

        return "\n".join(text)