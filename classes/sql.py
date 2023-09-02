import sqlite3
import tempfile
import requests

from constants.urlReference import URLs

from classes.card import Card
from classes.domain import Domain

class CardsCDB:
    db = None
    cursor = None

    @staticmethod
    def Setup() -> None:
         # Download the cards.cdb and save it into a temp file
        tempCDB = tempfile.NamedTemporaryFile()
        with open(tempCDB.name, "wb") as f:
            r = requests.get(URLs.CARDS_CDB)
            f.write(r.content)
            f.seek(0)

        CardsCDB.db = sqlite3.connect(tempCDB.name)
        CardsCDB.cursor = CardsCDB.db.cursor()
    
    @staticmethod
    def GetMonsterById(id: int) -> any:
        query = "SELECT {} WHERE datas.type & 1 = 1 AND datas.type & 16384 = 0 AND datas.id = {}"
        query = query.format(Card.QUERY_VALUES, id)
        return CardsCDB.cursor.execute(query).fetchone()
    
    @staticmethod
    def GetMonstersByAttributeAndRace(domain: Domain) -> sqlite3.Cursor:
        query = "SELECT {} WHERE datas.type & 1 = 1 AND datas.type & 16384 = 0 AND (datas.attribute in {} OR datas.race in {})"
        attributes = "({})".format(",".join(str(s) for s in domain.attributes))
        races = "({})".format(",".join(str(s) for s in domain.races))
        query = query.format(Card.QUERY_VALUES, attributes, races)
        return CardsCDB.cursor.execute(query)
    
    @staticmethod
    def GetMonstersExcludingAttributeAndRace(domain: Domain) -> sqlite3.Cursor:
        query = "SELECT {} WHERE datas.type & 1 = 1 AND datas.type & 16384 = 0 AND datas.attribute not in {} AND datas.race not in {}"
        attributes = "({})".format(",".join(str(s) for s in domain.attributes))
        races = "({})".format(",".join(str(s) for s in domain.races))
        query = query.format(Card.QUERY_VALUES, attributes, races)
        return CardsCDB.cursor.execute(query)

    @staticmethod
    def GetAllSpellsAndTraps() -> sqlite3.Cursor:
        query = "SELECT {} WHERE datas.type & 1 = 0 AND datas.type & 16384 = 0"
        query = query.format(Card.QUERY_VALUES)
        return CardsCDB.cursor.execute(query)