import os
import shutil
import requests

from constants.urlReference import URLs

# Handles the download of files used in the program.
class DownloadManager:
    FILES_BASE_FOLDER = "references"
    CARD_INFO_FOLDER = "cardinfo"
    CDB_FOLDER = "CDBs"

    ATTR_RACES_FILENAME = "attrRaces.txt"
    ARCHETYPES_FILENAME = "archetypes.txt"

    CARDS_CDB = "cards.cdb"
    RELEASE_CDB = "release-"

    @staticmethod
    # Returns true if the reference folder exists.
    # Sort of "check" to see if the files have been downloaded.
    def DoesReferenceFolderExist() -> bool:
        return os.path.exists(DownloadManager.FILES_BASE_FOLDER)

    @staticmethod
    # Returns the path to the folder with cards information.
    def GetCardInfoFolder() -> str:
        return os.path.join(DownloadManager.FILES_BASE_FOLDER, DownloadManager.CARD_INFO_FOLDER)
    
    @staticmethod
    # Returns the path to the folder with the cdbs.
    def GetCdbFolder() -> str:
        return os.path.join(DownloadManager.FILES_BASE_FOLDER, DownloadManager.CDB_FOLDER)

    @staticmethod
    # (Re)Downloads all files needed.
    def DownloadFiles() -> None:
        print("Downloading files.")

        # Delete reference folder if it exists.
        if(DownloadManager.DoesReferenceFolderExist()):
            shutil.rmtree(DownloadManager.FILES_BASE_FOLDER)

        cardInfoFolder = DownloadManager.GetCardInfoFolder()
        cdbFolder = DownloadManager.GetCdbFolder()

        # Make the dirs
        os.mkdir(DownloadManager.FILES_BASE_FOLDER)
        os.mkdir(cardInfoFolder)
        os.mkdir(cdbFolder)

        # Download the attributes and races file
        with open(os.path.join(cardInfoFolder, DownloadManager.ATTR_RACES_FILENAME), "wb") as f:
            r = requests.get(URLs.ATTRIBUTES_AND_RACES)
            f.write(r.content)
            f.seek(0)
        
        # Download the archetypes file
        with open(os.path.join(cardInfoFolder, DownloadManager.ARCHETYPES_FILENAME), "wb") as f:
            r = requests.get(URLs.ARCHETYPES)
            f.write(r.content)
            f.seek(0)
        
        # Download all the cdbs files
        cdbInfo = requests.get(URLs.BABEL_CDB).json()
        for info in cdbInfo:
            fileName = info["name"]
            if(fileName == DownloadManager.CARDS_CDB or fileName.startswith(DownloadManager.RELEASE_CDB)):
                with open(os.path.join(cdbFolder, fileName), "wb") as f:
                    r = requests.get(info["download_url"])
                    f.write(r.content)
                    f.seek(0)
        
        print("Done.\n")
