class Card:
    HEX_SETCODE = int('0xffff', 0)
    HEX_BASE_SETCODE = int('0xfff', 0)
    HEX_SUB_SETCODE = int('0xf000',0)

    QUERY_VALUES = "datas.id, setcode, atk, def, race, attribute, name, desc from datas NATURAL JOIN texts"

    CSV_HEADERS = ["cardname", "cardq", "cardrarity", "cardcondition", "card_edition", "cardset", "cardcode", "cardid"]

    def __init__(self, data) -> None:
        self.id = data[0]
        self.setcodesHex = data[1]

        self.attack = data[2]
        self.defense = data[3]
        self.race = data[4]
        self.attribute = data[5]

        self.name = data[6]
        self.desc = data[7]

        self.setcodes = []
        for i in range(0, 49, 16):
            setcode = (self.setcodesHex >> i) & self.HEX_SETCODE
            if(setcode > 0):
                self.setcodes.append(setcode)
    
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