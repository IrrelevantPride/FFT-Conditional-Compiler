from os import listdir
from classes.conditional import Conditional
from typing import List

class Compiler:
    def __init__(self, main, conditionals_directory, isBattle, upgrade):

        self.main = main
        self.isBattle = isBattle
        self.conditionals_directory = conditionals_directory
        self.upgrade = upgrade

        if self.isBattle: self.conditional_instructions = self.main.event_instructions["event_instructions"]
        else: self.conditional_instructions = self.main.world_instructions["world_instructions"]
        self.dir_files = listdir(self.conditionals_directory)
        self.txt_files = [file for file in self.dir_files if file[-4:] == ".txt"]
        
        self.final_string = None
        self.current_file = None
        self.scenarios : List = []
        self.highest_id: int = -1
        self.num_of_entries: int = 0
        self.entries : List = []
        self.entry_pointers : List = []
        self.scenario_pointers : List = []

    def compile(self) -> bool:
        self.current_scenario = None
        for file in self.txt_files:
            with open (f"{self.conditionals_directory}"
                       f"{file}", 'r') as file:
                self.current_file = file.readlines()

            for line in self.current_file:
                nws = line.strip()
                nws = self.check_line_for_comment(nws)
                if self.check_line_for_id(nws): continue
                if self.current_scenario == None: continue
                if self.check_line_for_entry(nws): continue
                if self.check_line_for_instruction(nws): continue
                self.main.logger.warning(f"The line containing '{line}' will not be compiled")
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
        entries_position = entries_start
        scenario_pointers = []
        entry_pointers = []
        entries = []

        for conditional in self.scenarios:
            scenario_pointers.append(self.main.to_halfword(entry_pointer_position, True))
            entry_pointer_position += ((conditional.entry_amount + 1) * 2)
            for conditional_set in conditional.total_conditionals:
                if conditional_set:
                    entry_pointers.append(self.main.to_halfword(entries_position, True))
                size = int(len(conditional_set) / 2)
                entries_position += size
                entries.append(conditional_set)
            entry_pointers.append("0000")

        list_all = []
        list_all.append("".join(scenario_pointers))
        list_all.append("".join(entry_pointers))
        list_all.append("".join(entries))
        self.final_string = "".join(list_all)
