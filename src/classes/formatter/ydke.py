from array import array
from base64 import b64encode, b64decode

from classes.card import Card

from classes.databases.cardsDB import CardsDB
from classes.databases.databaseExceptions import CardIdNotFoundError, CardNameNotFoundError

# Handles YDKE URLs
class YDKE:
    URL_START = "ydke://"
    SEPARATOR = "!"

    # Decodes an YDKE, returning a 3 lists of passcodes: main, extra and side.
    # If YDKE can't be processed, returns None instead.
    @staticmethod
    def Decode(url : str) -> list[array]:
        if(not url.startswith(YDKE.URL_START)):
            return None

        url = url.removeprefix(YDKE.URL_START)
        decks = url.split(YDKE.SEPARATOR)

        if(len(decks) < 3):
            return None

        passcodes = []
        # 0 for main, 1 for extra, and 2 for side
        for i in range(0, 3):
            # ydke files are stored in base64 unsigned ints
            idList = array("I")
            idList.frombytes(b64decode(decks[i]))
            
            decklist = []
            for id in idList:
                try:
                    data = CardsDB.Instance().GetCardById(id)
                    decklist.append(Card(data))
                except CardIdNotFoundError as error:
                    print(f"Couldn't process card with id [{error.args[0]}]. Keep in mind pre-release cards are not supported.")
                    continue

            passcodes.append(decklist)
        
        return passcodes
    
    # Encodes a deck (3 arrays of Cards) into a ydke url
    @staticmethod
    def Encode(decks : list[array]) -> str:
        encodedDecks = []

        for deck in decks:
            idList = array("I", [card.id for card in deck])
            b64str = b64encode(idList.tobytes()).decode("ascii")
            encodedDecks.append(b64str)

        return YDKE.URL_START + YDKE.SEPARATOR.join(encodedDecks) + YDKE.SEPARATOR