import state
import consts

state = state.State()
consts.WIDTH = 4


state.occupied = [[False,False,False,False],
                  [False,False,False,False],
                  [False,False,False,True],
                  [False,True,True,True],
                  [False,True,True,True]]

state.active = [(0,1),(0,2),(0,3),(0,4)] # a long skinny vertical piece at the bottom left

test =           [[False,False,False,False],
                  [False,False,False,False],
                  [False,False,False,False],
                  [True,False,False,False],
                  [True,False,False,True]]

state.place()
assert(state.occupied == test)
print("PASS")

state.occupied = [[False,False,False,False],
                  [False,False,False,False],
                  [False,False,False,True],
                  [False,True,True,True],
                  [False,True,True,True]]


state.active = [(1,2),(2,2),(2,1),(3,1)] # an s piece starting at (1,2)

test =           [[False,False,False,False],
                  [False,False,True,True],
                  [False,True,True,True],
                  [False,True,True,True],
                  [False,True,True,True]]

state.place()
assert(state.occupied == test)
print("PASS")

