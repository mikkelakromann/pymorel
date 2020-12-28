import pandas


class PyMorelInputData():
    """Class for holding input and output data to PyMorelModel"""

    def load_data_from_dict(self,dict_data):
        """Sets input data directly from hard coded dict (e.g. simple testing purposes)."""
        self.inputdata = dict_data
        self.declare_assign()

    def load_data_from_xls(self,xls_file_name):
        """Sets input data from Excel sheet by file name."""
        return None

    def declare_assign(self):
        """Set Pyomo Set() and Param() from given input data"""
        self.set_dataframes()
        self.set_sets()
        self.set_para_hourly()
        self.set_para_yearly()

    def set_dataframes(self):
        """Loads input data into internal dataframes, clean and set the main sets."""
        # Get data and put it into dataframes
        self.a = pandas.DataFrame(self.inputdata['a_data'])         # Asset data
        self.ae = pandas.DataFrame(self.inputdata['ae_data'])       # Technonology x energy carrier data
        self.ay = pandas.DataFrame(self.inputdata['ay_data'])       # Asset x year data

        self.h = pandas.DataFrame(self.inputdata['h_data'])         # Hourly data
        self.w = pandas.DataFrame(self.inputdata['w_data'])         # Weekly data
        self.wh = pandas.DataFrame(self.inputdata['wh_data'])       # Weekly x hourly data

        self.r = pandas.DataFrame(self.inputdata['r_data'])         # Region data
        self.e = pandas.DataFrame(self.inputdata['e_data'])         # Energy carrier data
        self.er = pandas.DataFrame(self.inputdata['er_data'])       # Energy carrier x region data

        # Clean out assets that are not relevant to the year or have zero endo & exo capacity limit
        self.ay[(self.ay.year == 'y2020') & ((self.ay.iniC > 0) | (self.ay.maxC > 0))]
        self.a = pandas.merge(self.a,self.ay['asst'], on='asst')    # merge will drop t rows that have no tech in ty
        self.ae = pandas.merge(self.ae,self.ay['asst'], on='asst')  # merge will drop te rows that have no tech in ty
        # TODO: Clean t for regions not in a
        # TODO: Clean te for eners not in e

    def set_sets(self):
        """Loads input data into internal dataframes, clean and set the main sets."""
        # Save the main sets in a dict of lists, e.g.
        # { 'E': ['elec','dhea', 'ngas'], 'A': ['dk0','no0','de0'], }
        self.sets = {
            'E':  self.e['ener'].to_list(),                          # Energy carriers
            'R':  self.r['regn'].to_list(),                          # Regions
            'A':  self.a['asst'].to_list(),                          # All active assets
            'W':  self.w['week'].to_list(),                          # Weeks
            'H':  self.h['hour'].to_list(),                          # Hours
        }

        # Merge asset role and trading frequency onto te in order to compute subsets of assets
        aee = pandas.merge(self.ae,self.e[['ener','tfrq']], on='ener')
        aee = pandas.merge(aee,self.a, on='asst')
        # Create ener,region,tech tuple-keys e.g. ('elec','dk0','ccgt') in the dataframe for later use
        aee['key_era'] = aee[['ener','regn','asst']].apply(tuple,axis=1)

        # Copy all transmission assets in order to put the import flows
        # into the TI*_ea subsets.
        # Now, dest becomes the origin region of the export
        dst = aee[aee.role == 'trms']
        # The dest tuple key use dest instead of region
        dst['key_era'] = dst[['ener','dest','asst']].apply(tuple,axis=1)
        # Save the main simple subsets in a dict of lists { 'TC': }
        self.subsets = {
            # Assets that can be invested in
            'AC': self.ay['asst'][self.ay.maxC > 0].to_list(),
            # Asset subsets by role [primary, transformation, transmission & storage]
            'AP':  self.a['asst'][self.a.role == 'prim'].to_list(),
            'AT':  self.a['asst'][self.a.role == 'tfrm'].to_list(),
            'AX':  self.a['asst'][self.a.role == 'trms'].to_list(),
            'AS':  self.a['asst'][self.a.role == 'stor'].to_list(),
            # Energy carrier subsets by trading frequency
            'EH':  self.e['ener'][self.e.tfrq == 'hourly'].to_list(),
            'EW':  self.e['ener'][self.e.tfrq == 'weekly'].to_list(),
            'EY':  self.e['ener'][self.e.tfrq == 'yearly'].to_list(),
            # Primary production assets by trading frequency
            'APH': aee['asst'][(aee.role == 'prim') & (aee.tfrq == 'hourly')].to_list(),
            'APW': aee['asst'][(aee.role == 'prim') & (aee.tfrq == 'weekly')].to_list(),
            'APY': aee['asst'][(aee.role == 'prim') & (aee.tfrq == 'yearly')].to_list(),
            # Transformation assets by trading frequency
            'ATH': aee['asst'][(aee.role == 'tfrm') & (aee.tfrq == 'hourly')].to_list(),
            'ATW': aee['asst'][(aee.role == 'tfrm') & (aee.tfrq == 'weekly')].to_list(),
            'ATY': aee['asst'][(aee.role == 'tfrm') & (aee.tfrq == 'yearly')].to_list(),
            # Transmission assets by trading frequency
            'AXH': aee['asst'][(aee.role == 'trms') & (aee.tfrq == 'hourly')].to_list(),
            'AXW': aee['asst'][(aee.role == 'trms') & (aee.tfrq == 'weekly')].to_list(),
            'AXY': aee['asst'][(aee.role == 'trms') & (aee.tfrq == 'yearly')].to_list(),
            # Storage assets by trading frequency
            'ASH': aee['asst'][(aee.role == 'stor') & (aee.tfrq == 'hourly')].to_list(),
            'ASW': aee['asst'][(aee.role == 'stor') & (aee.tfrq == 'weekly')].to_list(),
            'ASY': aee['asst'][(aee.role == 'stor') & (aee.tfrq == 'yearly')].to_list(),
            # Primary production assets by trading frequency
            'APH_er': aee['key_era'][(aee.role == 'prim') & (aee.tfrq == 'hourly')].to_list(),
            'APW_er': aee['key_era'][(aee.role == 'prim') & (aee.tfrq == 'weekly')].to_list(),
            'APY_er': aee['key_era'][(aee.role == 'prim') & (aee.tfrq == 'yearly')].to_list(),
            # Transformation assets by trading frequency
            'ATH_er': aee['key_era'][(aee.role == 'tfrm') & (aee.tfrq == 'hourly')].to_list(),
            'ATW_er': aee['key_era'][(aee.role == 'tfrm') & (aee.tfrq == 'weekly')].to_list(),
            'ATY_er': aee['key_era'][(aee.role == 'tfrm') & (aee.tfrq == 'yearly')].to_list(),
            # Transmission assets by trading frequency - exporting regions
            'AXH_er': aee['key_era'][(aee.role == 'trms') & (aee.tfrq == 'hourly')].to_list(),
            'AXW_er': aee['key_era'][(aee.role == 'trms') & (aee.tfrq == 'weekly')].to_list(),
            'AXY_er': aee['key_era'][(aee.role == 'trms') & (aee.tfrq == 'yearly')].to_list(),
            # Transmission assets by trading frequency- exporting regions
            'AIH_er': dst['key_era'][(dst.role == 'trms') & (aee.tfrq == 'hourly')].to_list(),
            'AIW_er': dst['key_era'][(dst.role == 'trms') & (aee.tfrq == 'weekly')].to_list(),
            'AIY_er': dst['key_era'][(dst.role == 'trms') & (aee.tfrq == 'yearly')].to_list(),
            # Storage assets by trading frequency
            'ASH_er': aee['key_era'][(aee.role == 'stor') & (aee.tfrq == 'hourly')].to_list(),
            'ASW_er': aee['key_era'][(aee.role == 'stor') & (aee.tfrq == 'weekly')].to_list(),
            'ASY_er': aee['key_era'][(aee.role == 'stor') & (aee.tfrq == 'yearly')].to_list(),
            # All (ener,region,tech) tuple-key combos
            'ERA': aee['key_era'].to_list() + dst['key_era'].to_list()
        }

    def set_para_hourly(self):
        """Make dict for all hourly model parameters."""
        # TODO: Make common framework for matching asset choices of hourly profiles
        #       for availability, variable unit costs etc., also allowing for differences
        #       in these between e.g. S, D and V for storage
        #       We will probably need a column in a_data for each merge
        # ah is asset x (weeks x hours), for now only variable cost
        # outer join of asst, week & hours so that we get a asst x (week x hour) matrix
        # Join on artificial key A=1 set for all rows in t_data and wh_data
        ah = pandas.merge(self.a.assign(A=1), self.wh.assign(A=1), on='A').drop('A',1)
        ah['cst'] = ah.cstV * ah.uniform
        ah['key'] = ah[['asst','week','hour']].apply(tuple,axis=1)
        ah_p = ah[ah.role == 'prim']
        ah_t = ah[ah.role == 'tfrm']
        ah_s = ah[ah.role == 'stor']
        ah_x = ah[ah.role == 'trms']

        # Stack wh_data availability from wide format (hours x weeks in rows and availability types in columns)
        # to long format (availability type x hours x weeks) in rows and one column for values
        wh = self.wh.set_index(['week','hour']).stack().reset_index()
        wh.columns = ['week','hour','vAva','ava']
        awh = pandas.merge(self.a[['asst','role','vAva']], wh, on='vAva').drop(['vAva'], axis=1)
        awh['key'] = awh[['asst','week','hour']].apply(tuple,axis=1)
        awh_p = awh[awh.role == 'prim']
        awh_t = awh[awh.role == 'tfrm']
        awh_s = awh[awh.role == 'stor']
        awh_x = awh[awh.role == 'trms']

        # Final consumption - mFin is the multiplier from the selected column lFin
        wh.columns = ['week','hour','vFin','mFin']
        fwh = pandas.merge(self.er[['ener','regn','vFin','lFin']], wh, on='vFin')
        fwh['fin'] = fwh.lFin*fwh.mFin
        fwh['key'] = fwh[['ener','regn','week','hour']].apply(tuple,axis=1)

        # Declare hourly parameters with dict keys (tth,w,h)
        self.para_h = {
            'cst_Ph': dict(zip(ah_p.key,ah_p.cst)),     # Hourly unit cost of prim. prod. asset
            'cst_Th': dict(zip(ah_t.key,ah_t.cst)),     # Hourly unit cost of transformation asset
            'cst_Sh': dict(zip(ah_s.key,ah_s.cst)),     # Hourly unit cost of storage asset
            'cst_Xh': dict(zip(ah_x.key,ah_x.cst)),     # Hourly unit cost of transmission asset
            'ava_Ph': dict(zip(awh_p.key,awh_p.ava)),   # Hourly availability of prim. prod. asset
            'ava_Th': dict(zip(awh_t.key,awh_t.ava)),   # Hourly availability of transformation asset
            'ava_Xh': dict(zip(awh_x.key,awh_x.ava)),   # Hourly availability of transmission export asset
            'ava_Ih': dict(zip(awh_x.key,awh_x.ava)),   # Hourly availability of transmission import asset
            'ava_Sh': dict(zip(awh_s.key,awh_s.ava)),   # Hourly availability of storage at storage asset
            'ava_Dh': dict(zip(awh_s.key,awh_s.ava)),   # Hourly availability of discharge at storage asset
            'ava_Vh': dict(zip(awh_s.key,awh_s.ava)),   # Hourly availability of volume at storage asset
            'fin_h': dict(zip(fwh.key,fwh.fin)),        # Hourly final consumption by ener, region, week and hour
        }

    def set_para_yearly(self):
        """Make dict for all yearly model parameters."""
        # Declare assets' yearly parameters with dict keys of (t) and (e,t)

        # Energy efficiency by energy carrier and asset (ener,tech): effe
        ae = self.ae.copy()
        ae['key'] = ae[['ener','asst']].apply(tuple,axis=1)

        # Initial and maximum capacity of asset
        # select this year and add role to dataframe ty
        ay = self.ay[self.ay.year == 'y2020'].copy()
        ay = pandas.merge(ay, self.a[['asst','role','cstC']], on='asst')
        ay['key'] = ay[['asst']].apply(tuple,axis=1)
        ay_p = ay[ay.role == 'prim']
        ay_t = ay[ay.role == 'tfrm']
        ay_x = ay[ay.role == 'trms']
        ay_s = ay[ay.role == 'stor']

        self.para_y = {
            'eff': dict(zip(ae.key,ae.effe)),           # Conversion efficiency by
            'ini_P': dict(zip(ay_p.key,ay_p.iniC)),     # Initial capacity of prim. prod. by asset and year
            'ini_T': dict(zip(ay_t.key,ay_t.iniC)),     # Initial capacity of transformation by asset and year
            'ini_X': dict(zip(ay_x.key,ay_x.iniC)),     # Initial capacity of transmission export by asset and year
            'ini_I': dict(zip(ay_x.key,ay_x.iniC)),     # Initial capacity of transmission import by asset and year
            'ini_S': dict(zip(ay_s.key,ay_s.iniC)),     # Initial capacity of storage asset by asset and year
            'ini_D': dict(zip(ay_s.key,ay_s.iniC)),     # Initial capacity of storage asset by asset and year
            'ini_V': dict(zip(ay_s.key,ay_s.iniC)),     # Initial capacity of storage asset by asset and year
            'max_C': dict(zip(ay.key,ay.maxC)),         # Maximum capacity of by asset and year
            'cst_C': dict(zip(ay.key,ay.cstC)),         # Cost of capacity of all by asset and year
        }
