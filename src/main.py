import sys
from multiprocessing import freeze_support

from interfaces.cli import CommandLineInterface
from interfaces.gui import GraphicalUserInterface

from constants.hexCodesReference import AttributesAndRaces
from classes.textParsers.archetypes import Archetypes
from classes.downloadManager import DownloadManager

from classes.sql import CardsCDB
from classes.lookup import DomainLookup

# Main function. Runs when main.py is called.
def main():
    freeze_support()

    # Setup
    DownloadManager.DownloadFiles()
    Archetypes.Instance()
    AttributesAndRaces.Setup()
    CardsCDB.Setup()
    DomainLookup.Setup()
    print("")

    if("--cli" in sys.argv):
        interface = CommandLineInterface()
    else:
        interface = GraphicalUserInterface()
    
    interface.StartInterface()

if __name__ == '__main__':
    main()