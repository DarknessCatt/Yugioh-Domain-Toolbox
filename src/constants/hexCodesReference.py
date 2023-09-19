import os
import re

from classes.downloadManager import DownloadManager

# Reference class for all the archetypes HEXCODES
class Archetypes:
    # The header of the section containing the archetypes.
    ARCHETYPE_HEADER = "#Official Archetypes\n"
    # The line that describes the format of each archetype entry in the section.
    ARCHETYPE_LINE = "!setname (\S+) (.*)"

    # A dictionary with the archetypes name as key and the HEXCODE as value.
    archetypes = {}
    # Reverse lookup of the archetypes dict
    reverseArch = {}

    # Reads the provided text and retrives information from it
    @staticmethod
    def ReadSection(text:str, header: str, line: str, dic: dict, reverseDic: dict) -> None:
        # First, retrive the entire section of the file.
        section = re.search("{}({}\n)*".format(header, line), text)
        # Remove the header from the section.
        list = section.group(0).strip().removeprefix(header)
        # For each entry in the section, retrieve the archetype's name and hexcode.
        for entry in list.split("\n"):
            info = re.search(line, entry)
            dic[info.group(2).lower()] = int(info.group(1), 0)
            reverseDic[int(info.group(1), 0)] = info.group(2).lower()

    # Retrives the reference file from the URL and
    # populates the dictionary.
    @staticmethod
    def Setup() -> None:
        Archetypes.archetypes = {}
        Archetypes.reverseArch = {}

        with open(os.path.join(DownloadManager.GetCardInfoFolder(), DownloadManager.ARCHETYPES_FILENAME), "r", encoding="utf8") as f:
            print("Setting up Archetype Reference.")
            text = f.read()
            Archetypes.ReadSection(
                text,
                Archetypes.ARCHETYPE_HEADER,
                Archetypes.ARCHETYPE_LINE,
                Archetypes.archetypes,
                Archetypes.reverseArch
            )
            print("Done.\n")

# Reference class for all the attributes and races HEXCODES
# Could have a separate class for each one, but they are both retrieved from the same file.
# Might split it in the future.
class AttributesAndRaces:
    # Divine-Beasts are named just "divine" in the reference file. 
    DIVINE = "divine"

    # The header of the section containing the attributes.
    ATTRIBUTES_HEADER = "//Attributes\n"
    # The line that describes the format of each attribute entry in the section.
    ATTRIBUTES_LINE = "#define ATTRIBUTE_([\w]+)\s+(\S+)"

    # The header of the section containing the types.
    RACES_HEADER = "//Races\n"
    # The line that describes the format of each type entry in the section.
    RACES_LINE = "#define RACE_([\w]+)\s+(\S+)"

    # A dictionary with the attributes name as key and the HEXCODE as value.
    attributes = {}
    # Reverse lookup of the attributes dict
    reverseAttr = {}

    # A dictionary with the types name as key and the HEXCODE as value.
    races = {}
    # Reverse lookup of the races dict
    reverseRace = {}

    # Reads the provided text and retrives the information from it
    @staticmethod
    def ReadSection(text:str, header: str, line: str, dic: dict, reverseDic: dict) -> None:
        section = re.search("{}({}\n)*".format(header, line), text)
        list = section.group(0).strip().removeprefix(header)
        for entry in list.split("\n"):
            info = re.search(line, entry)
            dic[info.group(1).lower()] = int(info.group(2), 0)
            reverseDic[int(info.group(2), 0)] = info.group(1).lower()

    # Retrives the reference file from the URL and
    # populates the dictionary.
    @staticmethod
    def Setup() -> None:
        AttributesAndRaces.attributes = {}
        AttributesAndRaces.races = {}

        with open(os.path.join(DownloadManager.GetCardInfoFolder(), DownloadManager.ATTR_RACES_FILENAME), "r", encoding="utf8") as f:
            text = f.read()

            print("Setting up Attributes Reference.")
            AttributesAndRaces.ReadSection(
                text,
                AttributesAndRaces.ATTRIBUTES_HEADER, 
                AttributesAndRaces.ATTRIBUTES_LINE,
                AttributesAndRaces.attributes,
                AttributesAndRaces.reverseAttr
            )
            print("Done.\n")
            
            print("Setting up Types Reference.")
            AttributesAndRaces.ReadSection(
                text,
                AttributesAndRaces.RACES_HEADER,
                AttributesAndRaces.RACES_LINE,
                AttributesAndRaces.races,
                AttributesAndRaces.reverseRace
            )
            print("Done.\n")