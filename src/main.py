import sys
from interfaces.cli import CommandLineInterface
from interfaces.gui import GraphicalUserInterface

from constants.hexCodesReference import AttributesAndRaces, Archetypes
from classes.downloadManager import DownloadManager

from classes.sql import CardsCDB
from classes.lookup import Lookup

# Main function. Runs when main.py is called.
def main():
    DownloadManager.DownloadFiles()
    Archetypes.Setup()
    AttributesAndRaces.Setup()
    CardsCDB.Setup()
    Lookup.Setup()
    print("")

    if("--cli" in sys.argv):
        interface = CommandLineInterface()
    else:
        interface = GraphicalUserInterface()
    
    interface.StartInterface()

main()