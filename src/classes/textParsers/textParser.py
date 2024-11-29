import re

class TextParser:

    # Text: the entire text to be parsed
    # Header: the start of the section to be parsed
    # Line: The regex to use when parsing
    # Dic: Where to store the information ordered by {first column : second column}
    # ReverseDic: same as dic, but reversed
    def ParseSection(self, text: str, header: str, line: str, dic: dict, reverseDic: dict) -> None:
        # First, retrive the entire section of the file.
        section = re.search("{}({}\n)*".format(header, line), text)

        if(section is None or section.group(0) is None):
            print("Could not find section [{}].".format(header))
            return

        # Remove the header from the section.
        list = section.group(0).strip().removeprefix(header)
        # For each entry in the section, retrieve the archetype's name and hexcode.
        for entry in list.split("\n"):
            info = re.search(line, entry)

            # if(info.group(1) in dic):
            #     print(f"Replacing \t{info.group(1)}\t[{dic[info.group(1)]}] -> [{info.group(2)}]")
            dic[info.group(1)] = info.group(2)

            # if(info.group(2) in reverseDic):
            #     print(f"Replacing \t{info.group(2)}\t[{reverseDic[info.group(2)]}] -> [{info.group(1)}]")
            reverseDic[info.group(2)] = info.group(1)