import os

from classes.textParsers.textParser import TextParser
from classes.downloadManager import DownloadManager

# Reference class for all the Races HEXCODES
class Races(TextParser):
    # Divine-Beasts are named just "divine" in the reference file. 
    DIVINE = "divine"

    # The header of the section containing the types.
    HEADER = "//Races\n"
    # The line that describes the format of each type entry in the section.
    PARSE_LINE = "#define RACE_([\\w]+)\\s+(\\S+)"

    _instance = None

    @staticmethod
    def Instance():
        if(Races._instance is None):
            Races()

        return Races._instance
    
    def __init__(self) -> None:
        if(not Races._instance is None):
            raise Warning("This class is a Singleton!")
        
        Races._instance = self

        self.hexName = {}
        self.nameHex = {}

        print("Setting up Types Reference.")
        
        with open(os.path.join(DownloadManager.GetCardInfoFolder(), DownloadManager.ATTR_RACES_FILENAME), "r", encoding="utf8") as f:
            text = f.read()
            self.ParseSection(
                text,
                Races.HEADER,
                Races.PARSE_LINE,
                self.nameHex,
                self.hexName
            )
        
        self.nameHex = {k.lower():int(v, 0) for k,v in self.nameHex.items()}
        self.hexName = {int(k, 0):v.lower() for k,v in self.hexName.items()}

        print("Done.\n")
