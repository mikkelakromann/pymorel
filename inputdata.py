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
        self.t = pandas.DataFrame(self.inputdata['t_data'])         # Asset data
        self.te = pandas.DataFrame(self.inputdata['te_data'])       # Technonology x energy carrier data
        self.ty = pandas.DataFrame(self.inputdata['ty_data'])       # Asset x year data

        self.h = pandas.DataFrame(self.inputdata['h_data'])         # Hourly data
        self.w = pandas.DataFrame(self.inputdata['w_data'])         # Weekly data
        self.wh = pandas.DataFrame(self.inputdata['wh_data'])       # Weekly x hourly data

        self.a = pandas.DataFrame(self.inputdata['a_data'])         # Area data
        self.e = pandas.DataFrame(self.inputdata['e_data'])         # Energy carrier data
        self.ea = pandas.DataFrame(self.inputdata['ea_data'])       # Energy carrier x area data

        # Clean out assets that are not relevant to the year or have zero endo & exo capacity limit
        self.ty[(self.ty.year == 'y2020') & ((self.ty.iniC > 0) | (self.ty.maxC > 0))]
        self.t = pandas.merge(self.t,self.ty['asst'], on='asst')    # merge will drop t rows that have no tech in ty
        self.te = pandas.merge(self.te,self.ty['asst'], on='asst')  # merge will drop te rows that have no tech in ty
        # TODO: Clean t for areas not in a
        # TODO: Clean te for eners not in e

    def set_sets(self):
        """Loads input data into internal dataframes, clean and set the main sets."""
        # Save the main sets in a dict of lists, e.g.
        # { 'E': ['elec','dhea', 'ngas'], 'A': ['dk0','no0','de0'], }
        self.sets = {
            'E':  self.e['ener'].to_list(),                          # Energy carriers
            'A':  self.a['area'].to_list(),                          # Areas
            'T':  self.t['asst'].to_list(),                          # All active assets
            'W':  self.w['week'].to_list(),                          # Weeks
            'H':  self.h['hour'].to_list(),                          # Hours
        }

        # Merge tech role and trading frequency onto te in order to compute subsets of assets
        tee = pandas.merge(self.te,self.e[['ener','tfrq']], on='ener')
        tee = pandas.merge(tee,self.t, on='asst')
        # Create ener,area,tech tuple-keys e.g. ('elec','dk0','ccgt') in the dataframe for later use
        tee['key_eat'] = tee[['ener','area','asst']].apply(tuple,axis=1)

        # Copy all transmission assets in order to put the import flows
        # into the TI*_ea subsets.
        # Now, dest becomes the origin area of the export
        dst = tee[tee.role == 'trms']
        # The dest tuple key use dest instead of area
        dst['key_eat'] = dst[['ener','dest','asst']].apply(tuple,axis=1)
        # Save the main simple subsets in a dict of lists { 'TC': }
        self.subsets = {
            # Technologies that can be invested in
            'TC': self.ty['asst'][self.ty.maxC > 0].to_list(),
            # Asset subsets by role
            'TT':  self.t['asst'][self.t.role == 'tfrm'].to_list(),
            'TX':  self.t['asst'][self.t.role == 'trms'].to_list(),
            'TS':  self.t['asst'][self.t.role == 'stor'].to_list(),
            # Energy carrier subsets by trading frequency
            'EH':  self.e['ener'][self.e.tfrq == 'hourly'].to_list(),
            'EW':  self.e['ener'][self.e.tfrq == 'weekly'].to_list(),
            'EY':  self.e['ener'][self.e.tfrq == 'yearly'].to_list(),
            # Transformation assets by trading frequency
            'TTH': tee['asst'][(tee.role == 'tfrm') & (tee.tfrq == 'hourly')].to_list(),
            'TTW': tee['asst'][(tee.role == 'tfrm') & (tee.tfrq == 'weekly')].to_list(),
            'TTY': tee['asst'][(tee.role == 'tfrm') & (tee.tfrq == 'yearly')].to_list(),
            # Transmission assets by trading frequency
            'TXH': tee['asst'][(tee.role == 'trms') & (tee.tfrq == 'hourly')].to_list(),
            'TXW': tee['asst'][(tee.role == 'trms') & (tee.tfrq == 'weekly')].to_list(),
            'TXY': tee['asst'][(tee.role == 'trms') & (tee.tfrq == 'yearly')].to_list(),
            # Storage assets by trading frequency
            'TSH': tee['asst'][(tee.role == 'stor') & (tee.tfrq == 'hourly')].to_list(),
            'TSW': tee['asst'][(tee.role == 'stor') & (tee.tfrq == 'weekly')].to_list(),
            'TSY': tee['asst'][(tee.role == 'stor') & (tee.tfrq == 'yearly')].to_list(),
            # Transformation assets by trading frequency
            'TTH_ea': tee['key_eat'][(tee.role == 'tfrm') & (tee.tfrq == 'hourly')].to_list(),
            'TTW_ea': tee['key_eat'][(tee.role == 'tfrm') & (tee.tfrq == 'weekly')].to_list(),
            'TTY_ea': tee['key_eat'][(tee.role == 'tfrm') & (tee.tfrq == 'yearly')].to_list(),
            # Transmission assets by trading frequency - exporting areas
            'TXH_ea': tee['key_eat'][(tee.role == 'trms') & (tee.tfrq == 'hourly')].to_list(),
            'TXW_ea': tee['key_eat'][(tee.role == 'trms') & (tee.tfrq == 'weekly')].to_list(),
            'TXY_ea': tee['key_eat'][(tee.role == 'trms') & (tee.tfrq == 'yearly')].to_list(),
            # Transmission assets by trading frequency- exporting areas
            'TIH_ea': dst['key_eat'][(dst.role == 'trms') & (tee.tfrq == 'hourly')].to_list(),
            'TIW_ea': dst['key_eat'][(dst.role == 'trms') & (tee.tfrq == 'weekly')].to_list(),
            'TIY_ea': dst['key_eat'][(dst.role == 'trms') & (tee.tfrq == 'yearly')].to_list(),
            # Storage assets by trading frequency
            'TSH_ea': tee['key_eat'][(tee.role == 'stor') & (tee.tfrq == 'hourly')].to_list(),
            'TSW_ea': tee['key_eat'][(tee.role == 'stor') & (tee.tfrq == 'weekly')].to_list(),
            'TSY_ea': tee['key_eat'][(tee.role == 'stor') & (tee.tfrq == 'yearly')].to_list(),
            # All (ener,area,tech) tuple-key combos
            'EAT': tee['key_eat'].to_list() + dst['key_eat'].to_list()
        }

    def set_para_hourly(self):
        """Make dict for all hourly model parameters."""
        # TODO: Make common framework for matching asset choices of hourly profiles
        #       for availability, variable unit costs etc., also allowing for differences
        #       in these between e.g. S, D and V for storage
        #       We will probably need a column in t_data for each merge
        # th is asset x (weeks x hours), for now only variable cost
        # outer join of tech, week & hours so that we get a tech x (week x hour) matrix
        # Join on artificial key A=1 set for all rows in t_data and wh_data
        th = pandas.merge(self.t.assign(A=1), self.wh.assign(A=1), on='A').drop('A',1)
        th['cst'] = th.cstV * th.uniform
        th['key'] = th[['asst','week','hour']].apply(tuple,axis=1)
        th_t = th[th.role == 'tfrm']
        th_s = th[th.role == 'stor']
        th_x = th[th.role == 'trms']

        # Stack wh_data availability from wide format (hours x weeks in rows and availability types in columns)
        # to long format (availability type x hours x weeks) in rows and one column for values
        wh = self.wh.set_index(['week','hour']).stack().reset_index()
        wh.columns = ['week','hour','vAva','ava']
        twh = pandas.merge(self.t[['asst','role','vAva']], wh, on='vAva').drop(['vAva'], axis=1)
        twh['key'] = twh[['asst','week','hour']].apply(tuple,axis=1)
        twh_t = twh[twh.role == 'tfrm']
        twh_s = twh[twh.role == 'stor']
        twh_x = twh[twh.role == 'trms']

        # Final consumption - mFin is the multiplier from the selected column lFin
        wh.columns = ['week','hour','vFin','mFin']
        fwh = pandas.merge(self.ea[['ener','area','vFin','lFin']], wh, on='vFin')
        fwh['fin'] = fwh.lFin*fwh.mFin
        fwh['key'] = fwh[['ener','area','week','hour']].apply(tuple,axis=1)

        # Declare hourly parameters with dict keys (tth,w,h)
        self.para_h = {
            'cst_Th': dict(zip(th_t.key,th_t.cst)),     # Hourly unit cost of transformation asset
            'cst_Sh': dict(zip(th_s.key,th_s.cst)),     # Hourly unit cost of storage asset
            'cst_Xh': dict(zip(th_x.key,th_x.cst)),     # Hourly unit cost of transmission asset
            'ava_Th': dict(zip(twh_t.key,twh_t.ava)),   # Hourly availability of transformation asset
            'ava_Xh': dict(zip(twh_x.key,twh_x.ava)),   # Hourly availability of transmission export asset
            'ava_Ih': dict(zip(twh_x.key,twh_x.ava)),   # Hourly availability of transmission import asset
            'ava_Sh': dict(zip(twh_s.key,twh_s.ava)),   # Hourly availability of storage at storage asset
            'ava_Dh': dict(zip(twh_s.key,twh_s.ava)),   # Hourly availability of discharge at storage asset
            'ava_Vh': dict(zip(twh_s.key,twh_s.ava)),   # Hourly availability of volume at storage asset
            'fin_h': dict(zip(fwh.key,fwh.fin)),        # Hourly final consumption by ener, area, week and hour
        }

    def set_para_yearly(self):
        """Make dict for all yearly model parameters."""
        # Declare assets' yearly parameters with dict keys of (t) and (e,t)

        # Energy efficiency by energy carrier and asset (ener,tech): effe
        te = self.te.copy()
        te['key'] = te[['ener','asst']].apply(tuple,axis=1)

        # Initial and maximum capacity of asset
        # select this year and add role to dataframe ty
        ty = self.ty[self.ty.year == 'y2020'].copy()
        ty = pandas.merge(ty, self.t[['asst','role','cstC']], on='asst')
        ty['key'] = ty[['asst']].apply(tuple,axis=1)
        ty_t = ty[ty.role == 'tfrm']
        ty_x = ty[ty.role == 'trms']
        ty_s = ty[ty.role == 'stor']

        self.para_y = {
            'eff': dict(zip(te.key,te.effe)),           # Conversion efficiency by (ener,tech)
            'ini_T': dict(zip(ty_t.key,ty_t.iniC)),     # Initial capacity of transformation asset by (tech)
            'ini_X': dict(zip(ty_x.key,ty_x.iniC)),     # Initial capacity of transmission export asset
            'ini_I': dict(zip(ty_x.key,ty_x.iniC)),     # Initial capacity of transmission import asset
            'ini_S': dict(zip(ty_s.key,ty_s.iniC)),     # Initial capacity of storage asset by storage capacity
            'ini_D': dict(zip(ty_s.key,ty_s.iniC)),     # Initial capacity of storage asset by discharge capacity
            'ini_V': dict(zip(ty_s.key,ty_s.iniC)),     # Initial capacity of storage asset by volume capacity
            'max_C': dict(zip(ty.key,ty.maxC)),         # Maximum capacity of all assets
            'cst_C': dict(zip(ty.key,ty.cstC)),         # Cost of capacity of all assets
        }
