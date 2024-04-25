import tkinter
from tkinter import *
import tkinter.scrolledtext

from classes.ydke import YDKE
from classes.card import Card
from classes.sql import CardsCDB

from classes.lookup import Lookup

# Creates the GUI for the Deck Checker tool.
class ReverseDomainGUI:
    
    def Tab(self, deckCheckerTab : Frame) -> None:

        def OnValidate():
            decks = YDKE.DecodeYDKE(ydkeText.get().strip())
            if(decks is None):
                ydkeText.set("")
                message.delete("1.0", END)
                message.insert(INSERT, "Could not process YDKE.")
                return

            desired : list[Card] = []
            for deck in decks:
                for passcode in deck:
                    data = CardsCDB.GetMonsterById(passcode)
                    if(not data is None):
                        desired.append(Card(data))
            
            candidates : list[set] = []
            for card in desired:
                candidates.append(set(Lookup.FilterMonster(card)))

            validDMs : set = candidates[0]
            for candidate in candidates:
                validDMs = validDMs.intersection(candidate)

            # TODO: Process this in some way (banlist?)
            dmList = []
            for dm in validDMs:
                dmList.append(CardsCDB.GetNameById(dm[0]))
            
            dmList.sort()

            ydkeText.set("")
            message.delete("1.0", END)
            message.insert(INSERT, "\n".join(dmList))

        # YDKE URL entry
        urlLabel = tkinter.Label(deckCheckerTab, text = "YDKE URL:", font=("Arial", 12))
        urlLabel.pack()

        ydkeText = StringVar()
        ydkeEntry = tkinter.Entry(deckCheckerTab, textvariable=ydkeText, width=60)
        ydkeEntry.pack()

        button = tkinter.Button(deckCheckerTab, text = "Search", command=OnValidate)
        button.pack(pady= 15)

        message = tkinter.scrolledtext.ScrolledText(deckCheckerTab, font=("Arial", 12))
        message.pack()