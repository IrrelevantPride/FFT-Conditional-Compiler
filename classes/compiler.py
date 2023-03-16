from os import listdir, path
from classes.conditional import Conditional
from typing import List

class Compiler:
    def __init__(self, main, isBattle, upgrade, willConsolidate, folder, file):

        self.main = main
        self.isBattle = isBattle
        self.conditionals_directory = folder
        self.upgrade = upgrade
        self.willConsolidate = willConsolidate

        if self.isBattle: self.conditional_instructions = self.main.event_instructions["event_instructions"]
        else: self.conditional_instructions = self.main.world_instructions["world_instructions"]

        self.txt_files = None

        if folder:
            self.isFolder = True
            dir_files = listdir(self.conditionals_directory)
            self.txt_files = [file for file in dir_files if file[-4:] == ".txt"]
        
        elif file:
            self.isFolder = False
            self.txt_files = [file]

        self.current_scenario = None
        self.final_string = None
        self.scenarios : List = []
        self.highest_id: int = -1
        self.num_of_entries: int = 0
        self.entries : List = []
        self.entry_pointers : List = []
        self.scenario_pointers : List = []

    def compile(self) -> bool:
        self.current_scenario = None
        for file in self.txt_files:
            if self.isFolder:
                with open (path.join(self.conditionals_directory, file), 'r') as f:
                    current_file = f.readlines()
            else:
                with open (file, 'r') as f:
                    current_file = f.readlines()

            for index, line in enumerate(current_file):
                nws = line.strip('\n ')
                nws = self.check_line_for_comment(nws)
                if self.check_line_for_id(nws): continue
                if self.current_scenario == None: continue
                if self.check_line_for_entry(nws): continue
                if self.check_line_for_instruction(nws): continue
                if nws: self.main.logger.warning(f"Line {index} in {file} will not be compiled.")
        self.current_scenario.update_total_conditionals()
        self.add_scenario(self.current_scenario)
        self.scenarios.sort(key=lambda x: x.conditionalid)
        self.create_data_set()

    def check_line_for_comment(self, line) -> bool:
        if "#" in line:
            split_line = line.split("#")
            line = line.replace(f"#{split_line[1]}", "")
        return line

    def check_line_for_id(self, line) -> bool:
        if "CONDITIONALID" in line.upper():
            split_lines = line.split(":")
            conditionalid : str = split_lines[1].strip('\n ')
            if self.main.check_valid_value(conditionalid) is not None:
                if self.current_scenario: self.current_scenario.update_total_conditionals()
                self.add_scenario(self.current_scenario)
                self.current_scenario = Conditional(self.main)
                self.current_scenario.update_id(conditionalid)
                if self.current_scenario.conditionalid > self.highest_id:
                    self.highest_id = self.current_scenario.conditionalid
                return True
        return False

    def check_line_for_entry(self, line) -> bool:
        entry_updated = False
        if "ENTRY" in line.upper():
            entry_updated = self.current_scenario.update_entry()
            if entry_updated: self.num_of_entries += 1
        return entry_updated

    def check_line_for_instruction(self, line) -> bool:
        if line.find("(") != -1 and line.find(")") != -1:
            instruction = line[0:line.find("(")]
            if instruction == "": return False
            arguments = line[line.find("(") + 1: line.rfind(")")]
            arguments_list = arguments.split(",")

          # For/Else returns False if instruction is not found in json
            for scenario_instruction in self.conditional_instructions:
                if not scenario_instruction.get("alias"): continue
                if instruction in scenario_instruction.get("alias"):
                    if scenario_instruction.get("requires upgrade") and not self.upgrade.get():
                        self.main.logger.warning(f'Instruction {scenario_instruction.get("id")} - {instruction} requires "Use Expanded Conditionals"! Instruction will not be encoded.')
                        return False
                    if scenario_instruction.get("requires upgrade") and self.upgrade.get():
                        size = scenario_instruction.get("upgrade size")
                    else: 
                        size = scenario_instruction.get("size")

                    was_command_encoded = self.current_scenario.encode_command(
                                id = scenario_instruction.get("id"), 
                                parameters = arguments_list, 
                                size = size)
                    if was_command_encoded:
                        return True
                    return False
            else: 
                self.main.logger.warning(f'Instruction {instruction} was not found! Instruction will not be encoded.')
                return False

        else: return False

    def add_scenario(self, conditional):
        if conditional: self.scenarios.append(conditional)

    def create_data_set(self):
        entry_pointer_start = len(self.scenarios) * 2
        entry_pointer_position = entry_pointer_start

        # Each scenario has a pointer to the specific entry, the entry pointers end with the string '0000'.
        # To account for each '0000' the entries start adds the total number of entries + the number of conditionals
        entries_start = entry_pointer_start + ((self.num_of_entries + len(self.scenarios)) * 2)
        self.scenario_pointers = []
        self.entry_pointers = []
        self.entries = []
        if self.willConsolidate:
            entries_position = 2
            self.entries.append('0000')
        else: entries_position = entries_start

        for conditional in self.scenarios:
            self.scenario_pointers.append(self.main.to_halfword(entry_pointer_position, True))
            entry_pointer_position += ((conditional.entry_amount + 1) * 2)
            for conditional_set in conditional.total_conditionals:
                if conditional_set:
                    self.entry_pointers.append(self.main.to_halfword(entries_position, True))
                size = int(len(conditional_set) / 2)
                entries_position += size
                self.entries.append(conditional_set)
            self.entry_pointers.append("0000")
        self.final_string = "".join(self.scenario_pointers) + "".join(self.entry_pointers) + "".join(self.entries)