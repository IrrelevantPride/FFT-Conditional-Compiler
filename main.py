import logging

from xml.etree.ElementTree import ElementTree, Element, SubElement, indent
from tkinter import Tk
from timeit import default_timer as timer
from json import load
from os import path
from classes.menubar import MenuBar
from classes.compiler import Compiler

class Main:

    def __init__(self):
        self.logger = logging
        logging.basicConfig(
            level=logging.INFO,
            filename='info.log',
            filemode='w',
            format='%(asctime)s %(levelname)-8s %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S')
        self.config = self.load_json(path.join("json_files", "config.json"))
        self.labels = self.load_json(path.join("json_files", self.config.get("labels_file_name")))
        self.event_instructions = self.load_json(path.join("json_files", "event_instructions.json"))
        self.world_instructions = self.load_json(path.join("json_files", "world_instructions.json"))

    def start_gui(self):
        self.window = Tk()
        self.window.title("FFT Conditional Compiler")
        self.window.iconbitmap(path.join("images","sword_icon.ico"))
        self.W_WIDTH, self.W_HEIGHT = 320, 20
        self.window.geometry(f"{self.W_WIDTH}x{self.W_HEIGHT}")
        self.window.resizable(width = False, height = False)

        self.menubar = MenuBar(self)
        self.window.mainloop()

    def compile(self, file, conditionals_directory, isBattle, upgrade):
        self.logger.info(f'Attempting to compile {conditionals_directory}.')
        start = timer()
        compiler = Compiler(self, conditionals_directory, isBattle, upgrade)
        compiler.compile()
        end = timer()
        self.create_xml(compiler.final_string, file, isBattle)

        self.logger.info(f'It took {end-start} seconds to complile.')
        if isBattle:
            self.logger.info(f"Used Space {int(len(compiler.final_string)/2)} / 8636")
        else:
            self.logger.info(f"Used Space {int(len(compiler.final_string)/2)} / 3546")

    def check_valid_value(self, number) -> int:

        if number[0:1] == 'x':
            try: return int(f'0{number}', 16)
            except ValueError: return None

        elif number[0:2] == "0x": 
            try: return int(number, 16)
            except ValueError: return None        

        elif number.isdecimal(): return int(number)
        elif number in self.labels:
            return self.check_valid_value(self.labels.get(number))
        else: return None

    def to_halfword(self, number, flip = False):
        try:
            tohex = f"{int(number, 16):04x}"
            if flip: return f"{tohex[2:]}{tohex[:2]}"
            else:  return tohex
        except TypeError: pass

        try:
            tohex = f"{number:04x}"
            if flip: return f"{tohex[2:]}{tohex[:2]}"
            else: return tohex

        except TypeError:  return None

    def load_json(self, file_name):
        json_dict = {}
        try:
            with open(file_name) as json_file:
                json_dict = load(json_file)
            
        except FileNotFoundError:
                self.logger.exception(f"The file, {file_name} was not found!")
                
        return json_dict

    def create_xml(self, text, file_name, isBattle):
        if isBattle:
            name = "Event Conditoinals"
            location_file = "EVENT_ATTACK_OUT"
            offset = "14938"

        else:
            name = "World Conditionals"
            location_file = "WORLD_WLDCORE_BIN"
            offset = "30234"

        patches_tree = Element("Patches")
        patch_tree = SubElement(patches_tree, "Patch", 
                name=name)
        
        SubElement(
                    patch_tree,
                    "Location",
                    file = location_file,
                    offset = offset,
                    mode="DATA").text = text
        xml = ElementTree(patches_tree)
        indent(xml, space='\t', level = 0)
        try: xml.write(file_name, encoding="utf-8", xml_declaration=True)
        except: self.logger.exception(f"The file, {file_name}, was not created!")

if __name__ == "__main__":
    main = Main()
    main.start_gui()