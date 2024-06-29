from array import array
from classes.databases.cardsDB import CardsDB
from classes.card import Card
from classes.domain import Domain
from classes.ydke import YDKE

# Provides methods for checking if a deck is valid for domain.
class DeckChecker:

    # Checks if the main, extra and side decks card count is valid.
    @staticmethod    
    def CheckCardCount(decks : list[array]) -> str:
        if(len(decks[0]) != 60):
            return "Main Deck must have exactly 60 cards."

        if(len(decks[1]) > 15):
            return "Extra Deck must have 15 or less cards."

        if(len(decks[2]) != 1):
            return "Side Deck must contain only your Deck Master."

        return None

    # Checks if there are no duplicate cards across the main, extra and side decks.
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
        
        if(len(duplicates) > 0):
            error = ["Duplicates found: "]
            for duplicate in duplicates:
                error.append(CardsDB.GetNameById(duplicate))
            message = "\n".join(error)
            return message

        return None

    # Checks if the DM is a monster card and if all other cards are within its domain.
    @staticmethod
    def CheckValidDomain(decks : list[array]) -> str:
        dmData = CardsDB.GetMonsterById(decks[2][0])
        if dmData is None:
            return "DeckMaster is not a monster card."

        domain = Domain(Card(dmData))
        print(domain)
        print()

        invalidCards: list[Card] = []
        # Check main and extra deck
        for i in range(0, 1):
            for passcode in decks[i]:
                data = CardsDB.GetMonsterById(passcode)

                # if data is None, it's a spell and trap and it's fine.
                # Domain restrictions only applies to monsters.
                if(not data is None):
                    card = Card(data)
                    if(not domain.CheckIfCardInDomain(card)):
                        invalidCards.append(card)

        if(len(invalidCards) > 0):
            error = ["Monsters outside of Domain found:"]
            for card in invalidCards:
                error.append(card.name)
            message = "\n".join(error)
            return message

        return None

    # Decodes the given ydke url and perform all deck checks.
    @staticmethod
    def CheckDeck(ydke : str) -> str:
        decks = YDKE.DecodeYDKE(ydke)
        if(decks is None):
            return "Could not process YDKE url."
        
        error = DeckChecker.CheckCardCount(decks)
        if(not error is None):
            return error

        error = DeckChecker.CheckSingleton(decks)
        if(not error is None):
            return error

        error = DeckChecker.CheckValidDomain(decks)
        if(not error is None):
            return error

        return "Deck is valid!"