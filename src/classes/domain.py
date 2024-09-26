import re

from classes.textParsers.archetypes import Archetypes
from classes.textParsers.attributes import Attributes
from classes.textParsers.races import Races

from classes.card import Card
from classes.databases.cardsDB import CardsDB

# A Deck masters domain, including information as well as the cards themselves.
class Domain:

    # In the cards cdb, run:
    # select '"' || replace(texts.name,'"','\"') || '",' as 'Name' from texts where texts.name LIKE '%"%' order by texts.name;
    QUOTE_CARDS = [
        "\"A\" Cell Breeding Device",
        "\"A\" Cell Incubator",
        "\"A\" Cell Recombination Device",
        "\"A\" Cell Scatter Burst",
        "\"Infernoble Arms - Almace\"",
        "\"Infernoble Arms - Durendal\"",
        "\"Infernoble Arms - Hauteclere\"",
        "\"Infernoble Arms - Joyeuse\"",
        "Confronting the \"C\"",
        "Contact \"C\"",
        "Corruption Cell \"A\"",
        "Detonator Circle \"A\"",
        "Flying \"C\"",
        "Gigantic \"Champion\" Sargas",
        "Interplanetary Invader \"A\"",
        "Karakuri Barrel mdl 96 \"Shinkuro\"",
        "Karakuri Bonze mdl 9763 \"Kunamzan\"",
        "Karakuri Bushi mdl 6318 \"Muzanichiha\"",
        "Karakuri Gama mdl 4624 \"Shirokunishi\"",
        "Karakuri Komachi mdl 224 \"Ninishi\"",
        "Karakuri Merchant mdl 177 \"Inashichi\"",
        "Karakuri Muso mdl 818 \"Haipa\"",
        "Karakuri Ninja mdl 339 \"Sazank\"",
        "Karakuri Ninja mdl 7749 \"Nanashick\"",
        "Karakuri Ninja mdl 919 \"Kuick\"",
        "Karakuri Shogun mdl 00 \"Burei\"",
        "Karakuri Soldier mdl 236 \"Nisamu\"",
        "Karakuri Steel Shogun mdl 00X \"Bureido\"",
        "Karakuri Strategist mdl 248 \"Nishipachi\"",
        "Karakuri Super Shogun mdl 00N \"Bureibu\"",
        "Karakuri Watchdog mdl 313 \"Saizan\"",
        "Maxx \"C\"",
        "Nouvelles Restaurant \"At Table\"",
        "Otherworld - The \"A\" Zone",
        "Retaliating \"C\"",
        "Shiny Black \"C\"",
        "Shiny Black \"C\" Squadder",
        "Sneaky \"C\"",
        "Spell Card: \"Monster Reborn\"",
        "Spell Card: \"Soul Exchange\"",
        "Spirit Message \"A\"",
        "Spirit Message \"I\"",
        "Spirit Message \"L\"",
        "Spirit Message \"N\"",
        "Super Armored Robot Armed Black Iron \"C\"",
        "Therion \"Bull\" Ain",
        "Therion \"Duke\" Yul",
        "Therion \"Empress\" Alasia",
        "Therion \"King\" Regulus",
        "Therion \"Lily\" Borea",
        "Therion \"Reaper\" Fum",
        "World Legacy - \"World Ark\"",
        "World Legacy - \"World Armor\"",
        "World Legacy - \"World Chalice\"",
        "World Legacy - \"World Crown\"",
        "World Legacy - \"World Key\"",
        "World Legacy - \"World Lance\"",
        "World Legacy - \"World Shield\"",
        "World Legacy - \"World Wand\"",
    ]

    # Helper method that searchs a text for a pattern then removes the matches from the text,
    # returning both the found values as well as the text after changes.
    def CleanDesc(text: str, regex: str) -> tuple[list, str]:
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
        NOT_TREATED_AS = "\\(This card is not treated as an? (\".*?\") card.\\)"
        # Find cards with quotes in their names.
        # This is important since the next search would bug and split the quotes.
        QUOTE_CARDS = "\"({})\"".format("|".join(self.QUOTE_CARDS))
        # Finds all direct mentions (words between quotes), which can be either card names or archetypes
        MENTIONED_QUOTES = "\"(.*?)\""
        # Used to remove tokens description from cards.
        # This is important in order to avoid problens in the next two searchs
        TOKENS = "(\\(.*?\\))"
        # Find exact battle stats mentions on the card, like the Monarch's Squires.
        # Cases (in order): X ATK/X DEF, X ATK and X DEF, X ATK and/or DEF, with X ATK/DEF
        BATTLE_STATS = "with ([0-9]{1,4} ATK\\/[0-9]{1,4} DEF|[0-9]{1,4} ATK and [0-9]{1,4} DEF|[0-9]{1,4} ATK and\\/or DEF|[0-9]{1,4} ATK\\/DEF)"
        # Find all the races (types) mentioned in the desc
        # The list is manually typed because in the ref file they are named "beastwarrior" / "divine" and so on, which would provide no matches.
        RACES = "(aqua|beast-warrior|beast|cyberse|dinosaur|divine-beast|dragon|fairy|fiend|fish|illusion|insect|machine|plant|psychic|pyro|reptile|rock|sea serpent|spellcaster|thunder|warrior|winged beast|wyrm|zombie)"
        # Find all the attributes mentioned in the desc 
        ATTRIBUTES = "({})".format("|".join(Attributes.Instance().nameHex.keys()))
        
        text = self.DM.desc
        _, text = Domain.CleanDesc(text, NOT_TREATED_AS)
        quotes, text = Domain.CleanDesc(text, QUOTE_CARDS)
        mentions, text = Domain.CleanDesc(text, MENTIONED_QUOTES)
        _, text = Domain.CleanDesc(text, TOKENS)
        battleStats, text = Domain.CleanDesc(text, BATTLE_STATS)
        races, text = Domain.CleanDesc(text, RACES)
        attributes, text = Domain.CleanDesc(text, ATTRIBUTES)

        # These are the names of the cards, so just add them.
        for quote_card in quotes:
            self.namedCards.add(quote_card)

        # Mentions is straightfoward: it's either an archetype or an card name.
        # (not always true about the card name, but doesn't lead to problems since it has to be an exact match anyway)
        for mention in mentions:
            if(mention in Archetypes.Instance().nameHex):
                # Add the HEXCODE of the archetypes.
                self.setcodes.add(Archetypes.Instance().nameHex[mention])
            else:
                self.namedCards.add(mention)

        # Add archetype of named cards.
        for name in self.namedCards:
            # Have to do to avoid a circular import.
            data = CardsDB.Instance().GetCardByName(name)
            if(not data is None):
                card = Card(data)
                self.setcodes.update(card.setcodes)

        # Retrieve the battle stats (ATK/DEF) mentioned and convert them to ints.
        for stats in battleStats:
            r = re.match("\\D*([0-9]{1,4})\\D+([0-9]{1,4})\\D*", stats)
            if(not r is None):
                self.battleStats.add(tuple([int(r.group(1)), int(r.group(2))]))
            else:
                # "X ATK and/or DEF" or "X ATK/DEF" case
                r = re.match("\\D*([0-9]{1,4})\\D*", stats)
                self.battleStats.add(tuple([int(r.group(1)), int(r.group(1))]))

        # Add the HEXCODE of the attributes.
        for race in races:
            #remove non character so beast-warrior -> beastwarrior, winged beast -> wingedbeast and so on.
            key = re.sub("\\W", "", race)
            if(key == "divinebeast"):
                # They are written "Divine-Beast" in card text
                # but named "divine" in the AttributesAndRaces reference.
                key = "divine"
            self.races.add(Races.Instance().nameHex[key])

        # Add the HEXCODE of the races.
        for attribute in attributes:
            self.attributes.add(Attributes.Instance().nameHex[attribute])

    # Creates a new Domain for the given deck master.
    def __init__(self) -> None:
        self.DM: Card = None
        # All these refer to attributes, races... belonging in the domain.
        self.attributes: set = None
        self.races: set = None
        self.setcodes: set = None
        self.battleStats: set = None
        self.namedCards: set = None

        self.cards = []

    def __str__(self) -> str:
        return "\n".join([
            self.DM.name,
            "Attributes: " + str([Attributes.Instance().hexName[code] for code in self.attributes]),
            "Types: " + str([Races.Instance().hexName[code] for code in self.races]),
            "Archetypes: " + str([Archetypes.Instance().hexName[code] for code in self.setcodes]),
            "Named Cards: " + (str(self.namedCards) if len(self.namedCards) > 0 else "{}"),
            "ATK/DEF: " + (str(self.battleStats) if len(self.battleStats) > 0 else "{}")
        ])

    # Creates a new Domain by parsing the DM's card text for information.
    # Mainly used by DomainLookup to add entries to the DB.
    @staticmethod
    def GenerateFromCard(DM: Card):
        domain = Domain()

        domain.DM = DM
        domain.attributes = set([DM.attribute])
        domain.races = set([DM.race])
        domain.setcodes = set(DM.setcodes)
        domain.battleStats = set()
        domain.namedCards = set()

        # Don't forget the DIVINES attribute
        domain.attributes.add(Attributes.Instance().nameHex[Attributes.DIVINE])
        domain.races.add(Races.Instance().nameHex[Races.DIVINE])

        # This checks if the monster is a normal ("vanilla") monster.
        # Flavor text is ignored for domain, so we don't check the description in these cases.
        if(domain.DM.type & 16 == 0):
            domain.GetCardDomainFromDesc()

        # Replace all sub-archetypes with their base archetypes,
        # allowing, for example, a "Black Luster Soldier" ritual monster to
        # include all "Chaos" monsters like "Chaos Valkyria."
        baseSetcodes = set()
        for arch in domain.setcodes:
            baseCodes = Archetypes.Instance().GetBaseArchetype(arch)
            if(not baseCodes is None):
                baseSetcodes = baseSetcodes.union(set(baseCodes))
        domain.setcodes = baseSetcodes

        return domain

    # Creates a new Domain from data.
    # Mainly used from data retrieved from DomainLookup.GetDomain, but could also be used for testing.
    @staticmethod
    def GenerateFromData(DM: Card, data: list):
        domain = Domain()

        domain.DM = DM
        domain.attributes = set(v[0] for v in data[0])
        domain.races = set(v[0] for v in data[1])
        domain.setcodes = set(v[0] for v in data[2])
        domain.battleStats = set(v for v in data[3])
        domain.namedCards = set(v[0] for v in data[4])

        return domain

    # Adds a card to this domain, no questions asked.
    # Used mostly for cards with an attribute or race in the domain,
    # since this check is more straightfoward.
    # Also used for spells / traps.
    def AddCardToDomain(self, card : Card):
        self.cards.append(card)

    # Check if a card belongs in the domain
    # During domain generation, can skip attribute and types checks
    # (since we can easily query/exclude these through the DB)
    def CheckIfCardInDomain(self, card : Card, skipAttributeType : bool = False) -> bool:
        if(not skipAttributeType):
            if(card.attribute in self.attributes):
                return True

            if(card.race in self.races):
                return True

        if(card.name.lower() in self.namedCards):
            return True

        atkAndDef = tuple([card.attack, card.defense])
        if(atkAndDef in self.battleStats):
            return True

        for cardSetcode in card.setcodes:
            # Since all setcodes in the domain are already their base version
            # (It's converted in the constructor)
            # We only have to compare it with the base archetype of the current card.
            cardBaseSetcodes = Archetypes.Instance().GetBaseArchetype(cardSetcode)

            if(not cardBaseSetcodes is None):
                for domainSetcode in self.setcodes:
                    for cardBaseSetcode in cardBaseSetcodes:
                        if(cardBaseSetcode == domainSetcode):
                            return True

        return False

    # Checks if a cards belong in the domain, then adds it if so.
    # Used to check direct name mentions, atk and def, and archetypes.
    def CheckAndAddCardToDomain(self, card : Card):
        if(self.CheckIfCardInDomain(card, True)):
            self.AddCardToDomain(card)

    # Removes all cards from the domain.
    def RemoveAllCards(self):
        self.cards = []

    # Removes all the spells and traps from the domain.
    def RemoveSpellsAndTraps(self):
        # if the first bit of type (card.type & 1) is 1, it means the card is a monster.
        self.cards = [card for card in self.cards if card.type & 1 == 1]
                