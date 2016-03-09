import itertools
from copy import deepcopy
import sys
import re


q_done = []
queriesFalseSoFar = []
query = ""
rawStatements = []
nc = 0
xvalue = ''
xprint = []
s1 = ""
s2 = ""
queryArgs=[]

class FolKB():
    def __init__(self, initial_clauses=[]):
        self.clauses = [] 
        for clause in initial_clauses:
            self.tell(clause)

    def tell(self, sentence):
        self.clauses.append(sentence)

    def retract(self, sentence):
        self.clauses.remove(sentence)

    def fetch_rules_for_goal(self, goal):

    	matchingRules = []
    	strGoal = "%s" %(goal)
    	for clause in self.clauses:
    		lhs, rhs = parse_definite_clause(standardizevar(clause))
    		if rhs.op == goal.op:
    			matchingRules.append(clause)
    	return matchingRules

    def __str__(self):
    	str = ""
    	for clause in self.clauses:
    		str += "%s\n" %(clause)
    	return str

class Expr:

	def __init__(self, op, *args):
		self.op = op
		self.args = map(expr, args)

	def __call__(self, *args):
		return Expr(self.op, *args)

	def __repr__(self):
		
		if not self.args:         
			return str(self.op)
		elif is_symbol(self.op):  
			return '%s(%s)' % (self.op, ', '.join(map(repr, self.args)))
		elif len(self.args) == 1: 
			return self.op + repr(self.args[0])
		else:                     
			return '(%s)' % (' '+self.op+' ').join(map(repr, self.args))

	def __and__(self, other):
		return Expr('&',  self, other)

	def __rshift__(self, other): return Expr('>>', self, other)

	def __eq__(self, other):
		return (other is self) or (isinstance(other, Expr) and self.op == other.op and self.args == other.args)

	def __hash__(self):
		return hash(self.op) ^ hash(tuple(self.args))

	
	def printstatement(self):
		str = ""
		if not self.args:
			str = str(self.op)
		elif is_symbol(self.op):  
			str = "%s" %(self.op)
			if len(self.args) > 0:
				str += "("
				for i in range(0, len(self.args)-1):
					strTemp = "%s" %(self.args[i])
					if strTemp[0].islower() == False:
						str += "%s, " %(self.args[i])
					else:
						str += "_, "
				strTemp = "%s" %(self.args[-1])
				if strTemp.islower() == False:
					str += "%s)" %(self.args[-1])
				else:
					str += "_)"

		elif len(self.args) == 1:
			str = self.op + repr(self.args[0])
		else:
			str = '(%s)' % (' '+self.op+' ').join(map(repr, self.args))
		return str

def Variable(value):
    if value.find("(") == -1:
        if value.find(",") == -1:
            if ord(str(value[0])) >= 97:
                return True

    else:
        return False



def expr(s):
	if isinstance(s, Expr):
		return s
	s = s.replace('=>', '>>')
	s = re.sub(r'([a-zA-Z0-9_.]+)', r'Expr("\1")', s)

	return eval(s, {'Expr':Expr})

def is_var_symbol(s):
	return s[0].islower()


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




def is_variable(x):
	return isinstance(x, Expr) and not x.args and is_var_symbol(x.op)

def variables(s):
	result = set([])
	def walk(s):
		if is_variable(s):
			result.add(s)
		else:
			for arg in s.args:
				walk(arg)
	walk(s)
	return result

def is_symbol(s):
    return isinstance(s, str) and s[:1].isalpha()

def unify_var(var, x, s):
    if var in s:
        return Unify(s[var], x, s)
    else:
        return extend(s, var, x)


def Unify(x, y, theta):
	if theta is None:
		return None
	elif x == y:
		return theta
	elif is_variable(x):
		return unify_var(x, y, theta)
	elif is_variable(y):
		return unify_var(y, x, theta)
	elif isinstance(x, Expr) and isinstance(y, Expr):
		return Unify(x.args, y.args, Unify(x.op, y.op, theta))
	elif isinstance(x, str) or isinstance(y, str):
		return None
	elif (type(x) is list) and (type(y) is list) and len(x) == len(y):
		if not x: return theta
		return Unify(x[1:], y[1:], Unify(x[0], y[0], theta))
	else:
		return None


def extend(s, var, val):
    s2 = s.copy()
    s2[var] = val
    return s2

def parse_definite_clause(s):
	if is_symbol(s.op):
		return [], s
	else:
		antecedent, consequent = s.args
		return con(antecedent), consequent

def dis(op, args):
	result = []
	def collect(subargs):
		for arg in subargs:
			if arg.op == op: collect(arg.args)
			else: result.append(arg)
	collect(args)
	return result

def con(s):
	return dis('&', [s])


def FOL_BC_ASK(KB, query):
	return FOL_BC_OR(KB, query, {})


def FOL_BC_OR(KB, goal, theta):
	global s1
	global s2
	global q_done
        global xprint
        global xvalue
	strPrintReady = Expr.printstatement(goal)
	strGoal = "%s" %(goal)
	if strGoal != s2 and strPrintReady != s1:
		
		print "Ask: %s" %(goal)
                z="Ask: %s\n" %(strPrintReady)
		o.write(z)
		q_done.append(strPrintReady)
		s2 = strGoal
		s1 = strPrintReady


#    za= str('Ask: '+goalx)
#    o.write(za)
#    o.write('\n')
#    print('Ask: '+goalx)

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
#    za= str('Ask: '+goalx)
#    o.write(za)
#    o.write('\n')
#    print za
##    wq=goal.split('(')
##    print wq[1][0]
#    print('Ask: '+goal.replace(xz,s))
    #flag=False


	rules = KB.fetch_rules_for_goal(goal)
	for i in range(0, len(rules)):
		rule = rules[i]
		stdExpr = standardizevar(rule)
		lhs, rhs = parse_definite_clause(standardizevar(rule))
		thetaBeforeAnd = Unify(rhs, goal, theta)
		strGoal = "%s" %(goal)
		noNeedToPrintThisFalseStatement = False
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

		if not lhs:
			strPrintReady = Expr.printstatement(goal)
			strGoal = "%s" %(goal)
			if strGoal != s2 and strPrintReady != s1:
				if strPrintReady in q_done:
					thetaUnify = Unify(rhs, goal, theta)
					
					if thetaUnify is not None:
						print "Ask: %s" %(goal)
                                                z1="Ask: %s\n" %(strPrintReady)
						o.write(z1)
						q_done.append(strPrintReady)
						s2 = strGoal
						s1 = strPrintReady
						
					else:
						noNeedToPrintThisFalseStatement = True
				else:
					print "Ask: %s" %(goal)
                                        z2="Ask: %s\n" %(strPrintReady)
					o.write()
					q_done.append(strPrintReady)
					s2 = strGoal
					s1 = strPrintReady

		thetasb4 = FOL_BC_AND(KB, lhs, thetaBeforeAnd, goal)
		value_has = False
		for theta1 in thetasb4:
			value_has = True
			goal = subst(theta, goal)
			strGoal = "%s" %(goal)
			if strGoal == stringq:
				yield theta1
				raise StopIteration
			yield theta1
		if value_has == False:
			if i == len(rules)-1:
				thetaUnify = Unify(rhs, goal, theta)
				unsubGoal = deepcopy(goal)
				
				if noNeedToPrintThisFalseStatement == False:
					goal = subst(theta, goal)
					strPrintReady = Expr.printstatement(goal)
					strGoal = "%s" %(goal)
					print "False: %s" %(goal)
                                        z3="False: %s\n" %(strPrintReady)
					o.write(z3)
					s2 = strGoal
					s1 = strPrintReady
					queriesFalseSoFar.append(strPrintReady)
			else:
				strPrintReady = Expr.printstatement(goal)
				strGoal = "%s" %(goal)
				if strGoal != s2 and strPrintReady != s1:
					
					print "Ask: %s" %(goal)
                                        z4="Ask: %s\n" %(strPrintReady)
					o.write(z4)
					q_done.append(strPrintReady)
					s2 = strGoal
					s1 = strPrintReady


def FOL_BC_AND(KB, goals, theta, goal):
	global s1
	global s2
	global q_done
	if theta is None:
            #        zaa= str('False: '+rhs)
#        o.write(zaa)
#        o.write('\n')
#        print str('False: '+rhs)
        #print('Ask: '+rhs)
		pass
	elif not goals:
		goal = subst(theta, goal)
		strGoal = "%s" %(goal)
		strPrintReady = Expr.printstatement(goal)
		print "True: %s" %(strGoal)
                z5="True: %s\n" %(strPrintReady)
		o.write(z5)
		s2 = strGoal
		s1 = strPrintReady

		yield theta
	else:
		first, rest = goals[0], goals[1:]
		strFirst = "%s" %(first)
		sen = subst(theta, first)
		for arg in sen.args:
			if arg in theta:
				sen = subst(theta, sen)
		strSen = "%s" %(sen)
		thetas = FOL_BC_OR(KB, sen, theta)
		for theta1 in thetas:
                     #print('Ask: '+substitution(theta, first))
                #print "AAAAAAAAAAAAAAAA"
#                zaaa= str('False: '+rhs)
#                o.write(zaaa)
#                o.write('\n')
#                print str('False: '+rhs)
			value_has = True
			thetasForAND = FOL_BC_AND(KB, rest, theta1, goal)
			for theta2 in thetasForAND:
				yield theta2

def standardizevar(sentence, dic=None):
	if dic is None: dic = {}
	if not isinstance(sentence, Expr):
		return sentence
	elif is_var_symbol(sentence.op):
		if sentence in dic:
			return dic[sentence]
		else:
			v = Expr('v_%d' % standardizevar.counter.next())
			dic[sentence] = v
			return v
	else:
		return Expr(sentence.op, *[standardizevar(a, dic) for a in sentence.args])

standardizevar.counter = itertools.count()

def subst(s, x):
	if isinstance(x, list):
		return [subst(s, xi) for xi in x]
	elif isinstance(x, tuple):
		return tuple([subst(s, xi) for xi in x])
	elif not isinstance(x, Expr):
		return x
	elif is_var_symbol(x.op):
		return s.get(x, x)
	else:
		return Expr(x.op, *[subst(s, arg) for arg in x.args])



def readFile(fileName):
	global query
	global rawStatements
	global nc
	lineNumber = 0
	with open(fileName,'r') as f:
		for l in f:
			l=l.rstrip()
			l = l.replace("&&", "&")
                        #print l
			if "=>" in l:
				l = "(%s" %(l)
				l = l.replace(" =>",") =>")
			if lineNumber == 0:
                                split_query = l.split("&")
				for token in split_query:
                                    queryArgs.append(token.rstrip())
				# query = line
                                lineNumber = 1
			elif lineNumber == 1:
				nc = int(l)
				lineNumber = 2
			else:
				rawStatements.append(l)
				lineNumber = lineNumber + 1
		f.close()


#fileName = sys.argv[-1]
fileName = "input.txt"
o = open('output.txt','w')
readFile(fileName)

sample_KB = FolKB(
    map(expr,
        rawStatements
        )
    )

#queryExpr = expr(query)
evalResults = []

for args in queryArgs:
	# print args
	queryExpr = expr(args)
	stringq = "%s" %(queryExpr)

	answers = FOL_BC_ASK(sample_KB, queryExpr)
	temp_ans = list(answers)
	if len(temp_ans) > 0:
		evalResults.append(True)
	else:
		evalResults.append(False)
		break
if False in evalResults:
	print "False"
        xx='False'
	o.write(xx)
else:
	print "True"
        xxx='True'
	o.write(xxx)
#if queryExpr.op == "&":
#	for args in queryExpr.args:
#		stringq = "%s" %(args)
#		answers = FOL_BC_ASK(sample_KB, args)
#		temp_ans = list(answers)
#		if len(temp_ans) > 0:
#			evalResults.append(True)
#		else:
#			evalResults.append(False)
#			break
#	if False in evalResults:
#		print "False"
#                xx='False'
#		o.write(xx)
#	else:
#		print "True"
#                xxx='True'
#		o.write(xxx)
#
#else:
#	stringq = "%s" %(queryExpr)
#	answers = FOL_BC_ASK(sample_KB, queryExpr)
#	temp_ans = list(answers)
#	if len(temp_ans) > 0:
#		evalResults.append(True)
#	else:
#		evalResults.append(False)
#	if False in evalResults:
#		print "False"
#                xxxx='False'
#		o.write(xxxx)
#	else:
#		print "True"
#                x6='True'
#		o.write(x6)