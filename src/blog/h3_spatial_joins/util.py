import numpy as np
import h3
from dataclasses import dataclass

@dataclass
class State:
    i: int
    j: int
    k: int
    arr: list
        
    def copy(self):
        return State(self.i, self.j, self.k, list(self.arr))

    
def get_siblings(h):
    p = h3.h3_to_parent(h)
    sibs = h3.h3_to_children(p)
    sibs = sorted(sibs)
    
    return sibs

def get_next_sibling(h):
    """ Returns None if h is the last child
    """
    sibs = get_siblings(h)
    i = sibs.index(h) + 1
    
    if i >= len(sibs):
        return None
    else:
        return sibs[i]
    
def get_prev_sibling(h):
    """ Returns None if h is the first child
    """
    sibs = get_siblings(h)
    i = sibs.index(h) - 1
    
    if i < 0:
        return None
    else:
        return sibs[i]
    
def is_a_first_child(h):
    if h3.h3_get_resolution(h) == 0:
        return False

    if get_prev_sibling(h) is None:
        return True
    else:
        return False
    
def is_first_descendent_of(p, h):
    res_p = h3.h3_get_resolution(p)
    res_h = h3.h3_get_resolution(h)
    
    if res_p <= res_h and h3.h3_to_parent(h, res_p):
        return is_a_first_child(h)
    else:
        return False
    
def siblings_up_to(h):
    sibs = get_siblings(h)
    for sib in sibs:
        yield sib
        if sib == h:
            break
            
def step(state):
    state = state.copy()
    i = state.i
    j = state.j
    k = state.k
    arr = state.arr
    
    assert i <= j <= k <= len(arr)
  
    # check for completed set...
    if i < j:
        h = arr[j-1]
        # check for completed children set
        if get_next_sibling(h) is None:
            j -= 7 # need to work on pentagons
            
            # can't just automatically put it on the stack
            # arr[j] = h3.h3_to_parent(h)
            # j += 1
            
            # gotta put it at the top of the input
            k -= 1
            arr[k] = h3.h3_to_parent(h)
            return State(i,j,k,arr)

    # this can't go before the completed set check. why? what's the loop invariant we need?
    if k >= len(arr):
        raise Exception('done iterating') # maybe flush stack?
        
    if i == j:  # if stack is empty
        h = arr[k]
        
        if is_a_first_child(h):
            arr[j] = arr[k]
            j += 1
            k += 1
            return State(i,j,k,arr)
        else:
            # flush element and stack stays empty
            arr[j] = arr[k]
            i += 1
            j += 1
            k += 1
            return State(i,j,k,arr)
            
    
    if i < j: # stack not empty
        h = arr[k]
        k += 1
        
        # easy to check next sibling with subtraction: expect a 1, just shifted by resolution
        next_wanted = get_next_sibling(arr[j-1])
        
        if h == next_wanted:
            # push h onto stack
            arr[j] = h
            j += 1
            return State(i,j,k,arr)
        
        elif is_first_descendent_of(next_wanted, h):  ## we can combine these two!!!
            arr[j] = h
            j += 1
            return State(i,j,k,arr)
        else: # flush the stack
            i = j # make stack empty
            k -= 1 # re run that element
            return State(i,j,k,arr)



def compact(arr):
    arr = sorted(arr)
    state = State(0,0,0,arr)
    
    try:
        while True:
            state = step(state)
    except:
        pass
    
    return state.arr[:state.j]
