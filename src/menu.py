class Menu:
    def __init__(self, root, lcd):
        self.curr = root.children[0] # on initialization, use the first child of the DUMMY root

        self.curr_list = root.children # this list keeps track of the current level of the menu
        self.curr_index = 0 # this is the index of the current node in the list

        
        self.parent = root # this is the parent of the current node
        self.children = self.curr.children # this is the children of the current node
        
        self.lcd = lcd
        self.curr.display(self.lcd) # initialize display
        
        self.input_mode = None
        self.input_queue = []

    
    def next(self):
        self.curr_index = (self.curr_index + 1) % len(self.curr_list) # go to next index
        self.curr = self.curr_list[self.curr_index] # set current node to the new index
        self.curr.display(self.lcd) # display it

    def prev(self):
        self.curr_index = (self.curr_index - 1) % len(self.curr_list)
        self.curr = self.curr_list[self.curr_index]
        self.curr.display(self.lcd)

    def select(self):
        if self.curr.is_workflow: # if the current node is a workflow (i.e., a node with an action)
            next_hop = self.curr.select() # when it returns a node, go to that node
            if next_hop is None: # if it returns None, stay at the current node (this is helpful when a workflow is done)
                self.curr.display(self.lcd)
            else: # if the workflow returns a node, go to that node
                self.curr = next_hop
                self.curr_list = self.curr.parent.children # get the list of curr level node from the parent
                self.curr_index = self.curr_list.index(self.curr) # get the index of the current node in the list
                self.curr.display(self.lcd) # display the current node
        else:
            if self.curr.children: # if the current option has at least one child
                self.curr_list = self.curr.children # if it's not a workflow, go to the next level of the menu
                self.curr_index = 0
                self.curr = self.curr_list[self.curr_index]
                self.curr.display(self.lcd)

    
    def clear(self):
        self.lcd.clear()