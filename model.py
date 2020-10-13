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
        # Single letter lower case indicate set element, 
        # Single letter upper case indicate set
        E = m.E = Set(initialize=sets['E'])     # Energy carrier set
        A = m.A = Set(initialize=sets['A'])     # Areas set
        T = m.T = Set(initialize=sets['T'])     # Technologies set
        W = m.W = Set(initialize=sets['W'])     # Weeks (time) set
        H = m.H = Set(initialize=sets['H'])     # Hours (time) set 

        # Subsets of energy carriers by trading frequency
        EH = m.EH = Set(initialise=sets['EH'],within=E)     # Energy carriers traded hourly
        EW = m.EW = Set(initialise=sets['EW'],within=E)     # Energy carriers traded weekly
        EA = m.EA = Set(initialise=sets['EA'],within=E)     # Energy carriers traded yearly

        # tech/time subsets of technologies superset
        TC = m.TC = Set(initialize=sets['TC'],within=t)     # Endogenous investment technologies
        TTH = m.TTH = Set(initialize=sets['TTH'],within=T)  # Transformation hourly technologies
        TSH = m.TSH = Set(initialize=sets['TSH'],within=T)  # Storage hourly technologies
        TXH = m.TXH = Set(initialize=sets['TXH'],within=T)  # Transmission hourly technologies
        TTW = m.TTW = Set(initialize=sets['TTW'],within=T)  # Transformation weekly technologies
        TSW = m.TSW = Set(initialize=sets['TSW'],within=T)  # Storage weekly technologies
        TXW = m.TXW = Set(initialize=sets['TXW'],within=T)  # Transmission weekly technologies
        TTA = m.TTA = Set(initialize=sets['TTA'],within=T)  # Transformation annual technologies
        TSA = m.TSA = Set(initialize=sets['TSA'],within=T)  # Storage annual technologies
        TXA = m.TXA = Set(initialize=sets['TXA'],within=T)  # Transmission annual technologies
        
        # tech/time subsets conditional on ener/area - store cond. subsets in a dict
        css = self.data.util.ss
        m.conditionalsubset = {}
        m.conditionalsubset['TTH_ea'] = Set(initialize=ss['TTH_ea'],within=TTH)  # Transformation hourly technologies
        m.conditionalsubset['TSH_ea'] = Set(initialize=ss['TSH_ea'],within=TSH)  # Storage hourly technologies
        m.conditionalsubset['TXH_ea'] = Set(initialize=ss['TXH_ea'],within=TXH)  # Transmission hourly technologies
        m.conditionalsubset['TTH_ea'] = Set(initialize=ss['YYW_ea'],within=TTW)  # Transformation weekly technologies
        m.conditionalsubset['TSH_ea'] = Set(initialize=ss['TSW_ea'],within=TSW)  # Storage weekly technologies
        m.conditionalsubset['TXH_ea'] = Set(initialize=ss['TXW_ea'],within=TXW)  # Transmission weekly technologies
        m.conditionalsubset['TTH_ea'] = Set(initialize=ss['TTA_ea'],within=TTA)  # Transformation annual technologies
        m.conditionalsubset['TSH_ea'] = Set(initialize=ss['TSA_ea'],within=TSA)  # Storage annual technologies
        m.conditionalsubset['TXH_ea'] = Set(initialize=ss['TXA_ea'],within=TXA)  # Transmission annual technologies


        ###############################################################################################################
        # Parameter declaration and assignment
        ###############################################################################################################

        para = self.data.para   # Pointer for parameter data structure (dict of dicts)
        

        ###############################################################################################################
        # Variable declaration and assignment
        ###############################################################################################################

        # Technology capacity additions are annual
        m.C = Var(TC, within=NonNegativeReals)          # Capacity addition for all endognenous investment technologies

        # Hourly transformation, storage and transmission technologies
        m.Th = Var(TTH,W,H, within=NonNegativeReals)    # Energy input effect into transformation 
        m.Xh = Var(TXH,W,H, within=NonNegativeReals)    # Transmission effect from 1st to 2nd area
        m.Ih = Var(TDH,W,H, within=NonNegativeReals)    # Transmission effect from 2nd to 1st area
        m.Sh = Var(TSH,W,H, within=NonNegativeReals)    # Storage input effect into storage  
        m.Dh = Var(TSH,W,H, within=NonNegativeReals)    # Discharge output effect from storage 
        m.Vh = Var(TSH,W,H, within=NonNegativeReals)    # Stored volume of energy 

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
        m.Q_equilibrium_h = Constraint(m.EH, m.A, m.W, m.H, rule=self.rule_equilibrium_h)
        
    ###################################################################################################################
    #
    #   OBJECTIVE FUNCTION RULE DEFINITION
    #
    ###################################################################################################################

    def rule_objective(self,m):
        """Total cost is discouted capex, fopex and vopex."""
        # Capital costs (CAPEX) is tied to ...
        cst_capex = sum(m.C[t]*cst_C[t] for t in m.T)
        # Fixed operations costs (FOPEX) is tied ...
        cst_fopex = 0
        # Variable operating costs is ...
        cst_vopex = 0
        # Fuel costs are tied to input to generation, only exogenous fuel costs
        cst_fuels = sum(m.Th[tth,w,h]*m.cst_Th[tth,w,h] for tth in m.TTH for w in m.W for h in m.H)
        cst_store = sum(m.Sh[tsh,w,h]*m.cst_Sh[tsh,w,h] for tsh in m.TSH for w in m.W for h in m.H)
        # Total costs is sum of CAPEX, Fixed OPEX, variable OPEX and fuel costs
        cst_total = cst_capex + cst_fopex + cst_vopex + cst_fuels
        return cst_total
    
    ###################################################################################################################
    #
    #   MARKET EQUILIBRIUM FOR AREAS RULE DEFINITION
    #   Market equilibrium for energy carriers, areas, weeks and hours
    #   ie  one equation per energy carrier, area and time step
    #
    ###################################################################################################################

    # Trading and exchange is on an energy carrier basis
    def rule_equilibrium_h(self,m,e,a,w,h) -> dict:
        """Constraint to ensure equilibrium for hourly traded energy carriers."""

        # Transformation between energy carriers: eff>0 is output, eff<0 is input
        # For heat pumps, eff needs to be modified to depend on time
        tra = sum(m.Th[tth,w,h]*m.eff[e,tth] for tth in m.conditionalsubset['TTH_ea'][e,a])

        # Gross import from area a - transmission technologies are directional
        # I is import into the owner area 
        # X is export from another owner area turned into import to this destination area
        imp = sum(m.Ih[txh,w,h]*m.eff[e,txh] for txh in m.conditionalsubset['TXH_ea'][e,a])\
             +sum(m.Xh[tih,w,h]*m.eff[e,tih] for tih in m.conditionalsubset['TIH_ea'][e,a])
                  
        # Gross export from area a - transmission technologies are directional
        # so export for the owner is import to the receiver
        exp = sum(m.Xh[txh,w,h] for txh in m.conditionalsubset['TXH_ea'][e,a])\
             +sum(m.Ih[tih,w,h] for tih in m.conditionalsubset['TIH_ea'][e,a]
 
        # Storage and discharge
        sto = sum(m.Sh[tsh,w,h] for tsh in m.conditionalsubset['TSH_ea'][e,a])
        dis = sum(m.Dh[tsh,w,h] for tsh in m.conditionalsubset['TSH_ea'][e,a])

        # Demand
        dem = m.lvl_DH[e,a,w,h]

        # Return equilibrium constraint rule if any
        if tra or exp or imp or sto or dis or dem:
            return tra + dis + imp == dem + sto + exp
        else:
            return Constraint.Skip
    
    ###################################################################################################################
    #
    #   STORAGE RELATIONS: INTERTEMPORAL AND OTHERS RULE DEFINITIONS
    #   Storage is on a technology basis, i.e. one equation per technology and time step
    #   Note: each technology is always connected to exactly one area 
    #
    ###################################################################################################################


    ###################################################################################################################
    #
    #   CAPACITY LIMITS RULE DEFINITIONS
    #
    ###################################################################################################################

    def rule_transformation_capacity_limit_hourly(self,m,tth,w,h):
        """Constraint for limiting input to hourly transformation technologies."""
        return m.Th[tth,w,h] < (m.ini_T[tth] + m.C[tth]) * m.avail_Th[tth,w,h]

    def rule_export_capacity_limit_hourly(self,m,txh,w,h):
        """Constraint for limiting input to hourly transmission technologies (export)."""
        return m.Xh[txh,w,h] < (m.ini_X[txh] + m.C[txh]) * m.avail_Xh[txh,w,h]

    def rule_import_capacity_limit_hourly(self,m,tdh,w,h):
        """Constraint for limiting input to hourly transmission technologies (import)."""
        return m.Ih[tdh,w,h] < (m.ini_I[tdh] + m.C[tdh]) * m.avail_Ih[tdh,w,h]

    def rule_storage_capacity_limit_hourly(self,m,tsh,w,h):
        """Constraint for limiting input to hourly storage sion technologies."""
        return m.Sh[tsh,w,h] < (m.ini_S[tsh] + m.C[tsh]) * m.avail_Sh[tsh,w,h] 

    def rule_discharge_capacity_limit_hourly(self,m,tsh,w,h):
        """Constraint for limiting output from hourly storage technologies."""
        return m.Dh[tsh,w,h] < (m.ini_D[tsh] + m.C[tsh]) * m.avail_Dh[tsh,w,h] 

    def rule_storage_volume_maxlimit_hourly(self,m,tsh,w,h):
        """Constraint for limiting upper volume of hourly storage technologies."""
        return m.Vh[tsh,w,h] < (m.ini_V[tsh] + m.C[tsh]) * m.avail_Vh[tsh,w,h]

    def rule_storage_volume_minlimit_hourly(self,m,tsh,w,h):
        """Constraint for limiting input to hourly storage technologies."""
        return m.Vh[tsh,w,h] > (m.ini_V[tsh] + m.C[tsh]) * m.avail_Vh[tsh,w,h]

    def rule_new_capacity(self,m,t):
        """Limit new capacity below exogenous choice."""
        return m.C[t] < max_C[t]

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

