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
        # Single letter lower case indicate index, single letter upper case indicate set
        E = m.E = Set(initialize=sets['E'])     # Energy carrier set
        A = m.A = Set(initialize=sets['A'])     # Areas set
        T = m.T = Set(initialize=sets['T'])     # Technologies set
        W = m.W = Set(initialize=sets['W'])     # Weeks (time) set
        H = m.H = Set(initialize=sets['H'])     # Hours (time) set 


        EH = m.EH = Set(initialise=sets['EH']
        EW = m.EW = 
        EA = m.EA = 

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
        m.C = Var(TC, within=NonNegativeReals)          # Capacity addition for all endognenous investment technologies

        # Hourly transformation, storage and transmission technologies
        m.Th = Var(TTH,W,H, within=NonNegativeReals)   # Energy input effect into transformation 
        m.Xh = Var(TXH,W,H, within=NonNegativeReals)   # Transmission effect from 1st to 2nd area
        m.Ih = Var(TDH,W,H, within=NonNegativeReals)   # Transmission effect from 2nd to 1st area
        m.Sh = Var(TSH,W,H, within=NonNegativeReals)   # Storage input effect into storage  
        m.Dh = Var(TSH,W,H, within=NonNegativeReals)   # Discharge output effect from storage 
        m.Vh = Var(TSH,W,H, within=NonNegativeReals)   # Stored volume of energy 

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
        cst_capex = 0
        # Fixed operations costs (FOPEX) is tied ...
        cst_fopex = 0
        # Variable operating costs is ...
        cst_vopex = 0
        # Fuel costs are tied to input to generation, only exogenous fuel costs
        cst_fuels = sum(m.Th[tth,w,h]*m.cst_Th[tth,w,h] for tth in m.tth for w in m.w for h in m.h)
        cst_store = sum(m.Sh[tsh,w,h]*m.cst_Sh[tsh,w,h] for tsh in m.tsh for w in m.w for h in m.h)
        # Total costs is sum of CAPEX, Fixed OPEX, variable OPEX and fuel costs
        cst_total = cst_capex + cst_fopex + cst_vopex + cst_fuels
        return cst_total
    
    ###################################################################################################################
    #
    #   MARKET EQUILIBRIUM FOR AREAS RULE DEFINITION
    #
    ###################################################################################################################

    # Market equilibrium for energy carriers, areas, weeks and hours
    def rule_equilibrium_h(self,m,e,a,w,h) -> dict:
        """Constraint to ensure effect equilibrium by hour & week."""

        # Transformation between energy carriers: eff_T>0 is output, eff_T<0 is input
        tra = sum(m.Th[tth,w,h]*m.eff[e,tth] for tth in m.conditionalsubset['tth_ea'][e,a])

        # Gross import from area a - transmission technologies are directional
        # I is import into the owner area 
        # X is export from another owner area turned into import to this destination area
        imp = sum(m.Ih[txh,w,h]*m.eff[e,txh] for txh in m.conditionalsubset['txh_ea'][e,a])\
             +sum(m.Xh[tih,w,h]*m.eff[e,tih] for tih in m.conditionalsubset['tdh_ea'][e,a])
                  
        # Gross export from area a - transmission technologies are directional
        # so export for the owner is import to the receiver
        exp = sum(m.Xh[txh,w,h] for txh in m.conditionalsubset['txh_ea'][e,a])\
             +sum(m.Ih[tih,w,h] for tih in m.conditionalsubset['tdh_ea'][e,a]
 
        # Storage and discharge
        sto = sum(m.Sh[tsh,w,h] for tsh in m.conditionalsubset['tsh_ea'][e,a])
        dis = sum(m.Dh[tsh,w,h] for tsh in m.conditionalsubset['tsh_ea'][e,a])

        # Demand
        dem = m.lvl_D[e,a,w,h]

        # Return equilibrium constraint rule if any
        if tra or exp or imp or sto or dis or dem:
            return tra + dis + imp == dem + sto + exp
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

    def rule_transformation_capacity_limit_hourly(self,m,tth,w,h):
        """Constraint for limiting input to hourly transformation technologies."""
        return m.Th[tth,w,h] < m.max_T[tth] + m.C[tth]

    def rule_export_capacity_limit_hourly(self,m,txh,w,h):
        """Constraint for limiting input to hourly transmission technologies (export)."""
        return m.Xh[txh,w,h] < m.max_X[txh] + m.C[txh]

    def rule_import_capacity_limit_hourly(self,m,tdh,w,h):
        """Constraint for limiting input to hourly transmission technologies (import)."""
        return m.Ih[tdh,w,h] < m.max_X[tdh] + m.C[tdh]

    def rule_storage_capacity_limit_hourly(self,m,tsh,w,h):
        """Constraint for limiting input to hourly transmission technologies (import)."""
        return m.Sh[tsh,w,h] < m.max_S[tsh] + m.C[tsh] if tsh in m.TC

    def rule_discharge_capacity_limit_hourly(self,m,tsh,w,h):
        """Constraint for limiting input to hourly transmission technologies (import)."""
        return m.Dh[tsh,w,h] < m.max_D[tsh] + m.C[tsh] if tsh in m.TC

    def rule_storage_volume_maxlimit_hourly(self,m,tsh,w,h):
        """Constraint for limiting input to hourly transmission technologies (import)."""
        return m.Vh[tsh,w,h] < m.max_V[tsh] + m.C[tsh] if tsh in m.TC

    def rule_storage_volume_minlimit_hourly(self,m,tsh,w,h):
        """Constraint for limiting input to hourly transmission technologies (import)."""
        return m.Vh[tsh,w,h] > m.min_V[tsh] + m.C[tsh] if tsh in m.TC

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

