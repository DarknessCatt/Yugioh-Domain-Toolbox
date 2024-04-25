import sys
import os
import sqlite3

from multiprocessing import Process, Manager

from classes.downloadManager import DownloadManager
from classes.sql import CardsCDB
from constants.hexCodesReference import AttributesAndRaces, Archetypes

from classes.card import Card
from classes.domain import Domain

class Lookup:
    
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

        lookupPath = os.path.join(lookupFolder, Lookup.LOOKUP_FILE)
        if(not os.path.exists(lookupPath)):
            Lookup.CreateDB(lookupPath)

        Lookup.db = sqlite3.connect(lookupPath)
        Lookup.UpdateDB()
        print("Done.\n")

    @staticmethod
    def CreateDB(path : str) -> None:
        Lookup.db = sqlite3.connect(path)

        Lookup.CreateTables()
        Lookup.CreateRelations()

        Lookup.db.commit()
        Lookup.db.close()

    @staticmethod
    def CreateTables() -> None:
        cursor = Lookup.db.cursor()

        create_masters = """
        CREATE TABLE IF NOT EXISTS '{}' (
                'id' INT PRIMARY KEY
            );
        """.format(Lookup.DM_TABLE)
        cursor.execute(create_masters)

        cursor.close()
    
    @staticmethod
    def CreateRelations() -> None:
        cursor = Lookup.db.cursor()

        create_master_relation = """
            CREATE TABLE IF NOT EXISTS '{relation}' (
                '{master}'	    INTEGER,
                '{relation}'	INTEGER,
                PRIMARY KEY('{relation}','{master}'),
                FOREIGN KEY('{master}') REFERENCES '{master}'('id')
            );
        """

        for table in [Lookup.ATTR_TABLE, Lookup.RACE_TABLE, Lookup.ARCH_TABLE]:
            cursor.execute(create_master_relation.format(master=Lookup.DM_TABLE, relation=table))
        
        create_master_stat = """
            CREATE TABLE IF NOT EXISTS '{stat}' (
                '{master}'	INTEGER,
                'atk'	INTEGER,
                'def'	INTEGER,
                PRIMARY KEY('{master}','atk','def'),
                FOREIGN KEY('{master}') REFERENCES '{master}'('id')
            );
        """.format(master=Lookup.DM_TABLE, stat=Lookup.STAT_TABLE)
        cursor.execute(create_master_stat)

        create_master_mention = """
            CREATE TABLE IF NOT EXISTS '{mention}' (
                '{master}'	INTEGER,
                '{mention}'	VARCHAR(255),
                PRIMARY KEY('{mention}','{master}'),
                FOREIGN KEY('{master}') REFERENCES '{master}'('id')
            );
        """.format(master=Lookup.DM_TABLE, mention=Lookup.QUOT_TABLE)
        cursor.execute(create_master_mention)

        cursor.close()

    @staticmethod
    def ProcessDomainsJob(data: list, allDMs: list, start: int, end: int):
        sys.stdout = open('trash', 'w')
        Archetypes.Setup()
        AttributesAndRaces.Setup()
        CardsCDB.Setup()

        for i in range(start, end):
            card = Card(CardsCDB.GetMonsterById(data[i][0]))
            dm = Domain(card)
            allDMs.append(dm)

    @staticmethod
    def UpdateDB() -> None:
        all_monsters = set(CardsCDB.GetAllMonsterIds())
        cursor = Lookup.db.cursor()
        lookup_monsters = set(cursor.execute("Select id FROM {}".format(Lookup.DM_TABLE)).fetchall())
        missing_monsters = all_monsters - lookup_monsters

        if(len(missing_monsters) > 0):
            print("Updating Lookup table (might take a few minutes).")
            
            data = list(missing_monsters)
            manager = Manager()
            allDMs : list[Domain] = manager.list()

            processes : list[Process] = []
            n = 0
            step = len(data) // (8 if len(data) > 7 else 1)

            while(n < len(data)):
                endIndex = min(n + step, len(data))
                processes.append(Process(target=Lookup.ProcessDomainsJob, args=(data, allDMs, n, endIndex)))
                n = endIndex

            for p in processes:
                p.start()

            for p in processes:
                p.join()

            Lookup.AddDomain(allDMs)

    @staticmethod
    def AddDomain(domains : list[Domain]) -> None:
        insert_master = "INSERT OR IGNORE INTO {}(id) VALUES (?);".format(Lookup.DM_TABLE)
        insert_relation = "INSERT OR IGNORE INTO {relation} ({master}, {relation}) VALUES (?,?);"
        insert_stats = "INSERT OR IGNORE INTO {stat}({master}, atk, def) VALUES (?, ?, ?)"

        cursor = Lookup.db.cursor()
        for domain in domains:
            cursor.execute(insert_master, (domain.DM.id,))

            for attr in domain.attributes:
                cursor.execute(insert_relation.format(master=Lookup.DM_TABLE, relation=Lookup.ATTR_TABLE), (domain.DM.id, attr,))

            for race in domain.races:
                cursor.execute(insert_relation.format(master=Lookup.DM_TABLE, relation=Lookup.RACE_TABLE), (domain.DM.id, race,))
            
            for arch in domain.setcodes:
                cursor.execute(insert_relation.format(master=Lookup.DM_TABLE, relation=Lookup.ARCH_TABLE), (domain.DM.id, arch,))
            
            for mention in domain.namedCards:
                cursor.execute(insert_relation.format(master=Lookup.DM_TABLE, relation=Lookup.QUOT_TABLE), (domain.DM.id, mention,))
            
            for stat in domain.battleStats:
                cursor.execute(insert_stats.format(master=Lookup.DM_TABLE, stat=Lookup.STAT_TABLE), (domain.DM.id, stat[0], stat[1]))

        cursor.close()
        Lookup.db.commit()

    @staticmethod
    def FilterMonster(monster : Card):

        filter = Lookup.db.cursor()
        
        select = """
            SELECT id from {master}
            WHERE
                EXISTS (SELECT {master} FROM {attr} WHERE {master}.id = {master} AND {attr} = ?)
                OR EXISTS (SELECT {master} FROM {race} WHERE {master}.id = {master} AND {race} = ?)
                OR EXISTS (SELECT {master} FROM {mention} WHERE {master}.id = {master} AND {mention} = ?)
                OR EXISTS (SELECT {master} FROM {stat} WHERE {master}.id = {master} AND atk = ? AND def = ?)
        """.format(master=Lookup.DM_TABLE,
                    attr=Lookup.ATTR_TABLE, 
                    race=Lookup.RACE_TABLE, 
                    mention=Lookup.QUOT_TABLE, 
                    stat=Lookup.STAT_TABLE)
        
        args = [monster.attribute, monster.race, monster.name.lower(), monster.attack, monster.defense]

        for arch in monster.setcodes:
            select += " OR EXISTS (SELECT {master} FROM {arch} WHERE {master}.id = {master} AND {arch} = ?)".format(master=Lookup.DM_TABLE, arch=Lookup.ARCH_TABLE)
            args.append(Card.GetBaseArchetype(arch))

        return filter.execute(select, tuple(args)).fetchall()
            
