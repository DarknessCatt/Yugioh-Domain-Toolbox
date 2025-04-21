import re
from array import array
from collections import Counter

from classes.card import Card

from classes.databases.cardsDB import CardsDB
from classes.databases.databaseExceptions import CardIdNotFoundError, CardNameNotFoundError

# Handles Untap lists
class UntapDeck:
    MAIN_DECK = "//deck-1"
    EXTRA_DECK = "//deck-2"
    SIDE_DECK = "//play-1"

    UNTAP_LINE_REGEX = "(\\d+) (.*)"
    UNTAP_FORMAT_LINE = "{} {}"

    # Decodes an Untap List, returning a 3 lists of passcodes: main, extra and side.
    # If a line can't be processed, skip it.
    @staticmethod
    def Decode(decklist : str) -> list[array]:
        untap_lines = [[], [], []] # [main], [extra], [side]
        curr_deck = untap_lines[0]

        lines = decklist.split("\n")
        for line in lines:
            line = line.strip()
            
            if not line: # is empty
                continue

            if line.startswith(UntapDeck.MAIN_DECK):
                curr_deck = untap_lines[0]
                continue

            if line.startswith(UntapDeck.EXTRA_DECK):
                curr_deck = untap_lines[1]
                continue

            if line.startswith(UntapDeck.SIDE_DECK):
                curr_deck = untap_lines[2]
                continue

            curr_deck.append(line)

        decks = [[], [], []]

        for i in range(0,3):
            for line in untap_lines[i]:
                info = re.search(UntapDeck.UNTAP_LINE_REGEX, line)

                if info is None or info.group(0) is None:
                    print(f"Couldn't process line [{line}]. Skipping.")
                    continue

                amount = 1
                name = info.group(2)
                
                if info.group(1).isdigit():
                    amount = int(info.group(1))
                else:
                    print(f"Couldn't process card amount [{info.group(1)}].")

                try:
                    data = CardsDB.Instance().GetCardByName(name)
                    card = Card(data)
                    for _ in range(amount):
                        decks[i].append(card)

                except CardNameNotFoundError as error:
                    print(f"Couldn't process card with name [{error.args[0]}]. Keep in mind pre-release cards are not supported.")
                    continue
        
        return decks
    
    # Encodes a deck (3 arrays of Cards) into a untap file
    @staticmethod
    def Encode(decks : list[array]) -> str:
        text = [UntapDeck.SIDE_DECK]
        counter = Counter(decks[2])
        for card, amount in counter.items():
            text.append(UntapDeck.UNTAP_FORMAT_LINE.format(amount, card.name))
        
        text.append("")
        text.append(UntapDeck.MAIN_DECK)
        counter = Counter(decks[0])
        for card, amount in counter.items():
            text.append(UntapDeck.UNTAP_FORMAT_LINE.format(amount, card.name))
        
        text.append("")
        text.append(UntapDeck.EXTRA_DECK)
        counter = Counter(decks[1])
        for card, amount in counter.items():
            text.append(UntapDeck.UNTAP_FORMAT_LINE.format(amount, card.name))

        return "\n".join(text)