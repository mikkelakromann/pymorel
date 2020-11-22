#from pyomo.environ import Objective, Constraint, Var, Set, Param
#from pyomo.environ import NonNegativeReals 
#from pyomo.environ import SolverFactory, ConcreteModel

from pyomo.environ import ConcreteModel, AbstractModel, Set


#m = AbstractModel()
m = ConcreteModel()

# Letters set
m.L = Set(initialize=['A','B'])
m.L.pprint()

# Numbers set
m.N = Set(initialize=[1,2,3,4,])
m.N.pprint()

# Mapping numbers to letters set
m.d1 = {'A': [1,2,3], 'B': [3,4]}
m.d2 = [('A',1),('A',2),('A',3),('B',2),('B',3),('B',4),]
m.Z = Set(dimen=2, within=m.L*m.N, initialize=m.d2)
m.Z.pprint()