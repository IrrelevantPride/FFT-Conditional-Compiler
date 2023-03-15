from typing import List

class Conditional:
    def __init__(self, main):
        self.main = main
        self.conditionalid : int = None
        self.entry_amount : int = 0
        self.MAX_ENTRIES : int = self.main.config["max_amount_of_entries"]
        self.entries : List = []
        self.total_conditionals : List = []

    def update_id(self, id) -> bool:
        temp_id = self.main.check_valid_value(id)
        if temp_id != None:
            self.conditionalid = temp_id
            return True
        return False

    def update_entry(self) -> bool:
        if self.entry_amount >= self.MAX_ENTRIES: return False
        if self.entry_amount: self.update_total_conditionals()
        self.entry_amount += 1
        return True

    def update_total_conditionals(self):
        temp_entries = "".join(self.entries)
        self.total_conditionals.append(temp_entries)
        self.entries.clear()

    def encode_command(self, id, parameters, size) -> bool:
        if len(parameters) != size and parameters != ['']:
            self.main.logger.warning(f'The arguments({parameters}) are not valid for Instruction {id}! Instruction {id} can only take {size} arguments. Instruction will not be encoded.')
            return False
        instruction_encoded : List = [self.main.to_halfword(id, True)]
        if parameters != ['']:
            for parameter in parameters:
                validated_parameter = self.main.check_valid_value(parameter.strip())
                if validated_parameter == None: 
                    self.main.logger.warning(f'The value {parameter} is not valid! Instruction {id} will not be encoded.')
                    return False
                instruction_encoded.append(self.main.to_halfword(validated_parameter, True))
        if instruction_encoded: self.entries.append("".join(instruction_encoded))
        return True
