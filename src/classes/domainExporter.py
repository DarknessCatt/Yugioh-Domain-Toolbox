import os
import re

from classes.card import Card
from classes.domain import Domain

class DomainExporter:

    # The header for the file
    IFLIST_HEADER = "#[{}]\n!{}\n$whitelist"
    
    # The line for each entry.
    # Limit all cards to 1 since it's a highlander format.
    IFLIST_LINE = "{} 1 -- {}"

    # Creates an EDOPRO/Ygo Omega iflist (banlist) containing only the cards within this domain.
    @staticmethod
    def toIflist(domain : Domain) -> None:
        print("Creating iflist for " + domain.DM.name)

        title = "[Domain] " + domain.DM.name
        text = [DomainExporter.IFLIST_HEADER.format(title, title)]

        for card in domain.cards:
            text.append(DomainExporter.IFLIST_LINE.format(card.id, card.name))

        # Removes all now alphabetic characters from the filename to prevent errors.
        filename = re.sub("\W", "", title) + ".iflist.conf"

        if os.path.exists(filename):
            os.remove(filename)

        with open(filename, "w", encoding="utf8") as f:
            f.write("\n".join(text))
        
        print("iflist created!\n")
    
    # Headers used when generating the csv.
    CSV_HEADERS = ["cardname", "cardq", "cardrarity", "cardcondition", "card_edition", "cardset", "cardcode", "cardid"]

    # Convertes the card information into a line for the csv.
    # Thanks @Zefile8 for the original code.
    @staticmethod
    def cardToCSVLine(card : Card) -> str:
        data = []

        data.append("\"" + card.name.replace("\"","\"\"") + "\"") #cardname
        data.append("1") #cardq
        data.append(str(None)) #cardrarity
        data.append(str(None)) #cardcondition
        data.append(str(None)) #card_edition
        data.append(str(None)) #cardset
        data.append("DOMAIN") #cardcode
        data.append(str(card.id)) #cardid

        return ",".join(data)

    # Creates an CSV for YGOPRODECK containing the cards within this domain.
    # Thanks @Zefile8 for the original code in JS.
    @staticmethod
    def toCSV(domain : Domain) -> None:
        print("Creating CSV for " + domain.DM.name)

        data = []
        data.append(",".join(DomainExporter.CSV_HEADERS))

        for card in domain.cards:
            data.append(DomainExporter.cardToCSVLine(card))
        
        filename = "[Domain]" + re.sub("\W", "", domain.DM.name) + ".csv"

        if os.path.exists(filename):
            os.remove(filename)

        with open(filename, "w", encoding="utf8") as f:
            f.write("\n".join(data))

        print("CSV created!\n")