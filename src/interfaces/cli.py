from sys import exit

from constants.hexCodesReference import AttributesAndRaces, Archetypes

from classes.downloadManager import DownloadManager
from classes.card import Card
from classes.domain import Domain
from classes.sql import CardsCDB

class CommandLineInterface:

    PLEASE_NUMBER = "Please, input only the required number."
    OR_EXIT = "Or \"exit\" (without quotes) to close the program."
    
    PRESS_ENTER_CONTINUE = "Press enter to continue."

    NOT_DIGIT_ANSWER = "The value provided doesn't seem to be an integer."
    INVALID_ANSWER = "The value provided is not a valid option."

    # Runs setups for classes which require external classes.
    def Setup(self):
        if(not DownloadManager.DoesReferenceFolderExist()):
            DownloadManager.DownloadFiles()

        Archetypes.Setup()
        AttributesAndRaces.Setup()
        CardsCDB.Setup()
        print("")

    def RequestInput(self) -> str:
        print(self.PLEASE_NUMBER)
        print(self.OR_EXIT)
        
        answer = input()
        print("")

        if(answer.lower() == 'exit'):
            print("Bye bye!\n")
            exit()
        
        return answer

    def InfoMessage(self, msg: str) -> None:
        print(msg)
        print(self.PRESS_ENTER_CONTINUE)
        input()
        print("")

    def IntroInput(self) -> None:
        print("Welcome to Domain Generator!\n")
        while(True):
            print("Please choose one option:")
            print("(1) Choose a Deck Master.")
            print("(2) Update card database.")
            answer = self.RequestInput()

            if(not answer.isdigit()):
                self.InfoMessage(self.NOT_DIGIT_ANSWER)
                continue

            elif(answer == '1'):
                return
            
            elif(answer == '2'):
                CardsCDB.CloseDB()
                DownloadManager.DownloadFiles()
                self.Setup()
                continue

            else:
                self.InfoMessage(self.INVALID_ANSWER)
                continue
                
    def GetDeckMasterAndDomain(self) -> Domain:
        while(True):
            print("What is the Deck Master's id? (passcode).")
            answer = self.RequestInput()

            if(not answer.isdigit()):
                self.InfoMessage(self.NOT_DIGIT_ANSWER)
                continue
            
            else:
                dm = CardsCDB.GetMonsterById(answer)
                if(dm is None):
                    self.InfoMessage("Sorry, I could not find card with id: [{}]\nAre you sure this is the correct id?\nRemember only monster cards can be Deck Masters.".format(answer))
                    continue

                else:
                    card = Card(dm)
                    domain = Domain(card)
                    print(domain)
                    print("")
                    return domain
                
    def GetDomainCards(self, domain: Domain) -> None:
        print("Retrieving monsters in this domain...")

        data = CardsCDB.GetMonstersByAttributeAndRace(domain)
        for row in data:
            card = Card(row)
            domain.AddCardToDomain(card)

        data = CardsCDB.GetMonstersExcludingAttributeAndRace(domain)
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
                data = CardsCDB.GetAllSpellsAndTraps()
                for row in data:
                    card = Card(row)
                    domain.AddCardToDomain(card)
                return 
            
            elif(answer == '2'):
                return

            else:
                self.InfoMessage(self.INVALID_ANSWER)
                continue
            
    def ExportDomain(self, domain: Domain) -> None:
        while(True):
            print("\nDo you want me to export the list to:")
            print("(1) YGOPRODeck's Collection CSV.")
            print("(2) EDOPro's Banlist.")
            print("(3) Both.")
            answer = self.RequestInput()

            if(not answer.isdigit()):
                self.InfoMessage(self.NOT_DIGIT_ANSWER)
                continue

            elif(answer == '1'):
                domain.CreateCSV()
                return 
            
            elif(answer == '2'):
                domain.CreateIflist()
                return

            elif(answer == '3'):
                domain.CreateCSV()
                domain.CreateIflist()
                return

            else:
                self.InfoMessage(self.INVALID_ANSWER)
                continue

    def StartInterface(self) -> None:
        # Step 0) Setup stuff.
        self.Setup()

        # Step 1) Intro Screen
        self.IntroInput()

        while(True):
            # Step 2) Get the Deckmaster and Domain.
            domain = self.GetDeckMasterAndDomain()

            # Step 3) Add cards to Domain.
            self.GetDomainCards(domain)

            # Step 4) Export the domain.
            self.ExportDomain(domain)

            self.InfoMessage("\nProcess completed, you may now exit or create another domain.")
