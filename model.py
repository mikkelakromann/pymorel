from pyomo.environ import Objective, Constraint, Var, Set, Param
from pyomo.environ import Binary, NonNegativeReals 
from pyomo.environ import SolverFactory, ConcreteModel


class PyMorelModel():
    
    def __init__(self, data_object: object):
        self.data = data_object
        self.model = ConcreteModel()
        self.declare_assign()

    ###################################################################################################################
    #
    #   DECLARATION AND ASSIGNMENT OF SETS, PARAMETERS AND EQUATIONS
    #
    ###################################################################################################################

    def declare_assign(self) -> object:
        """"Read self.data to declare and assign to sets and parameters."""
        m = self.model          # Pointer for model object
        
        ###############################################################################################################
        # Set declaration and assignment
        ###############################################################################################################
        
        sets = self.data.sets   # Pointer for set data structure (dict of lists)
        
        # Declare and assign sets (double assignment a=b=f(x) for easy reading)
        # Single letter lower case indicate index
        e = m.e = Set(initialize=sets['e'])     # Energy carrier set
        a = m.a = Set(initialize=sets['a'])     # Areas set
        t = m.t = Set(initialize=sets['t'])     # Technologies set
        w = m.w = Set(initialize=sets['w'])     # Weeks (time) set
        h = m.h = Set(initialize=sets['h'])     # Hours (time) set 

        # Subsets of technologies superset
        tc = m.tc = Set(initialize=sets['tc'],within=t)     # Endogenous investment technologies
        tth = m.tth = Set(initialize=sets['tth'],within=t)  # Transformation hourly technologies
        
        tsh = m.tsh = Set(initialize=sets['tsh'],within=t)  # Storage hourly technologies
        txh = m.txh = Set(initialize=sets['txh'],within=t)  # Transmission hourly technologies
        
        # Subset dicts for quicker for .. in interations in constraint rules
        self.set_conditionalset_dict(self.data.conditionalsets)
        
        cs = self.conditionalsubset('tth_in_ea',('ele','dk0'))
        print("Printing type ...")
        print(cs.type())
        print("PPrinting Pyomo Set ...")
        print(cs.pprint())
        print(len(cs))
        print("Done printing ...")
        print("")
        

        ###############################################################################################################
        # Parameter declaration and assignment
        ###############################################################################################################

        para = self.data.para   # Pointer for parameter data structure (dict of dicts)
        
        # m.cst_TIh = Param(t,w,h,initialize=para['cst_TIh'])       # Unit cost of energy input and variable cost 
        # m.max_TIh = Param(t,w,h,initialize=para['max_TIh'])       # Maximum energy input into transformation  
        # m.eff_TIe = Param(e,t,initialize=para['eff_TIe'])         # Transformation efficiency: energy carrier/input
        # m.eff_X = Param(t,initialize=para['eff_X'])               # Efficiency of transmission connection
        # m.max_X1h = Param(t,w,h, initialize=para['max_X1h'])      # Maximum capacity of transmission 1st way    
        # m.max_X2h = Param(t,w,h, initialize=para['max_X2h'])      # Maximum capacity of transmission 2nd way   
        # m.lvl_DEh = Param(e,a,w,h, initialize=para['lvl_DEh'])    # Demand of energy carrier in area by week and hour
        m.cst_TIh = para['cst_TIh']     # Unit cost of energy input and variable cost 
        m.max_TIh = para['max_TIh']     # Maximum energy input into transformation  
        m.eff_TIe = para['eff_TIe']     # Transformation efficiency: energy carrier/input
        m.eff_X = para['eff_X']         # Efficiency of transmission connection
        m.max_X1h = para['max_X1h']     # Maximum capacity of transmission 1st way    
        m.max_X2h = para['max_X2h']     # Maximum capacity of transmission 2nd way   
        m.lvl_DEh = para['lvl_DEh']     # Demand of energy carrier in area by week and hour

        ###############################################################################################################
        # Variable declaration and assignment
        ###############################################################################################################

        # Technology capacity additions are annual
        m.C = Var(tc, within=NonNegativeReals)          # Capacity addition for all endognenous investment technologies

        # Hourly transformation, storage and transmission technologies
        m.TIh = Var(tth,w,h, within=NonNegativeReals)   # Energy input effect into transformation 
        m.SSh = Var(tsh,w,h, within=NonNegativeReals)   # Storage input effect into storage  
        m.SDh = Var(tsh,w,h, within=NonNegativeReals)   # Discharge output effect from storage 
        m.SVh = Var(tsh,w,h, within=NonNegativeReals)   # Stored volume of energy 
        m.X1h = Var(txh,w,h, within=NonNegativeReals)   # Transmission effect from 1st to 2nd area
        m.X2h = Var(txh,w,h, within=NonNegativeReals)   # Transmission effect from 2nd to 1st area

        # Weekly transformation, storage and transmission technologies
        #m.TIw = Var(ttw,w, within=NonNegativeReals)    # Energy input effect into transformation  
        #m.SSw = Var(tsw,w, within=NonNegativeReals)    # Storage input effect into storage
        #m.SDw = Var(tsw,w, within=NonNegativeReals)    # Discharge output effect from storage 
        #m.SVw = Var(tsw,w, within=NonNegativeReals)    # Stored volume of energy by week 
        #m.X1w = Var(txw,w, within=NonNegativeReals)    # Transmission effect from 1st to 2nd area
        #m.X2w = Var(txw,w, within=NonNegativeReals)    # Transmission effect from 2nd to 1st area

        ###############################################################################################################
        # Objective and constraints declaration and assignment
        ###############################################################################################################

        # Objective
        m.obj = Objective(rule=self.rule_objective)
        # Constraints: Capital Q indicates constraint, R indicates rule
        m.Q_equilibrium_wh = Constraint(m.e, m.a, m.w, m.h, rule=self.rule_equilibrium_wh)
        
    ###################################################################################################################
    #
    #   OBJECTIVE FUNCTION RULE DEFINITION
    #
    ###################################################################################################################

    def rule_objective(self,m):
        """Total cost is discouted capex, fopex and vopex."""
        # Capital costs (CAPEX) is tied to ...
        cst_capex = 0
        # Fixed operations costs (FOPEX) is tied ...
        cst_fopex = 0
        # Variable operating costs is ...
        cst_vopex = 0
        # Fuel costs are tied to input to generation, only exogenous fuel costs
        cst_fuels = sum(m.TIh[tth,w,h]*m.cst_TIh[tth,w,h] for tth in m.tth for w in m.w for h in m.h)
        # Total costs is sum of CAPEX, Fixed OPEX, variable OPEX and fuel costs
        cst_total = cst_capex + cst_fopex + cst_vopex + cst_fuels
        return cst_total
    
    ###################################################################################################################
    #
    #   MARKET EQUILIBRIUM FOR AREAS RULE DEFINITION
    #
    ###################################################################################################################

    # Market equilibrium for energy carriers, areas, weeks and hours
    def rule_equilibrium_wh(self,m,e,a,w,h) -> dict:
        """Constraint to ensure effect equilibrium by hour & week."""
        # Only some energy carriers are traded on hourly basis, skip if not
        if not self.selector('e_is_hourly',(e)):
            return Constraint.Skip
        # Transformation only if energy carrier is generated inside area
        if self.selector('TIh_in_ea',(e,a)):
            # Supply is mapped from energy carrier/generation to area
#            tra = sum(m.TIh[tth,w,h]*m.eff_TO[e,tth] for tth in self.conditionalsubset('tth_in_ea',(e,a)))
            tra = sum(m.TIh[tth,w,h]*m.eff_TO[e,tth] for tth in self.tth if tth in self.conditionalsets['tth_in_ea'][e,a]
        else:
            tra = 0
        # Import if energy carrier has transmission into area
        if self.selector('XXh_into_ea',(e,a)):            
            # Import is mapped through directional transmission line
            imp = sum(m.X1[txh,w,h]*m.eff_X[txh] for txh in self.conditionalsubset('x1_into_ea',(e,a))) \
                 +sum(m.X2[txh,w,h]*m.eff_X[txh] for txh in self.conditionalsubset('x2_into_ea',(e,a))) 
        else:
            imp = 0
        # Export if energy carrier has transmission from area
        if self.selector('XXh_from_ea',(e,a)):            
            # Export is mapped through directional transmission line
            exp = sum(m.X1[txh,w,h] for txh in self.conditionalsubset('x1_from_ea',(e,a))) \
                 +sum(m.X2[txh,w,h] for txh in self.conditionalsubset('x2_from_ea',(e,a))) 
        else:
            exp = 0
        # Storage only if energy carrier has storage in area 
        if self.selector('SS_in_ea',(e,a)):
            sto = sum(m.SS[tsh,w,h] for tsh in self.conditionalsubset('tsh_in_ea'(e,a)))
        else:
            sto = 0
        # Discharge only if energy carrier has storage in area 
        if self.selector('SS_in_ea',(e,a)):
            dis = sum(m.SD[tsh,w,h] for tsh in self.conditionalsubset('tsh_in_ea'(e,a)))
        else:
            dis = 0
        # Demand
        if self.selector('DE_in_ea', (e,a)):
            dem = m.lvl_DEh[e,a,w,h]
        else:
            dem = 0
#       inp = sum(m.TIh[tth,w,h]*m.shr_TI[e,tth] for tth in m.tth if self.conditionalsubset('tth_in_ea',tth,(e,a)))
        # Only make constraint if [e,a] combination has supply or demand
        if tra or imp or dis or exp or sto or dem:
            return tra + imp + dis == dem + exp + sto 
        else:
            return Constraint.Skip
    
    ###################################################################################################################
    #
    #   STORAGE RELATIONS: INTERTEMPORAL AND OTHERS RULE DEFINITIONS
    #
    ###################################################################################################################


    ###################################################################################################################
    #
    #   CAPACITY LIMITS RULE DEFINITIONS
    #
    ###################################################################################################################

    def generation_capacity_limit_hourly(self,m,tth,w,h):
        """Constraint for limiting input to hourly generation technologies."""
        return m.TIh[tth,w,h] < m.max_TIh[tth,w,h] + m.C[tth]

    def transmission1_capacity_limit_hourly(self,m,txh,w,h):
        """Constraint for limiting input to hourly transmission technologies."""
        return m.X1h[txh,w,h] < m.Xxh_max[txh,w,h] + m.C[txh]

    def transmission2_capacity_limit_hourly(self,m,txh,w,h):
        """Constraint for limiting input to hourly transmission technologies."""
        return m.X2h[txh,w,h] < m.Xxh_max[txh,w,h] + m.C[txh]

    ###################################################################################################################
    #
    #   HELPER FUNCTIONS
    #
    ###################################################################################################################

    def solve(self):
        """Solve model."""
        self.solver = SolverFactory('glpk')             # 'solver' often named 'opt' in Pyomo docs: https://pyomo.readthedocs.io/en/stable/working_models.html
        self.results = self.solver.solve(self.model)

    def print_debug(self):
        """Print debug information."""
        print(self.results)

    def selector(self, selector_name: str, indices: set) -> bool:
        """Selector for inclusion or exclusion of expression by set indexer."""
        try:
            return self.data.selector_dict[selector_name][indices]
        except: 
            print("No selector " + selector_name + " for index " + str(indices))
            return False
    
    def conditionalsubset(self, csubset_name: str, key, indices: set) -> object:
        """Returns Pyomo subset conditional to index."""
        cset_dict = getattr(self,'csubset_' + csubset_name)
        return key in cset_dict[indices]
#        return getattr(self,'csubset_' + csubset_name + "_" + str(indices), Set())
       
    def set_conditionalset_dict(self, cs_data):
        """Setup dict for conditionalsubsets()"""
        # cs_data is a dict of dicts
        for cs_name in cs_data.keys():
            cs_dict = cs_data[cs_name]
            print(cs_name + str(cs_dict))
            for indice in cs_dict.keys():
                subset_name = "csubset_" + cs_name + "_" + str(indice)
                print(subset_name + str(cs_dict[indice]))
                if cs_dict[indice] == []:
                    setattr(self.model,subset_name,Set())
                else:
                    setattr(self.model,subset_name,Set(initialize=cs_dict[indice]))

