from tkinter import filedialog
from tkinter import Menu, BooleanVar

class MenuBar:
    
    def __init__(self, main):
        self.main = main
        self.menubar = Menu(self.main.window)
        self.filemenu = Menu(self.menubar, tearoff = 0)
        self.battlemenu = Menu(self.menubar, tearoff = 0)
        self.worldmenu = Menu(self.menubar, tearoff = 0)
        self.upgrade = BooleanVar()
        self.create_filemenu()
        self.create_battlemenu()
        self.create_worldmenu()
        self.main.window.config(menu = self.menubar)
        self.main.window.bind('b', lambda event: self.compile_scenarios(isBattle = True, isFolder = False))
        self.main.window.bind('w', lambda event: self.compile_scenarios(isBattle = False, isFolder = False))
        self.main.window.bind('<Escape>', lambda event: self.exit())

    def create_filemenu(self):
        self.filemenu.add_checkbutton(label = "Use Expanded Conditionals", onvalue = 1, offvalue = 0, variable = self.upgrade)
        self.filemenu.add_command(label = "Exit", command = self.exit)
        self.menubar.add_cascade(label = "File", menu = self.filemenu)

    def create_battlemenu(self):
        self.battlemenu.add_command(label = "Compile Event Conditionals File", command = lambda: self.compile_scenarios(isBattle = True, isFolder = False))
        self.battlemenu.add_command(label = "Compile Event Conditionals Folder", command = lambda: self.compile_scenarios(isBattle = True, isFolder = True))
        self.menubar.add_cascade(label = "Event Conditionals", menu = self.battlemenu)

    def create_worldmenu(self):
        self.worldmenu.add_command(label = "Compile World Conditionals File", command = lambda: self.compile_scenarios(isBattle = False, isFolder = False))
        self.worldmenu.add_command(label = "Compile World Conditionals Folder", command = lambda: self.compile_scenarios(isBattle = False, isFolder = True))
        self.menubar.add_cascade(label = "World Conditionals", menu = self.worldmenu)

    def compile_scenarios(self, isBattle, isFolder):
        compile_folder = None
        compile_file = None
        if isFolder:
            compile_folder = filedialog.askdirectory(title = "Compile Input Folder")
            if not compile_folder or compile_folder == '\\': return
        else:
            compile_file = filedialog.askopenfilename(title = "Compile Input File", filetypes=(("Text files", "*.txt"),
                                       ("All files", "*.*") ))

        file_name = filedialog.asksaveasfilename(
                                    title = "XML file to save as",
                                    defaultextension = ".xml",
                                    filetypes=(("XML files", "*.xml*"),
                                               ("All Files", "*.*") ))
        if not file_name: return
        self.main.compile(file_name, compile_folder, compile_file, isBattle, self.upgrade)

    def exit(self):
        self.main.window.destroy()