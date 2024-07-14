import sys
from multiprocessing import freeze_support

from interfaces.cli import CommandLineInterface
from interfaces.gui import GraphicalUserInterface

from classes.textParsers.archetypes import Archetypes
from classes.textParsers.attributes import Attributes
from classes.textParsers.races import Races
from classes.downloadManager import DownloadManager

from classes.databases.cardsDB import CardsDB
from classes.databases.domainLookup import DomainLookup

# Main function. Runs when main.py is called.
def main():
    freeze_support()

    # Setup
    DownloadManager.DownloadFiles()
    Archetypes.Instance()
    Attributes.Instance()
    Races.Instance()
    CardsDB.Instance()
    DomainLookup.Instance()
    print("")

    if("--cli" in sys.argv):
        interface = CommandLineInterface()
    else:
        interface = GraphicalUserInterface()
    
    interface.StartInterface()

if __name__ == '__main__':
    main()