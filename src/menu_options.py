from anytree import Node

class MenuOptions(Node):
    def __init__(self, name:str, line1: str, line1_marker: bool, line2: str, line2_marker: bool, action: callable, parent=None):
        super().__init__(name, parent)
        self.line1 = line1.center(16) if not line1_marker else f'< {line1.center(12)} >'
        self.line2 = line2.center(16) if not line2_marker else f'< {line2.center(12)} >'
        self.action = action
        self.is_workflow = True if self.action is not None else False
        
    def display(self, lcd):
        lcd.text(self.line1, 1)
        lcd.text(self.line2, 2)

    def select(self):
        return self.action()