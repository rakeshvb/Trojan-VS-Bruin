from copy import deepcopy
import sys
class KnowledgeBase:

    def __init__ (self, ruleList):
        self.rules = ruleList[:]

    def fetch_all_Rules(self, goal):
        name_Goal = goal[0:goal.index('(')]

        fetched_Rules = []                                       
        for rule in self.rules:
            rulesp = rule.split(' => ')                      
            impliname = ''

            if len(rulesp) == 2:                             
                implication = rulesp[1].strip()
                impliname = implication[0:implication.index('(')]
            else:
                impliname = rule[0:rule.index('(')]

            if impliname == name_Goal:
                fetched_Rules.append(rule)                       

        return fetched_Rules

def Variable(value):
    if value.find("(") == -1:
        if value.find(",") == -1:
            if ord(str(value[0])) >= 97:
                return True

    else:
        return False

def Compound(value):
    if value.find("(") == -1:
        return False
    else:
        return True

def isList(value):
    if Variable(value) or Compound(value):
        return False
    elif str(value).find(',') != -1:
        return True
    else:
        return False

def is_var_symbol(s):
	return s[0].islower()

def is_variable(x):
	return isinstance(x, Expr) and not x.args and is_var_symbol(x.op)


def pfun(value):
    op = value.split("(")
    return op[0]

def parg(value):
    op = value.split("(")
    arguments = op[1].split(")")
    return arguments[0]

def pfirst(value):

    first = value.partition(", ")

    return first[0]

def prest(value):
    first = value.partition(", ")
    return first[2]


def UnifyVariables(var, x, theta):

    theta = deepcopy(theta)

    if theta.has_key(var):
        return Unify(theta[var], x, theta)
    elif theta.has_key(x):
        return Unify(var, theta[x], theta)
    else:
        theta[var] = x
        return theta

def Unify(x, y, theta):
    theta = deepcopy(theta)

    if theta == 'failure':
        return 'failure'
    elif x == y:
        return theta

    elif Variable(x):
        return UnifyVariables(x, y, theta)
    elif Variable(y):
        return UnifyVariables(y, x, theta)
    elif Compound(x) and Compound(y):
        return Unify(parg(x), parg(y), Unify(pfun(x), pfun(y), theta))
    elif isList(x) and isList(y):
        return Unify(prest(x), prest(y), Unify(pfirst(x), pfirst(y), theta))
    else:
        return 'failure'

def splitRule(rule):

    lhs = ''
    rhs = ''

    split = rule.split(" => ")

    if rule.find("=>") != -1:          
        lhs = split[0]
        rhs = split[1]
    else:
        rhs = split[0]

    return lhs, rhs


def convertRuleToDict(rule):

    ruleDict = ''

    implicationSplit = rule.split(' => ')

    #If it is a complex sentence
    if len(implicationSplit) == 2:
        #Premise Section
        conjunctionSplit = implicationSplit[0].split(" && ")
        ruleDict = {'premiseCount':len(conjunctionSplit)}

        for i in range(0,len(conjunctionSplit)):
            premise = conjunctionSplit[i].strip()

            if premise[0] == '~':
                ruleDict['premise'+str(i+1)] = {'not': True}
                premise = premise[1:]
            else:
                ruleDict['premise'+str(i+1)] = {'not': False}

            name = premise[0:premise.index('(')]
            variables = premise[premise.index('(')+1:premise.index(')')]
            variables = variables.split(',')
            for op in range (0,len(variables)):
                variables[l] = variables[l].strip()
            varCount = len(variables)

            ruleDict['premise'+str(i+1)]['varCount'] = varCount
            ruleDict['premise'+str(i+1)]['variables'] = variables
            ruleDict['premise'+str(i+1)]['variableSubs'] = variables[:]
            ruleDict['premise'+str(i+1)]['name'] = name

        #Conclusion Section
        conclusion = implicationSplit[1].strip()

        if conclusion[0] == '~':
            ruleDict['conclusion'] = {'not': True}
            conclusion = conclusion[1:]
        else:
            ruleDict['conclusion'] = {'not': False}

        name = conclusion[0:conclusion.index('(')]
        variables = conclusion[conclusion.index('(')+1:conclusion.index(')')]
        variables = variables.split(',')
        for l in range (0,len(variables)):
            variables[l] = variables[l].strip()
        varCount = len(variables)

        ruleDict['conclusion']['varCount'] = varCount
        ruleDict['conclusion']['variables'] = variables
        ruleDict['conclusion']['variableSubs'] = variables[:]
        ruleDict['conclusion']['name'] = name


    #If it is an atomic sentence
    elif len(implicationSplit) == 1:

        ruleDict = {'premiseCount': 0}

        conclusion = implicationSplit[0].strip()

        if conclusion[0] == '~':
            ruleDict['conclusion'] = {'not': True}
            conclusion = conclusion[1:]
        else:
            ruleDict['conclusion'] = {'not': False}

        name = conclusion[0:conclusion.index('(')]
        variables = conclusion[conclusion.index('(')+1:conclusion.index(')')]
        variables = variables.split(',')
        for l in range (0,len(variables)):
            variables[l] = variables[l].strip()
        varCount = len(variables)

        ruleDict['conclusion']['varCount'] = varCount
        ruleDict['conclusion']['variables'] = variables
        ruleDict['conclusion']['variableSubs'] = variables[:]
        ruleDict['conclusion']['name'] = name

    return ruleDict

def convertGoalInferenceToDict(goalInference):
    conjunctionSplit = goalInference.split(" && ")
#    print ('ASK: '+str(conjunctionSplit[0]))
#    y=('ASK: '+str(conjunctionSplit[0]))
#    output.write(y)
#    output.write("\n")
    ruleDict = {'premiseCount':len(conjunctionSplit)}

    for i in range(0,len(conjunctionSplit)):
        premise = conjunctionSplit[i].strip()

        if premise[0] == '~':
            ruleDict['premise'+str(i+1)] = {'not': True}
            premise = premise[1:]
        else:
            ruleDict['premise'+str(i+1)] = {'not': False}

        name = premise[0:premise.index('(')]
        variables = premise[premise.index('(')+1:premise.index(')')]
        variables = variables.split(',')
        varCount = len(variables)

        ruleDict['premise'+str(i+1)]['varCount'] = varCount
        ruleDict['premise'+str(i+1)]['variables'] = variables
        ruleDict['premise'+str(i+1)]['variableSubs'] = variables[:]
        ruleDict['premise'+str(i+1)]['name'] = name

    return ruleDict


def FR(rule):

    first = ''
    rest = ''

    split = rule.partition(" && ")

    if rule.find("&&") != -1:
        first = split[0]
        rest = split[2]
    else:
        first = split[0]

    return first, rest

def substitution(theta,premise):
    braco = premise.find('(')
    bracc = premise.find(')')

    variables = premise[braco+1:bracc]
    variables = variables.split(',')
    premise1 = premise[0:braco]

    substitutevar = ''
    for v in range (0,len(variables)):
        variables[v] = variables[v].strip()
        if ord(str(variables[v][0])) >= 97 and theta.has_key(variables[v]):
            substitutevar = substitutevar + theta[variables[v]]+', '
        else:
            substitutevar = substitutevar + variables[v] + ', '

    substitutevar = '(' + substitutevar[0:len(substitutevar)-2] + ')'
    premise1 = premise1 + substitutevar

    return premise1



def Back_Chain_Ask(KB, query):
    return Back_Chain_OR(KB, query, {})

def Back_Chain_OR(KB, goal, theta):
    
    
    ox = goal.find('(')
    cx = goal.find(')')

    variables = goal[ox+1:cx]
    variables = variables.split(',')
    goalx = goal[0:ox]



    s = ''
    for op in range (0,len(variables)):
        variables[op] = variables[op].strip()
        if ord(str(variables[op][0])) >= 97:
            dd=variables[op]
            if theta.has_key(dd):
                sub = str(theta[variables[op]])

                while ord(sub[0]) >= 97 and theta.has_key(sub):
                    sub = str(theta[sub])

                s = s + sub + ', '

            else:
                s = s + '_, '

        else:
            s = s + variables[op] + ', '

    s = '(' + s[0:len(s)-2] + ')'
    goalx = goalx + s
    za= str('Ask: '+goalx)
    o.write(za)
    o.write('\n')
    print('Ask: '+goalx)

#    name = goal[0:goal.index('(')]
#    variables = goal[goal.index('(')+1:goal.index(')')]
#    xz=variables
#    variables = variables.split(',')
#    for op in range (0,len(variables)):
#        variables[op] = variables[op].strip()
#        if variables[op][0].islower():
#            variables[op]='_'
#    #print variables
#    s=''
#    varCount = len(variables)
#    for ii in range(varCount):
#        if ii == varCount-1:
#            s=s+variables[ii]
#        else:
#            s=s+variables[ii]+', '
#    #print s
#    #print goal.replace(xz,s)
#    
#    
#    
#    za= str('Ask: '+goal.replace(xz,s))
#    o.write(za)
#    o.write('\n')
##    wq=goal.split('(')
##    print wq[1][0]
#    print('Ask: '+goal.replace(xz,s))
    #flag=False
    ij=0
    for rule in KB.fetch_all_Rules(goal):
        ij+=1
        ij1=len(KB.fetch_all_Rules(goal))
#        print ij1
#        print ij
        lhs, rhs = splitRule(rule)
        uni=Unify(rhs, goal, theta)
        flag=False
        for thetaOne in Back_Chain_And(KB, lhs, uni, rhs):
            #print('Ask: '+lhs)
#            zaaaa= str('True: '+goal)
#            o.write(zaaaa)
#            o.write('\n')
#            print str('True: '+goal)
            #if thetaOne != -1:
#            zaa= str('False: '+goal)
#            o.write(zaa)
#            o.write('\n')
#            print str('False: '+goal)
           # print "______"
            #print rhs
            #print "______"
            flag=True
            yield thetaOne
        if flag == False:
            if ij == ij1:
                zaaaa= str('False: '+goalx)
                o.write(zaaaa)
                o.write('\n')
                print str('False: '+goalx)
            else:
                zaaaaa= str('Ask: '+goalx)
                o.write(zaaaaa)
                o.write('\n')
                print str('Ask: '+goalx)
#                    strPrintReady = Expr.generatePrintReadyStatement(goal)
#                    # print "False: %s" %(strPrintReady)
#                    fileOutput.write("Ask: %s\n" %(strPrintReady))
#        if flag==False:
#            print str('False: '+goal)
#            else:
#                zaa= str('False: '+rhs)
#                o.write(zaa)
#                o.write('\n')
#                print str('False: '+rhs)



def Back_Chain_And(KB, goals, theta, rhs):
    #print goals
    if theta == 'failure':
#        zaa= str('False: '+rhs)
#        o.write(zaa)
#        o.write('\n')
#        print str('False: '+rhs)
        #print('Ask: '+rhs)
        return
    elif len(goals) == 0:
        
        
        ox = rhs.find('(')
        cx = rhs.find(')')

        variables = rhs[ox+1:cx]
        variables = variables.split(',')
        goalx = rhs[0:ox]

        s = ''
        for op in range (0,len(variables)):
            variables[op] = variables[op].strip()
            if ord(str(variables[op][0])) >= 97:

                sub = str(theta[variables[op]])

                while ord(sub[0]) >= 97:
                    sub = str(theta[sub])

                s = s + sub+', '
            else:
                s = s + variables[op] + ', '

        s = '(' + s[0:len(s)-2] + ')'
        goalx = goalx + s
        #print('True: '+goalx)
        
        
        
        '''
        name = goal[0:goal.index('(')]
    variables = goal[goal.index('(')+1:goal.index(')')]
    xz=variables
    variables = variables.split(',')
    for op in range (0,len(variables)):
        variables[op] = variables[op].strip()
        if variables[op][0].islower():
            variables[op]='_'
    #print variables
    s=''
    varCount = len(variables)
    for ii in range(varCount):
        if ii == varCount-1:
            s=s+variables[ii]
        else:
            s=s+variables[ii]+', '
    #print s
    #print goal.replace(xz,s)
        '''
        #rhs=substitution(theta, rhs)
        zaaa= str('True: '+goalx)
        o.write(zaaa)
        o.write('\n')
        #print theta
        print str('True: '+goalx)
        yield theta
    else:
        first, rest = FR(goals)
        for thetaOne in Back_Chain_OR(KB, substitution(theta, first), theta):
            for thetaTwo in Back_Chain_And(KB, rest, thetaOne, rhs):
                #print('Ask: '+substitution(theta, first))
                #print "AAAAAAAAAAAAAAAA"
#                zaaa= str('False: '+rhs)
#                o.write(zaaa)
#                o.write('\n')
#                print str('False: '+rhs)
                yield thetaTwo


# Apply substitition {Has(x),Has(john) -- {x/John}}
# {theta : x/john} returns Has(john) if Has(x) is passed
#def sub_str(self,theta,concl):
#        start_index = concl.index('(')
#        last_index = concl.index(')')
#        result = concl[start_index+1:last_index]
#        params = result.split(',')
#        part = theta.split(',')
#        if(len(part) == 1):
#                part2 = part[0].split("/")
#                for i in params:
#                        if part2[0] == i:
#                                concl = concl.replace(i,part2[1])
#        else:
#                for j in part:
#                        part2 = j.split('/')
#                        for x in params:
#                                if part2[0] == x:
#                                        concl = concl.replace(x,part2[1])
#        return concl



f = open('input.txt')
o = open('output.txt','w')
query = f.readline().strip()
queryList = query.split(' && ')     
kbc = f.readline()
kb = []
for i in range(1,int(kbc)+1):       
        s = f.readline()
        kb.append(s.rstrip('\n'))

for i in range(0, int(kbc)):
    index = 0
    while index < len(kb[i]):
            letter = kb[i][index]

            if letter == '(':
                letter = kb[i][index+1]
                if ord(letter)>=97:                 
                    letter = letter+str(i+1)
                    kb[i]=kb[i][:index+1]+letter+kb[i][index+2:]

            elif letter == ',':
                letter = kb[i][index+2]
                if ord(letter)>=97:
                    letter = letter+str(i+1)
                    kb[i]=kb[i][:index+2]+letter+kb[i][index+3:]

            index = index+1

# q1 = expr("(Pig(x) & Slug(y)) => Faster(x, y)")
# q2 = expr("(Pig(Bob) & Slug(Steve)) => Faster(Bob, Steve)")
# print Unify(q1, q2, {})

KB = KnowledgeBase(kb)
finala = True

for query in queryList:

    x = Back_Chain_Ask(KB ,query)
    
    try:
        substitutionList = next(x)
        finala = True
        
       # print substitutionList
    except StopIteration:
        finala = False
        break

if finala:
    zax='True'
    o.write(zax)
    print True
else:
    zax='False'
    o.write(zax)
    print False
