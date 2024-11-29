import os

from classes.textParsers.textParser import TextParser
from classes.downloadManager import DownloadManager

# Reference class for all the archetypes HEXCODES
class Archetypes(TextParser):
    # The header of the section containing the archetypes.
    HEADER = "#Official Archetypes\n"
    PRE_HEADER = "#Official archetypes\n" #The pre-archetype file has a undercase 'a'.
    PRE_ARCHETYPE_HEADER = "#Pre-release archetypes\n"

    # The line that describes the format of each archetype entry in the section.
    PARSE_LINE = "!setname (\\S+) (.*)"

    # Hex value for the base archetype bits of a setcode.
    HEX_BASE_SETCODE = int('0xfff', 0)

    # List of archetypes in edo to ignore.
    # Mostly series that are miss categorized as archetypes.
    IGNORE_LIST = [
        "genex ally",
        "xx-saber",
        "evol",
        "dark lucius",
        "ultimate insect",
        "iron",
        "tin",
        "lightray",
        "djinn of rituals",
        "noble",
        "envy",
        "spiritual beast tamer",
        "entity",
        "supreme king",
        "spiritual art",
        "of the forest",
        "byssted",
        "kshatri-la",
        "purery",
        "earthbound servant",
        "infernoble",
        "helios"
    ]

    # Hexes that need to be manually replaced cause
    # they appear more than once in the same list in an incorrect order
    ARCH_REPLACES = {
        int('0xa2', 0) : int('0x98', 0), # Magician
        int('0x16c', 0): int('0x48', 0), # Number
    }

    EXTRA_CASES = {
        "true draco": int('0xf9', 0),
        "true king": int('0xf9', 0),
        "magician": int('0x98', 0), # Magician is getting the hex 0xa2, this overrides it
    }

    BASE_ARCH_EXCEPTIONS = {
        int('0x10a2', 0): [int('0x10a2', 0)], # Dark Magician is the base archetype, not magician.
        int('0x20a2', 0): [int('0x20a2', 0)], # Magician Girl is the base archetype, not magician.
        int('0x30a2', 0): [int('0x10a2', 0), int('0x20a2', 0)], # Dark Magician Girl is both a dark magician and a magician girl.
        int('0x1048', 0): [int('0x48', 0), int('0xcf', 0)], # Number C is both a Number and a Chaos.
        int('0x5048', 0): [int('0x48', 0), int('0xcf', 0)], # Number C39 is both a Number and a Chaos.
        int('0x1073', 0): [int('0xcf', 0), int('0x73', 0)], # CXyz is both a Chaos and a XYZ.
        int('0x307b', 0): [int('0x7b', 0), int('0x1ab', 0)],# Galaxy-Eyes Tachyon Dragon is both a Galaxy and Tachyon.
    }

    _instance = None

    @staticmethod
    def Instance():
        if(Archetypes._instance is None):
            Archetypes()

        return Archetypes._instance
    
    def __init__(self) -> None:
        if(not Archetypes._instance is None):
            raise Warning("This class is a Singleton!")
        
        Archetypes._instance = self

        self.hexName = {}
        self.nameHex = {}

        self.Update()
    
    def Update(self) -> None:
        updateHexName = {}
        updateNameHex = {}

        print("Setting up Archetype Reference.")

        with open(os.path.join(DownloadManager.GetCardInfoFolder(), DownloadManager.ARCHETYPES_FILENAME), "r", encoding="utf8") as f:
            text = f.read()
            self.ParseSection(
                text,
                Archetypes.HEADER,
                Archetypes.PARSE_LINE,
                updateHexName,
                updateNameHex
            )

        with open(os.path.join(DownloadManager.GetCardInfoFolder(), DownloadManager.PRE_ARCHETYPES_FILENAME), "r", encoding="utf8") as f:
            text = f.read()
            
            # The Pre-Archetypes has two sections, one for released and other for pre-released.
            self.ParseSection(
                text,
                Archetypes.PRE_HEADER,
                Archetypes.PARSE_LINE,
                updateHexName,
                updateNameHex
            )
            self.ParseSection(
                text,
                Archetypes.PRE_ARCHETYPE_HEADER,
                Archetypes.PARSE_LINE,
                updateHexName,
                updateNameHex
            )

        updateHexName = {int(k, 0):v.lower() for k,v in updateHexName.items()}
        updateNameHex = {k.lower():int(v, 0) for k,v in updateNameHex.items()}

        for original_hex, replacement in Archetypes.ARCH_REPLACES.items():
            if(original_hex in updateHexName):
                name = updateHexName[original_hex]
                del updateHexName[original_hex]
                updateHexName[replacement] = name
                updateNameHex[name] = replacement

        for item in Archetypes.IGNORE_LIST:
            if(item in updateNameHex):
                hexCode =  updateNameHex.pop(item)

                # Some hexCodes are shared across multiple names, (like both bystial and byssed are the same)
                # So we need to make sure only delete those that are in the IGNORE_LIST
                if(hexCode in updateHexName and updateHexName[hexCode] == item):
                    del updateHexName[hexCode]
        
        for name, hex in Archetypes.EXTRA_CASES.items():
            updateNameHex[name] = hex

        self.hexName = updateHexName
        self.nameHex = updateNameHex

        print("Done.\n")

    # Helper method to extract the base and valid code of an archetype.
    def GetBaseArchetype(self, hexCode: int) -> list[int]:

        # Some archetypes that are incorrected classified
        # get special treatment.
        if(hexCode in Archetypes.BASE_ARCH_EXCEPTIONS):
            return Archetypes.BASE_ARCH_EXCEPTIONS[hexCode]

        baseCode = hexCode & Archetypes.HEX_BASE_SETCODE

        # While "Genex Ally" is not an archetype,
        # Just "Genex" is (and it's marked as a sub-archetype).
        if(baseCode in self.hexName):
            return [baseCode]

        # "Supreme King Gate" and "Supreme King Dragon", for example,
        # don't have a base hexCode, but are still valid archetypes.
        if(hexCode in self.hexName):
            return [hexCode]
        
        # Probably something from the IGNORE_LIST, so just ignore.
        return None
