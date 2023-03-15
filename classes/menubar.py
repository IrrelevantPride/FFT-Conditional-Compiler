from tkinter import filedialog
from tkinter import Menu, BooleanVar

class MenuBar:
    
    def __init__(self, main):
        self.main = main
        self.menubar = Menu(self.main.window)
        self.filemenu = Menu(self.menubar, tearoff = 0)
        self.compilemenu = Menu(self.menubar, tearoff = 0)
        self.decompilemenu = Menu(self.menubar, tearoff = 0)
        self.upgrade = BooleanVar()
        self.create_filemenu()
        self.create_compilemenu()
        self.main.window.config(menu = self.menubar)
        self.main.window.bind('b', lambda event: self.compile_scenarios(True))
        self.main.window.bind('w', lambda event: self.compile_scenarios(False))
        self.main.window.bind('<Escape>', lambda event: self.exit())

    def create_filemenu(self):
        self.filemenu.add_checkbutton(label = "Use Expanded Conditionals", onvalue = 1, offvalue = 0, variable = self.upgrade)
        self.filemenu.add_command(label = "Exit", command = self.exit)
        self.menubar.add_cascade(label = "File", menu = self.filemenu)

    def create_compilemenu(self):
        self.compilemenu.add_command(label = "Compile Battle Scenarios", command = lambda: self.compile_scenarios(True))
        self.compilemenu.add_command(label = "Compile World Scenarios", command = lambda: self.compile_scenarios(False))
        self.menubar.add_cascade(label = "Compile", menu = self.compilemenu)

    def compile_scenarios(self, isBattle):
        compile_folder = filedialog.askdirectory(title = "Compile Input Folder") + "\\"
        if not compile_folder or compile_folder == '\\': return
        file_name = filedialog.asksaveasfilename(
                                    defaultextension = ".xml",
                                    filetypes=(("XML files", "*.xml*"),
                                               ("All Files", "*.*") ))
        if not file_name: return
        self.main.compile(file_name, compile_folder, isBattle, self.upgrade)

    def exit(self):
        self.main.window.destroy()