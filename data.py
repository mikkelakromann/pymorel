import pandas

class PyMorelData():
    
    def __init__(self):
        """Perform these functions when initiating a PyMorelData object."""
        self.set_data()
        self.set_util()
        self.set_sets()
        self.set_para_hourly()
        self.set_para_yearly()
        
    def set_data(self):
        """Loads input data into internal dataframes."""
        # Get data and put it into dataframes
        data = self.get_default_data()
        self.a_data = pandas.DataFrame(data['a_data'])      # Area data
        self.e_data = pandas.DataFrame(data['e_data'])      # Energy carrier data
        self.t_data = pandas.DataFrame(data['t_data'])      # Technology data
        self.te_data = pandas.DataFrame(data['te_data'])    # Technonology x energy carrier data
        self.h_data = pandas.DataFrame(data['h_data'])      # Hourly data
        self.w_data = pandas.DataFrame(data['w_data'])      # Weekly data
        self.wh_data = pandas.DataFrame(data['wh_data'])    # Weekly/hourly data

    def set_util(self):
        """Compute utility dict of subsets."""
        # Add tech/area and ener/time data to a copy of the tech/ener data
        te_full = pandas.merge(self.t_data, self.te_data, on='tech')
        # Add ener/time from e_data
        te_full = pandas.merge(te_full, self.e_data, on='ener')
        self.te_full = te_full
        # Loop over energy carriers and areas and make technology type subset list of techs
        s = {}
        ss = {}
        for y in ['tfrm','trms','stor']:
            for t in ['hourly','weekly','yearly']:
                ss[y,t] = {}
                # Get a tech and time search 0/1 list for length of te_full 
                search_yt = (te_full['type']==y) & (te_full['time']==t)
                # Get the tech labels for 
                s[y,t] = list(set(te_full.loc[search_yt].tech.tolist()))
                for e in self.e_data.ener.tolist():
                    for a in self.a_data.area.tolist():
                        # Get tech/time lists by area and energy carrier
                        search_ea = (search_yt & (te_full['area']==a) & (te_full['ener']==e))
                        ss[y,t][e,a] = list(set(te_full.loc[search_ea].tech.tolist()))
                        # For transmission, we need additional set for destination area
                        if y=='trms':
                            ss['dest',t] = {}
                            search = (search_yt &  (te_full['dest']==a) & (te_full['ener']==e))
                            ss['dest',t][e,a] = list(set(te_full.loc[search].tech.tolist()))
        self.ss = ss
        self.s = s

        # Declare and assign utility dicts
        # dict of empty lists spanning combinations of all areas and energy carriers
        self.util = {
            # Full subsets by tech/time combination
            'TTH': s['tfrm','hourly'],     # Hourly transformation techs for all (ener,area)
            'TXH': s['trms','hourly'],     # Hourly transmission techs for all (ener,area)
            'TSH': s['stor','hourly'],     # Hourly storage techs for all (ener,area)
            'TTW': s['tfrm','weekly'],     # Weekly transformation techs for all (ener,area)
            'TXW': s['trms','weekly'],     # Weekly transmission techs for all (ener,area)
            'TSW': s['stor','weekly'],     # Weekly storage techs for all (ener,area)
            'TTY': s['tfrm','yearly'],     # Annual transformation techs for all (ener,area)
            'TXY': s['trms','yearly'],     # Annual transmission techs for all (ener,area)
            'TSY': s['stor','yearly'],     # Annual storage techs for all (ener,area)
            # Tech/time subsets conditional by ener/area
            'TTH_ea': ss['tfrm','hourly'], # Hourly transformation techs by (ener,area)
            'TXH_ea': ss['trms','hourly'], # Hourly transmission techs by (ener, exporting area)
            'TIH_ea': ss['dest','hourly'], # Hourly transmission techs by (ener, importing area)
            'TSH_ea': ss['stor','hourly'], # Hourly storage techs by (ener,area)
            'TTW_ea': ss['tfrm','weekly'], # Weekly transformation techs by (ener,area)
            'TXW_ea': ss['trms','weekly'], # Weekly transmission techs by (ener,exporting area)
            'TIW_ea': ss['dest','yearly'], # Weekly transmission techs by (ener,importing area)
            'TSW_ea': ss['stor','weekly'], # Weekly storage techs by (ener,area)
            'TTY_ea': ss['tfrm','yearly'], # Annual transformation techs by (ener,area)
            'TXY_ea': ss['trms','yearly'], # Annual transmission techs by (ener,exporting area)
            'TIY_ea': ss['dest','yearly'], # Annual transmission techs by (ener,importing area)
            'TSY_ea': ss['stor','yearly'], # Annual storage techs by (ener,area)
        }

    def set_sets(self):
        """Create dict for primary sets"""
        self.sets = {
            'E': self.e_data['ener'].to_list(),    # Energy carriers
            'A': self.a_data['area'].to_list(),    # Areas
            'T': self.t_data['tech'].to_list(),    # Technologies
            'W': self.w_data['week'].to_list(),    # Weeks
            'H': self.h_data['hour'].to_list(),    # Hours
        }


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
        th['cst'] = th.vopx * th.uniform
        th['key'] = th[['tech','week','hour']].apply(tuple,axis=1)
        th_t = th[th.type=='tfrm']
        th_s = th[th.type=='stor']
        th_x = th[th.type=='trms']

        # Stack wh_data availability from wide format (hours x weeks in rows and availability types in columns)
        # to long format (availability type x hours x weeks) in rows and one column for values 
        wh = self.wh_data.set_index(['week','hour']).stack().reset_index()
        wh.columns = ['week','hour','avai','ava']
        wh = pandas.merge(self.t_data[['tech','type','avai']], wh, on='avai').drop(['avai'], axis=1)
        wh['key'] = wh[['tech','week','hour']].apply(tuple,axis=1)
        wh_t = wh [wh.type=='tfrm']
        wh_s = wh [wh.type=='stor']
        wh_x = wh [wh.type=='trms']

        # Declare hourly parameters with dict keys (tth,w,h)
        self.para_h = {
            'cst_Th': dict(zip(th_t.key,th_t.cst)), # Hourly unit cost of transformation technology
            'cst_Sh': dict(zip(th_s.key,th_s.cst)), # Hourly unit cost of storage technology
            'cst_Xh': dict(zip(th_x.key,th_x.cst)), # Hourly unit cost of transmission technology
            'ava_Th': dict(zip(wh_t.key,wh_t.ava)), # Hourly availability of transformation technology 
            'ava_Xh': dict(zip(wh_x.key,wh_x.ava)), # Hourly availability of transmission export technology
            'ava_Ih': dict(zip(wh_x.key,wh_x.ava)), # Hourly availability of transmission import technology
            'ava_Sh': dict(zip(wh_s.key,wh_s.ava)), # Hourly availability of storage at storage technology
            'ava_Dh': dict(zip(wh_s.key,wh_s.ava)), # Hourly availability of discharge at storage technology
            'ava_Vh': dict(zip(wh_s.key,wh_s.ava)), # Hourly availability of volume at storage technology
        }

    def set_para_yearly(self):
        """Make dict for all yearly model parameters."""
        # Declare technologies' annual parameters with dict keys of (t) and (e,t)
        
        te = self.te_data
        te['key'] = te[['ener','tech']].apply(tuple,axis=1)
        print(te)
        
        self.para_y = {
            'eff': dict(zip(te.key,te.effe)),       # Conversion efficiency by (ener,tech)
            'ini_T': {},     # Initial capacity of transformation technology by (tech)
            'ini_X': {},     # Initial capacity of transmission export technology
            'ini_I': {},     # Initial capacity of transmission import technology
            'ini_S': {},     # Initial capacity of storage technology by storage capacity
            'ini_D': {},     # Initial capacity of storage technology by discharge capacity
            'ini_V': {},     # Initial capacity of storage technology by volume capacity
        }
        print(self.para_y)

    def misc_tmp(self):
        # temporary function for misc to be rewritten soon
        # Transformation variable costs including fuel, money/energy input
        self.para['cst_TIh'] = {}
        for tth in self.sets['tth']:
            for w in self.sets['w']:
                for h in self.sets['h']:
                    self.para['cst_TIh'][tth,w,h] = 50

        # Maximum transformation capacity by input
        self.para['max_TIh'] = {}
        for tth in self.sets['tth']:
            for w in self.sets['w']:
                for h in self.sets['h']:
                    self.para['max_TIh'][tth,w,h] = 100

        # Transmission efficiency (100% - loss %)
        self.para['eff_X'] = {('x_dk_no'): 0.95, ('x_dk_de'): 0.95 }

        # Transmission capacity 
        self.para['max_X1h'] = { }
        self.para['max_X2h'] = { }
        for txh in self.sets['txh']:
            for w in self.sets['w']:
                for h in self.sets['h']:
                    self.para['max_X1h'][(txh,w,h)] = 50
                    self.para['max_X2h'][(txh,w,h)] = 50
        # Demand
        self.para['lvl_DEh'] = {}
        for e in self.sets['e']:
            for a in self.sets['a']:
                for w in self.sets['w']:
                    for h in self.sets['h']:
                        self.para['lvl_DEh'][(e,a,w,h)] = 50


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
            'time': ['hourly',  'hourly',   'yearly'    ],
        }
        data['ea_data'] = {
            'ener': ['elec', 'elec', 'elec', 'dhea', 'dhea', 'dhea', ],
            'area': ['dk0',  'de0',  'no0',  'dk0',  'de0',  'no0',  ],
            'dmnd': [40.00,  400.0,  40.00,  80.00,  800.0,  50.00,  ],
        }
        # Technology database
        data['t_data'] = {
            # Technology name (duplicates as technology set)
            'tech': ['bpgt_dk0','bpgt_de0','bpgt_no0','wind_dk0','wind_de0','wind_no0','sopv_dk0','sopv_de0','sopv_no0',],
            # Type: tfrm: transformation, tmis: transmission, stor: storage
            'type': ['tfrm',    'tfrm',    'tfrm',    'tfrm',    'tfrm',    'tfrm',    'tfrm',    'tfrm',    'tfrm',    ],
            # Area of location
            'area': ['dk0',     'de0',     'no0',     'dk0',     'de0',     'no0',     'dk0',     'de0',     'no0',     ],
            # Destination of transmission if applicable
            'dest': ['',        '',        '',        '',        '',        '',        '',        '',        '',        ],
            # Availability 
            'avai': ['uniform', 'uniform', 'uniform', 'wnd_dk',  'wnd_dk',  'wnd_dk',  'dayonly', 'dayonly', 'dayonly', ],
            # Capital expenditure, money/MW
            'capx': [1.00,      1.00,      1.00,      2.00,      2.00,      2.00,      1.00,      1.00,      1.00,      ],
            # Fixed operational expenditure, money/MW/year
            'fopx': [50000,     50000,     50000,     50000,     50000,     50000,     25000,     25000,     25000,     ],
            # Variable operational costs, money/MWh
            'vopx': [1,         1,         1,         1,         1,         1,         0,         0,         0,         ],
            # Already installed capacity in modelling year, MW
            'inic': [5000,      80000,     5000,      4000,      5000,      1000,      1000,      20000,     0          ],
            # Ratio between capacity of S and V for storaage
            'ratSV':[0,         0,         0,         0,         0,         0,         0,         0,         0,         ], 
            # Ratio between capacity of D and V for storaage
            'ratDV':[0,         0,         0,         0,         0,         0,         0,         0,         0,         ], 
            # Maximum potential investment, MW
            'pcap': ['Inf',     'Inf',     'Inf',     'Inf',     'Inf',     'Inf',     'Inf',     'Inf',     'Inf',     ],
            # Availability choice, % per hour/week/year
            'avai': ['uniform' ,'uniform' ,'uniform' ,'wind_dk', 'wind_de', 'wind_no', 'dayonly', 'dayonly', 'dayonly', ], 
        }
        # Technology/energt carrier database
        data['te_data'] = {
            # Technology name
            'tech': ['bpgt_dk0','bpgt_de0','bpgt_no0','bpgt_dk0','bpgt_de0','bpgt_no0','bpgt_dk0','bpgt_de0','bpgt_no0',
                     'wind_dk0','wind_de0','wind_no0','sopv_dk0','sopv_de0','sopv_no0',],
            # Energy carrier
            'ener': ['elec',    'elec',    'elec',    'chea',    'chea',    'chea',    'ngas',    'ngas',    'ngas',    
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
        }
        # Annual technology data - index: (tech,year)
        data['ty_data'] = {
            'tech':     ['bpgt_dk0','bpgt_de0','bpgt_no0','wind_dk0','wind_de0','wind_no0','sopv_dk0','sopv_de0','sopv_no0',],
            'year':     ['y2020',   'y2020',   'y2020',   'y2020',   'y2020',   'y2020',   'y2020',   'y2020',   'y2020',   ],
            'iniC':     [0,         0,         0,         0,         0,         0,         0,         0,         0,         ],
            'maxC':     [1000,      1000,      1000,      1000,      1000,      1000,      1000,      1000,      1000,      ],
        }


        return data
    
    def testdataframes(self):
        """dataframes for testing dataframe functionality, not for model inclusion."""
        import pandas
        e = pandas.DataFrame(data=
            { 'ener': ['elec','ngas','h2pr'],
              'time': ['hour','year','week'], })
        t = pandas.DataFrame(data=
            { 'tech': ['ccgt','e2h2','ngas','batt','expt' ],
              'type': ['trfm','trfm','trfm','stor','trms'], 
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
        te_full.loc[(te_full['type']=='trfm') & (te_full['area']=='dk_0')].tech.tolist()
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
        
pmd = PyMorelData()