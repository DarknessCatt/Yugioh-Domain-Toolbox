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

    # Merges all CDB files into a single database.
    # Used since some pre-release cards are in separate files.
    @staticmethod
    def MergeCDBs() -> None:
        print("Merging all CDBs into a single file.")

        # Since the cards.cdb is always the biggest, we will use it as a base
        db = sqlite3.connect(os.path.join(DownloadManager.GetCdbFolder(), DownloadManager.CARDS_CDB))
        cursor = db.cursor()

        # Retrieve all tables and columns from the CDB
        queryTables = "SELECT name FROM sqlite_master WHERE type='table';"
        tablesList = cursor.execute(queryTables).fetchall()

        # Dict of tables into their insertion queries
        tableColumns = {}

        for table in tablesList:
            queryColumn = "PRAGMA table_info({})".format(table[0])
            columns = cursor.execute(queryColumn).fetchall()
            # Creates a list of (?, ?, ?, ... , ?) to be used when inserting values in the cdb
            tableColumns[table[0]] = ','.join(['?'] * len(columns))

        for file in os.listdir(DownloadManager.GetCdbFolder()):
            # For each CDB file other than cards.cdb
            if(file != DownloadManager.CARDS_CDB and file.endswith(".cdb")):
                # Create a temp database connection
                tempDB = sqlite3.connect(os.path.join(DownloadManager.GetCdbFolder(), file))
                tempCursor = tempDB.cursor()

                # For each table in cards.cdb
                for table, column in tableColumns.items():
                    selectQuery = "SELECT * FROM {}".format(table)
                    insertQuery = "INSERT OR IGNORE INTO {} VALUES ({})"
                    query = insertQuery.format(table, column)
                    # For each row in the same table
                    for row in tempCursor.execute(selectQuery).fetchall():
                        # Insert it into the cards.cdb
                        cursor.execute(query, row)

                tempDB.close()

                # Delete CDB after it has been merged
                os.remove(os.path.join(DownloadManager.GetCdbFolder(), file))
        
        # For some reason, alt arts have no setcode. This small code updates them accordingly.
        updateAltArts = "UPDATE datas SET setcode = (SELECT setcode FROM datas as d2 WHERE datas.alias = d2.id) WHERE datas.alias != 0 AND datas.setcode = 0"
        cursor.execute(updateAltArts)

        # Commiting save this to the current file (cards.cdb)
        db.commit()
        db.close()

        # Rename cards.cdb into merged_cards.cdb
        os.rename(
            os.path.join(DownloadManager.GetCdbFolder(), DownloadManager.CARDS_CDB),
            DownloadManager.GetMergedCDBPath()
        )

    # Prepares the database by reading the cdb files.
    @staticmethod
    def Setup() -> None:
        print("Setting up card database.")

        mergedCdbPath = DownloadManager.GetMergedCDBPath()
        if(not os.path.exists(mergedCdbPath)):
            CardsCDB.MergeCDBs()

        CardsCDB.db = sqlite3.connect(mergedCdbPath)
        CardsCDB.cursor = CardsCDB.db.cursor()

        print("Done.\n")

    # Closes the db, if any.
    @staticmethod
    def CloseDB() -> None:
        if(CardsCDB.db != None):
            CardsCDB.cursor = None
            CardsCDB.db.close()
            CardsCDB.db = None

    # Gets a single card's name through it's id (passcode)
    @staticmethod
    def GetNameById(id: int) -> str:
        query = "SELECT name FROM texts WHERE id = ?"
        parameters = (id,)
        return CardsCDB.cursor.execute(query, parameters).fetchone()[0]

    # Gets a single monster through it's id (passcode)
    @staticmethod
    def GetMonsterById(id: int) -> any:
        query = "SELECT {} WHERE datas.type & 1 = 1 AND datas.type & 16384 = 0 AND datas.id = ?"
        query = query.format(Card.QUERY_VALUES)
        parameters = (id,)
        return CardsCDB.cursor.execute(query, parameters).fetchone()
    
    # Gets a single monster through it's name
    # Ideally called by the Domain class when finding cards referenced in the text.
    @staticmethod
    def GetMonsterByName(name: str) -> any:
        query = "SELECT {} WHERE datas.type & 1 = 1 AND datas.type & 16384 = 0 AND texts.name = ? COLLATE NOCASE"
        query = query.format(Card.QUERY_VALUES)
        parameters = (name,)
        return CardsCDB.cursor.execute(query, parameters).fetchone()

    # Gets all monsters' ids.
    @staticmethod
    def GetAllMonsterIds() -> sqlite3.Cursor:
        query = "SELECT id from datas WHERE datas.type & 1 = 1 AND datas.type & 16384 = 0"
        return CardsCDB.cursor.execute(query).fetchall()

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