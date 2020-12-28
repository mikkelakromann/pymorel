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
        R = m.R = get_set(sets['R'])    # Regions set
        A = m.A = get_set(sets['A'])    # Assets set
        W = m.W = get_set(sets['W'])    # Weeks (tfrq) set
        H = m.H = get_set(sets['H'])    # Hours (tfrq) set

        # Subsets: Multi-letter upper case indicate subset of first letter superset
        subsets = self.data.subsets     # Alias with local scope
        # The ener subsets are distinguished by second letter refering to trading frequency
        EH = m.EH = get_subset(subsets['EH'], E)        # Energy carriers traded (H)ourly
        EW = m.EW = get_subset(subsets['EW'], E)        # Energy carriers traded (W)eekly
        EY = m.EY = get_subset(subsets['EY'], E)        # Energy carriers traded (Y)early

        # Tech subsets are distinguished by second letter referring to asset role (T,S,X) or capacity (C)
        # Note: AP, AT, AX and AS are true, mutually exclusive subsets of assets with differnt roles
        AP = m.AP = get_subset(subsets['AP'], A)        # Assets for (P)rimary production
        AT = m.AT = get_subset(subsets['AT'], A)        # Assets for (T)ransformation
        AX = m.AX = get_subset(subsets['AX'], A)        # Assets for e(X)change
        AS = m.AS = get_subset(subsets['AS'], A)        # Assets for (S)torage
        AC = m.AC = get_subset(subsets['AC'], A)        # Assets with (C)apacity investment

        APH = m.APH = get_subset(subsets['APH'],AP)     # Assets for (P)rimary production (H)ourly
        APW = m.APW = get_subset(subsets['APW'],AP)     # Assets for (P)rimary production (W)weekly
        APY = m.APY = get_subset(subsets['APY'],AP)     # Assets for (P)rimary production (Y)early
        ATH = m.ATH = get_subset(subsets['ATH'],AT)     # Assets for (T)ransformation (H)ourly
        ATW = m.ATW = get_subset(subsets['ATW'],AT)     # Assets for (T)ransformation (W)eekly
        ATY = m.ATY = get_subset(subsets['ATY'],AT)     # Assets for (T)ransformation (Y)early
        AXH = m.AXH = get_subset(subsets['AXH'],AX)     # Assets for (X)transmission (H)ourly
        AXW = m.AXW = get_subset(subsets['AXW'],AX)     # Assets for (X)transmission (W)eekly
        AXY = m.AXY = get_subset(subsets['AXY'],AX)     # Assets for (X)transmission (Y)early
        ASH = m.ASH = get_subset(subsets['ASH'],AS)     # Assets for (S)torage (H)ourly
        ASW = m.ASW = get_subset(subsets['ASW'],AS)     # Assets for (S)torage (W)eekly
        ASY = m.ASY = get_subset(subsets['ASY'],AS)     # Assets for (S)torage (Y)early

        # asst/tfrq subsets conditional on ener/region - store cond. subsets in a dict
        ERA = subsets['ERA']
        m.APH_er = get_subset(subsets['APH_er'],ERA)  # Primary production hourly assets
        m.APW_er = get_subset(subsets['APW_er'],ERA)  # Primary production weekly assets
        m.APY_er = get_subset(subsets['APY_er'],ERA)  # Primary production yearly assets
        m.ATH_er = get_subset(subsets['ATH_er'],ERA)  # Transformation hourly assets
        m.ATW_er = get_subset(subsets['ATW_er'],ERA)  # Transformation weekly assets
        m.ATY_er = get_subset(subsets['ATY_er'],ERA)  # Transformation yearly assets
        m.AXH_er = get_subset(subsets['AXH_er'],ERA)  # Export hourly assets
        m.AXW_er = get_subset(subsets['AXW_er'],ERA)  # Export weekly assets
        m.AXY_er = get_subset(subsets['AXY_er'],ERA)  # Transmission yearly assets
        m.AIH_er = get_subset(subsets['AIH_er'],ERA)  # Import hourly assets
        m.AIW_er = get_subset(subsets['AIW_er'],ERA)  # Import weekly assets
        m.AIY_er = get_subset(subsets['AIY_er'],ERA)  # Transmission yearly assets
        m.ASH_er = get_subset(subsets['ASH_er'],ERA)  # Storage hourly assets
        m.ASW_er = get_subset(subsets['ASW_er'],ERA)  # Storage weekly assets
        m.ASY_er = get_subset(subsets['ASY_er'],ERA)  # Storage yearly assets

        ###############################################################################################################
        # Variable declaration and assignment
        ###############################################################################################################

        # Asset capacity additions are annual
        m.C = Var(AC, within=NonNegativeReals)          # Capacity addition for all endognenous investment assets

        # Hourly transformation, storage and transmission assets
        m.Ph = Var(APH,W,H, within=NonNegativeReals)    # Energy input effect into transformation
        m.Th = Var(ATH,W,H, within=NonNegativeReals)    # Energy input effect into transformation
        m.Xh = Var(AXH,W,H, within=NonNegativeReals)    # Transmission effect from 1st to 2nd region
        m.Ih = Var(AXH,W,H, within=NonNegativeReals)    # Transmission effect from 2nd to 1st region
        m.Sh = Var(ASH,W,H, within=NonNegativeReals)    # Storage input effect into storage
        m.Dh = Var(ASH,W,H, within=NonNegativeReals)    # Discharge output effect from storage
        m.Vh = Var(ASH,W,H, within=NonNegativeReals)    # Stored volume of energy

        # Weekly transformation, storage and transmission assets
        #m.TIw = Var(ttw,w, within=NonNegativeReals)    # Energy input effect into transformation
        #m.SSw = Var(tsw,w, within=NonNegativeReals)    # Storage input effect into storage
        #m.SDw = Var(tsw,w, within=NonNegativeReals)    # Discharge output effect from storage
        #m.SVw = Var(tsw,w, within=NonNegativeReals)    # Stored volume of energy by week
        #m.X1w = Var(txw,w, within=NonNegativeReals)    # Transmission effect from 1st to 2nd region
        #m.X2w = Var(txw,w, within=NonNegativeReals)    # Transmission effect from 2nd to 1st region

        ###############################################################################################################
        # Parameter declaration and assignment
        ###############################################################################################################

        para_h = self.data.para_h   # Pointer for hourly parameter data structure (dict of dicts)
        para_y = self.data.para_y   # Pointer for yearly parameter data structure (dict of dicts)

        # Parameters potentially varying hourly to be multiplied to or constraining hourly variables
        m.cst_Ph = Param(APH,W,H, initialize=para_h['cst_Ph'], default=0)   # Unit variable cost of primary production
        m.cst_Th = Param(ATH,W,H, initialize=para_h['cst_Th'], default=0)   # Unit variable cost of transformation
        m.cst_Sh = Param(ASH,W,H, initialize=para_h['cst_Sh'], default=0)   # Unit variable cost of storage
        m.cst_Xh = Param(AXH,W,H, initialize=para_h['cst_Xh'], default=0)   # Unit variable cost of transmission
        m.ava_Th = Param(ATH,W,H, initialize=para_h['ava_Th'], default=0)   # Hourly availability of transformation
        m.ava_Xh = Param(AXH,W,H, initialize=para_h['ava_Xh'], default=0)   # Hourly availability of export
        m.ava_Ih = Param(AXH,W,H, initialize=para_h['ava_Ih'], default=0)   # Hourly availability of import
        m.ava_Sh = Param(ASH,W,H, initialize=para_h['ava_Sh'], default=0)   # Hourly availability of storage
        m.ava_Dh = Param(ASH,W,H, initialize=para_h['ava_Dh'], default=0)   # Hourly availability of discharge
        m.ava_Vh = Param(ASH,W,H, initialize=para_h['ava_Vh'], default=0)   # Hourly availability of storage volume

        m.fin_h = Param(E,R,W,H, initialize=para_h['fin_h'], default=0)     # Hourly demand for energy carrier by region

        # Parameters that are fixed across the year, to be multiplied or constraining any variable
        m.eff = Param(E,A, initialize=para_y['eff'], default=0)             # Conversion efficiency ratio output/input
        m.ini_T = Param(AT, initialize=para_y['ini_T'], default=0)          # Initial capacity of transformation asst.
        print(para_y['ini_X'])

        m.ini_X = self.get_para([AX], para_y['ini_X'])                      # Initial capacity of export asset
        m.ini_I = Param(AX, initialize=para_y['ini_I'], default=0)          # Initial capacity of import asset
        m.ini_S = Param(AS, initialize=para_y['ini_S'], default=0)          # Initial capacity of storage asset
        m.ini_D = Param(AS, initialize=para_y['ini_D'], default=0)          # Initial capacity of discharge asset
        m.ini_V = Param(AS, initialize=para_y['ini_V'], default=0)          # Initial capacity of volume asset
        m.max_C = Param(A, initialize=para_y['max_C'], default=0)           # Maximum capacity of any asset
        m.cst_C = Param(A, initialize=para_y['cst_C'], default=0)           # Unit capital cost of asset

        ###############################################################################################################
        # Objective and constraints declaration and assignment
        ###############################################################################################################

        # Objective
        m.obj = Objective(rule=self.rule_objective)
        # Constraints: Capital Q indicates constraint, R indicates rule
        m.Q_equilibrium_h = Constraint(EH,R,W,H, rule=self.rule_equilibrium_h)

    ###################################################################################################################
    #
    #   OBJECTIVE FUNCTION RULE DEFINITION
    #
    ###################################################################################################################

    def rule_objective(self,m):
        """Total cost is discouted capex, fopex and vopex."""
        # Capital costs (CAPEX) is tied to ...
        cst_capex = sum(m.C[a]*m.cst_C[a] for a in m.A)
        # Fixed operations costs (FOPEX) is tied ...
        cst_fopex = 0
        # Variable operating costs is ...
        cst_vopex = 0
        # Fuel costs are tied to input to generation, only exogenous fuel costs
        # TODO: Multiply with weights for weeks x hours
        cst_prim_h = sum(m.Ph[aph,w,h]*m.cst_Ph[aph,w,h] for aph in m.APH for w in m.W for h in m.H)
        cst_tfrm_h = sum(m.Th[ath,w,h]*m.cst_Th[ath,w,h] for ath in m.ATH for w in m.W for h in m.H)
        cst_stor_h = sum(m.Sh[ash,w,h]*m.cst_Sh[ash,w,h] for ash in m.ASH for w in m.W for h in m.H)
        # Total costs is sum of CAPEX, Fixed OPEX, variable OPEX and fuel costs
        cst_total = cst_capex + cst_fopex + cst_vopex + cst_prim_h + cst_tfrm_h + cst_stor_h
        return cst_total

    ###################################################################################################################
    #
    #   MARKET EQUILIBRIUM FOR REGIONS RULE DEFINITION
    #   Market equilibrium for energy carriers, regions, weeks and hours
    #   ie one equation per energy carrier, region and trading frequency
    #
    ###################################################################################################################

    # Trading and exchange is on an energy carrier basis
    def rule_equilibrium_h(self,m,e,r,w,h) -> dict:
        """Constraint to ensure equilibrium for hourly traded energy carriers."""

        # Primary energy production
        pri = sum(m.Ph[aph,w,h]*m.eff[e,aph] for aph in m.APH if (e,r,aph) in m.APH_er)

        # Transformation between energy carriers: eff>0 is output, eff<0 is input
        # For heat pumps, eff needs to be modified to depend on hour and week
        # TTH_ea is a list of (ener,region,asst) hour transformation assets
        # (e,r) is under control already, so summing will yield the assts
        tra = sum(m.Th[ath,w,h]*m.eff[e,ath] for ath in m.ATH if (e,r,ath) in m.ATH_er)

        # Gross import from region a - transmission assets are directional
        # I is import into the owner region
        # X is export from another owner region turned into import to this destination region
        imp = sum(m.Ih[axh,w,h]*m.eff[e,axh] for axh in m.AXH if (e,r,axh) in m.AXH_er)\
             +sum(m.Xh[aih,w,h]*m.eff[e,aih] for aih in m.AXH if (e,r,aih) in m.AIH_er)

        # Gross export from region a - transmission assets are directional
        # so export for the owner is import to the receiver
        exp = sum(m.Xh[axh,w,h] for axh in m.AXH if (e,r,axh) in m.AXH_er)\
             +sum(m.Ih[aih,w,h] for aih in m.AXH if (e,r,aih) in m.AIH_er)

        # Storage and discharge
        sto = sum(m.Sh[ash,w,h] for ash in m.ASH if (e,r,ash) in m.ASH_er)
        dis = sum(m.Dh[ash,w,h] for ash in m.ASH if (e,r,ash) in m.ASH_er)

        # Final consumption (gross)
        fin = m.fin_h[e,r,w,h]

        # Return equilibrium constraint rule
        return pri + tra + dis + imp == fin + sto + exp

    ###################################################################################################################
    #
    #   STORAGE RELATIONS: INTERTEMPORAL AND OTHERS RULE DEFINITIONS
    #   Storage is on a asset basis, i.e. one equation per asset and trading frequency step
    #   Note: each asset is always connected to exactly one region
    #
    ###################################################################################################################

    ###################################################################################################################
    #
    #   CAPACITY LIMITS RULE DEFINITIONS
    #
    ###################################################################################################################

    def rule_transformation_capacity_limit_hourly(self,m,ath,w,h):
        """Constraint for limiting input to hourly transformation assets."""
        return m.Th[ath,w,h] < (m.ini_T[ath] + m.C[ath]) * m.ava_Th[ath,w,h]

    def rule_export_capacity_limit_hourly(self,m,axh,w,h):
        """Constraint for limiting input to hourly transmission assets (export)."""
        return m.Xh[axh,w,h] < (m.ini_X[axh] + m.C[axh]) * m.ava_Xh[axh,w,h]

    def rule_import_capacity_limit_hourly(self,m,aih,w,h):
        """Constraint for limiting input to hourly transmission assets (import)."""
        return m.Ih[aih,w,h] < (m.ini_I[aih] + m.C[aih]) * m.ava_Ih[aih,w,h]

    def rule_storage_capacity_limit_hourly(self,m,ash,w,h):
        """Constraint for limiting input to hourly storage sion assets."""
        return m.Sh[ash,w,h] < (m.ini_S[ash] + m.C[ash]) * m.ava_Sh[ash,w,h]

    def rule_discharge_capacity_limit_hourly(self,m,ash,w,h):
        """Constraint for limiting output from hourly storage assets."""
        return m.Dh[ash,w,h] < (m.ini_D[ash] + m.C[ash]) * m.ava_Dh[ash,w,h]

    def rule_storage_volume_maxlimit_hourly(self,m,ash,w,h):
        """Constraint for limiting upper volume of hourly storage assets."""
        return m.Vh[ash,w,h] < (m.ini_V[ash] + m.C[ash]) * m.ava_Vh[ash,w,h]

    def rule_storage_volume_minlimit_hourly(self,m,ash,w,h):
        """Constraint for limiting input to hourly storage assets."""
        return m.Vh[ash,w,h] > (m.ini_V[ash] + m.C[ash]) * m.ava_Vh[ash,w,h]

    def rule_new_capacity(self,m,a):
        """Limit new capacity below exogenous choice."""
        return m.C[a] < m.max_C[a]

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
        self.model.ATH.pprint()
        self.model.ATH_er.pprint()
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
