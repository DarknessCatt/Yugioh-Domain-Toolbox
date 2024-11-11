import tkinter
from tkinter import *
from tkinter import ttk
import tkinter.scrolledtext

from classes.card import Card
from classes.domain import Domain
from classes.databases.cardsDB import CardsDB
from classes.databases.databaseExceptions import CardIdNotFoundError, CardNameNotFoundError
from classes.databases.domainLookup import DomainLookup

from classes.domainExporter import DomainExporter

from interfaces.guiTabs.autoCompleteEntry import AutoCompleteEntry

# Creates the GUI for the Domain Generator tool.
class DomainGeneratorGUI:
    MSG_WAITING_ID = "\n\nWaiting for monster's name...\n\n\n"

    EXPORT_OPT_YGOPRO_CSV = "YGOPRODeck Collection's CSV."
    EXPORT_OPT_SIMULATOR_BANLIST = "EDOPro / YGO Omega Banlist."
    EXPORT_OPT_ALL_ABOVE = "All of the above."

    SPELL_OPT_ONLY_MONSTERS = "Domain (won't include spell/traps)"
    SPELL_OPT_ADD_SPELLS = "Domain + spells/traps"
    
    EXPORT_SUCCESS = "'s Domain successfully exported!"

    currDomain = None

    # Gets the deck master and it's domain.
    def GetDeckMasterAndDomain(self, answer: str) -> Domain:
        dm = None

        try:
            if(answer.isnumeric()):
                dm = CardsDB.Instance().GetCardById(answer)
            else:
                dm = CardsDB.Instance().GetCardByName(answer)
    
            card = Card(dm)
            if(not card.IsMonster()):
                return None

            data = DomainLookup.Instance().GetDomain(card)
            domain = Domain.GenerateFromData(card, data)
            return domain
        
        except (CardIdNotFoundError, CardNameNotFoundError):
            # Printing messages here spams the console.
            # Most of the time, it's just that the user is mid typing.
            return None
    
    # Adds cards to a deckmaster's domain.
    def GetDomainCards(self, domain: Domain, spelltrap: str) -> None:
        # Remove all cards before adding new ones.
        domain.RemoveAllCards()

        data = CardsDB.Instance().GetMonstersByAttributeAndRace(domain.attributes, domain.races)
        for row in data:
            card = Card(row)
            domain.AddCardToDomain(card)

        data = CardsDB.Instance().GetMonstersExcludingAttributeAndRace(domain.attributes, domain.races)
        for row in data:
            card = Card(row)
            domain.CheckAndAddCardToDomain(card)
        
        if(spelltrap == self.SPELL_OPT_ADD_SPELLS):
            data = CardsDB.Instance().GetAllSpellsAndTraps()
            for row in data:
                card = Card(row)
                domain.AddCardToDomain(card)
    
    # Prompt to check which formats the user wants to export the domain.
    def ExportDomain(self, domain: Domain, export) -> None:
        if(export == self.EXPORT_OPT_YGOPRO_CSV):
            DomainExporter.toCSV(domain)
            return
        
        elif(export == self.EXPORT_OPT_SIMULATOR_BANLIST):
            DomainExporter.toLflist(domain)
            return
        
        else:
            DomainExporter.toCSV(domain)
            DomainExporter.toLflist(domain)
            return

    def Tab(self, domainGeneratorTab : Frame) -> None:
        # "Global" Variables
        domain = None
        button = None

        domainText = StringVar()
        domainText.set(self.MSG_WAITING_ID)

        generatedText = StringVar()
        generatedText.set("")

        monsterNames = [name[0] for name in CardsDB.Instance().GetAllMonsterNames()]      

        # Interface Callbacks
        def OnIdChanged(*args):
            button["state"] = "disabled"
            answer = idtext.get().strip()

            nonlocal domain 
            domain = self.GetDeckMasterAndDomain(answer)

            if domain != None:
                print(domain)
                print()
                domainText.set(str(domain))
                button["state"] = "normal"
            else:
                domainText.set(self.MSG_WAITING_ID)
        
        def OnGeneratePressed():
            # Add cards to Domain.
            self.GetDomainCards(domain, stchoice.get())

            # Export the domain.
            self.ExportDomain(domain, exportchoice.get())
            
            # Notify on export successful.
            success.insert(INSERT, domain.DM.name + self.EXPORT_SUCCESS + "\n")

        # DeckMaster's ID and input
        infoFrame = ttk.Frame(domainGeneratorTab, )

        # Left side of the info
        leftside = ttk.Frame(infoFrame)

        idlabel = tkinter.Label(leftside, text = "Deck Master's Name:", font=("Arial", 12))
        idlabel.pack()

        idtext = StringVar()
        idtext.trace_add("write", OnIdChanged)
        id = AutoCompleteEntry(monsterNames, leftside, textvariable=idtext, width=30)
        id.pack()

        leftside.pack(side=tkinter.LEFT, padx=15)

        # Right side of the info
        idconfirm = tkinter.Label(infoFrame, textvariable=domainText, font=("Arial", 12), justify="left", width=100, wraplength=350)
        idconfirm.pack(side=tkinter.RIGHT)

        infoFrame.pack(pady= 15)

        # Export To
        exportlabel = tkinter.Label(domainGeneratorTab, text = "Export to:", font=("Arial", 12))
        exportlabel.pack()

        # Include Spells (or not)
        spelltrap = [self.SPELL_OPT_ADD_SPELLS, self.SPELL_OPT_ONLY_MONSTERS]
        stchoice = ttk.Combobox(domainGeneratorTab, values = spelltrap, state = "readonly", width=28)
        stchoice.set(self.SPELL_OPT_ADD_SPELLS)
        stchoice.pack(pady= 15)

        # File Type
        export = [self.EXPORT_OPT_YGOPRO_CSV, self.EXPORT_OPT_SIMULATOR_BANLIST, self.EXPORT_OPT_ALL_ABOVE]
        exportchoice = ttk.Combobox(domainGeneratorTab, values = export, state = "readonly", width=28)
        exportchoice.set(self.EXPORT_OPT_YGOPRO_CSV)
        exportchoice.pack(pady= 15)
        
        button = tkinter.Button(domainGeneratorTab, text = "Generate Domain", command=OnGeneratePressed, state="disabled")
        button.pack(pady= 15)

        success = tkinter.scrolledtext.ScrolledText(domainGeneratorTab, font=("Arial", 12), fg='#0f0')
        success.pack()