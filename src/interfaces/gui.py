
import tkinter
from tkinter import ttk

from constants.programInfo import ProgramInfo

from interfaces.guiTabs.domGenTab import DomainGeneratorGUI
from interfaces.guiTabs.deckCheckerTab import DeckCheckerGUI
from interfaces.guiTabs.reverseDomainTab import ReverseDomainGUI

# Class that handles the CLI interface of the program
class GraphicalUserInterface:

    TITLE = "Yugioh Domain Generator ({})"

    # The main interface loop.
    def StartInterface(self) -> None:            
        # TKinter setup.
        frame = tkinter.Tk()
        frame.geometry("500x450+700+300")
        frame.title(self.TITLE.format(ProgramInfo.VERSION))

        # Tab setup
        tabControl = ttk.Notebook(frame)
        domainGeneratorTab = ttk.Frame(tabControl)
        deckCheckerTab = ttk.Frame(tabControl)
        reverseDomainTab = ttk.Frame(tabControl) 

        tabControl.add(domainGeneratorTab, text="Domain Generator")
        tabControl.add(deckCheckerTab, text="Deck Validator")
        tabControl.add(reverseDomainTab, text="Reverse Domain Searcher")
        tabControl.pack(expand = 1, fill ="both") 

        # Domain Generator
        domGenTabClass = DomainGeneratorGUI()
        domGenTabClass.Tab(domainGeneratorTab)
        
        # Deck Checker
        deckCheckerClass = DeckCheckerGUI()
        deckCheckerClass.Tab(deckCheckerTab)

        # Reverse Domain
        reverseDomainClass = ReverseDomainGUI()
        reverseDomainClass.Tab(reverseDomainTab)

        frame.mainloop()
        