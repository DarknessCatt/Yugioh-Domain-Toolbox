import os
import re

from constants.hexCodesReference import AttributesAndRaces, Archetypes
from classes.card import Card

class Domain:

    def CleanDesc(text: str, regex: str) -> (list, str):
        matches = set()
        def sub(match: str) -> str:
            matches.add(match.group(1).lower())
            return ""

        cleaned = re.sub(regex, sub, text, flags=re.IGNORECASE)
        return matches, cleaned

    def GetCardDomainFromDesc(self) -> None:
        NOT_TREATED_AS = "\(This card is not treated as an? \".*\" card.\)"
        MENTIONED_QUOTES = "\"(.*?)\""
        TOKENS = "(\(.*\))"
        BATTLE_STATS = "([0-9]{1,4} ATK\/[0-9]{1,4} DEF|ATK [0-9]{1,4}\/DEF [0-9]{1,4}|[0-9]{1,4} ATK and [0-9]{1,4} DEF)"
        RACES = "({})".format("|".join(AttributesAndRaces.races.keys()))
        ATTRIBUTES = "({})".format("|".join(AttributesAndRaces.attributes.keys()))

        text = self.DM.desc
        _, text = Domain.CleanDesc(text, NOT_TREATED_AS)
        mentions, text = Domain.CleanDesc(text, MENTIONED_QUOTES)
        _, text = Domain.CleanDesc(text, TOKENS)
        battleStats, text = Domain.CleanDesc(text, BATTLE_STATS)
        races, text = Domain.CleanDesc(text, RACES)
        attributes, text = Domain.CleanDesc(text, ATTRIBUTES)

        for mention in mentions:
            if(mention in Archetypes.archetypes):
                self.setcodes.add(Archetypes.archetypes[mention])
            else:
                self.namedCards.add(mention)

        for stats in battleStats:
            r = re.match("\D*([0-9]{1,4})\D+([0-9]{1,4})\D*", stats)
            self.battleStats.add(tuple([int(r.group(1)), int(r.group(2))]))

        for attribute in races:
            self.races.add(AttributesAndRaces.races[attribute])

        for attribute in attributes:
            self.attributes.add(AttributesAndRaces.attributes[attribute])

    def __init__(self, DM: Card) -> None:
        self.DM = DM
        self.attributes = set()
        self.races = set()
        self.setcodes = set(DM.setcodes)
        self.battleStats = set()
        self.namedCards = set()

        self.attributes.add(DM.attribute)
        self.attributes.add(AttributesAndRaces.attributes[AttributesAndRaces.DIVINE])
        
        self.races.add(DM.race)
        self.races.add(AttributesAndRaces.races[AttributesAndRaces.DIVINE])

        self.GetCardDomainFromDesc()

        self.cards = []

    def __str__(self) -> str:
        return "\n".join([
            self.DM.name,
            "Attributes:" + str(self.attributes),
            "Types:" + str(self.races),
            "Archetypes:" + str(self.setcodes),
            "ATK/DEF: " + str(self.battleStats),
            "Named Cards: " + str(self.namedCards)
        ])

    def AddCardToDomain(self, card : Card):
        self.cards.append(card)

    def CheckAndAddCardToDomain(self, card : Card):
        if(card.name.lower() in self.namedCards):
            self.cards.append(card)
            return

        atkAndDef = tuple([card.attack, card.defense])
        if(atkAndDef in self.battleStats):
            self.cards.append(card)
            return

        for cardSetcode in card.setcodes:
            cardBaseSetcode = cardSetcode & Card.HEX_BASE_SETCODE
            cardSubSetcode = cardSetcode & Card.HEX_SUB_SETCODE

            for domainSetcode in self.setcodes:
                domainBaseSetcode = domainSetcode & Card.HEX_BASE_SETCODE
                domainSubSetcode = domainSetcode & Card.HEX_SUB_SETCODE

                if(cardBaseSetcode == domainBaseSetcode and (cardSubSetcode & domainSubSetcode) == domainSubSetcode):
                    self.AddCardToDomain(card)
                    return

    def CreateIflist(self) -> None:
        print("Creating iflist for " + self.DM.name)

        IFLIST_HEADER = "#[{}]\n!{}\n$whitelist"
        IFLIST_LINE = "{} 1 -- {}"

        title = "[Domain] " + self.DM.name
        text = [IFLIST_HEADER.format(title, title)]

        for card in self.cards:
            text.append(IFLIST_LINE.format(card.id, card.name))

        filename = re.sub("\W", "", title) + ".iflist.conf"

        if os.path.exists(filename):
            os.remove(filename)

        with open(filename, "w") as f:
            f.write("\n".join(text))
        
        print("iflist created!")
    
    def CreateCSV(self) -> None:
        print("Creating CSV for " + self.DM.name)

        data = []
        data.append(",".join(Card.CSV_HEADERS))

        for card in self.cards:
            data.append(card.toCSVLine())
        
        filename = "[Domain]" + re.sub("\W", "", self.DM.name) + ".csv"

        if os.path.exists(filename):
            os.remove(filename)

        with open(filename, "w") as f:
            f.write("\n".join(data))

        print("CSV created!")
