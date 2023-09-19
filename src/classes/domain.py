import os
import re

from constants.hexCodesReference import AttributesAndRaces, Archetypes
from classes.card import Card

# A Deck masters domain, including information as well as the cards themselves.
class Domain:

    # Helper method that searchs a text for a pattern then removes the matches from the text,
    # returning both the found values as well as the text after changes.
    def CleanDesc(text: str, regex: str) -> (list, str):
        matches = set()
        def sub(match: str) -> str:
            matches.add(match.group(1).lower())
            return ""

        cleaned = re.sub(regex, sub, text, flags=re.IGNORECASE)
        return matches, cleaned

    # Retrieves the domain information from the DM's description.
    def GetCardDomainFromDesc(self) -> None:
        # Amazing regex done by @Zefile8 and @EokLennon
        # These meticulously retrieve the information from the card's description
        # into ordered arrays ready for processing.

        # Remove the "this card is not treated as ..."
        # Since we already retrieve the information from the DB, this is not useful for us.
        NOT_TREATED_AS = "\(This card is not treated as an? \".*\" card.\)"
        # Finds all direct mentions (words between quotes), which can be either card names or archetypes
        MENTIONED_QUOTES = "\"(.*?)\""
        # Used to remove tokens description from cards.
        # This is important in order to avoid problens in the next two searchs
        TOKENS = "(\(.*\))"
        # Find exact battle stats mentions on the card, like the Monarch's Squires.
        BATTLE_STATS = "([0-9]{1,4} ATK\/[0-9]{1,4} DEF|ATK [0-9]{1,4}\/DEF [0-9]{1,4}|[0-9]{1,4} ATK and [0-9]{1,4} DEF)"
        # Find all the races (types) mentioned in the desc
        # The list is manually typed because in the ref file they are named "beastwarrior" / "divine" and so on, which would provide no matches.
        RACES = "(aqua|beast-warrior|beast|cyberse|dinosaur|divine-beast|dragon|fairy|fiend|fish|insect|machine|plant|psychic|pyro|reptile|rock|sea serpent|spellcaster|thunder|warrior|winged beast|wyrm|zombie)"
        # Find all the attributes mentioned in the desc 
        ATTRIBUTES = "({})".format("|".join(AttributesAndRaces.attributes.keys()))
        
        text = self.DM.desc
        _, text = Domain.CleanDesc(text, NOT_TREATED_AS)
        mentions, text = Domain.CleanDesc(text, MENTIONED_QUOTES)
        _, text = Domain.CleanDesc(text, TOKENS)
        battleStats, text = Domain.CleanDesc(text, BATTLE_STATS)
        races, text = Domain.CleanDesc(text, RACES)
        attributes, text = Domain.CleanDesc(text, ATTRIBUTES)

        # Mentions is straightfoward: it's either an archetype or an card name.
        # (not always true about the card name, but doesn't lead to problems since it has to be an exact match anyway)
        for mention in mentions:
            if(mention in Archetypes.archetypes):
                # Add the HEXCODE of the archetypes.
                self.setcodes.add(Archetypes.archetypes[mention])
            else:
                self.namedCards.add(mention)

        # Retrieve the battle stats (ATK/DEF) mentioned and convert them to ints.
        for stats in battleStats:
            r = re.match("\D*([0-9]{1,4})\D+([0-9]{1,4})\D*", stats)
            self.battleStats.add(tuple([int(r.group(1)), int(r.group(2))]))

        # Add the HEXCODE of the attributes.
        for race in races:
            #remove non character so beast-warrior -> beastwarrior, winged beast -> wingedbeast and so on.
            self.races.add(AttributesAndRaces.races[re.sub("\W", "", race)])

        # Add the HEXCODE of the races.
        for attribute in attributes:
            self.attributes.add(AttributesAndRaces.attributes[attribute])

    # Creates a new Domain for the given deck master.
    def __init__(self, DM: Card) -> None:
        self.DM = DM
        # All these refer to attributes, races... belonging in the domain.
        self.attributes = set()
        self.races = set()
        self.setcodes = set(DM.setcodes)
        self.battleStats = set()
        self.namedCards = set()

        self.attributes.add(DM.attribute)
        # Don't forget the DIVINE attribute
        self.attributes.add(AttributesAndRaces.attributes[AttributesAndRaces.DIVINE])
        
        self.races.add(DM.race)
        # Theoretically not necessary, since all divine-beasts are already divine attribute,
        # but better safe than sorry.
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

    # Adds a card to this domain, no questions asked.
    # Used for cards with an attribute or race in the domain,
    # since this check is more straightfoward.
    def AddCardToDomain(self, card : Card):
        self.cards.append(card)

    # Checks if a cards belong in the domain, then adds it if so.
    # Used to check direct name mentions, atk and def, and archetypes.
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

                # Alright, the archetype check is a bit confusing at first.
                # Basically, this allows subarchetypes to be included into the base archtype, but not vice-versa;
                # So "Gem-" deckmaster will add "Gem-Knight" monsters, but not the other way around.
                
                # This is done in two steps: 
                # First we check if the base setcode is the same ("Gem-" in this example).
                # Next, we check if the sub-archetype code is the same, if one exists at all.
                
                # The sub-archetype is defined by the 4 first bits of the setcode.
                # If 0, this means it's not a sub-archetype,
                # So (cardSubSetcode & domainSubSetcode) always equals 0, which is equal to domainSubSetcode.
                # Otherwise, (cardSubSetcode & domainSubSetcode) will not be 0 and their sub-archetypes must match.

                # There's a few caveats to it, but that's the concept.
                if(cardBaseSetcode == domainBaseSetcode and (cardSubSetcode & domainSubSetcode) == domainSubSetcode):
                    self.AddCardToDomain(card)
                    return

    # Creates an EDOPRO iflist (banlist) containing only the cards within this domain.
    def CreateIflist(self) -> None:
        print("Creating iflist for " + self.DM.name)

        # The header for the file
        IFLIST_HEADER = "#[{}]\n!{}\n$whitelist"
        # The line for each entry.
        # Limit all cards to 1 since it's a highlander format.
        IFLIST_LINE = "{} 1 -- {}"

        title = "[Domain] " + self.DM.name
        text = [IFLIST_HEADER.format(title, title)]

        for card in self.cards:
            text.append(IFLIST_LINE.format(card.id, card.name))

        # Removes all now alphabetic characters from the filename to prevent errors.
        filename = re.sub("\W", "", title) + ".iflist.conf"

        if os.path.exists(filename):
            os.remove(filename)

        with open(filename, "w", encoding="utf8") as f:
            f.write("\n".join(text))
        
        print("iflist created!")
    
    # Creates an CSV for YGOPRODECK containing the cards within this domain.
    # Thanks @Zefile8 for the original code.
    def CreateCSV(self) -> None:
        print("Creating CSV for " + self.DM.name)

        data = []
        data.append(",".join(Card.CSV_HEADERS))

        for card in self.cards:
            data.append(card.toCSVLine())
        
        filename = "[Domain]" + re.sub("\W", "", self.DM.name) + ".csv"

        if os.path.exists(filename):
            os.remove(filename)

        with open(filename, "w", encoding="utf8") as f:
            f.write("\n".join(data))

        print("CSV created!")
