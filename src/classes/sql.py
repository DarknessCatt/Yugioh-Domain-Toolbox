import os
import sqlite3

from classes.downloadManager import DownloadManager
from classes.card import Card
from classes.domain import Domain

# Handles all the sqlite3 queries. 
class CardsCDB:

    """ About the queries:
    Well, the queries might sound a bit weird at first, so here's some info about then:
    * datas.type & 1 = 1 -> this checks for the first bit of the datas.type. If it's 1, it means the card is a monster.
    * datas.type & 16384 = 0 -> same as last check, but removes tokens from the search, since they are still considered monsters.
    * Card.QUERY_VALUES -> Since the data retrieved here is feed directly into the data class, I believed it would be best
    to let them handle what and which order it was retrieved. I agree it's debatable, might change in the future.
    * Races -> Monster types (warrior, zombie, etc) are called races in the DB.
    """
    db = None
    cursor = None

    # Prepares the database by downloading the cards.cdb from github and reading it.
    @staticmethod
    def Setup() -> None:
        CardsCDB.db = sqlite3.connect(os.path.join(DownloadManager.GetCdbFolder(), DownloadManager.CARDS_CDB))
        CardsCDB.cursor = CardsCDB.db.cursor()
    
    # Gets a single monster through it's id (passcode)
    @staticmethod
    def GetMonsterById(id: int) -> any:
        query = "SELECT {} WHERE datas.type & 1 = 1 AND datas.type & 16384 = 0 AND datas.id = {}"
        query = query.format(Card.QUERY_VALUES, id)
        return CardsCDB.cursor.execute(query).fetchone()
    
    # Gets all monsters within the domain's race and attributes
    @staticmethod
    def GetMonstersByAttributeAndRace(domain: Domain) -> sqlite3.Cursor:
        query = "SELECT {} WHERE datas.type & 1 = 1 AND datas.type & 16384 = 0 AND (datas.attribute in {} OR datas.race in {})"
        attributes = "({})".format(",".join(str(s) for s in domain.attributes))
        races = "({})".format(",".join(str(s) for s in domain.races))
        query = query.format(Card.QUERY_VALUES, attributes, races)
        return CardsCDB.cursor.execute(query)
    
    # Gets all monsters outside of the domain's race and attributes; the oppositive of the above method.
    # These are manually checked if they are the same archetype, named in the DM's desc and so on.
    @staticmethod
    def GetMonstersExcludingAttributeAndRace(domain: Domain) -> sqlite3.Cursor:
        query = "SELECT {} WHERE datas.type & 1 = 1 AND datas.type & 16384 = 0 AND datas.attribute not in {} AND datas.race not in {}"
        attributes = "({})".format(",".join(str(s) for s in domain.attributes))
        races = "({})".format(",".join(str(s) for s in domain.races))
        query = query.format(Card.QUERY_VALUES, attributes, races)
        return CardsCDB.cursor.execute(query)

    # Gets all the cards which are not monsters (nor tokens), so should be only spell and trap cards.
    @staticmethod
    def GetAllSpellsAndTraps() -> sqlite3.Cursor:
        query = "SELECT {} WHERE datas.type & 1 = 0 AND datas.type & 16384 = 0"
        query = query.format(Card.QUERY_VALUES)
        return CardsCDB.cursor.execute(query)