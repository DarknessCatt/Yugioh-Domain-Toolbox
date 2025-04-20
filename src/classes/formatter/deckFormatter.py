from array import array
from enum import Enum

from classes.card import Card
from classes.formatter.ydk import YDK
from classes.formatter.ydke import YDKE
from classes.formatter.nameList import NameList

# Exports an array of cards into a defined format
class DeckFormatter:
    
    class Format(Enum):
        BANLIST = 0
        YGOPRODECK_CSV = 1
        YDK = 2
        YDKE = 3
        NAMES = 4

    _instance = None

    @staticmethod
    def Instance():
        if(DeckFormatter._instance is None):
            DeckFormatter()

        return DeckFormatter._instance

    def __init__(self) -> None:
        if(not DeckFormatter._instance is None):
            raise Warning("This class is a Singleton!")

        DeckFormatter._instance = self
        
        self.formatters = {
            DeckFormatter.Format.YDK : YDK,
            DeckFormatter.Format.YDKE : YDKE,
            DeckFormatter.Format.NAMES : NameList
        }
    
    def Encode(self, format: Format, decks: list[array]) -> str:
        if(format not in self.formatters):
            raise Warning(f"Format [{format}] doesn't exist")
        
        return self.formatters[format].Encode(decks)

    def Decode(self, format: Format, code: str) -> list[array]:
        if(format not in self.formatters):
            raise Warning(f"Format [{format}] doesn't exist")
        
        return self.formatters[format].Decode(code)
        