import pandas


class PyMorelData():
    """Class for holding input and output data to PyMorelModel"""

    def __init__(self):
        """Perform these functions when initiating a PyMorelData object."""
        self.set_sets()
        self.set_para_hourly()
        self.set_para_yearly()

    def set_sets(self):
        """Loads input data into internal dataframes, clean and set the main sets."""
        # Get data and put it into dataframes
        data = self.get_default_data()
        t = self.t_data = pandas.DataFrame(data['t_data'])      # Technology data
        te = self.te_data = pandas.DataFrame(data['te_data'])   # Technonology x energy carrier data
        ty = self.ty_data = pandas.DataFrame(data['ty_data'])   # Technology x year data

        h = self.h_data = pandas.DataFrame(data['h_data'])      # Hourly data
        w = self.w_data = pandas.DataFrame(data['w_data'])      # Weekly data
        wh = self.wh_data = pandas.DataFrame(data['wh_data'])   # Weekly x hourly data

        a = self.a_data = pandas.DataFrame(data['a_data'])      # Area data
        e = self.e_data = pandas.DataFrame(data['e_data'])      # Energy carrier data
        ea = self.ea_data = pandas.DataFrame(data['ea_data'])   # Energy carrier x area data

        # Clean out technologies that are not relevant to the year or have zero endo & exo capacity limit
        ty = ty[(ty.year == 'y2020') & ((ty.iniC > 0) | (ty.maxC > 0))]
        t = pandas.merge(t,ty['tech'], on='tech')   # merge will drop t rows that have no tech in ty
        te = pandas.merge(te,ty['tech'], on='tech')  # merge will drop te rows that have no tech in ty
        # TODO: Clean t for areas not in a
        # TODO: Clean te for eners not in e

        # Save the main sets in a dict of lists
        self.sets = {
            'E':  e['ener'].to_list(),                          # Energy carriers
            'A':  a['area'].to_list(),                          # Areas
            'T':  t['tech'].to_list(),                          # All active technologies
            'W':  w['week'].to_list(),                          # Weeks
            'H':  h['hour'].to_list(),                          # Hours
        }

        # Merge tech role and trading frequency onto te in order to compute subsets of technologies
        tee = pandas.merge(te,e[['ener','tfrq']], on='ener')
        tee = pandas.merge(tee,t, on='tech')
        tee['key_eat'] = tee[['ener','area','tech']].apply(tuple,axis=1)

        # Copy all transmission technologies in order to put the import flows
        # into the TI*_ea subsets.
        # Now, dest becomes the origin area of the export
        dst = tee[tee.role == 'trms']
        dst['key_eat'] = dst[['ener','dest','tech']].apply(tuple,axis=1)
        # Save the main simple subsets in a dict of lists { 'TC': }
        self.subsets = {
            # Technology subsets by role
            'TC': ty['tech'][ty.maxC > 0].to_list(),               # Technologies that can be invested in
            'TT':  t['tech'][t.role == 'tfrm'].to_list(),          # Technologies for transformation
            'TX':  t['tech'][t.role == 'trms'].to_list(),          # Technologies for transmission
            'TS':  t['tech'][t.role == 'stor'].to_list(),          # Technologies for storage
            # Energy carrier subsets by trading frequency
            'EH':  e['ener'][e.tfrq == 'hourly'].to_list(),        # Energy carriers traded hourly
            'EW':  e['ener'][e.tfrq == 'weekly'].to_list(),        # Energy carriers traded weekly
            'EY':  e['ener'][e.tfrq == 'yearly'].to_list(),        # Energy carriers traded yearly
            # Transformation technologies by freq
            'TTH': tee['tech'][(tee.role == 'tfrm') & (tee.tfrq == 'hourly')].to_list(),
            'TTW': tee['tech'][(tee.role == 'tfrm') & (tee.tfrq == 'weekly')].to_list(),
            'TTY': tee['tech'][(tee.role == 'tfrm') & (tee.tfrq == 'yearly')].to_list(),
            # Transmission technologies by freq
            'TXH': tee['tech'][(tee.role == 'trms') & (tee.tfrq == 'hourly')].to_list(),
            'TXW': tee['tech'][(tee.role == 'trms') & (tee.tfrq == 'weekly')].to_list(),
            'TXY': tee['tech'][(tee.role == 'trms') & (tee.tfrq == 'yearly')].to_list(),
            # Storage technologies by freq
            'TSH': tee['tech'][(tee.role == 'stor') & (tee.tfrq == 'hourly')].to_list(),
            'TSW': tee['tech'][(tee.role == 'stor') & (tee.tfrq == 'weekly')].to_list(),
            'TSY': tee['tech'][(tee.role == 'stor') & (tee.tfrq == 'yearly')].to_list(),
            # Transformation technologies by freq
            'TTH_ea': tee['key_eat'][(tee.role == 'tfrm') & (tee.tfrq == 'hourly')].to_list(),
            'TTW_ea': tee['key_eat'][(tee.role == 'tfrm') & (tee.tfrq == 'weekly')].to_list(),
            'TTY_ea': tee['key_eat'][(tee.role == 'tfrm') & (tee.tfrq == 'yearly')].to_list(),
            # Transmission technologies by freq - exporting areas
            'TXH_ea': tee['key_eat'][(tee.role == 'trms') & (tee.tfrq == 'hourly')].to_list(),
            'TXW_ea': tee['key_eat'][(tee.role == 'trms') & (tee.tfrq == 'weekly')].to_list(),
            'TXY_ea': tee['key_eat'][(tee.role == 'trms') & (tee.tfrq == 'yearly')].to_list(),
            # Transmission technologies by freq - exporting areas
            'TIH_ea': dst['key_eat'][(dst.role == 'trms') & (tee.tfrq == 'hourly')].to_list(),
            'TIW_ea': dst['key_eat'][(dst.role == 'trms') & (tee.tfrq == 'weekly')].to_list(),
            'TIY_ea': dst['key_eat'][(dst.role == 'trms') & (tee.tfrq == 'yearly')].to_list(),
            # Storage technologies by freq
            'TSH_ea': tee['key_eat'][(tee.role == 'stor') & (tee.tfrq == 'hourly')].to_list(),
            'TSW_ea': tee['key_eat'][(tee.role == 'stor') & (tee.tfrq == 'weekly')].to_list(),
            'TSY_ea': tee['key_eat'][(tee.role == 'stor') & (tee.tfrq == 'yearly')].to_list(),
            # All (ener,area,tech) combos
            'EAT': tee['key_eat'].to_list() + dst['key_eat'].to_list()
        }

        # Conditional subsets (css) is a (role,freq)-dict of (ener,area)-dicts of tech-lists e.g.
        # css = { ('tfrm','hourly'): {('elec','dk0'): ['dk_wind','dk_ccgt'], ('heat','dk0'): [dk_ccgt], ...}, ... }
        teea = pandas.merge(tee, a, on='area')
        teea['key'] = teea[['ener','area','tech']].apply(tuple,axis=1)
        css = self.get_conditionalsubsets(teea)
        self.conditionalsubsets = {
            # Tech/tfrq subsets conditional by ener/area
            'TTH_ea': css['tfrm','hourly'],     # Hourly transformation techs by (ener,area)
            'TXH_ea': css['trms','hourly'],     # Hourly transmission techs by (ener, exporting area)
            'TIH_ea': css['dest','hourly'],     # Hourly transmission techs by (ener, importing area)
            'TSH_ea': css['stor','hourly'],     # Hourly storage techs by (ener,area)
            'TTW_ea': css['tfrm','weekly'],     # Weekly transformation techs by (ener,area)
            'TXW_ea': css['trms','weekly'],     # Weekly transmission techs by (ener,exporting area)
            'TIW_ea': css['dest','yearly'],     # Weekly transmission techs by (ener,importing area)
            'TSW_ea': css['stor','weekly'],     # Weekly storage techs by (ener,area)
            'TTY_ea': css['tfrm','yearly'],     # Yearly transformation techs by (ener,area)
            'TXY_ea': css['trms','yearly'],     # Yearly transmission techs by (ener,exporting area)
            'TIY_ea': css['dest','yearly'],     # Yearly transmission techs by (ener,importing area)
            'TSY_ea': css['stor','yearly'],     # Yearly storage techs by (ener,area)
        }

    def get_conditionalsubsets(self, tee: object) -> dict:
        """Compute dict of tech subsets conditional on ener and area from tee dataframe."""
        # Loop over energy carriers and areas and make technology role subset list of techs
        css = {}  # Dict of dict of lists
        for r in ['tfrm','trms','stor']:
            for f in ['hourly','weekly','yearly']:
                css[r,f] = {}
                # Get a tech and tfrq search 0/1 list for length of te_full
                search_rf = (tee['role'] == r) & (tee['tfrq'] == f)
                for e in self.e_data.ener.tolist():
                    for a in self.a_data.area.tolist():
                        # Get tech/tfrq lists by area and energy carrier
                        search_ea = (search_rf & (tee['area'] == a) & (tee['ener'] == e))
                        css[r,f][e,a] = list(set(tee.loc[search_ea]['tech'].tolist()))
                        # For transmission, we need additional set for destination area
                        if r == 'trms':
                            css['dest',f] = {}
                            search = (search_rf & (tee['dest'] == a) & (tee['ener'] == e))
                            css['dest',f][e,a] = list(set(tee.loc[search].tech.tolist()))
        return css

    def set_para_hourly(self):
        """Make dict for all hourly model parameters."""
        # TODO: Make common framework for matching technology choices of hourly profiles
        #       for availability, variable unit costs etc., also allowing for differences
        #       in these between e.g. S, D and V for storage
        #       We will probably need a column in t_data for each merge
        # th is technology x (weeks x hours), for now only variable cost
        # outer join of tech, week & hours so that we get a tech x (week x hour) matrix
        # Join on artificial key A=1 set for all rows in t_data and wh_data
        th = pandas.merge(self.t_data.assign(A=1), self.wh_data.assign(A=1), on='A').drop('A',1)
        th['cst'] = th.cstV * th.uniform
        th['key'] = th[['tech','week','hour']].apply(tuple,axis=1)
        th_t = th[th.role == 'tfrm']
        th_s = th[th.role == 'stor']
        th_x = th[th.role == 'trms']

        # Stack wh_data availability from wide format (hours x weeks in rows and availability types in columns)
        # to long format (availability type x hours x weeks) in rows and one column for values
        wh = self.wh_data.set_index(['week','hour']).stack().reset_index()
        wh.columns = ['week','hour','vAva','ava']
        twh = pandas.merge(self.t_data[['tech','role','vAva']], wh, on='vAva').drop(['vAva'], axis=1)
        twh['key'] = twh[['tech','week','hour']].apply(tuple,axis=1)
        twh_t = twh[twh.role == 'tfrm']
        twh_s = twh[twh.role == 'stor']
        twh_x = twh[twh.role == 'trms']

        # Final consumption - mFin is the multiplier from the selected column lFin
        wh.columns = ['week','hour','vFin','mFin']
        fwh = pandas.merge(self.ea_data[['ener','area','vFin','lFin']], wh, on='vFin')
        fwh['fin'] = fwh.lFin*fwh.mFin
        fwh['key'] = fwh[['ener','area','week','hour']].apply(tuple,axis=1)

        # Declare hourly parameters with dict keys (tth,w,h)
        self.para_h = {
            'cst_Th': dict(zip(th_t.key,th_t.cst)),     # Hourly unit cost of transformation technology
            'cst_Sh': dict(zip(th_s.key,th_s.cst)),     # Hourly unit cost of storage technology
            'cst_Xh': dict(zip(th_x.key,th_x.cst)),     # Hourly unit cost of transmission technology
            'ava_Th': dict(zip(twh_t.key,twh_t.ava)),   # Hourly availability of transformation technology
            'ava_Xh': dict(zip(twh_x.key,twh_x.ava)),   # Hourly availability of transmission export technology
            'ava_Ih': dict(zip(twh_x.key,twh_x.ava)),   # Hourly availability of transmission import technology
            'ava_Sh': dict(zip(twh_s.key,twh_s.ava)),   # Hourly availability of storage at storage technology
            'ava_Dh': dict(zip(twh_s.key,twh_s.ava)),   # Hourly availability of discharge at storage technology
            'ava_Vh': dict(zip(twh_s.key,twh_s.ava)),   # Hourly availability of volume at storage technology
            'fin_h': dict(zip(fwh.key,fwh.fin)),        # Hourly final consumption by ener, area, week and hour
        }

    def set_para_yearly(self):
        """Make dict for all yearly model parameters."""
        # Declare technologies' yearly parameters with dict keys of (t) and (e,t)

        # Energy efficiency by energy carrier and technology (ener,tech): effe
        te = self.te_data
        te['key'] = te[['ener','tech']].apply(tuple,axis=1)

        # Initial and maximum capacity of technology
        # select this year and add role to dataframe ty
        ty = self.ty_data[self.ty_data.year == 'y2020']
        ty = pandas.merge(ty, self.t_data[['tech','role','cstC']], on='tech')
        ty['key'] = ty[['tech']].apply(tuple,axis=1)
        ty_t = ty[ty.role == 'tfrm']
        ty_x = ty[ty.role == 'trms']
        ty_s = ty[ty.role == 'stor']

        self.para_y = {
            'eff': dict(zip(te.key,te.effe)),           # Conversion efficiency by (ener,tech)
            'ini_T': dict(zip(ty_t.key,ty_t.iniC)),     # Initial capacity of transformation technology by (tech)
            'ini_X': dict(zip(ty_x.key,ty_x.iniC)),     # Initial capacity of transmission export technology
            'ini_I': dict(zip(ty_x.key,ty_x.iniC)),     # Initial capacity of transmission import technology
            'ini_S': dict(zip(ty_s.key,ty_s.iniC)),     # Initial capacity of storage technology by storage capacity
            'ini_D': dict(zip(ty_s.key,ty_s.iniC)),     # Initial capacity of storage technology by discharge capacity
            'ini_V': dict(zip(ty_s.key,ty_s.iniC)),     # Initial capacity of storage technology by volume capacity
            'max_C': dict(zip(ty.key,ty.maxC)),         # Maximum capacity of all technologies
            'cst_C': dict(zip(ty.key,ty.cstC)),         # Cost of capacity of all technologies
        }

    def get_default_data(self) -> dict:
        """Provide a default dataset."""
        data = {}
        # Area database
        data['a_data'] = {
            'area': ['dk0',     'de0',      'no0',      ],
        }
        # Energy carrier database
        data['e_data'] = {
            'ener': ['elec',    'dhea',     'ngas'      ],
            'tfrq': ['hourly',  'hourly',   'yearly'    ],
        }
        data['ea_data'] = {
            'ener': ['elec',    'elec',    'elec',    'dhea',    'dhea',    'dhea',    ],
            'area': ['dk0',     'de0',     'no0',     'dk0',     'de0',     'no0',     ],
            'lFin': [40.00,     400.0,     40.00,     0.00,      0.0,       0.00,     ],
            'vFin': ['varElec', 'varElec', 'varElec', 'varDHea', 'varDHea', 'varDHea', ],
        }
        # Technology database
        data['t_data'] = {
            # Technology name (duplicates as technology set)
            'tech': ['bpgt_dk0','bpgt_de0','bpgt_no0','wind_dk0','wind_de0','wind_no0','sopv_dk0','sopv_de0','sopv_no0',],
            # Role: tfrm: transformation, tmis: transmission, stor: storage
            'role': ['tfrm',    'tfrm',    'tfrm',    'tfrm',    'tfrm',    'tfrm',    'tfrm',    'tfrm',    'tfrm',    ],
            # Area of location
            'area': ['dk0',     'de0',     'no0',     'dk0',     'de0',     'no0',     'dk0',     'de0',     'no0',     ],
            # Destination of transmission if applicable
            'dest': ['',        '',        '',        '',        '',        '',        '',        '',        '',        ],
            # Availability
            'avai': ['uniform', 'uniform', 'uniform', 'wnd_dk',  'wnd_dk',  'wnd_dk',  'dayonly', 'dayonly', 'dayonly', ],
            # Capital expenditure, money/MW
            'cstC': [1.00,      1.00,      1.00,      2.00,      2.00,      2.00,      1.00,      1.00,      1.00,      ],
            # Fixed operational expenditure, money/MW/year
            'cstF': [50000,     50000,     50000,     50000,     50000,     50000,     25000,     25000,     25000,     ],
            # Variable operational costs, money/MWh
            'cstV': [1,         1,         1,         1,         1,         1,         0,         0,         0,         ],
            # Already installed capacity in modelling year, MW
            'inic': [5000,      80000,     5000,      4000,      5000,      1000,      1000,      20000,     0          ],
            # Ratio between capacity of S and V for storaage
            'ratSV':[0,         0,         0,         0,         0,         0,         0,         0,         0,         ],
            # Ratio between capacity of D and V for storaage
            'ratDV':[0,         0,         0,         0,         0,         0,         0,         0,         0,         ],
            # Maximum potential investment, MW
            'pcap': ['Inf',     'Inf',     'Inf',     'Inf',     'Inf',     'Inf',     'Inf',     'Inf',     'Inf',     ],
            # Availability choice, % per hour/week/year
            'vAva': ['uniform' ,'uniform' ,'uniform' ,'wind_dk', 'wind_de', 'wind_no', 'dayonly', 'dayonly', 'dayonly', ],
        }
        # Technology/energt carrier database
        data['te_data'] = {
            # Technology name
            'tech': ['bpgt_dk0','bpgt_de0','bpgt_no0','bpgt_dk0','bpgt_de0','bpgt_no0','bpgt_dk0','bpgt_de0','bpgt_no0',
                     'wind_dk0','wind_de0','wind_no0','sopv_dk0','sopv_de0','sopv_no0',],
            # Energy carrier
            'ener': ['elec',    'elec',    'elec',    'dhea',    'dhea',    'dhea',    'ngas',    'ngas',    'ngas',
                     'elec',    'elec',    'elec',    'elec',    'elec',    'elec',],
            # Efficiency by energy carrier, share of total energy input
            # Negative means energy input, positive means energy output
            'effe': [0.45,      0.45,      0.45,      0.55,      0.55,      0.55,      -1.00,     -1.00,     -1.00,
                     1.00,      1.00,      1.00,      1.00,      1.00,      1.00,      ],
        }
        # 6 hour intervals across 1 week = 4x7 = 28 hours/week
        data['h_data'] = {
            'hour': ['h003','h009','h015','h021','h027','h033','h039','h045','h051','h057','h063','h069',
                     'h075','h081','h087','h093','h099','h105','h111','h117','h123','h129','h135','h141',
                     'h147','h153','h159','h165',],
        }
        data['w_data'] = {
            'week': ['w01']
        }
        data['wh_data'] = {
            'hour':     ['h003','h009','h015','h021','h027','h033','h039','h045','h051','h057','h063','h069',
                         'h075','h081','h087','h093','h099','h105','h111','h117','h123','h129','h135','h141',
                         'h147','h153','h159','h165',],
            'week':     ['w01', 'w01', 'w01', 'w01', 'w01', 'w01', 'w01', 'w01', 'w01', 'w01', 'w01', 'w01',
                         'w01', 'w01', 'w01', 'w01', 'w01', 'w01', 'w01', 'w01', 'w01', 'w01', 'w01', 'w01',
                         'w01', 'w01', 'w01', 'w01', ],
            'uniform':  [1.000, 1.000, 1.000, 1.000, 1.000, 1.000, 1.000, 1.000, 1.000, 1.000, 1.000, 1.000,
                         1.000, 1.000, 1.000, 1.000, 1.000, 1.000, 1.000, 1.000, 1.000, 1.000, 1.000, 1.000,
                         1.000, 1.000, 1.000, 1.000,],
            'dayonly':  [0.000, 1.000, 1.000, 0.000, 0.000, 1.000, 1.000, 0.000, 0.000, 1.000, 1.000, 0.000,
                         0.000, 1.000, 1.000, 0.000, 0.000, 1.000, 1.000, 0.000, 0.000, 1.000, 1.000, 0.000,
                         0.000, 1.000, 1.000, 0.000,],
            'wnd_dk':   [0.400, 0.700, 0.800, 0.300, 0.300, 0.500, 0.400, 0.200, 0.100, 0.300, 0.300, 0.200,
                         0.200, 0.400, 0.700, 0.800, 0.800, 0.900, 0.900, 0.800, 0.800, 0.700, 0.500, 0.400,
                         0.100, 0.300, 0.400, 0.100,],
            'wnd_no':   [0.400, 0.700, 0.800, 0.300, 0.300, 0.500, 0.400, 0.200, 0.100, 0.300, 0.300, 0.200,
                         0.200, 0.400, 0.700, 0.800, 0.800, 0.900, 0.900, 0.800, 0.800, 0.700, 0.500, 0.400,
                         0.100, 0.300, 0.400, 0.100,],
            'wnd_de':   [0.300, 0.600, 0.700, 0.300, 0.200, 0.400, 0.300, 0.100, 0.000, 0.200, 0.200, 0.100,
                         0.100, 0.300, 0.600, 0.700, 0.700, 0.800, 0.800, 0.700, 0.700, 0.600, 0.400, 0.300,
                         0.000, 0.200, 0.300, 0.000,],
            'varElec':  [0.400, 0.700, 0.900, 0.800, 0.300, 0.800, 1.000, 0.900, 0.400, 0.700, 0.900, 0.800,
                         0.200, 0.700, 0.800, 0.800, 0.400, 0.800, 0.900, 0.800, 0.500, 0.600, 0.800, 0.800,
                         0.500, 0.800, 0.800, 0.600,],
            'varDhea':  [0.900, 0.700, 0.500, 0.800, 1.000, 0.800, 0.600, 0.900, 0.800, 0.600, 0.400, 0.800,
                         0.900, 0.700, 0.500, 0.800, 1.000, 0.800, 0.600, 0.900, 0.800, 0.600, 0.400, 0.800,
                         0.500, 0.400, 0.400, 0.600,],

        }
        # Yearly technology data - index: (tech,year)
        data['ty_data'] = {
            'tech':     ['bpgt_dk0','bpgt_de0','bpgt_no0','wind_dk0','wind_de0','wind_no0','sopv_dk0','sopv_de0','sopv_no0',],
            'year':     ['y2020',   'y2020',   'y2020',   'y2020',   'y2020',   'y2020',   'y2020',   'y2020',   'y2020',   ],
            'iniC':     [1000,      1000,      1000,      1000,      1000,      1000,      1000,      1000,      1000,      ],
            'maxC':     [1000,      1000,      1000,      1000,      1000,      1000,      1000,      1000,      1000,      ],
        }
        return data

    def testdataframes(self):
        """dataframes for testing dataframe functionality, not for model inclusion."""
        import pandas
        e = pandas.DataFrame(data=
            { 'ener': ['elec','ngas','h2pr'],
              'tfrq': ['hour','year','week'], })
        t = pandas.DataFrame(data=
            { 'tech': ['ccgt','e2h2','ngas','batt','expt' ],
              'role': ['trfm','trfm','trfm','stor','trms'],
              'area': ['dk_0','dk_0','no_0','dk_0','se_0'],
              'avai': ['ava1','ava2','ava2','ava1','ava2'],
              'cstV': [20,    25,     15,    5,     1],
            })
        te = pandas.DataFrame(data={
            'tech': ['ccgt','ccgt','e2h2','e2h2','ngas','batt','expt',],
            'ener': ['ngas','elec','elec','h2pr','ngas','elec','elec',],
            'effe': [-1.00, 0.550, -1.00, 0.700, 1.000, 0.970, 0.965, ]
        })
        te_full = pandas.merge(t, te, on='tech')
        te_full.loc[(te_full['role']=='trfm') & (te_full['area']=='dk_0')].tech.tolist()
        h = pandas.DataFrame(data= {
            'hour': ['h002','h005','h008','h011','h014','h017','h020','h022'],
            'unif': [1,     1,     1,     1,     1,     1,     1,     1,    ],
        })
        th = pandas.merge(h.assign(A=1), t.assign(A=1), on='A').drop('A', 1)
        th['key'] = th[['tech','hour']].apply(tuple,axis=1)
        th['cst'] = th.cstV*th.unif
        ha = pandas.DataFrame(data= {
            'hour': ['h002','h005','h008','h011','h014','h017','h020','h022'],
            'ava1': [1,     1,     1,     1,     1,     1,     1,     1,    ],
            'ava2': [0.5,   0.5,   0.5,   0.5,   0.5,   0.5,   0.5,   0.5,  ],
        })
        # Transform to long format with unstack() and merge with t to get (tech,hour) availability
        ha = ha.set_index('hour').unstack().reset_index()
        ha.columns = ['avai','hour','val']
        ha = pandas.merge(t[['tech','avai']], ha, on='avai').drop(['avai'], axis=1)
        ha['key'] = ha[['tech','hour']].apply(tuple,axis=1)

    def testdataframes2(self):
        """More example dataframes for testing dataframe functionality, not for model inclusion."""
        t = pandas.DataFrame(data=
            { 'tech': ['t1','t2','t3', ],
              'role': ['aa','bb','cc', ]
            })
        ty = pandas.DataFrame(data=
            { 'tech': ['t1','t2','t3', ],
              'year': ['y1','y1','y2', ]
            })



pmd = PyMorelData()