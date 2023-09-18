from constants.hexCodesReference import AttributesAndRaces, Archetypes

from classes.downloadManager import DownloadManager
from classes.card import Card
from classes.domain import Domain
from classes.sql import CardsCDB

# Runs setups for classes which require external classes.
def setup():
    if(not DownloadManager.DoesReferenceFolderExist()):
        DownloadManager.DownloadFiles()

    Archetypes.Setup()
    AttributesAndRaces.Setup()
    CardsCDB.Setup()

# Main function. Runs when main.py is called.
def main():
    # Step 0) Setup stuff.
    setup()
   
   # Step 1) Get the Deckmaster.
    print("Please type the Deck Master's id:")
    answer = input()

    while(not answer.isdigit()):
        print("\nThe value provided doesn't seem to be an integer.\n")
        print("Please input only the card's id digits.")
        print("Or enter \"exit\" to leave.")
        answer = input()

        if(answer.lower() == 'exit'):
            print("\nBye bye!\n")
            return

    data = CardsCDB.GetMonsterById(answer)
    if(data is None):
        print("\nSorry, I could not find card with id: [{}]".format(answer))
        print("Are you sure this is the correct id?")
        print("Remember only monster cards can be Deck Masters.")
        print("Exiting.\n")
        return

    # Step 2) Get the domain.
    card = Card(data)
    domain = Domain(card)
    print(domain)
    
    data = CardsCDB.GetMonstersByAttributeAndRace(domain)
    for row in data:
        card = Card(row)
        domain.AddCardToDomain(card)

    data = CardsCDB.GetMonstersExcludingAttributeAndRace(domain)
    for row in data:
        card = Card(row)
        domain.CheckAndAddCardToDomain(card)

    data = CardsCDB.GetAllSpellsAndTraps()
    for row in data:
        card = Card(row)
        domain.AddCardToDomain(card)

    print("\nDo you want me to also add spells and traps to the list? (y/n)")
    answer = input()

    while(answer != 'y' and answer != 'n'):
        print("\nThe value provide doesn't seem to be valid.")
        print("Please answer just \"y\" or \"n\".")
        print("Or enter \"exit\" to leave.")
        answer = input()

        if(answer.lower() == 'exit'):
            print("\nBye bye!\n")
            return
    
    if(answer == 'y'):
        data = CardsCDB.GetAllSpellsAndTraps()
        for row in data:
            card = Card(row)
            domain.AddCardToDomain(card)

    # Step 3) Export the domain.
    print("\nDo you want me to export the list to:")
    print("(1) YGOPRODeck's Collection CSV, or")
    print("(2) EDOPro's Banlist, or")
    print("(3) Both")
    print("Just enter the number of the option.")
    answer = input()

    while(answer != '1' and answer != '2' and answer != '3'):
        print("\nThe value provide doesn't seem to be valid.")
        print("(1) YGOPRODeck's Collection CSV")
        print("(2) EDOPro's Banlist")
        print("(3) Both")
        print("Please answer just \"1\", \"2\" or \"3\".")
        print("Or enter \"exit\" to leave.")

        answer = input()

        if(answer.lower() == 'exit'):
            print("\nBye bye!\n")
            return

    if(answer == '1'):
        domain.CreateCSV()

    elif(answer == '2'):
        domain.CreateIflist()

    else:
        domain.CreateCSV()
        domain.CreateIflist()

main()