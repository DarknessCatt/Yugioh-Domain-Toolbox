# YGODomainGenerator
This repository is a simple python script that generates a CSV or IFlist containing the cards in your Deckmaster's domain.
The CSV can be loaded into a YGOPRODeck's Collection while th IFlist can be added to EDOPRO.

## Deckmaster? Domain?
These are terms refer to the Yugioh's Domain Format.
More info can be found in their discord's server: https://discord.gg/dpUsHxqu

# Using the executable and caveats:
Windows executables for this program are available in [Releases](https://github.com/DarknessCatt/YGODomainGenerator/releases).
It should be ready to use once downloaded, just run it (check the "Using the program") section below.

However, due to current limitations, the executables use local files for card information instead of downloading the most updated version available. This can potentially cause outdated domains if the release is too old.

There are two ways to deal with this:
* Wait for a new release.
* Download and replace the files yourself. They are located in the folder "references" next to the exe.
    * Make sure the filename is the same otherwise it won't work.
    * [cards.cdb](https://github.com/ProjectIgnis/BabelCDB/raw/master/cards.cdb)
    * [common.h](https://raw.githubusercontent.com/ProjectIgnis/EDOPro/master/gframe/common.h)
    * [strings.conf](https://raw.githubusercontent.com/ProjectIgnis/EDOPro/master/config/strings.conf)

# How to run it without the executable:
First, you will need to download these files.
You can either git clone the repository (if you know how) or download it as a zip by clicking the green button "Code" -> "Download Zip"

Next, there are two ways of running these scrips: through python or docker.
Unfortunately, both require you to install something. I tried to make a executable python file but it didn't work )=

## Python
If you don't have python, download it here: https://www.python.org/downloads
When installing, make sure you keep the option "Add python to PATH" MARKED!

Open your terminal and navigate to the same folder as "main.py".
In windows, this can be done by opening the folder in explorer then right-click -> "Open in Terminal"

If this is the first time running the program, you will need to install it's dependencies. Type:
> pip install --no-cache-dir -r requirements.txt

Into the terminal and press enter.

When that's done, enter:
> python3 ./main.py

To start the program.

## Docker
This option is a little bit more complicated and is recommended for advanced users.
(Not saying that python was simple.)

If you don't have it, download and install docker: https://www.docker.com/products/docker-desktop/
Depending on the OS you are on, you installing steps vary; you will have to install WSL if you are using Windows, for example.

When that's up and running, open your terminal to the same folder as "main.py".
In windows, this can be done by opening the folder in explorer then right-click -> "Open in Terminal"
Now just enter:
> docker-compose run --rm -it python python3 ./main.py

To start the program.

# Using the program
The program itself is a simple text based interface.
Just provide the requested info and it should work smoothly.

## DeckMaster's ID
The id request refers to the card's passcode. There are many ways to find these, but the easiest I find is through YGOPRODECK:
* Open the card's page in YGOPRODECK.
* In the information showed, click on the button "Image (.jpg)"
    * You can also just right click the card's image -> Open image in new tab.
* This should take you into a url similar to https://images.ygoprodeck.com/images/cards/XXXXXXXX.jpg
* The 'X' in the URl is the card's id.

### Example
* If "3-Hump Lacooda" is your DM, first you would go to: https://ygoprodeck.com/card/3-hump-lacooda-7280
* The "Image (.jpg)" should lead you to: https://images.ygoprodeck.com/images/cards/86988864.jpg
* The card's id is: **86988864**