from pyomo.environ import Objective, Constraint, Var, Set, Param
from pyomo.environ import NonNegativeReals
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

        def get_set(element_list: list) -> object:
            """Create and return Pyomo Set(), provide debugging information if necessary."""
            try:
                s = Set(initialize=element_list)
            except:
                print("Could not initialize Pyomo Set" + str(element_list))
                s = Set()
            return s

        def get_subset(element_list: list, superset: object) -> object:
            """Return Pyomo (sub)Set() with validation towards superset, provide debugging information if necessary."""
            try:
                s = Set(initialize=element_list, within=superset)
            except:
                print("Could not initialize Pyomo Set" + str(element_list) + " with superset "
                      + superset.__name__ + " containing " + str(superset))
                s = Set()
            return s

        # Declare and assign Pyomo sets (where A=self.B=f(X) makes A local scope alias for global scope self.B)
        # Single letter lower case indicate set element,
        # Single letter upper case indicate set (or variable, see variables section)
        sets = self.data.sets           # Alias with local scope
        E = m.E = get_set(sets['E'])    # Energy carrier set
        A = m.A = get_set(sets['A'])    # Areas set
        T = m.T = get_set(sets['T'])    # Technologies set
        W = m.W = get_set(sets['W'])    # Weeks (time) set
        H = m.H = get_set(sets['H'])    # Hours (time) set

        # Subsets: Multi-letter upper case indicate subset of first letter superset
        subsets = self.data.subsets     # Alias with local scope
        # The ener subsets are distinguished by second letter refering to trading frequency
        EH = m.EH = get_subset(subsets['EH'], E)        # Energy carriers traded (H)ourly
        EW = m.EW = get_subset(subsets['EW'], E)        # Energy carriers traded (W)eekly
        EY = m.EY = get_subset(subsets['EY'], E)        # Energy carriers traded (Y)early

        # Tech subsets are distinguished by second letter referring to technology role (T,S,X) or capacity (C)
        # Note: TT, TX and TS are true, mutually exclusive subsets
        TT = m.TT = get_subset(subsets['TT'], T)        # Technologies for (T)ransformation
        TX = m.TX = get_subset(subsets['TX'], T)        # Technologies for e(X)change
        TS = m.TS = get_subset(subsets['TS'], T)        # Technologies for (S)torage
        TC = m.TC = get_subset(subsets['TC'], T)        # Technologies with (C)apacity investment

        TTH = m.TTH = get_subset(subsets['TTH'],TT)     # Technologies for (T)ransformation (H)ourly
        TTW = m.TTW = get_subset(subsets['TTW'],TT)     # Technologies for (T)ransformation (W)eekly
        TTY = m.TTY = get_subset(subsets['TTY'],TT)     # Technologies for (T)ransformation (Y)early
        TXH = m.TXH = get_subset(subsets['TXH'],TX)     # Technologies for (X)transmission (H)ourly
        TXW = m.TXW = get_subset(subsets['TXW'],TX)     # Technologies for (X)transmission (W)eekly
        TXY = m.TXY = get_subset(subsets['TXY'],TX)     # Technologies for (X)transmission (Y)early
        TSH = m.TSH = get_subset(subsets['TSH'],TS)     # Technologies for (S)torage (H)ourly
        TSW = m.TSW = get_subset(subsets['TSW'],TS)     # Technologies for (S)torage (W)eekly
        TSY = m.TSY = get_subset(subsets['TSY'],TS)     # Technologies for (S)torage (Y)early

        # tech/time subsets conditional on ener/area - store cond. subsets in a dict
        EAT = subsets['EAT']
        m.TTH_ea = get_subset(subsets['TTH_ea'],EAT)  # Transformation hourly technologies
        m.TXH_ea = get_subset(subsets['TXH_ea'],EAT)  # Export hourly technologies
        m.TIH_ea = get_subset(subsets['TIH_ea'],EAT)  # Import hourly technologies
        m.TSH_ea = get_subset(subsets['TSH_ea'],EAT)  # Storage hourly technologies
        m.TTW_ea = get_subset(subsets['TTW_ea'],EAT)  # Transformation weekly technologies
        m.TXW_ea = get_subset(subsets['TXW_ea'],EAT)  # Export weekly technologies
        m.TIW_ea = get_subset(subsets['TIW_ea'],EAT)  # Import weekly technologies
        m.TSW_ea = get_subset(subsets['TSW_ea'],EAT)  # Storage weekly technologies
        m.TTY_ea = get_subset(subsets['TTY_ea'],EAT)  # Transformation yearly technologies
        m.TXY_ea = get_subset(subsets['TXY_ea'],EAT)  # Transmission yearly technologies
        m.TIY_ea = get_subset(subsets['TIY_ea'],EAT)  # Transmission yearly technologies
        m.TSY_ea = get_subset(subsets['TSY_ea'],EAT)  # Storage yearly technologies

        ###############################################################################################################
        # Variable declaration and assignment
        ###############################################################################################################

        # Technology capacity additions are annual
        m.C = Var(TC, within=NonNegativeReals)          # Capacity addition for all endognenous investment technologies

        # Hourly transformation, storage and transmission technologies
        m.Th = Var(TTH,W,H, within=NonNegativeReals)    # Energy input effect into transformation
        m.Xh = Var(TXH,W,H, within=NonNegativeReals)    # Transmission effect from 1st to 2nd area
        m.Ih = Var(TXH,W,H, within=NonNegativeReals)    # Transmission effect from 2nd to 1st area
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
        # Parameter declaration and assignment
        ###############################################################################################################

        para_h = self.data.para_h   # Pointer for hourly parameter data structure (dict of dicts)
        para_y = self.data.para_y   # Pointer for yearly parameter data structure (dict of dicts)

        # Parameters potentially varying hourly to be multiplied to or constraining hourly variables
        m.cst_Th = Param(TTH,W,H, initialize=para_h['cst_Th'], default=0)   # Unit variable cost of transformation
        m.cst_Sh = Param(TSH,W,H, initialize=para_h['cst_Sh'], default=0)   # Unit variable cost of storage
        m.cst_Xh = Param(TXH,W,H, initialize=para_h['cst_Xh'], default=0)   # Unit variable cost of transmission

        m.ava_Th = Param(TTH,W,H, initialize=para_h['ava_Th'], default=0)   # Hourly availability of transformation
        m.ava_Xh = Param(TXH,W,H, initialize=para_h['ava_Xh'], default=0)   # Hourly availability of export
        m.ava_Ih = Param(TXH,W,H, initialize=para_h['ava_Ih'], default=0)   # Hourly availability of import
        m.ava_Sh = Param(TSH,W,H, initialize=para_h['ava_Sh'], default=0)   # Hourly availability of storage
        m.ava_Dh = Param(TSH,W,H, initialize=para_h['ava_Dh'], default=0)   # Hourly availability of discharge
        m.ava_Vh = Param(TSH,W,H, initialize=para_h['ava_Vh'], default=0)   # Hourly availability of storage volume

        m.fin_h = Param(E,A,W,H, initialize=para_h['fin_h'], default=0)     # Hourly demand for energy carrier by area

        # Parameters that are fixed across the year, to be multiplied or constraining any variable
        m.eff = Param(E,T, initialize=para_y['eff'], default=0)             # Conversion efficiency ratio output/input
        m.ini_T = Param(TT, initialize=para_y['ini_T'], default=0)          # Initial capacity of transformation tech.
        print(para_y['ini_X'])

        m.ini_X = self.get_para([TX], para_y['ini_X'])                      # Initial capacity of export technology
        m.ini_I = Param(TX, initialize=para_y['ini_I'], default=0)          # Initial capacity of import technology
        m.ini_S = Param(TS, initialize=para_y['ini_S'], default=0)          # Initial capacity of storage technology
        m.ini_D = Param(TS, initialize=para_y['ini_D'], default=0)          # Initial capacity of discharge technology
        m.ini_V = Param(TS, initialize=para_y['ini_V'], default=0)          # Initial capacity of volume technology
        m.max_C = Param(T, initialize=para_y['max_C'], default=0)           # Maximum capacity of any technology
        m.cst_C = Param(T, initialize=para_y['cst_C'], default=0)           # Unit capital cost of technology

        ###############################################################################################################
        # Objective and constraints declaration and assignment
        ###############################################################################################################

        # Objective
        m.obj = Objective(rule=self.rule_objective)
        # Constraints: Capital Q indicates constraint, R indicates rule
        m.Q_equilibrium_h = Constraint(EH,A,W,H, rule=self.rule_equilibrium_h)

    ###################################################################################################################
    #
    #   OBJECTIVE FUNCTION RULE DEFINITION
    #
    ###################################################################################################################

    def rule_objective(self,m):
        """Total cost is discouted capex, fopex and vopex."""
        # Capital costs (CAPEX) is tied to ...
        cst_capex = sum(m.C[t]*m.cst_C[t] for t in m.T)
        # Fixed operations costs (FOPEX) is tied ...
        cst_fopex = 0
        # Variable operating costs is ...
        cst_vopex = 0
        # Fuel costs are tied to input to generation, only exogenous fuel costs
        # TODO: Multiply with weights for weeks x hours
        cst_fuels_h = sum(m.Th[tth,w,h]*m.cst_Th[tth,w,h] for tth in m.TTH for w in m.W for h in m.H)
        cst_store_h = sum(m.Sh[tsh,w,h]*m.cst_Sh[tsh,w,h] for tsh in m.TSH for w in m.W for h in m.H)
        # Total costs is sum of CAPEX, Fixed OPEX, variable OPEX and fuel costs
        cst_total = cst_capex + cst_fopex + cst_vopex + cst_fuels_h + cst_store_h
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
        # TTH_ea is a list of (ener,area,tech) hour transformation technologies
        # (e,a) is under control already, so summing will yield the techs
        tra = sum(m.Th[tth,w,h]*m.eff[e,tth] for tth in m.TTH if (e,a,tth) in m.TTH_ea)

        # Gross import from area a - transmission technologies are directional
        # I is import into the owner area
        # X is export from another owner area turned into import to this destination area
        imp = sum(m.Ih[txh,w,h]*m.eff[e,txh] for (e,a,txh) in m.TXH_ea)\
             +sum(m.Xh[tih,w,h]*m.eff[e,tih] for (e,a,tih) in m.TIH_ea)

        # Gross export from area a - transmission technologies are directional
        # so export for the owner is import to the receiver
        exp = sum(m.Xh[txh,w,h] for (e,a,txh) in m.TXH_ea)\
             +sum(m.Ih[tih,w,h] for (e,a,tih) in m.TIH_ea)

        # Storage and discharge
        sto = sum(m.Sh[tsh,w,h] for (e,a,tsh) in m.TSH_ea)
        dis = sum(m.Dh[tsh,w,h] for (e,a,tsh) in m.TSH_ea)

        # Final consumption (gross)
        fin = m.fin_h[e,a,w,h]

        # Return equilibrium constraint rule
        return tra + dis + imp == fin + sto + exp

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
        return m.Th[tth,w,h] < (m.ini_T[tth] + m.C[tth]) * m.ava_Th[tth,w,h]

    def rule_export_capacity_limit_hourly(self,m,txh,w,h):
        """Constraint for limiting input to hourly transmission technologies (export)."""
        return m.Xh[txh,w,h] < (m.ini_X[txh] + m.C[txh]) * m.ava_Xh[txh,w,h]

    def rule_import_capacity_limit_hourly(self,m,tdh,w,h):
        """Constraint for limiting input to hourly transmission technologies (import)."""
        return m.Ih[tdh,w,h] < (m.ini_I[tdh] + m.C[tdh]) * m.ava_Ih[tdh,w,h]

    def rule_storage_capacity_limit_hourly(self,m,tsh,w,h):
        """Constraint for limiting input to hourly storage sion technologies."""
        return m.Sh[tsh,w,h] < (m.ini_S[tsh] + m.C[tsh]) * m.ava_Sh[tsh,w,h]

    def rule_discharge_capacity_limit_hourly(self,m,tsh,w,h):
        """Constraint for limiting output from hourly storage technologies."""
        return m.Dh[tsh,w,h] < (m.ini_D[tsh] + m.C[tsh]) * m.ava_Dh[tsh,w,h]

    def rule_storage_volume_maxlimit_hourly(self,m,tsh,w,h):
        """Constraint for limiting upper volume of hourly storage technologies."""
        return m.Vh[tsh,w,h] < (m.ini_V[tsh] + m.C[tsh]) * m.ava_Vh[tsh,w,h]

    def rule_storage_volume_minlimit_hourly(self,m,tsh,w,h):
        """Constraint for limiting input to hourly storage technologies."""
        return m.Vh[tsh,w,h] > (m.ini_V[tsh] + m.C[tsh]) * m.ava_Vh[tsh,w,h]

    def rule_new_capacity(self,m,t):
        """Limit new capacity below exogenous choice."""
        return m.C[t] < m.max_C[t]

    ###################################################################################################################
    #
    #   HELPER FUNCTIONS
    #
    ###################################################################################################################

    def solve(self):
        """Solve model."""
        self.solver = SolverFactory('glpk')             # 'solver' often named 'opt' in Pyomo docs: https://pyomo.readthedocs.io/en/stable/working_models.html
        self.results = self.solver.solve(self.model)

    def report(self):
        self.model.TTH.pprint()
        self.model.TTH_ea.pprint()
        self.model.Q_equilibrium_h.pprint()
        print(self.results)

    def print_debug(self):
        """Print debug information."""
        print(self.results)

    def get_para(self, sets: list, data: dict) -> object:
        """Return Pyomo parameter, provide debugging information if fail."""
        print("Mjello!")
        print(sets)
        print(data)
        try:
            p = Param(*sets, initialize=data, default=0)
        except KeyError as error:
            print(error)
            print("Could not initialize set from " + str(data))
            p = None
        return p
