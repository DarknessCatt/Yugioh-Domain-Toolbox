import tkinter
from tkinter import *
import tkinter.scrolledtext

from classes.ydke import YDKE
from classes.card import Card
from classes.databases.cardsDB import CardsDB
from classes.databases.databaseExceptions import CardIdNotFoundError, CardNameNotFoundError

from classes.databases.domainLookup import DomainLookup

# Creates the GUI for the Deck Checker tool.
class ReverseDomainGUI:
    
    def Tab(self, deckCheckerTab : Frame) -> None:

        def OnValidate():
            try:
                decks = YDKE.DecodeYDKE(ydkeText.get().strip())
                if(decks is None):
                    ydkeText.set("")
                    message.delete("1.0", END)
                    message.insert(INSERT, "Could not process YDKE.")
                    return

                desired : list[Card] = []
                for deck in decks:
                    for passcode in deck:
                        data = CardsDB.Instance().GetCardById(passcode)
                        card = Card(data)
                        if card.IsMonster():
                            desired.append(card)

                if(len(desired) == 0):
                    ydkeText.set("")
                    message.delete("1.0", END)
                    message.insert(INSERT, "The deck provided has no monsters.")
                    return

                candidates : list[set] = []
                for card in desired:
                    candidates.append(set(DomainLookup.Instance().FilterMonster(card)))

                validDMs : set = candidates[0]
                for candidate in candidates:
                    validDMs = validDMs.intersection(candidate)

                # TODO: Process this in some way (banlist?)
                dmList = []
                for dm in validDMs:
                    dmList.append(CardsDB.Instance().GetNameById(dm[0]))

                dmList.sort()
                answer = "\n".join(dmList)

            except (CardIdNotFoundError, CardNameNotFoundError) as error:
                answer = f"Couldn't process card [{error.args[0]}].\nKeep in mind pre-released cards are not supported."

            ydkeText.set("")
            message.delete("1.0", END)
            message.insert(INSERT, answer)
            

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