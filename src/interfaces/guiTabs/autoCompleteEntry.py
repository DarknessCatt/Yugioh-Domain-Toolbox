"""
Based on: https://gist.github.com/uroshekic/11078820
Changes:
    * Can click directly to itens in the list
    * Needs to double click to "confirm"
"""

from tkinter import Entry, StringVar, Listbox, ACTIVE, END
import re

class AutoCompleteEntry(Entry):
    def __init__(self, autocompleteList, *args, **kwargs):

        # Listbox length
        if 'listboxLength' in kwargs:
            self.listboxLength = kwargs['listboxLength']
            del kwargs['listboxLength']
        else:
            self.listboxLength = 8

        # Custom matches function
        if 'matchesFunction' in kwargs:
            self.matchesFunction = kwargs['matchesFunction']
            del kwargs['matchesFunction']
        else:
            def matches(fieldValue, acListEntry):
                pattern = re.compile('.*' + re.escape(fieldValue) + '.*', re.IGNORECASE)
                return re.match(pattern, acListEntry)
                
            self.matchesFunction = matches
        
        Entry.__init__(self, *args, **kwargs)
        self.focus()

        self.autocompleteList = autocompleteList

        self.var = kwargs["textvariable"]
        if(self.var is None):
            self.var = self["textvariable"] = StringVar()

        self.var.trace_add('write', self.changed)
        self.bind("<Right>", self.selection)
        self.bind("<Return>", self.selection)
        self.bind("<Up>", self.moveUp)
        self.bind("<Down>", self.moveDown)
        
        self.listboxUp = False
        self.clicked = False

    def changed(self, name, index, mode):
        if self.clicked:
            self.clicked = False
            return

        if self.var.get() == '':
            if self.listboxUp:
                self.listbox.destroy()
                self.listboxUp = False
        else:
            words = self.comparison()
            if words:
                if not self.listboxUp:
                    self.listbox = Listbox(width=int(self["width"] * 1.25), height=self.listboxLength)
                    self.listbox.bind("<<ListboxSelect>>", self.click)
                    self.listbox.bind("<Right>", self.selection)
                    self.listbox.place(in_=self, y=self.winfo_height())
                    self.listboxUp = True
                
                self.listbox.delete(0, END)
                for w in words:
                    self.listbox.insert(END,w)
            else:
                if self.listboxUp:
                    self.listbox.destroy()
                    self.listboxUp = False

    def click(self, event):
        if self.listboxUp:
            selection = self.listbox.curselection()
            if(len(selection) == 0):
                return

            self.listbox.activate(selection[0])

            currValue = self.var.get()
            selectedValue = self.listbox.get(ACTIVE)

            if(currValue != selectedValue):
                self.clicked = True
                self.var.set(selectedValue)
                self.icursor(END)
            else:
                self.selection("<<ListboxSelect>>")
    
    def selection(self, event):
        if self.listboxUp:
            self.var.set(self.listbox.get(ACTIVE))
            self.listbox.destroy()
            self.listboxUp = False
            self.icursor(END)

    def moveUp(self, event):
        if self.listboxUp:
            if self.listbox.curselection() == ():
                index = '0'
            else:
                index = self.listbox.curselection()[0]
                
            if index != '0':                
                self.listbox.selection_clear(first=index)
                index = str(int(index) - 1)
                
                self.listbox.see(index) # Scroll!
                self.listbox.selection_set(first=index)
                self.listbox.activate(index)

    def moveDown(self, event):
        if self.listboxUp:
            if self.listbox.curselection() == ():
                index = '0'
            else:
                index = self.listbox.curselection()[0]
                
            if index != END:                        
                self.listbox.selection_clear(first=index)
                index = str(int(index) + 1)
                
                self.listbox.see(index) # Scroll!
                self.listbox.selection_set(first=index)
                self.listbox.activate(index) 

    def comparison(self):
        return [ w for w in self.autocompleteList if self.matchesFunction(self.var.get(), w) ]