from tkinter import filedialog
from tkinter import Menu, BooleanVar

class MenuBar:
    
    def __init__(self, main):
        self.main = main
        self.menubar = Menu(self.main.window)
        self.filemenu = Menu(self.menubar, tearoff = 0)
        self.battlemenu = Menu(self.menubar, tearoff = 0)
        self.worldmenu = Menu(self.menubar, tearoff = 0)
        self.settingsmenu = Menu(self.menubar, tearoff = 0)
        self.upgrade = BooleanVar()
        self.battleConsolidate = BooleanVar()
        self.worldConsolidate = BooleanVar()
        self.create_filemenu()
        self.create_battlemenu()
        self.create_worldmenu()
        self.create_settingsmenu()
        self.main.window.config(menu = self.menubar)
        self.main.window.bind('b', lambda event: self.compile_scenarios(isBattle = True, isFolder = False, consolidate = self.battleConsolidate.get()))
        self.main.window.bind('w', lambda event: self.compile_scenarios(isBattle = False, isFolder = False, consolidate = self.worldConsolidate.get()))
        self.main.window.bind('<Escape>', lambda event: self.exit())

    def create_filemenu(self):
        self.filemenu.add_command(label = "Exit", command = self.exit)
        self.menubar.add_cascade(label = "File", menu = self.filemenu)

    def create_battlemenu(self):
        self.battlemenu.add_command(
                label = "Compile Event Conditionals File",
                command = lambda: self.compile_scenarios(isBattle = True, isFolder = False, consolidate = self.battleConsolidate.get()))
        self.battlemenu.add_command(
                label = "Compile Event Conditionals Folder",
                command = lambda: self.compile_scenarios(isBattle = True, isFolder = True, consolidate = self.battleConsolidate.get()))
        self.menubar.add_cascade(label = "Event Conditionals", menu = self.battlemenu)

    def create_worldmenu(self):
        self.worldmenu.add_command(
                label = "Compile World Conditionals File",
                command = lambda: self.compile_scenarios(isBattle = False, isFolder = False, consolidate = self.worldConsolidate.get()))
        self.worldmenu.add_command(
                label = "Compile World Conditionals Folder",
                command = lambda: self.compile_scenarios(isBattle = False, isFolder = True, consolidate = self.worldConsolidate.get()))
        self.menubar.add_cascade(label = "World Conditionals", menu = self.worldmenu)

    def compile_scenarios(self, isBattle, isFolder, consolidate):
        compile_folder = None
        compile_file = None
        if isFolder:
            compile_folder = filedialog.askdirectory(title = "Compile Input Folder")
            if not compile_folder or compile_folder == '\\': return
        else:
            compile_file = filedialog.askopenfilename(title = "Compile Input File", filetypes=(
                    ("Text files", "*.txt"),
                    ("All files", "*.*") ))
            if not compile_file: return

        file_name = filedialog.asksaveasfilename(
                                    title = "XML file to save as",
                                    defaultextension = ".xml",
                                    filetypes=(("XML files", "*.xml*"),
                                               ("All Files", "*.*") ))
        if not file_name: return
        self.main.compile(
                savefilename = file_name,
                folder = compile_folder,
                file = compile_file,
                isBattle = isBattle,
                upgrade = self.upgrade.get(),
                willConsolidate = consolidate)

    def create_settingsmenu(self):
        self.settingsmenu.add_checkbutton(label = "Use Expanded Conditional Instructions", onvalue = 1, offvalue = 0, variable = self.upgrade)
        self.settingsmenu.add_checkbutton(label = "Consolidate ATTACK.OUT usage", onvalue = 1, offvalue = 0, variable = self.battleConsolidate)
        self.settingsmenu.add_checkbutton(label = "Expand World Conditionals to WORLD.BIN", onvalue = 1, offvalue = 0, variable = self.worldConsolidate)
        self.menubar.add_cascade(label = "Config", menu = self.settingsmenu)
        if self.main.config.get("use_expanded_conditionals"): self.upgrade.set(1)
        if self.main.config.get("minimize_attack_out_usage"): self.battleConsolidate.set(1)
        if self.main.config.get("expand_world_conditionals_to_world_bin"): self.worldConsolidate.set(1)

    def exit(self):
        self.main.window.destroy()