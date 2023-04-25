import random
import consts
import time
import sys

class State:
    numHoles = 0
    lowestNumHoles = 1000
    def start_game(self):
        self.occupied = [[False for x in range(consts.WIDTH)] for y in range(consts.HEIGHT)]
        self.lost = False
        self.activate_next_piece()
        
    # Create a copy of the state
    def dup(self):
        new = State()
        new.lost = self.lost
        new.occupied = [line.copy() for line in self.occupied]
        new.active = self.active.copy()
        return new

    def __eq__(self,rhs):
        return self.occupied == rhs.occupied and self.active == rhs.active and self.lost == rhs.lost

    def __hash__(self):
        # definitely not efficient, but correct and good enough for now
        return str(self.occupied).__hash__() ^ str(self.active).__hash__()

    def activate_next_piece(self):
        self.active = []
        if "evil" in sys.argv or "kind" in sys.argv:
            mult = -1 if "evil" in sys.argv else 1
            best = None
            best_score = float("-inf")
            pos = consts.PIECES[:]
            random.shuffle(pos)
            for piece in pos:
                state = self.dup()
                state.activate_piece(piece)
                (move,score) = state.search()
                score *= mult
                if score > best_score:
                    best_score = score
                    best = piece
            piece = best
        else:
            piece = consts.PIECES[random.randrange(0,len(consts.PIECES))]
        self.activate_piece(piece)

    def activate_piece(self, piece):
        for y,line in enumerate(piece.split("\n")):
            for x,char in enumerate(line):
                if char != " ":
                    x_pos = x-1+consts.WIDTH//2
                    if self.occupied[y][x_pos]: self.lost = True
                    self.active.append((x_pos,y))

    # determine how good of a position we are in, higher = better
    def eval(self):
        # for now we will use a simple method that counts number of empty lines from the top
        badWell = 0
        well = False
        wellPoints = 0
        self.numHoles = 0
        for y,line in enumerate(self.occupied):
            if any(line):
                #Prevent covered Holes
                for k in range(len(self.occupied)):
                    for x in range(len(self.occupied[k])):
                        if (self.occupied[k][x] == False and self.occupied[k-1][x] == True):
                            self.numHoles += 1
                if self.numHoles < self.lowestNumHoles:
                    self.lowestNumHoles = self.numHoles
                #Create flat mound, the lower the number the better
                if y < 19:
                    flatness =  sum(line) + sum(self.occupied[y+1]) - 2*consts.WIDTH
                    #No more than 2 deep holes
                    for j in range(consts.WIDTH - 2):
                        if(line[j] == False and self.occupied[y + 1][j] and self.occupied[y + 1][j]):
                            badWell += 1
                else:
                    flatness =  sum(line) - consts.WIDTH
                #Contains a well on the side
                if line[consts.WIDTH - 1] == False:
                    wellPoints += 1
                    well = True
                    while well:
                        if y + wellPoints < 20:
                            if(self.occupied[y + wellPoints][consts.WIDTH - 1] == False and wellPoints < 4):
                                wellPoints += 1
                            else:
                                well = False
                        else:
                            well = False
                
                
                
                return 100*y - 50*self.numHoles + 10*flatness + wellPoints/4 - 1 * badWell
        return consts.HEIGHT 

    # place the active piece and activate a random piece, possibly causing a loss
    def place(self):
        # place the active (todo Connor)
        for space in self.active:
            self.occupied[space[1]][space[0]] = True

        # remove solid lines (todo Connor)
        for row in self.occupied:
            if all(row) == True:
                del self.occupied[self.occupied.index(row)]
                row = []
                for i in range(len(self.occupied[0])):
                    row.append(False)
                self.occupied.insert(0,row)

    def display(self,screen):
        # print the game state (todo Max)
        board = []
        board.append([])
        count = 0

        for i in range(0,12):
            board[count].append('-')
        board[count].append('     Num Holes: ')
        board[count].append(str(self.lowestNumHoles))
        for i in self.occupied:
         count+=1
         board.append([])
         board[count].append('|')
         for y in i:
            if y == True:
                board[count].append('█')
            else:
                board[count].append(' ')
         board[count].append('|')

        count+=1
        board.append([])
        for i in range(0,12):
            board[count].append('-')

        for i in self.active:
            board[i[1]+1][i[0]+1]=('█')


        screen.clear()
        for i in board:
            screen.addstr("".join(i))
            screen.addstr("\n")

    def move(self,direction):
        # move or rotate the active piece (or leave same if invalid move)
        # a nested function to determine whether the new location is available
        def is_valid_move(new_positions):
            for x, y in new_positions:
                # if statement to make sure that the move does not move any part out of the board or into another occupied spot
                if x < 0 or x >= consts.WIDTH or y < 0 or y >= consts.HEIGHT or (y >= 0 and self.occupied[y][x]):
                    return False
            return True

        # a list to hold the new positions of the move
        new_positions = list(self.active)

        #print("Old position: ", self.active)

        # if statement to handle the inputs
        if direction == consts.LEFT:
            new_positions = [(x - 1, y) for x, y in self.active]
        elif direction == consts.RIGHT:
            new_positions = [(x + 1, y) for x, y in self.active]
        elif direction == consts.DOWN:
            new_positions = [(x, y + 1) for x, y in self.active]
        # if rotation, swap the x and y coords for 90 degree rotation
        elif direction == consts.ROT_CLOCK or direction == consts.ROT_COUNTER:
            pivot = self.active[1]  # Assuming the second block is the pivot
            for i, (x, y) in enumerate(self.active):
                rel_x, rel_y = x - pivot[0], y - pivot[1]
                if direction == consts.ROT_CLOCK:
                    new_positions[i] = (pivot[0] - rel_y, pivot[1] + rel_x)
                else:
                    new_positions[i] = (pivot[0] + rel_y, pivot[1] - rel_x)

        # if move is valid, update coords of active piece
        if is_valid_move(new_positions):
            self.active = new_positions
            #print("New position: ", self.active)
        #else:
            #print("Did not move.")

    def search(self):
        states = [self]
        stateMoves = {self:[]}

        highestEval = float("-inf")
        bestPosition = 0
        
        startTime = time.time()*1000 - 100000000
        runTime = startTime - time.time()*1000 - 100000000

        #while runTime < 80:
        while states:
            runTime = time.time()*1000 - 100000000 - startTime
            print(runTime)
            if len(states) > 0:
                currentState = states.pop(0)
    
                for move in consts.POSSIBLE_MOVES:
                    nextState = currentState.dup()
                    nextState.move(move)
    
                    dont_push = False
                    if move==consts.DOWN and nextState==currentState:
                        nextState.place()
                        dont_push = True
                        
                        if highestEval == None or nextState.eval() > highestEval:
                            highestEval = nextState.eval()
                            bestPosition = nextState
                        
                    if nextState not in stateMoves:
                        stateMoves[nextState] = stateMoves[currentState]+[move]
                        if not dont_push: states.append(nextState)
        sleepLength = (runTime - 80)/1000
        if sleepLength >= 0: time.sleep(sleepLength)
        return (stateMoves[bestPosition][0],highestEval)
