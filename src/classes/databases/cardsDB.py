import os
import sqlite3

from classes.downloadManager import DownloadManager

# Handles all the sqlite3 queries. 
class CardsDB:

    """ About the queries:
    Well, the queries might sound a bit weird at first, so here's some info about then:
    * datas.type & 1 = 1 -> this checks for the first bit of the datas.type. If it's 1, it means the card is a monster.
    * datas.type & 16384 = 0 -> same as last check, but removes tokens from the search, since they are still considered monsters.
    * Races -> Monster types (warrior, zombie, etc) are called races in the DB.
    """
    
    # Data which should be retrieved for the cards.
    # Make sure this matches the Card's constructor.
    CARD_QUERY = "datas.id, setcode, atk, def, race, attribute, name, desc, type from datas NATURAL JOIN texts"

    _instance = None

    @staticmethod
    def Instance():
        if(CardsDB._instance is None):
            CardsDB()

        return CardsDB._instance

    def __init__(self) -> None:
        if(not CardsDB._instance is None):
            raise Warning("This class is a Singleton!")

        CardsDB._instance = self

        print("Setting up card database.")

        mergedCdbPath = DownloadManager.GetMergedCDBPath()
        CardsDB.UpdateDBs()

        self.db = sqlite3.connect(mergedCdbPath)
        self.cursor = self.db.cursor()

        print("Done.\n")


    # Merges all CDB files into a single database.
    # Used since some pre-release cards are in separate files.
    @staticmethod
    def UpdateDBs() -> None:
        print("Merging all CDBs into a single file.")

        # Since the cards.cdb is always the biggest, we will use it as a base
        initial_db_file = DownloadManager.CARDS_CDB

        # However, if merged_cards.cdb already exists, use it instead
        if(os.path.isfile(DownloadManager.GetMergedCDBPath())):
                initial_db_file = DownloadManager.MERGED_CDB_PREFIX + DownloadManager.CARDS_CDB

        merge_db = sqlite3.connect(os.path.join(DownloadManager.GetCdbFolder(), initial_db_file))
        merge_cursor = merge_db.cursor()

        # Retrieve all tables and columns from the CDB
        queryTables = "SELECT name FROM sqlite_master WHERE type='table';"
        tablesList = merge_cursor.execute(queryTables).fetchall()

        # Dict of tables into their insertion queries
        tableColumns = {}

        for table in tablesList:
            queryColumn = "PRAGMA table_info({})".format(table[0])
            columns = merge_cursor.execute(queryColumn).fetchall()
            # Creates a list of (?, ?, ?, ... , ?) to be used when inserting values in the cdb
            tableColumns[table[0]] = ','.join(['?'] * len(columns))

        for file in os.listdir(DownloadManager.GetCdbFolder()):
            # For each CDB file other than cards.cdb
            if(file != initial_db_file and file.endswith(".cdb")):
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
                        merge_cursor.execute(query, row)

                tempDB.close()

                # Delete CDB after it has been merged
                os.remove(os.path.join(DownloadManager.GetCdbFolder(), file))
        
        # For some reason, alt arts have no setcode. This small code updates them accordingly.
        updateAltArts = "UPDATE datas SET setcode = (SELECT setcode FROM datas as d2 WHERE datas.alias = d2.id) WHERE datas.alias != 0 AND datas.setcode = 0"
        merge_cursor.execute(updateAltArts)

        # Commiting save this to the current file (cards.cdb)
        merge_db.commit()
        merge_db.close()

        # Rename cards.cdb into merged_cards.cdb
        if(initial_db_file == DownloadManager.CARDS_CDB):
            os.rename(
                os.path.join(DownloadManager.GetCdbFolder(), DownloadManager.CARDS_CDB),
                DownloadManager.GetMergedCDBPath()
            )

    # Closes the db, if any.
    def CloseDB(self) -> None:
        if(self.db != None):
            self.cursor = None
            self.db.close()
            self.db = None

    # Gets a single card's name through it's id (passcode)
    def GetNameById(self, id: int) -> str:
        query = "SELECT name FROM texts WHERE id = ?"
        parameters = (id,)
        return self.cursor.execute(query, parameters).fetchone()[0]

    # Returns the alias of a card, or 0 if there's none.
    # "Alias" refers to the "original name" of the card, like each harpy lady being "Harpy Lady"
    def GetAliasById(self, id: int) -> any:
        query = "SELECT alias FROM datas WHERE datas.id = ?"
        parameters = (id,)
        return self.cursor.execute(query, parameters).fetchone()[0]

    # Gets a single monster through it's id (passcode)
    def GetMonsterById(self, id: int) -> any:
        query = "SELECT {} WHERE datas.type & 1 = 1 AND datas.type & 16384 = 0 AND datas.id = ?"
        query = query.format(CardsDB.CARD_QUERY)
        parameters = (id,)
        return self.cursor.execute(query, parameters).fetchone()

    # Gets a single monster through it's name
    def GetMonsterByName(self, name: str) -> any:
        query = "SELECT {} WHERE datas.type & 1 = 1 AND datas.type & 16384 = 0 AND texts.name = ? COLLATE NOCASE"
        query = query.format(CardsDB.CARD_QUERY)
        parameters = (name,)
        return self.cursor.execute(query, parameters).fetchone()

    # Gets a single card through it's name
    def GetCardByName(self, name: str) -> any:
        query = "SELECT {} WHERE texts.name = ? COLLATE NOCASE"
        query = query.format(CardsDB.CARD_QUERY)
        parameters = (name,)
        return self.cursor.execute(query, parameters).fetchone()

    # Gets all monsters within the domain's race and attributes
    def GetMonstersByAttributeAndRace(self, attributes: list[int], races: list[int]) -> sqlite3.Cursor:
        query = "SELECT {} WHERE datas.type & 1 = 1 AND datas.type & 16384 = 0 AND (datas.attribute in {} OR datas.race in {})"
        attributes_query = "({})".format(",".join(str(s) for s in attributes))
        races_query = "({})".format(",".join(str(s) for s in races))
        query = query.format(CardsDB.CARD_QUERY, attributes_query, races_query)
        return self.cursor.execute(query)
    
    # Gets all monsters outside of the domain's race and attributes; the oppositive of the above method.
    # These are manually checked if they are the same archetype, named in the DM's desc and so on.
    def GetMonstersExcludingAttributeAndRace(self, attributes: list[int], races: list[int]) -> sqlite3.Cursor:
        query = "SELECT {} WHERE datas.type & 1 = 1 AND datas.type & 16384 = 0 AND datas.attribute not in {} AND datas.race not in {}"
        attributes_query = "({})".format(",".join(str(s) for s in attributes))
        races_query = "({})".format(",".join(str(s) for s in races))
        query = query.format(CardsDB.CARD_QUERY, attributes_query, races_query)
        return self.cursor.execute(query)

    # Gets all monsters' ids.
    def GetAllMonsterIds(self) -> list:
        query = "SELECT id from datas WHERE datas.type & 1 = 1 AND datas.type & 16384 = 0"
        return self.cursor.execute(query).fetchall()

    # Get all monsters' names.
    def GetAllMonsterNames(self) -> list:
        query = "SELECT DISTINCT name FROM texts NATURAL JOIN datas WHERE datas.type & 1 = 1 AND datas.type & 16384 = 0 ORDER BY name"
        return self.cursor.execute(query).fetchall()

    # Gets all the cards which are not monsters (nor tokens), so should be only spell and trap cards.
    def GetAllSpellsAndTraps(self) -> sqlite3.Cursor:
        query = "SELECT {} WHERE datas.type & 1 = 0 AND datas.type & 16384 = 0"
        query = query.format(CardsDB.CARD_QUERY)
        return self.cursor.execute(query)