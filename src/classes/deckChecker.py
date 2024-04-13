from array import array
from classes.sql import CardsCDB
from classes.ydke import YDKE

class DeckChecker:

    @staticmethod    
    def CheckCardCount(decks : list[array]) -> str:
        if len(decks[0]) != 60:
            return "Main Deck must have exactly 60 cards."

        if len(decks[1] > 15):
            return "Extra Deck must have 15 or less cards."

        if len(decks[2]) != 1:
            return "Side Deck must contain only your Deck Master."

        return None

    @staticmethod
    def CheckSingleton(decks : list[array]) -> str:
        duplicates = set()
        cards = set()

        for deck in decks:
            for passcode in deck:
                if passcode in cards:
                    duplicates.add(passcode)
                else:
                    cards.add(passcode)
        
        if len(duplicates) > 0:
            error = ["Duplicates found: "]
            for duplicate in duplicates:
                error.append(CardsCDB.GetNameById(duplicate))
            message = "\n".join(error)
            return message

        return None

    @staticmethod
    def CheckValidDomain(decks : list[array]) -> str:
        return None

    @staticmethod
    def CheckDeck(ydke : str) -> str:
        decks = YDKE.DecodeYDKE(ydke)
        if decks is None:
            return "Could not process YDKE."
        
        error = DeckChecker.CheckCardCount(decks)
        if not error is None:
            return error

        error = DeckChecker.CheckSingleton(decks)
        if not error is None:
            return error

        return "Deck is valid!"