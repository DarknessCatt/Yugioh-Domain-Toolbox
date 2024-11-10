import tkinter
from tkinter import *
import tkinter.scrolledtext

from classes.deckChecker import DeckChecker
from classes.databases.databaseExceptions import CardIdNotFoundError

# Creates the GUI for the Deck Checker tool.
class DeckCheckerGUI:
    
    def Tab(self, deckCheckerTab : Frame) -> None:

        def OnValidate():
            try:
                validation = DeckChecker.CheckDeck(ydkeText.get().strip())
            except CardIdNotFoundError as error:
                validation = f"Couldn't process card with id [{error.args[0]}]. Keep in mind pre-release cards are not supported."

            ydkeText.set("")
            message.delete("1.0", END)
            message.insert(INSERT, validation)

        # YDKE URL entry
        urlLabel = tkinter.Label(deckCheckerTab, text = "YDKE URL:", font=("Arial", 12))
        urlLabel.pack()

        ydkeText = StringVar()
        ydkeEntry = tkinter.Entry(deckCheckerTab, textvariable=ydkeText, width=60)
        ydkeEntry.pack()

        button = tkinter.Button(deckCheckerTab, text = "Validate", command=OnValidate)
        button.pack(pady= 15)

        message = tkinter.scrolledtext.ScrolledText(deckCheckerTab, font=("Arial", 12))
        message.pack()