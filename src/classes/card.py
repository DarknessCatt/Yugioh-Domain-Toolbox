# Class that represents a single card.
class Card:
    # The hex value for a single setcode (archetype) belonging to a card.
    HEX_SETCODE = int('0xffff', 0)

    # Creates a new card from the data retrieved from the DB.
    def __init__(self, data) -> None:
        # Order of values depend on the values retrieve, so any changes here
        # should be updated in QUERY_VALUES and vice-versa.
        self.id = data[0]
        self.setcodesHex = data[1]

        self.attack = data[2]
        self.defense = data[3]
        self.race = data[4]
        self.attribute = data[5]

        self.name = data[6]
        self.desc = data[7]

        # this one is converted to int since we actually need to use it
        # unlike the other values which are just reference.
        self.type = int(data[8])

        # The setcodes (archetypes) are a bit tricky to retrieve.
        # They are stored in the DB by concatenating hexdecimal values.
        # So this just performs the oppositive operation:
        # Get the first 16 bits, then the next 16, and so on.
        self.setcodes = []
        for i in range(0, 49, 16):
            setcode = (self.setcodesHex >> i) & self.HEX_SETCODE
            if(setcode > 0):
                self.setcodes.append(setcode)
    
    # Returns if this card is a (non-token) monster
    def IsMonster(self) -> bool:
        # & 1 means it's a monster and & 16384 a token.
        return self.type & 1 == 1 and self.type & 16384 == 0