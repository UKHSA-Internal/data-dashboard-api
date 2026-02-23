from enum import Enum

class BaseEnum(Enum):
    def return_list(self):
        return [e.value for e in self.value]