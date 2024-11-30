import sys
import os
import sqlite3

from multiprocessing import Process, Manager

from classes.downloadManager import DownloadManager
from classes.databases.cardsDB import CardsDB
from classes.databases.databaseExceptions import CardIdNotFoundError, CardNameNotFoundError
from classes.textParsers.archetypes import Archetypes

from classes.card import Card
from classes.domain import Domain

# Holds all domains' information.
# Used by the Reverse Searcher to quick lookup domains.
class DomainLookup:
    
    LOOKUP_FILE = "lookup.sqlite3"

    ATTR_TABLE = "attribute"
    RACE_TABLE = "race"
    ARCH_TABLE = "archetype"
    QUOT_TABLE = "mention"
    DM_TABLE = "master"

    _instance = None

    @staticmethod
    def Instance():
        if(DomainLookup._instance is None):
            DomainLookup()

        return DomainLookup._instance

    def __init__(self) -> None:
        if(not DomainLookup._instance is None):
            raise Warning("This class is a Singleton!")

        DomainLookup._instance = self

        print("Setting up lookup database.")
        lookupFolder = DownloadManager.GetLookupFolder()
        if(not os.path.exists(lookupFolder)):
           os.mkdir(lookupFolder)

        lookupPath = os.path.join(lookupFolder, DomainLookup.LOOKUP_FILE)
        if(not os.path.exists(lookupPath)):
            DomainLookup.CreateDB(lookupPath)

        self.db = sqlite3.connect(lookupPath)
        self.UpdateDB()
        print("Done.\n")

    @staticmethod
    def CreateDB(path : str) -> None:
        db = sqlite3.connect(path)

        DomainLookup.CreateTables(db)
        DomainLookup.CreateRelations(db)

        db.commit()
        db.close()

    # Creates the basic "DM" table.
    @staticmethod
    def CreateTables(db: sqlite3.Connection) -> None:
        cursor = db.cursor()

        create_masters = """
        CREATE TABLE IF NOT EXISTS '{}' (
                'id' INT PRIMARY KEY
            );
        """.format(DomainLookup.DM_TABLE)
        cursor.execute(create_masters)

        cursor.close()
    
    # Creates all the relation tables (DM & attribute, DM & type...)
    @staticmethod
    def CreateRelations(db: sqlite3.Connection) -> None:
        cursor = db.cursor()

        create_master_relation = """
            CREATE TABLE IF NOT EXISTS '{relation}' (
                '{master}'	    INTEGER,
                '{relation}'	INTEGER,
                PRIMARY KEY('{relation}','{master}'),
                FOREIGN KEY('{master}') REFERENCES '{master}'('id')
            );
        """

        for table in [DomainLookup.ATTR_TABLE, DomainLookup.RACE_TABLE, DomainLookup.ARCH_TABLE]:
            cursor.execute(create_master_relation.format(master=DomainLookup.DM_TABLE, relation=table))

        create_master_mention = """
            CREATE TABLE IF NOT EXISTS '{mention}' (
                '{master}'	INTEGER,
                '{mention}'	VARCHAR(255),
                PRIMARY KEY('{mention}','{master}'),
                FOREIGN KEY('{master}') REFERENCES '{master}'('id')
            );
        """.format(master=DomainLookup.DM_TABLE, mention=DomainLookup.QUOT_TABLE)
        cursor.execute(create_master_mention)

        cursor.close()

    # Generates the domain for a list of cards in the given interval.
    # Called by "UpdateDB" in a multiprocesses.
    @staticmethod
    def ProcessDomainsJob(data: list, allDMs: list, start: int, end: int):
        sys.stdout = open(os.devnull, 'w')

        for i in range(start, end):
            try:
                card = Card(CardsDB.Instance().GetMonsterById(data[i][0]))
                dm = Domain.GenerateFromCard(card)
                allDMs.append(dm)
            except CardIdNotFoundError as error:
                print(f"Could not find card with id [{error.args[0]}]")

    # Updates the DB by adding missing DMs' information.
    def UpdateDB(self) -> None:
        all_monsters = set(CardsDB.Instance().GetAllMonsterIds())
        cursor = self.db.cursor()
        lookup_monsters = set(cursor.execute("Select id FROM {}".format(DomainLookup.DM_TABLE)).fetchall())

        # Here we compare all the DMs in the CardCDB with all the DMs in the Lookup.
        # If both tables are up to date, missing monsters should be empty.
        missing_monsters = all_monsters - lookup_monsters

        if(len(missing_monsters) > 0):
            print("Updating Lookup table (might take a few minutes).")
            
            data = list(missing_monsters)
            manager = Manager()
            allDMs : list[Domain] = manager.list()

            processes : list[Process] = []
            n = 0

            # division by 8 so it splits into 8 processes (most pcs have 4 multicores, so thats why)
            # but if there are less than 8 monsters to insert, use one instead (otherwise the indexes get bad)
            step = len(data) // (8 if len(data) > 7 else 1)

            while(n < len(data)):
                endIndex = min(n + step, len(data))
                processes.append(Process(target=DomainLookup.ProcessDomainsJob, args=(data, allDMs, n, endIndex)))
                n = endIndex

            for p in processes:
                p.start()

            for p in processes:
                p.join()

            self.AddDomains(allDMs)

    # Adds a new domain to the database.
    def AddDomains(self, domains : list[Domain]) -> None:
        insert_master = "INSERT OR IGNORE INTO {}(id) VALUES (?);".format(DomainLookup.DM_TABLE)
        insert_relation = "INSERT OR IGNORE INTO {relation} ({master}, {relation}) VALUES (?,?);"

        cursor = self.db.cursor()
        for domain in domains:
            cursor.execute(insert_master, (domain.DM.id,))

            for attr in domain.attributes:
                cursor.execute(insert_relation.format(master=DomainLookup.DM_TABLE, relation=DomainLookup.ATTR_TABLE), (domain.DM.id, attr,))

            for race in domain.races:
                cursor.execute(insert_relation.format(master=DomainLookup.DM_TABLE, relation=DomainLookup.RACE_TABLE), (domain.DM.id, race,))
            
            for arch in domain.setcodes:
                cursor.execute(insert_relation.format(master=DomainLookup.DM_TABLE, relation=DomainLookup.ARCH_TABLE), (domain.DM.id, arch,))
            
            for mention in domain.namedCards:
                cursor.execute(insert_relation.format(master=DomainLookup.DM_TABLE, relation=DomainLookup.QUOT_TABLE), (domain.DM.id, mention,))
            
        cursor.close()
        self.db.commit()

    # Returns all DMs that have the given monster card in their domain.
    def FilterMonster(self, monster : Card):
        filter = self.db.cursor()
        
        select = """
            SELECT id from {master}
            WHERE
                EXISTS (SELECT {master} FROM {attr} WHERE {master}.id = {master} AND {attr} = ?)
                OR EXISTS (SELECT {master} FROM {race} WHERE {master}.id = {master} AND {race} = ?)
                OR EXISTS (SELECT {master} FROM {mention} WHERE {master}.id = {master} AND {mention} = ?)""".format(
                    master=DomainLookup.DM_TABLE,
                    attr=DomainLookup.ATTR_TABLE, 
                    race=DomainLookup.RACE_TABLE, 
                    mention=DomainLookup.QUOT_TABLE
            )
        
        args = [monster.attribute, monster.race, monster.name.lower()]

        for arch in monster.setcodes:
            base_archs = Archetypes.Instance().GetBaseArchetype(arch)
            if base_archs is not None:
                for base_arch in base_archs:
                    select += "\n                OR EXISTS (SELECT {master} FROM {arch} WHERE {master}.id = {master} AND {arch} = ?)".format(master=DomainLookup.DM_TABLE, arch=DomainLookup.ARCH_TABLE)
                    args.append(base_arch)

        return filter.execute(select, tuple(args)).fetchall()
    
    # Retrieves all data from the given monster card
    # Make sure the data retrieve matches Domain's "GenerateFromLookup" method.
    def GetDomain(self, monster : Card) -> list:
        cursor = self.db.cursor()

        generic_query = "Select {table} from {table} where {master} = ?"

        data = []
        arg = tuple([monster.id])

        for table in [DomainLookup.ATTR_TABLE, DomainLookup.RACE_TABLE, DomainLookup.ARCH_TABLE, DomainLookup.QUOT_TABLE]:
            query = generic_query.format(master=DomainLookup.DM_TABLE, table=table)
            data.append(cursor.execute(query, arg).fetchall())
        
        cursor.close()

        return data