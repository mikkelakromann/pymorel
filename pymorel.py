from pyomo.environ import Objective, Constraint, Var, Set, Param
from pyomo.environ import Binary, NonNegativeReals 
from pyomo.environ import SolverFactory, ConcreteModel


class PyMorel():
    
    def __init__(self, data_object: object):
        self.data = data_object
        self.model = ConcreteModel()
        self.declare_assign()

    def solve(self):
        """Solve model."""
        self.solver = SolverFactory('glpk')             # 'solver' often named 'opt' in Pyomo docs: https://pyomo.readthedocs.io/en/stable/working_models.html
        self.results = self.solver.solve(self.model)

    def print_debug(self):
        """Print debug information."""
        print(self.results)

    # Read set elements from own data object and return Pyomo Set
    def init_set(self, name_str) -> Set:
        """Return Pyomo set as list using set name."""
        set_elements = self.data.sets[name_str]
        return Set(initialize=set_elements)

    # Read set elements from own data object and return Pyomo Set
    def init_map(self, index_list, name_str) -> Param:
        """Return Pyomo set as list using set name."""
        set_elements = self.data.maps[name_str]
        return Param(*index_list, initialize=set_elements)
        
    # Read data dict from data object and return Pyomo parameter
    def init_par(self, index_list, name_str) -> Param:
        """Return Pyomo parameter as dict using list of indices and parameter name. """
        data_dict = self.data.parameters[name_str]
        return Param(*index_list, initialize=data_dict)        

    def declare_assign(self) -> object:
        """"Read self.data to declare and assign to sets and parameters."""
        m = self.model
        # Declare and assign sets (double assignment a=b=f(x) for easy reading)
        # Single letter lower case indicate index
        e = m.e = self.init_set('e')        # Energy carrier set
        a = m.a = self.init_set('a')        # Areas set
        t = m.t = self.init_set('t')        # Technologies set
        tt = m.tt = self.init_subset('tt')  # Transformation technology subset
        ts = m.ts = self.init_subset('ts')  # Storage technology subset 
        tx = m.tx = self.init_subset('tx')  # Transmission technology subset
        w = m.w = self.init_set('w')        # Weeks (time) set
        h = m.h = self.init_set('h')        # Hours (time) set 

#        m.gfShr = self.init_par([l,g,f,y],'gfShr')

        # Declare variables: Capital V indicates variable 
        # GIh: Energy input effect into transformation technology g by hour & week 
        m.GIh = Var(tgw,w,h, within=NonNegativeReals)
        # GIw: Energy input effect into transformation technology g by week 
        m.GIw = Var(tgh,w, within=NonNegativeReals)
        # GCa: Capacity effect of transformation technology (implicitly annual)
        m.GCa = Var(tg, within=NonNegativeReals)

        # SSh: Storage input effect (energy carrier is mapped to ts) by hour & week
        m.SSh = Var(tsh,w,h, within=NonNegativeReals)
        # SS: Storage input effect (energy carrier is mapped to ts) by hour
        m.SSw = Var(tsw,w, within=NonNegativeReals)
        # SDh: Discharge from storage effect (energy carrier is mapped to ts) by hour & week
        m.SDh = Var(tsh,w,h, within=NonNegativeReals)
        # SDw: Discharge from storage effect (energy carrier is mapped to ts) by week
        m.SDh = Var(tsw,w, within=NonNegativeReals)
        # SV: Stored volume of energy by hour and week
        m.SVh = Var(tsh,w,h, within=NonNegativeReals)
        # SV: Stored volume of energy by week 
        m.SVw = Var(tsw,w, within=NonNegativeReals)
        # SC: Volume Capacity of storage technology (SV < SC)
        m.SC = Var(ts, within=NonNegativeReals)

        # X1 and X2: Transmission effect (areas and energy carrier mapped to tx) by hour & week
        m.X1h = Var(txh,w,h, within=NonNegativeReals)
        m.X2h = Var(txh,w,h, within=NonNegativeReals)
        # X1 and X2: Transmission effect (areas and energy carrier mapped to tx) by week
        m.X1w = Var(txw,w, within=NonNegativeReals)
        m.X2w = Var(txw,w, within=NonNegativeReals)
        # XC: Transmission effect limit (two ways: X1 < XC and X2 < XC)
        m.XC = Var(x, within=NonNegativeReals)
        
        # Objective
        m.obj = Objective(rule=self.R_objective)
        # Constraints: Capital Q indicates constraint, R indicates rule
        m.Q_equilibrium = Constraint(m.e, m.a, m.h, rule=self.Q_equilibrium)
        
    ###########################################################################
    #
    #   OBJECTIVE FUNCTION
    #
    ###########################################################################
    def objective_rule(self,m):
        """Total cost is discouted capex, fopex and vopex."""
        # Capital costs (CAPEX) is tied to investment year V
        cst_capex = { y: sum(m.V[p,v]*m.vCst[p,v] \
            for p in m.p for v in m.v if m.yvMap[y,v]) for y in m.y }
        # Fixed operations costs (FOPEX) is tied to plant existence E
        cst_fopex = { y: sum(m.E[p,y]*m.eCst[p,y,v] \
            for p in m.p for v in m.v if m.yvMap[y,v]) for y in m.y }
        # Variable operating costs is tied to plant treated input T
        cst_vopex = { y: sum(m.T[p,f,y]*m.tCst[p,f,y] \
            for p in m.p for f in m.f ) for y in m.y }
        # Sales revenue is tied to plant treated input T by fraction
        rev_sales = { y: sum(m.T[p,f,y]*m.tRev[p,f,y] \
            for p in m.p for f in m.f ) for y in m.y }
        # Transport costs are tied to flows from generators to plants
        cst_trans = { y: sum(m.F[l,g,p,y]*m.fCst[l,g,p,y] \
            for l in m.l for g in m.g for p in m.p) for y in m.y }
        cst_total = { y: cst_capex[y] + cst_fopex[y] + cst_vopex[y] + \
                       cst_trans[y] + rev_sales[y] for y in m.y }
        return sum( m.yDis[y]*cst_total[y] for y in m.y)
    
    ###########################################################################
    #
    #   MARKET EQUILIBRIUM FOR AREAS
    #
    ###########################################################################

    # Market equilibrium for energy carriers, areas and hours
    def Q_equilibrium(self,m,e,a,h):
        """Constraint to ensure energy equilibrium."""
        # Generation y only if energy carrier is generated inside area
        if m.map_GI_in_ea[e,a]:
            # Supply is mapped from energy-carrier/generation to area
            gen = sum(m.GI[tg,h]*m.eff_GI[e,tg] for tg in m.map_tg_in_ea[e,a] )
        else:
            gen = 0
        # Import if energy carrier has transmission into area
        if m.map_Xx_into_ea[e,a]:            
            # Import is mapped through directional transmission line
            imp = sum(m.X1[tx,h]*m.effX[tx] for tx in m.map_x1_into_ea[e,a]) \
                 +sum(m.X2[tx,h]*m.effX[tx] for tx in m.map_x2_into_ea[e,a]) 
        else:
            imp = 0
        # Export if energy carrier has transmission from area
        if m.map_Xx_from_ea[e,a]:            
            # Export is mapped through directional transmission line
            exp = sum(m.X1[tx,h] for tx in m.map_x1_from_ea[e,a]) \
                 +sum(m.X2[tx,h] for tx in m.map_x2_from_ea[e,a]) 
        else:
            exp = 0
        # Storage only if energy carrier has storage in area 
        if m.map_SS_in_ea[e,a]:
            sto = sum(m.SS[ts,h] for ts in m.map_ts_in_ea[e,a])
        else:
            sto = 0
        # Discharge only if energy carrier has storage in area 
        if m.map_SS_in_ea[e,a]:
            dis = sum(m.SD[ts,h] for ts in m.map_ts_in_ea[e,a])
        else:
            dis = 0


        # Only make constraint if [e,a] combination has supply or demand
        if gen or imp or dis or exp or sto or dem:
            return gen + imp + dis == dem + exp + sto 
        else:
            return Constraint.Skip
    
    def Q_production(self,m,e,g,s,t)
