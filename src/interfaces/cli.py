from sys import exit

from constants.programInfo import ProgramInfo

from classes.card import Card
from classes.domain import Domain
from classes.databases.cardsDB import CardsDB
from classes.databases.databaseExceptions import CardIdNotFoundError, CardNameNotFoundError
from classes.domainExporter import DomainExporter
from classes.formatter.deckFormatter import DeckFormatter

from classes.deckChecker import DeckChecker
from classes.databases.domainLookup import DomainLookup

# Class that handles the CLI interface of the program
class CommandLineInterface:

    # Common messages used throughout the interface

    PLEASE_NUMBER = "Please, input only the required number."
    OR_EXIT = "Or \"exit\" (without quotes) to close the program."
    
    PRESS_ENTER_CONTINUE = "Press enter to continue."

    NOT_DIGIT_ANSWER = "The value provided doesn't seem to be an integer."
    INVALID_ANSWER = "The value provided is not a valid option."

    # Requests the user input, adding common prints and exiting if needed.
    def RequestInput(self, inputMessage : str = None) -> str:
        print(self.PLEASE_NUMBER if inputMessage is None else inputMessage)
        print(self.OR_EXIT)
        
        answer = input().strip()
        print("")

        if(answer.lower() == 'exit'):
            print("Bye bye!\n")
            exit()
        
        return answer

    # Prints an information message, requiring the user to press enter before continuing
    def InfoMessage(self, msg: str) -> None:
        print(msg)
        print(self.PRESS_ENTER_CONTINUE)
        input()
        print("")

    # The program's intro, which gives the user the option to update files before continuing.
    def IntroInput(self) -> None:
        print("Welcome to Domain Toolbox! Version {}\n".format(ProgramInfo.VERSION))
    
    def DecideTool(self) -> int:
        while(True):
            print("Which tool do you want to use?")
            print("(1) Domain Generator.")
            print("(2) Deck Validator.")
            print("(3) Reverse Domain Searcher.")
            print("(4) Deck Format Converter.")
            answer = self.RequestInput()

            if(not answer.isdigit()):
                self.InfoMessage(self.NOT_DIGIT_ANSWER)
                continue
            
            else:
                option = int(answer)
                if(option <= 0 or option > 4):
                    self.InfoMessage(self.INVALID_ANSWER)
                    continue
                else:
                    return option
                    

    # Prompt to get the deck master and it's domain.
    def GetDeckMasterAndDomain(self) -> Domain:
        while(True):
            print("What is the Deck Master's id? (passcode).")
            answer = self.RequestInput()

            if(not answer.isdigit()):
                self.InfoMessage(self.NOT_DIGIT_ANSWER)
                continue
            
            else:
                try:
                    card = Card(CardsDB.Instance().GetCardById(answer))
                    if(not card.IsMonster()):
                        self.InfoMessage(f"Sorry, the card with id [{error.args[0]}] is not a monster.\nAre you sure this is the correct id?")

                    data = DomainLookup.Instance().GetDomain(card)
                    domain = Domain.GenerateFromData(card, data)
                    print(domain)
                    print("")
                    return domain
                except CardIdNotFoundError as error:
                    self.InfoMessage(f"Sorry, I could not find card with id: [{error.args[0]}]\nKeep in mind pre-release cards are not supported.")
                    continue
        
    
    # Prompt that adds cards to a deckmaster's domain.
    def GetDomainCards(self, domain: Domain) -> None:
        print("Retrieving monsters in this domain...")

        data = CardsDB.Instance().GetMonstersByAttributeAndRace(domain.attributes, domain.races)
        for row in data:
            card = Card(row)
            domain.AddCardToDomain(card)

        data = CardsDB.Instance().GetMonstersExcludingAttributeAndRace(domain.attributes, domain.races)
        for row in data:
            card = Card(row)
            domain.CheckAndAddCardToDomain(card)
        
        while(True):
            print("Should I add spells and traps to the domain?")
            print("(1) Yes, add spells and traps to the list.")
            print("(2) No, I want just the monsters.")
            answer = self.RequestInput()

            if(not answer.isdigit()):
                self.InfoMessage(self.NOT_DIGIT_ANSWER)
                continue

            elif(answer == '1'):
                data = CardsDB.Instance().GetAllSpellsAndTraps()
                for row in data:
                    card = Card(row)
                    domain.AddCardToDomain(card)
                return 
            
            elif(answer == '2'):
                return

            else:
                self.InfoMessage(self.INVALID_ANSWER)
                continue
    
    # Prompt to check which formats the user wants to export the domain.
    def ExportDomain(self, domain: Domain) -> None:
        while(True):
            print("Do you want me to export the list to:")
            print("(1) YGOPRODeck's Collection CSV.")
            print("(2) EDOPro's / YGO Omega's Banlist.")
            print("(3) Both.")
            answer = self.RequestInput()

            if(not answer.isdigit()):
                self.InfoMessage(self.NOT_DIGIT_ANSWER)
                continue

            elif(answer == '1'):
                DomainExporter.toCSV(domain)
                return 
            
            elif(answer == '2'):
                DomainExporter.toLflist(domain)
                return

            elif(answer == '3'):
                DomainExporter.toCSV(domain)
                DomainExporter.toLflist(domain)
                return

            else:
                self.InfoMessage(self.INVALID_ANSWER)
                continue

    # Prompt to decide which format to use.
    def SelectDeckFormat(self) -> DeckFormatter.Format:
        options = [
            DeckFormatter.Format.YGOPRODECK_CSV,
            DeckFormatter.Format.YDK,
            DeckFormatter.Format.YDKE,
            DeckFormatter.Format.NAMES
        ]

        while(True):
            print("(1) YGOProDeck CSV.")
            print("(2) YDK.")
            print("(3) YDKE.")
            print("(4) List Name.")
            answer = self.RequestInput()

            if(not answer.isdigit()):
                self.InfoMessage(self.NOT_DIGIT_ANSWER)
                continue
            
            else:
                option = int(answer)
                if(option <= 0 or option > 4):
                    self.InfoMessage(self.INVALID_ANSWER)
                    continue
                else:
                    return options[option-1]


    # The main interface loop.
    def StartInterface(self) -> None:
        # Step 1) Intro Screen and decide tool
        self.IntroInput()
        tool = self.DecideTool()

        if tool == 1:
            while(True):
                # Step 2) Get the Deckmaster and Domain.
                domain = self.GetDeckMasterAndDomain()

                # Step 3) Add cards to Domain.
                self.GetDomainCards(domain)

                # Step 4) Export the domain.
                self.ExportDomain(domain)

                self.InfoMessage("\nProcess completed, you may now exit or create another domain.")
        
        elif tool == 2:
            while(True):
                answer = self.RequestInput("Please, provide the YDKE url.")
                try:
                    print(DeckChecker.CheckDeck(answer))
                except CardIdNotFoundError as error:
                    print(f"Couldn't process card with id [{error.args[0]}]. Keep in mind pre-release cards are not supported.")
                self.InfoMessage("\nProcess completed, you may now exit or check another deck.")
        
        elif tool == 3:            
            while(True):
                answer = self.RequestInput("Please, provide the YDKE url.")
                decks = DeckFormatter.Instance().Decode(DeckFormatter.Format.YDKE, answer)
                if(decks is None):
                    print("Could not process YDKE url.")
                
                else:
                    desired : list[Card] = []
                    for deck in decks:
                        desired += [card for card in deck if card.IsMonster()]
                    
                    if(len(desired) > 0):
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

                        for dm in dmList:
                            print(dm)
                    
                    else:
                        print("The deck provided has no monsters.")
                
                self.InfoMessage("\nProcess completed, you may now exit or perform another search.")
        
        elif tool == 4:
            while(True):
                print("What is the format you are converting from?")
                from_format = self.SelectDeckFormat()

                print("Provide your deck in the selected format.\n(Press enter twice more after pasting all lines)")
                lines = []
                while(True):
                    line = input().strip()
                    if line:
                        lines.append(line)
                    else:
                        break
                encoded_deck = "\n".join(lines)

                deck = DeckFormatter.Instance().Decode(from_format, encoded_deck)
                if deck is None:
                    print("Couldn't convert deck.\nMake sure you selected the correct format.")
                    self.InfoMessage("\nProcess completed, you may now exit or perform another conversion.")

                print("\nWhat is the format you want it to be?")
                to_format = self.SelectDeckFormat()

                converted_deck = DeckFormatter.Instance().Encode(to_format, deck)
                print(converted_deck)

                self.InfoMessage("\nProcess completed, you may now exit or perform another conversion.")

                        
