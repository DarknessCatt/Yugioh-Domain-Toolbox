import os

from classes.textParsers.textParser import TextParser
from classes.downloadManager import DownloadManager

# Reference class for all the Attributes HEXCODES
class Attributes(TextParser):
    # Divine-Beasts are named just "divine" in the reference file. 
    DIVINE = "divine"

    # The header of the section containing the attributes.
    HEADER = "//Attributes\n"
    # The line that describes the format of each attribute entry in the section.
    PARSE_LINE = "#define ATTRIBUTE_([\\w]+)\\s+(\\S+)"

    _instance = None

    @staticmethod
    def Instance():
        if(Attributes._instance is None):
            Attributes()

        return Attributes._instance
    
    def __init__(self) -> None:
        if(not Attributes._instance is None):
            raise Warning("This class is a Singleton!")

        Attributes._instance = self

        self.hexName = {}
        self.nameHex = {}

        print("Setting up Attributes Reference.")
        
        with open(os.path.join(DownloadManager.GetCardInfoFolder(), DownloadManager.ATTR_RACES_FILENAME), "r", encoding="utf8") as f:
            text = f.read()
            self.ParseSection(
                text,
                Attributes.HEADER,
                Attributes.PARSE_LINE,
                self.nameHex,
                self.hexName
            )
        
        self.nameHex = {k.lower():int(v, 0) for k,v in self.nameHex.items()}
        self.hexName = {int(k, 0):v.lower() for k,v in self.hexName.items()}

        print("Done.\n")