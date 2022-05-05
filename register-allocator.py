TOTAL_REGISTERS = 4

class SymbolTable:
    def __init__(self):
        self.variables = []
    def AddVariable(self, v):
        self.variables.append(v)
    def AddNeighbors(self):
        for i in self.variables:
            for j in self.variables:
                if i != j:
                    CheckInterference(i, j)

class Variable:
    def __init__(self, identifier, num_accesses, start, end):
        self.identifier = identifier
        self.neighbors = set()
        self.num_accesses = num_accesses
        self.liveness = start, end
    def __str__(self):
        return self.identifier

class Color:
    def __init__(self, id):
        self.id = id
        self.vars = set()
        self.access = 0

        
def CheckInterference(a, b):
    interfere = False
    if a.liveness[0] >= b.liveness[0]:
        if a.liveness[0] <= b.liveness[1] and a.liveness[1] >= b.liveness[1]:
            interfere = True
        if a.liveness[0] <= b.liveness[1] and a.liveness[1] <= b.liveness[1]:
            interfere = True
    if interfere:
        a.neighbors.add(b)
        b.neighbors.add(a)

def AttemptMove(var, colors):
    can_attempt = False
    temp = var.color
    curr_payoff = len(temp.vars)
    for i in colors:
        if len(i.vars) + 1 > curr_payoff and i != temp:
            if not bool(var.neighbors & i.vars):
                temp = i
                can_attempt = True
                curr_payoff = len(i.vars) + 1
    t = var.color
    t.vars.remove(var)
    t.access -= var.num_accesses
    var.color = temp
    temp.vars.add(var)
    temp.access += var.num_accesses
    return can_attempt

def AttemptMoveNew(var, colors):
    can_attempt = False
    temp = var.color
    curr_payoff = temp.access
    for i in colors:
        if i.access + var.num_accesses > curr_payoff and i != temp:
            if not bool(var.neighbors & i.vars):
                temp = i
                can_attempt = True
                curr_payoff = i.access + var.num_accesses
    t = var.color
    t.vars.remove(var)
    t.access -= var.num_accesses
    var.color = temp
    temp.vars.add(var)
    temp.access += var.num_accesses
    return can_attempt

def GraphColoring(s, colors):
    cnt = 0
    for i in s.variables:
        col = Color(cnt)
        col.access += i.num_accesses
        col.vars.add(i)
        colors.add(col)
        i.color = col
        cnt += 1
    return colors

def init_table(filename):
    s = SymbolTable()
    try:
        f = open(filename, 'r')
        lines = f.readlines()
        for i in lines:
            print(i)
            name, occurence, start, end = i.split(' ')
            var = Variable(name, int(occurence), int(start), int(end))
            s.AddVariable(var)
    except:
        print("No such file")
        var = Variable("alpha", 3, 1, 10)
        s.AddVariable(var)
        var = Variable("beta", 3, 5, 7)
        s.AddVariable(var)
        var = Variable("gamma", 1, 9, 15)
        s.AddVariable(var)
        var = Variable("delta", 3, 13, 20)
        s.AddVariable(var)
        var = Variable("epsilon", 3, 10, 27)
        s.AddVariable(var)

    s.AddNeighbors()
    # for i in s.variables:
    #     print("Variable "+i.identifier + " Liveness " + str(i.liveness[0]) + ", " + str(i.liveness[1]) + " Neighbours ")
    #     for j in i.neighbors:
    #         print(j.identifier)
    return s


def test():
    filename = input("Please enter the file containing variable information : ")
    s = init_table(filename)
    cols = set()
    res = GraphColoring(s, cols)
    iter = 0
    poss = True
    s.variables.sort(key = lambda x: x.num_accesses)
    mode = input("Please enter the mode you want to run (0 for original game, and 1 for modification to game : ")
    while iter >= 0 and poss:
        iter += 1
        can = set()
        for i in s.variables:
            if int(mode) == 1:
                c = AttemptMoveNew(i, cols)
            else:
                c = AttemptMove(i, cols)
            can.add(c)
            # for i in can:
            #     print(i, end = ' ')
        if True not in can:
            poss = False
            print("\n\n\nNo more moves possible.")
    print('-'*20)
    print("It used " + str(iter) + " iterations")
    reg_count = 0
    accesses = []
    for i in res:
        print(str(i.id) + " Accesses: " + str(i.access) , end = ' : ')
        if i.access != 0:
            reg_count += 1
            accesses.append(i.access)
        for j in i.vars:
            print(j, end = ' ')
        print()
    print("The register count required for this code is " + str(reg_count))
    print()
    accesses.sort()
    if reg_count > TOTAL_REGISTERS:
        spill_cand = accesses[:reg_count-TOTAL_REGISTERS]
        print("More registers required than provided, spilling some variables")
        spill = Color("spill")
        cnt = 0
        for i in res:
            if i.access != 0:
                if i.access in spill_cand and cnt < reg_count - TOTAL_REGISTERS:
                    print(spill_cand)
                    for j in i.vars:
                        t = j.color
                        #t.vars.remove(j)
                        if i.access in spill_cand:
                            spill_cand.remove(i.access)
                        t.access -= j.num_accesses
                        j.color = spill
                        spill.vars.add(j)
                        print(i.id, i.access)
                        cnt += 1
                    for j in spill.vars:
                        if j in i.vars:
                            i.vars.remove(j)
        print("Spilled variables: ")
        for i in spill.vars:
            print(i.identifier, end = ', ')
        print("\n\nThe final configuration is : ")
        for i in res:
            print(str(i.id) + " Accesses: " + str(i.access) , end = ' : ')
            if i.access != 0:
                accesses.append(i.access)
            for j in i.vars:
                print(j, end = ' ')
        print()

if __name__ == "__main__":
    test()
