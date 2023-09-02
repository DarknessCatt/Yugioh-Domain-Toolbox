import re
import requests

from constants.urlReference import URLs

class Archetypes:
    ARCHETYPE_HEADER = "#Official Archetypes\n"
    ARCHETYPE_LINE = "!setname (\S+) (.*)"

    archetypes = {}

    @staticmethod
    def ReadSection(text:str, header: str, line: str, dic: dict) -> None:
        section = re.search("{}({}\n)*".format(header, line), text)
        list = section.group(0).strip().removeprefix(header)
        for entry in list.split("\n"):
            info = re.search(line, entry)
            dic[info.group(2).lower()] = int(info.group(1), 0)

    @staticmethod
    def Setup() -> None:
        r = requests.get(URLs.ARCHETYPES)
        text = r.text
        Archetypes.ReadSection(
            text,
            Archetypes.ARCHETYPE_HEADER,
            Archetypes.ARCHETYPE_LINE,
            Archetypes.archetypes
        )

class AttributesAndRaces:
    DIVINE = "divine"

    ATTRIBUTES_HEADER = "//Attributes\n"
    ATTRIBUTES_LINE = "#define ATTRIBUTE_([\w]+)\s+(\S+)"

    RACES_HEADER = "//Races\n"
    RACES_LINE = "#define RACE_([\w]+)\s+(\S+)"

    attributes = {}
    races = {}

    @staticmethod
    def ReadSection(text:str, header: str, line: str, dic: dict) -> None:
        section = re.search("{}({}\n)*".format(header, line), text)
        list = section.group(0).strip().removeprefix(header)
        for entry in list.split("\n"):
            info = re.search(line, entry)
            dic[info.group(1).lower()] = int(info.group(2), 0)

    @staticmethod
    def Setup() -> None:
        r = requests.get(URLs.ATTRIBUTES_AND_RACES)
        text = r.text

        AttributesAndRaces.ReadSection(
            text,
            AttributesAndRaces.ATTRIBUTES_HEADER, 
            AttributesAndRaces.ATTRIBUTES_LINE,
            AttributesAndRaces.attributes
        )
        
        AttributesAndRaces.ReadSection(
            text,
            AttributesAndRaces.RACES_HEADER,
            AttributesAndRaces.RACES_LINE,
            AttributesAndRaces.races
        )