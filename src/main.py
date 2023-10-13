import sys
from interfaces.cli import CommandLineInterface
from interfaces.gui import GraphicalUserInterface

# Main function. Runs when main.py is called.
def main():
    if("--cli" in sys.argv):
        interface = CommandLineInterface()
    else:
        interface = GraphicalUserInterface()
    
    interface.StartInterface()

main()