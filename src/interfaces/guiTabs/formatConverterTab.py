import tkinter
from tkinter import *
from tkinter import ttk
import tkinter.scrolledtext

from classes.formatter.deckFormatter import DeckFormatter

# Creates the GUI for the Format Converter tool.
class FormatConverterGUI:
    
    FORMAT_YDK = "YDK File"
    FORMAT_YDKE = "YDKE URL"
    FORMAT_NAME = "Name List"
    FORMAT_UNTAP = "Untap Deck"

    def Tab(self, FormatConverterTab : Frame) -> None:

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

        def OnConvert():
            button.config(state=DISABLED)

            from_format = formatDict[fromChoice.get()]
            to_format = formatDict[toChoice.get()]

            encoded_deck = fromText.get('1.0', END)
            deck = DeckFormatter.Instance().Decode(from_format, encoded_deck)

            fromText.delete("1.0", END)
            message.delete("1.0", END)
            button.config(state=NORMAL)

            if deck is None:
                message.insert(INSERT, f"Couldn't convert from [{fromChoice.get()}]")
                return

            converted = DeckFormatter.Instance().Encode(to_format, deck)
            message.insert(INSERT, converted)

        # Select From Format
        fromFormatFrame = ttk.Frame(FormatConverterTab, )

        fromLabel = tkinter.Label(fromFormatFrame, text = "Convert from format:", font=("Arial", 12))
        fromLabel.pack(side=tkinter.LEFT, padx=15)

        fromChoice = ttk.Combobox(fromFormatFrame, values = formatOptions, state = "readonly", width=28)
        fromChoice.set(self.FORMAT_NAME)
        fromChoice.pack(side=tkinter.RIGHT)

        fromFormatFrame.pack(pady= 15)

        # From input field
        fromText = tkinter.scrolledtext.ScrolledText(FormatConverterTab, height=5, font=("Arial", 12))
        fromText.pack()

        # Select To Format
        toFormatFrame = ttk.Frame(FormatConverterTab, )

        toLabel = tkinter.Label(toFormatFrame, text = "Convert to format:", font=("Arial", 12))
        toLabel.pack(side=tkinter.LEFT, padx=15)

        toChoice = ttk.Combobox(toFormatFrame, values = formatOptions, state = "readonly", width=28)
        toChoice.set(self.FORMAT_YDKE)
        toChoice.pack(side=tkinter.RIGHT)

        toFormatFrame.pack(pady= 15)

        # YDKE URL entry
        button = tkinter.Button(FormatConverterTab, text = "Convert", command=OnConvert)
        button.pack(pady= 15)

        message = tkinter.scrolledtext.ScrolledText(FormatConverterTab, height=5, font=("Arial", 12))
        message.pack()