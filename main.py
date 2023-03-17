import logging

from xml.etree.ElementTree import ElementTree, Element, SubElement, indent
from tkinter import Tk
from timeit import default_timer as timer
from json import load
from os import path
from pathlib import Path
from shutil import copy
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
    
    def compile(self, savefilename, folder, file, isBattle, upgrade, willConsolidate):
        if folder:
            self.logger.info(f'Attempting to compile {folder}.')
        elif file:
            self.logger.info(f"Attempting to compile {path.basename(file)}.")
        start = timer()
        self.compiler = Compiler(self, isBattle, upgrade, willConsolidate, folder, file)
        self.compiler.compile()
        end = timer()
        self.create_xml(self.compiler.final_string, savefilename, isBattle, willConsolidate)

        self.logger.info(f'It took {end-start} seconds to complile.')
        if isBattle:
            if len(self.compiler.final_string) > 8636:
                self.logger.error(f"Used Space is over the limit of 8636! It is not recommended to patch!")
            self.logger.info(f"Used Space {int(len(self.compiler.final_string)/2)} / 8636")
        else:
            if len(self.compiler.final_string) > 3546:
                self.logger.error(f"Used Space is over the limit of 3546! It is not recommended to patch!")
            self.logger.info(f"Used Space {int(len(self.compiler.final_string)/2)} / 3546")

    def check_valid_value(self, number) -> int:
        if isinstance(number, int): return number
        if number.isdecimal(): return int(number)
        if 'x' in number:
            split_number = number.split('x')
            try: return int(f"0x{split_number[1]}", 16)  
            except: return None

        for category in self.labels.values():
            if number in category:
                return self.check_valid_value(category.get(number))
        return None

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

    def create_xml(self, text, saveFileName, isBattle, consolidate):
        patches = Element("Patches")
        if isBattle:
            name = "Event Conditionals"
            file = "EVENT_ATTACK_OUT"
            offset = "14938"
            consolidateName = "Load Event Conditionals Rewrite"
            consolidateFile = "EVENT_ATTACK_OUT"
            consolidateOffset = "1c38f4"

        else:
            name = "World Conditionals"
            file = "WORLD_WLDCORE_BIN"
            offset = "30234"
            consolidateName = "Process World Conditionals Rewrite"
            consolidateFile = "WORLD_WORLD_BIN"
            consolidateOffset = "13D590"
        
        conditionalPatch = SubElement(patches, "Patch", name = name)
        if not consolidate:
            datatext = text
            self.create_location_tag(conditionalPatch, file = file, offset = offset, text = datatext)

        elif isBattle and consolidate:
            pointers = "".join(self.compiler.scenario_pointers) + "".join(self.compiler.entry_pointers)
            self.create_location_tag(conditionalPatch, file = file, offset = offset, text = pointers)
            sector = "14B08"
            offset = "0"
            datatext = "".join(self.compiler.entries)
            self.create_location_tag(conditionalPatch, sector = sector, offset = offset, text = datatext)
            asmPatch = SubElement(patches, "Patch", name = consolidateName)
            asmFile = f"\n{Path(path.join('asm', 'Load Event Conditionals Rewrite.asm')).read_text()}"
            self.create_location_tag(asmPatch, file = consolidateFile, offset = consolidateOffset, offsetMode = "RAM", mode="ASM", text = asmFile)

        elif not isBattle and consolidate:
            pointers = self.compiler.scenario_pointers + self.compiler.entry_pointers

        tree = ElementTree(patches)
        indent(tree, space='    ', level = 0)
        try: tree.write(saveFileName, encoding="utf-8", xml_declaration=True)
        except: self.logger.exception(f"The file, {saveFileName}, was not created!")
        
    def create_location_tag(self, parent, file = None, sector = None, offset = None, offsetMode = None, mode = "DATA", text = None):
        locationTag = SubElement(parent, "Location")
        if file is not None: locationTag.attrib["file"] = file
        if sector is not None: locationTag.attrib["sector"] = sector
        if offset is not None: locationTag.attrib["offset"] = offset
        if offsetMode is not None: locationTag.attrib["offsetMode"] = offsetMode
        if mode is not None: locationTag.attrib["mode"] = mode
        if text is not None: locationTag.text = text


if __name__ == "__main__":
    main = Main()
    main.start_gui()