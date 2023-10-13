from sys import exit
import tkinter
from tkinter import *
from tkinter import ttk

from constants.hexCodesReference import AttributesAndRaces, Archetypes

from classes.downloadManager import DownloadManager
from classes.card import Card
from classes.domain import Domain
from classes.sql import CardsCDB
from classes.domainExporter import DomainExporter

# Class that handles the CLI interface of the program
class GraphicalUserInterface:

    TITLE = "Yugioh Domain Generator"

    MSG_WAITING_ID = "Waiting for valid monster ID..."
    MSG_ID_MUST_NUMBER = "ID must be a number!"

    EXPORT_OPT_YGOPRO_CSV = "YGOPRODeck Collection's CSV."
    EXPORT_OPT_SIMULATOR_BANLIST = "EDOPro / YGO Omega Banlist."
    EXPORT_OPT_ALL_ABOVE = "All the above."

    SPELL_OPT_ONLY_MONSTERS = "Domain (won't include spell/traps)"
    SPELL_OPT_ADD_SPELLS = "Domain + spells/traps"
    
    EXPORT_SUCCESS = "'s Domain successfully exported!"

    currDomain = None

    # Runs setups for classes which require external classes.
    def Setup(self):
        if(not DownloadManager.DoesReferenceFolderExist()):
            DownloadManager.DownloadFiles()

        Archetypes.Setup()
        AttributesAndRaces.Setup()
        CardsCDB.Setup()
        print("")
    
    # Gets the deck master and it's domain.
    def GetDeckMasterAndDomain(self, answer: str) -> Domain:
        dm = CardsCDB.GetMonsterById(answer)
        if(not dm is None):
            card = Card(dm)
            domain = Domain(card)
            return domain
        
        return None
    
    # Adds cards to a deckmaster's domain.
    def GetDomainCards(self, domain: Domain, spelltrap: str) -> None:
        data = CardsCDB.GetMonstersByAttributeAndRace(domain)
        for row in data:
            card = Card(row)
            domain.AddCardToDomain(card)

        data = CardsCDB.GetMonstersExcludingAttributeAndRace(domain)
        for row in data:
            card = Card(row)
            domain.CheckAndAddCardToDomain(card)
        
        if(spelltrap == self.SPELL_OPT_ADD_SPELLS):
            data = CardsCDB.GetAllSpellsAndTraps()
            for row in data:
                card = Card(row)
                domain.AddCardToDomain(card)
    
    # Prompt to check which formats the user wants to export the domain.
    def ExportDomain(self, domain: Domain, export) -> None:
        if(export == self.EXPORT_OPT_YGOPRO_CSV):
            DomainExporter.toCSV(domain)
            return
        
        elif(export == self.EXPORT_OPT_SIMULATOR_BANLIST):
            DomainExporter.toIflist(domain)
            return
        
        else:
            DomainExporter.toCSV(domain)
            DomainExporter.toIflist(domain)
            return

    # The main interface loop.
    def StartInterface(self) -> None:
        
        # "Global" Variables
        domain = None
        button = None

        # Interface Callbacks
        def OnIdChanged(*args):
            button["state"] = "disabled"
            answer = idtext.get().strip()

            if not answer.isnumeric():
                idconfirm["text"] = self.MSG_ID_MUST_NUMBER
                return

            nonlocal domain 
            domain = self.GetDeckMasterAndDomain(answer)

            if domain != None:
                print(domain)
                idconfirm["text"] = domain.DM.name
                button["state"] = "normal"
            else:
                idconfirm["text"] = self.MSG_WAITING_ID
        
        def OnGeneratePressed():
            # Add cards to Domain.
            self.GetDomainCards(domain, stchoice.get())

            # Export the domain.
            self.ExportDomain(domain, exportchoice.get())
            
            # Notify on export successful.
            success = tkinter.Label(frame, text = idconfirm["text"] + self.EXPORT_SUCCESS, font=("Arial", 12), fg='#0f0')
            success.pack()
            
            
        # Setup stuff.
        self.Setup()
        
        # TKinter stuff.
        frame = tkinter.Tk()
        frame.geometry("500x450+700+300")
        frame.title(self.TITLE)
        
        # DeckMaster's ID and input
        idlabel = tkinter.Label(frame, text = "Deck Master's id:", font=("Arial", 12))
        idlabel.pack()

        idtext = StringVar()
        idtext.trace("w", OnIdChanged)
        id = tkinter.Entry(frame, textvariable=idtext, width=30)
        id.pack()

        idconfirm = tkinter.Label(frame, text = self.MSG_WAITING_ID, font=("Arial", 12), justify="left")
        idconfirm.pack(pady= 15)

        # Export To
        exportlabel = tkinter.Label(frame, text = "Export to:", font=("Arial", 12))
        exportlabel.pack()

        # Include Spells (or not)
        spelltrap = [self.SPELL_OPT_ADD_SPELLS, self.SPELL_OPT_ONLY_MONSTERS]
        stchoice = ttk.Combobox(frame, values = spelltrap, state = "readonly", width=28)
        stchoice.set(self.SPELL_OPT_ADD_SPELLS)
        stchoice.pack(pady= 15)

        # File Type
        export = [self.EXPORT_OPT_YGOPRO_CSV, self.EXPORT_OPT_SIMULATOR_BANLIST, self.EXPORT_OPT_ALL_ABOVE]
        exportchoice = ttk.Combobox(frame, values = export, state = "readonly", width=28)
        exportchoice.set(self.EXPORT_OPT_YGOPRO_CSV)
        exportchoice.pack(pady= 15)
        
        button = tkinter.Button(frame, text = "Generate Domain", command=OnGeneratePressed, state="disabled")
        button.pack()
        
        frame.mainloop()
        