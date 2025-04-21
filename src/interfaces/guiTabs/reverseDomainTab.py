import tkinter
from tkinter import *
from tkinter import ttk
import tkinter.scrolledtext

from classes.card import Card
from classes.databases.cardsDB import CardsDB
from classes.databases.databaseExceptions import CardIdNotFoundError, CardNameNotFoundError
from classes.formatter.deckFormatter import DeckFormatter

from classes.databases.domainLookup import DomainLookup

# Creates the GUI for the Deck Checker tool.
class ReverseDomainGUI:
    
    FORMAT_YDK = "YDK File"
    FORMAT_YDKE = "YDKE URL"
    FORMAT_NAME = "Name List"
    FORMAT_UNTAP = "Untap Deck"

    def Tab(self, deckCheckerTab : Frame) -> None:

        formatOptions = [
            self.FORMAT_YDK,
            self.FORMAT_YDKE,
            self.FORMAT_NAME,
            self.FORMAT_UNTAP
        ]

        formatDict = {
            self.FORMAT_YDK  : DeckFormatter.Format.YDK,            
            self.FORMAT_YDKE : DeckFormatter.Format.YDKE,
            self.FORMAT_NAME : DeckFormatter.Format.NAMES,
            self.FORMAT_UNTAP: DeckFormatter.Format.UNTAP
        }

        def OnValidate():
            try:
                decks = DeckFormatter.Instance().Decode(DeckFormatter.Format.YDKE, ydkeText.get().strip())
                if(decks is None):
                    ydkeText.set("")
                    message.delete("1.0", END)
                    message.insert(INSERT, "Could not process YDKE.")
                    return

                desired : list[Card] = []
                for deck in decks:
                    desired += [card for card in deck if card.IsMonster()]

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

                # Convert DMs to list
                to_format = formatDict[toChoice.get()]

                deck = [[], [], []]
                for dm in validDMs:
                    card = Card(CardsDB.Instance().GetCardById(dm[0]))
                    if card.IsExtraDeckMonster():
                        deck[1].append(card)
                    else:
                        deck[0].append(card)

                answer = DeckFormatter.Instance().Encode(to_format, deck)

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

        # Select To Format
        toFormatFrame = ttk.Frame(deckCheckerTab, )

        toChoice = ttk.Combobox(toFormatFrame, values = formatOptions, state = "readonly", width=14)
        toChoice.set(self.FORMAT_NAME)
        toChoice.pack(side=tkinter.LEFT)

        button = tkinter.Button(toFormatFrame, text = "Search", command=OnValidate)
        button.pack(side=tkinter.RIGHT, padx=5)

        toFormatFrame.pack(pady= 15)

        message = tkinter.scrolledtext.ScrolledText(deckCheckerTab, font=("Arial", 12))
        message.pack()