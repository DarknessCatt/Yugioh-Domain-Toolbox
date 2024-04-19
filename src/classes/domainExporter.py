import os
import re

from classes.card import Card
from classes.domain import Domain

class DomainExporter:

    # The header for the file
    LFLIST_HEADER = "#[{}]\n!{}\n$whitelist"
    
    # The line for each entry.
    # Limit all cards to 1 since it's a highlander format.
    LFLIST_LINE = "{} 1 -- {}"

    # Creates an EDOPRO/Ygo Omega lflist (banlist) containing only the cards within this domain.
    @staticmethod
    def toLflist(domain : Domain) -> None:
        print("Creating lflist for " + domain.DM.name)

        title = "[Domain] " + domain.DM.name
        text = [DomainExporter.LFLIST_HEADER.format(title, title)]

        for card in domain.cards:
            text.append(DomainExporter.LFLIST_LINE.format(card.id, card.name))

        # Removes all now alphabetic characters from the filename to prevent errors.
        filename = re.sub("\W", "", title) + ".lflist.conf"

        if os.path.exists(filename):
            os.remove(filename)

        with open(filename, "w", encoding="utf8") as f:
            f.write("\n".join(text))
        
        print("lflist created!\n")
    

    # Dict of characters we have to replace in YGOPRODECK
    YGOPRODECK_REPLACEMENTS = {
        # Symbols
        "・" : "",
        "Ω" : "Omega",
        "\"": "\"\"",

        # Specific Names
        "Twin Long Rods #1" : "Twin Long Rods 1", # This '#' is missing in YGOProDeck.
        "Power Pro Knight Girls" : "Power Pro Knight Sisters", # No official translation, it seems.
        "Falchionβ" : "Falchion Beta", # Not going to replace just the symbol for now due to the extra space.
    }

    # Headers used when generating the csv.
    CSV_HEADERS = ["cardname", "cardq", "cardrarity", "card_edition", "cardset", "cardcode", "cardid"]

    # Convertes the card information into a line for the csv.
    # Thanks @Zefile8 for the original code.
    @staticmethod
    def cardToCSVLine(card : Card, pattern : str) -> str:
        data = []

        # Replaces the card's name symbols for YGOPRODECK,
        name = re.sub(pattern, 
                      lambda m : DomainExporter.YGOPRODECK_REPLACEMENTS.get(m.group(0)),
                      card.name)
        data.append("\"" + name + "\"") #cardname
        data.append("1") #cardq
        data.append(str(None)) #cardrarity
        data.append(str(None)) #card_edition
        data.append(str(None)) #cardset
        data.append("DOMA-" + str(card.id)) #cardcode
        data.append(str(card.id)) #cardid

        return ",".join(data)

    # Creates an CSV for YGOPRODECK containing the cards within this domain.
    # Thanks @Zefile8 for the original code in JS.
    @staticmethod
    def toCSV(domain : Domain) -> None:
        print("Creating CSV for " + domain.DM.name)

        # Pattern to replace the names in YGOPRODECK
        pattern = '|'.join(sorted(re.escape(k) for k in DomainExporter.YGOPRODECK_REPLACEMENTS))

        data = []
        data.append(",".join(DomainExporter.CSV_HEADERS))

        for card in domain.cards:
            data.append(DomainExporter.cardToCSVLine(card, pattern))
        
        filename = "[Domain]" + re.sub("\W", "", domain.DM.name) + ".csv"

        if os.path.exists(filename):
            os.remove(filename)

        with open(filename, "w", encoding="utf8") as f:
            f.write("\n".join(data))

        print("CSV created!\n")