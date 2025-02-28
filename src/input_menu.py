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
        MAX_CHARS = 16
        line1 = f'<{self.input_list[self.current_index]}>'
        
        # center it and count the spaces on the left
        spaces_left = (MAX_CHARS - len(line1)) // 2
        print(spaces_left)
        
        line1_left = ''
        
        # add previous self.input_list to line 1
        i = 1
        while spaces_left > 0:
            to_add = self.input_list[(self.current_index - i) % len(self.input_list)]
            if len(to_add) + 1 <= spaces_left:
                line1_left = to_add + " " + line1_left
                spaces_left -= (len(to_add) + 1)
                i += 1
            else:
                break
            

            
        # add next self.input_list to line 1
        
        spaces_right = MAX_CHARS - len(line1) - len(line1_left)
        i = 1
        line1_right = ''
        while spaces_right > 0:
            to_add = self.input_list[(self.current_index + i) % len(self.input_list)]
            if len(to_add) + 1 <= spaces_right:
                line1_right += " " + to_add
                spaces_right -= (len(to_add) + 1)
                i += 1
            else:
                break
        
        
        line1 = line1_left + line1 + line1_right
        
        self.lcd.text(line1, 1)
        self.lcd.text(":" + self.input, 2)
            
        
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