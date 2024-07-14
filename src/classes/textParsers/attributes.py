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

        self.Update()

    def Update(self) -> None:
        print("Setting up Attributes Reference.")
        
        updateNameHex = {}
        updateHexName = {}

        with open(os.path.join(DownloadManager.GetCardInfoFolder(), DownloadManager.ATTR_RACES_FILENAME), "r", encoding="utf8") as f:
            text = f.read()
            self.ParseSection(
                text,
                Attributes.HEADER,
                Attributes.PARSE_LINE,
                updateNameHex,
                updateHexName
            )
        
        updateNameHex = {k.lower():int(v, 0) for k,v in updateNameHex.items()}
        updateHexName = {int(k, 0):v.lower() for k,v in updateHexName.items()}

        self.hexName = updateHexName
        self.nameHex = updateNameHex

        print("Done.\n")