from array import array
from base64 import b64decode

class YDKE:
    URL_START = "ydke://"
    SEPARATOR = "!"

    # Decodes an YDKE, returning a 3 lists of passcodes: main, extra and side.
    # If YDKE can't be processed, returns None instead.
    @staticmethod
    def DecodeYDKE(url : str) -> list[array]:
        if(not url.startswith(YDKE.URL_START)):
            return None

        url = url.removeprefix(YDKE.URL_START)
        decks = url.split(YDKE.SEPARATOR)

        if(len(decks) < 3):
            return None

        passcodes = []
        # 0 for main, 1 for extra, and 2 for side
        for i in range(0, 3):
            # ydke files are stored in base64 unsigned ints
            decklist = array("I")
            decklist.frombytes(b64decode(decks[i]))
            passcodes.append(decklist)
        
        return passcodes