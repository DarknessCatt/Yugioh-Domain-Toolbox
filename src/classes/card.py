# Class that represents a single card.
class Card:
    # The hex value for a single setcode (archetype) belonging to a card.
    HEX_SETCODE = int('0xffff', 0)
    # Hex value for the base archetype bits of a setcode.
    HEX_BASE_SETCODE = int('0xfff', 0)
    # Hex value for the sub-archetype bits of a setcode.
    HEX_SUB_SETCODE = int('0xf000',0)

    # Data which should be retrieved from the sqlite query.
    QUERY_VALUES = "datas.id, setcode, atk, def, race, attribute, name, desc from datas NATURAL JOIN texts"

    # Headers used when generating the csv.
    # Having then here is quite debatable, not gonna lie.
    CSV_HEADERS = ["cardname", "cardq", "cardrarity", "cardcondition", "card_edition", "cardset", "cardcode", "cardid"]

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

        # The setcodes (archetypes) are a bit tricky to retrieve.
        # They are stored in the DB by concatenating hexdecimal values.
        # So this just performs the oppositive operation:
        # Get the first 16 bits, then the next 16, and so on.
        self.setcodes = []
        for i in range(0, 49, 16):
            setcode = (self.setcodesHex >> i) & self.HEX_SETCODE
            if(setcode > 0):
                self.setcodes.append(setcode)
    
    # Convertes the card information into a line for the csv.
    # Thanks @Zefile8 for the original code.
    def toCSVLine(self) -> str:
        data = []

        data.append("\"" + self.name.replace("\"","\"\"") + "\"") #cardname
        data.append("1") #cardq
        data.append(str(None)) #cardrarity
        data.append(str(None)) #cardcondition
        data.append(str(None)) #card_edition
        data.append(str(None)) #cardset
        data.append("DOMA-" + str(self.id)) #cardcode
        data.append(str(self.id)) #cardid

        return ",".join(data)