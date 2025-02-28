import string, time
class InputMenu:
    def __init__(self, options, lcd, max_input_length, min_input_length):
        self.lcd = lcd
        if options == 'digits':
            self.input_list = list(string.digits)
        elif options == 'letters':
            self.input_list = list(string.ascii_uppercase + '_' + '-')
        else:
            self.input_list = list(string.ascii_uppercase + string.digits + '_' + '-')
            
        self.input_list.append('DONE')
        self.input_list.append('DEL')
        self.current_index = 0
        self.input = ''
        self.max_input_length = max_input_length
        self.min_input_length = min_input_length
        
    def __display__(self):
        MAX_CHARS = 14
        line1 = ''
        i = self.current_index
        while True:
            if len(line1) + len(self.input_list[i]) <= MAX_CHARS:
                line1 += self.input_list[i] + ' '
                i = (i + 1) % len(self.input_list)
            else:
                break
            
            
        # add < and > to line 1
        line1 = line1.strip()
        line1 = '<' + line1
        # padd line 1 to 15 characters
        line1 = line1.ljust(15, ' ')
        line1 = line1 + '>'
        
        self.lcd.text(line1, 1)
        self.lcd.text(self.input, 2)
            
        
    def next(self):
        self.current_index = (self.current_index + 1) % len(self.input_list)
        self.__display__()
        
    def previous(self):
        self.current_index = (self.current_index - 1) % len(self.input_list)
        self.__display__()
        
    def select(self):
        if self.input_list[self.current_index] == 'DONE':
            if len(self.input) < self.min_input_length:
                self.lcd.text("TOO SHORT".center(16), 2)
                time.sleep(1)
                self.__display__()
            else:
                return_val = self.input
                self.input = "" # Reset input
                self.current_index = 0 # Reset index
                return return_val
        
        elif self.input_list[self.current_index] == 'DEL':
            if len(self.input) > 0:
                self.input = self.input[:-1]
            else :
                self.lcd.text("EMPTY INPUT".center(16), 2)
                time.sleep(1)
            self.__display__()
            
        else:
            if len(self.input) < self.max_input_length:
                self.input += self.input_list[self.current_index]
            else:
                self.lcd.text("LIMIT REACHED".center(16), 2)
                time.sleep(1)
            self.__display__()