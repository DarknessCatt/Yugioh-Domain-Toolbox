
import tkinter
from tkinter import ttk

from constants.programInfo import ProgramInfo

from interfaces.guiTabs.domGenTab import DomainGeneratorGUI
from interfaces.guiTabs.deckCheckerTab import DeckCheckerGUI
from interfaces.guiTabs.reverseDomainTab import ReverseDomainGUI
from interfaces.guiTabs.formatConverterTab import FormatConverterGUI

# Class that handles the CLI interface of the program
class GraphicalUserInterface:

    TITLE = "Yugioh Domain Toolbox ({})"

    # The main interface loop.
    def StartInterface(self) -> None:            
        # TKinter setup.
        frame = tkinter.Tk()
        frame.geometry("600x450+700+300")
        frame.title(self.TITLE.format(ProgramInfo.VERSION))

        # Tab setup
        tabControl = ttk.Notebook(frame)
        domainGeneratorTab = ttk.Frame(tabControl)
        deckCheckerTab = ttk.Frame(tabControl)
        reverseDomainTab = ttk.Frame(tabControl) 
        formatConverterTab = ttk.Frame(tabControl) 

        tabControl.add(domainGeneratorTab, text="Domain Generator")
        tabControl.add(deckCheckerTab, text="Deck Validator")
        tabControl.add(reverseDomainTab, text="Reverse Domain Searcher")
        tabControl.add(formatConverterTab, text="Format Converter")
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

        # Format Converter
        formatConverterClass = FormatConverterGUI()
        formatConverterClass.Tab(formatConverterTab)

        frame.mainloop()
        