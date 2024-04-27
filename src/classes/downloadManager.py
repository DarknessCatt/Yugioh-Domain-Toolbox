import os
import requests

from datetime import datetime, timezone, timedelta
from constants.urlReference import URLs

# Handles the download of files used in the program.
class DownloadManager:
    FILES_BASE_FOLDER = "references"
    CARD_INFO_FOLDER = "cardinfo"
    CDB_FOLDER = "CDBs"
    LOOKUP_FOLDER = "Lookup"

    DOWNLOAD_INFO_FILENAME = "downData"
    ATTR_RACES_FILENAME = "attrRaces.txt"
    ARCHETYPES_FILENAME = "archetypes.txt"
    PRE_ARCHETYPES_FILENAME = "archetypes2.txt"

    # The prefix used in the file with all the merged CDBs
    MERGED_CDB_PREFIX = 'merged_'
    CARDS_CDB = "cards.cdb"
    RELEASE_CDB = "release-"

    # Checks if the reference folder (where all data is stored)
    # exists or not.
    @staticmethod
    def DoesReferenceFolderExist() -> bool:
        return os.path.exists(DownloadManager.FILES_BASE_FOLDER)

    # Returns the path to the download information time,
    # that stores information regarding the download manager.
    @staticmethod
    def GetDownloadInfoFile() -> str:
        return os.path.join(DownloadManager.FILES_BASE_FOLDER, DownloadManager.DOWNLOAD_INFO_FILENAME)

    @staticmethod
    # Returns the path to the folder with cards information.
    def GetCardInfoFolder() -> str:
        return os.path.join(DownloadManager.FILES_BASE_FOLDER, DownloadManager.CARD_INFO_FOLDER)
    
    @staticmethod
    # Returns the path to the folder with the cdbs.
    def GetCdbFolder() -> str:
        return os.path.join(DownloadManager.FILES_BASE_FOLDER, DownloadManager.CDB_FOLDER)

    @staticmethod
    def GetLookupFolder() -> str:
        return os.path.join(DownloadManager.FILES_BASE_FOLDER, DownloadManager.LOOKUP_FOLDER)

    # Returns the path to the merged CDB file.
    @staticmethod
    def GetMergedCDBPath() -> str:
        return os.path.join(DownloadManager.GetCdbFolder(), DownloadManager.MERGED_CDB_PREFIX + DownloadManager.CARDS_CDB)

    # Returns all cdb files that should be downloaded from BabelCDB.
    @staticmethod
    def GetCdbsForDownload() -> list:
        files = []
        cdbInfo = requests.get(URLs.BABEL_CDB).json()
        for info in cdbInfo:
            fileName = info["name"]
            if(fileName == DownloadManager.CARDS_CDB or fileName.startswith(DownloadManager.RELEASE_CDB)):
                files.append((fileName, info["download_url"]))
        return files

    # Checks if a given file was changed since the last_update.
    # This is done by pinging github's api to get the last commit that changed this file
    # and using it's date as reference.
    @staticmethod
    def CheckIfFileWasUpdatedFromURL(URL : str, last_update : datetime) -> bool:
        fileInfo = requests.get(URL).json()
        
        # If it contains "message", it means it returned this:
            # {'message': "API rate limit exceeded for IP. 
            # (But here's the good news: Authenticated requests get a higher rate limit. Check out the documentation for more details.)",
            # 'documentation_url': 'https://docs.github.com/rest/overview/resources-in-the-rest-api#rate-limiting'}
        if("message" in fileInfo):
            return False

        fileTime = datetime.fromisoformat(fileInfo[0]["commit"]["committer"]["date"].replace("Z","+00:00"))
        
        if(fileTime > last_update):
            return True
        
        return False

    @staticmethod
    # (Re)Downloads all files needed.
    def DownloadFiles() -> None:
        print("Checking for updates...")

        # Make the dirs
        if(not os.path.exists(DownloadManager.FILES_BASE_FOLDER)):
            os.mkdir(DownloadManager.FILES_BASE_FOLDER)

        cardInfoFolder = DownloadManager.GetCardInfoFolder()
        if(not os.path.exists(cardInfoFolder)):
            os.mkdir(cardInfoFolder)

        cdbFolder = DownloadManager.GetCdbFolder()
        if(not os.path.exists(cdbFolder)):
            os.mkdir(cdbFolder)

        lastUpdate = datetime.min.replace(tzinfo=timezone.utc)
        infoPath = DownloadManager.GetDownloadInfoFile()
        if(os.path.isfile(infoPath)):
            with open(infoPath, "r") as f:
                lastUpdate = datetime.fromisoformat(f.read())

        # Only check for updates if it has been 30 minutes since last check
        # Just to avoid spamming github's api, but also saves internet I guess.
        shouldCheckForUpdate = datetime.now(timezone.utc) - lastUpdate > timedelta(minutes=30)
        updated = False

        # Download the attributes and races file
        attrRacesFile = os.path.join(cardInfoFolder, DownloadManager.ATTR_RACES_FILENAME)
        if(not os.path.isfile(attrRacesFile) 
            or (shouldCheckForUpdate 
                and DownloadManager.CheckIfFileWasUpdatedFromURL(URLs.ATTRIBUTES_AND_RACES_TIME, lastUpdate))):
            
            updated = True
            print("Updating attributes and types.")
            with open(attrRacesFile, "wb") as f:
                r = requests.get(URLs.ATTRIBUTES_AND_RACES)
                f.write(r.content)
                f.seek(0)
            
        # Download the archetypes files
        archFile = os.path.join(cardInfoFolder, DownloadManager.ARCHETYPES_FILENAME)
        if(not os.path.isfile(archFile) 
            or (shouldCheckForUpdate 
                and DownloadManager.CheckIfFileWasUpdatedFromURL(URLs.ARCHETYPES_TIME, lastUpdate))):
            
            updated = True
            print("Updating archetypes.")
            with open(archFile, "wb") as f:
                r = requests.get(URLs.ARCHETYPES)
                f.write(r.content)
                f.seek(0)
        
        preArchFile = os.path.join(cardInfoFolder, DownloadManager.PRE_ARCHETYPES_FILENAME)
        if(not os.path.isfile(preArchFile) 
            or (shouldCheckForUpdate 
                and DownloadManager.CheckIfFileWasUpdatedFromURL(URLs.PRE_ARCHETYPES_TIME, lastUpdate))):
            
            updated = True
            print("Updating pre-release archetypes.")
            with open(preArchFile, "wb") as f:
                r = requests.get(URLs.PRE_ARCHETYPES)
                f.write(r.content)
                f.seek(0)
        
        # Download all the cdbs files
        mergedCDBPath = DownloadManager.GetMergedCDBPath()
        if(not os.path.isfile(mergedCDBPath)
            # We only check the last commit of babelCDB because it would be too many requests to
            # do a per-file check. Not perfect, but better than nothing.
            or (shouldCheckForUpdate 
                and DownloadManager.CheckIfFileWasUpdatedFromURL(URLs.BABEL_CDB_TIME, lastUpdate))):

            updated = True
            print("Updating cards database.")

            if(os.path.isfile(mergedCDBPath)):
                os.remove(mergedCDBPath)

            for file in DownloadManager.GetCdbsForDownload():
                with open(os.path.join(cdbFolder, file[0]), "wb") as f:
                    r = requests.get(file[1])
                    f.write(r.content)
                    f.seek(0)
    
        # Update the download information file with the last date updated
        if(shouldCheckForUpdate or updated):
            with open(DownloadManager.GetDownloadInfoFile(), "w") as f:
                f.write(str(datetime.now(timezone.utc).isoformat()))
                f.seek(0)

        print("Done.\n")
