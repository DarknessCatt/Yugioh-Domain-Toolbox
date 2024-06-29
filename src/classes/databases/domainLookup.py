import sys
import os
import sqlite3

from multiprocessing import Process, Manager

from classes.downloadManager import DownloadManager
from classes.databases.cardsDB import CardsDB
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
    STAT_TABLE = "stat"
    QUOT_TABLE = "mention"
    DM_TABLE = "master"

    db = None

    @staticmethod
    def Setup() -> None:
        print("Setting up lookup database.")

        lookupFolder = DownloadManager.GetLookupFolder()
        if(not os.path.exists(lookupFolder)):
           os.mkdir(lookupFolder)

        lookupPath = os.path.join(lookupFolder, DomainLookup.LOOKUP_FILE)
        if(not os.path.exists(lookupPath)):
            DomainLookup.CreateDB(lookupPath)

        DomainLookup.db = sqlite3.connect(lookupPath)
        DomainLookup.UpdateDB()
        print("Done.\n")

    @staticmethod
    def CreateDB(path : str) -> None:
        DomainLookup.db = sqlite3.connect(path)

        DomainLookup.CreateTables()
        DomainLookup.CreateRelations()

        DomainLookup.db.commit()
        DomainLookup.db.close()

    # Creates the basic "DM" table.
    @staticmethod
    def CreateTables() -> None:
        cursor = DomainLookup.db.cursor()

        create_masters = """
        CREATE TABLE IF NOT EXISTS '{}' (
                'id' INT PRIMARY KEY
            );
        """.format(DomainLookup.DM_TABLE)
        cursor.execute(create_masters)

        cursor.close()
    
    # Creates all the relation tables (DM & attribute, DM & type...)
    @staticmethod
    def CreateRelations() -> None:
        cursor = DomainLookup.db.cursor()

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
        
        create_master_stat = """
            CREATE TABLE IF NOT EXISTS '{stat}' (
                '{master}'	INTEGER,
                'atk'	INTEGER,
                'def'	INTEGER,
                PRIMARY KEY('{master}','atk','def'),
                FOREIGN KEY('{master}') REFERENCES '{master}'('id')
            );
        """.format(master=DomainLookup.DM_TABLE, stat=DomainLookup.STAT_TABLE)
        cursor.execute(create_master_stat)

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

        # Jobs don't share the same static variables, so we need to setup these again.
        CardsDB.Setup()

        for i in range(start, end):
            card = Card(CardsDB.GetMonsterById(data[i][0]))
            dm = Domain(card)
            allDMs.append(dm)

    # Updates the DB by adding missing DMs' information.
    @staticmethod
    def UpdateDB() -> None:
        all_monsters = set(CardsDB.GetAllMonsterIds())
        cursor = DomainLookup.db.cursor()
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

            DomainLookup.AddDomain(allDMs)

    # Adds a new domain to the database.
    @staticmethod
    def AddDomain(domains : list[Domain]) -> None:
        insert_master = "INSERT OR IGNORE INTO {}(id) VALUES (?);".format(DomainLookup.DM_TABLE)
        insert_relation = "INSERT OR IGNORE INTO {relation} ({master}, {relation}) VALUES (?,?);"
        insert_stats = "INSERT OR IGNORE INTO {stat}({master}, atk, def) VALUES (?, ?, ?)"

        cursor = DomainLookup.db.cursor()
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
            
            for stat in domain.battleStats:
                cursor.execute(insert_stats.format(master=DomainLookup.DM_TABLE, stat=DomainLookup.STAT_TABLE), (domain.DM.id, stat[0], stat[1]))

        cursor.close()
        DomainLookup.db.commit()

    # Returns all DMs that have the given monster card in their domain.
    @staticmethod
    def FilterMonster(monster : Card):
        filter = DomainLookup.db.cursor()
        
        select = """
            SELECT id from {master}
            WHERE
                EXISTS (SELECT {master} FROM {attr} WHERE {master}.id = {master} AND {attr} = ?)
                OR EXISTS (SELECT {master} FROM {race} WHERE {master}.id = {master} AND {race} = ?)
                OR EXISTS (SELECT {master} FROM {mention} WHERE {master}.id = {master} AND {mention} = ?)
                OR EXISTS (SELECT {master} FROM {stat} WHERE {master}.id = {master} AND atk = ? AND def = ?)
        """.format(master=DomainLookup.DM_TABLE,
                    attr=DomainLookup.ATTR_TABLE, 
                    race=DomainLookup.RACE_TABLE, 
                    mention=DomainLookup.QUOT_TABLE, 
                    stat=DomainLookup.STAT_TABLE)
        
        args = [monster.attribute, monster.race, monster.name.lower(), monster.attack, monster.defense]

        for arch in monster.setcodes:
            select += " OR EXISTS (SELECT {master} FROM {arch} WHERE {master}.id = {master} AND {arch} = ?)".format(master=DomainLookup.DM_TABLE, arch=DomainLookup.ARCH_TABLE)
            args.append(Archetypes.Instance().GetBaseArchetype(arch))

        return filter.execute(select, tuple(args)).fetchall()
            
