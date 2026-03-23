from enum import Enum


class BaseEnum(Enum):
    def return_list(self):
        return [e.value for e in self.value]

    def return_name_list(self):
        return [e.name for e in self.value]
    
    def return_tuple_list(self):
        return [(e.value, e.name.replace("_", " ").title()) for e in self.value]
