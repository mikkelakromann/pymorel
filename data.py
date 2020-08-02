import pandas.DataFrame

class PyMorelData():
    
    def __init__(self):
        self.set_data()
    
    def set_data(self):
        # Get data and put it into dataframes
        data = self.get_default_data()
        self.a_data = pandas.DataFrame(data['a_data'])
        self.e_data = pandas.DataFrame(data['e_data'])
        self.t_data = pandas.DataFrame(data['t_data'])
        self.te_data = pandas.DataFrame(data['te_data'])

        # Set indices of data frames for better sorting and joining
        self.a_data.set_index('area', inplace=True)
        self.e_data.set_index('ener', inplace=True)
        self.t_data.set_index('tech', inplace=True)
        self.te_data.set_index(['tech','ener'], inplace=True)

        # Add tech/area and ener/time data to a copy of the tech/ener data
        te_full = (te.join(t, on='tech')).join(e, on='ener')
        # Remove indices to enable searches on multi column
        te_full.reset_index(inplace=True)
        # Loop over energy carriers and areas and make technology type subset list of techs
        s = {}
        ss = {}
        for y in ['trfm','trms','stor']:
            for t in ['hour','week','year']:
                ss[y,t] = {}
                # Get a tech and time search 0/1 list for length of te_full 
                search_yt = (te_full['type']==y) & (te_full['time']==y))
                # Get the tech labels for 
                s[y,t] = list(set(te_full.loc[search_yt].tech.tolist()))
                for e in self.e_data.index.tolist():
                    for a in self.a_data.index.tolist():
                        # Get tech/time lists by area and energy carrier
                        search_ea = (search_yt & (te_full['area']==a) & (te_full['ener']==e)
                        ss[y,t][e,a] = list(set(te_full.loc[search_ea].tech.tolist()))
                        # For transmission, we need additional set for destination area
                        if y=='trfm':
                            search = (search_yt &  (te_full['dest']==a) & (te_full['ener']==e)
                            ss[y,'dest'][e,a] = list(set(te_full.loc[search].tech.tolist()))

        # Declare and assign utility dicts
        # dict of empty lists spanning combinations of all areas and energy carriers
        self.util = {
            # Full subsets by tech/time combination
            'TTH': s['trfm','hour']     # Hourly transformation techs for all (ener,area)
            'TXH': s['trms','hour']     # Hourly transmission techs for all (ener,area)
            'TSH': s['stor','hour']     # Hourly storage techs for all (ener,area)
            'TTW': s['trfm','week']     # Weekly transformation techs for all (ener,area)
            'TXW': s['trms','week']     # Weekly transmission techs for all (ener,area)
            'TSW': s['stor','week']     # Weekly storage techs for all (ener,area)
            'TTA': s['trfm','year']     # Annual transformation techs for all (ener,area)
            'TXA': s['trms','year']     # Annual transmission techs for all (ener,area)
            'TSA': s['stor','year']     # Annual storage techs for all (ener,area)
            # Tech/time subsets conditional by ener/area
            'TTH_ea': ss['trfm','hour'] # Hourly transformation techs by (ener,area)
            'TXH_ea': ss['trms','hour'] # Hourly transmission techs by (ener,area)
            'TDH_ea': ss['dest','hour'] # Hourly transmission techs by (ener,destination area)
            'TSH_ea': ss['stor','hour'] # Hourly storage techs by (ener,area)
            'TTW_ea': ss['trfm','week'] # Weekly transformation techs by (ener,area)
            'TXW_ea': ss['trms','week'] # Weekly transmission techs by (ener,area)
            'TDW_ea': ss['dest','year'] # Weekly transmission techs by (ener,destination area)
            'TSW_ea': ss['stor','week'] # Weekly storage techs by (ener,area)
            'TTA_ea': ss['trfm','year'] # Annual transformation techs by (ener,area)
            'TXA_ea': ss['trms','year'] # Annual transmission techs by (ener,area)
            'TDA_ea': ss['dest','year'] # Annual transmission techs by (ener,destination area)
            'TSA_ea': ss['stor','year'] # Annual storage techs by (ener,area)
        }

       # Declare and assign sets
        self.sets = {
            'W': ['w01'],
            'H': ['h03','h09','h15','h21','h27','h33','h39','h45'],
            'E': self.e_data['ener'].to_list(),    # Energy carriers
            'A': self.a_data['area'].to_list(),    # Areas
            'T': self.t_data['tech'].to_list(),    # Technologies
        }

        # Declare parameters 
        self.para = {
            'effe': {}   # Transformation/transmission/storage efficiency
            'icap': {}   # 
        }


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


    def self.get_default_data(self) -> dict:
        """Provide a default dataset."""
        # Area database
        data['a_data'] = {
            'area': ['dk0',     'de0',      'no0',      ]
            }
        # Energy carrier database
        data['e_data'] = { 
            'ener': ['elec',    'dhea',     'ngas'      ], 
            'time': ['hourly',  'hourly',   'annual'    ],
            }
        # Technology database
        data['t_data'] = {
            # Technology name (duplicates as technology set)
            'tech': ['bpgt_dk0','bpgt_de0','bpgt_no0','wind_dk0','wind_de0','wind_no0','sopv_dk0','sopv_de0','sopv_no0',],
            # Type: tfrm: transformation, tmis: transmission, stor: storage
            'type': ['tfrm',    'tfrm',    'tfrm',    'tfrm',    'tfrm',    'tfrm',    'tfrm',    'tfrm',    'tfrm',    ]
            # Area of location
            'area': ['dk0',     'de0',     'no0',     'dk0',     'de0',     'no0',     'dk0',     'de0',     'no0',     ],
            # Capital expenditure, money/MW
            'capx': [1.00,      1.00,      1.00,      2.00,      2.00,      2.00,      1.00,      1.00,      1.00,      ],
            # Fixed operational expenditure, money/MW/year
            'fopx': [50000,     50000,     50000,     50000,     50000,     50000,     25000,     25000,     25000,     ],
            # Variable operational costs, money/MWh
            'vopx': [1,         1,         1,         1,         1,         1,         0,         0,         0,         ],
            # Already installed capacity in modelling year, MW
            'icap': [5000,      80000,     5000,      4000,      5000,      1000,      1000,      20000,     0          ],
            # Maximum potential investment, MW
            'pcap': ['Inf',     'Inf',     'Inf',     'Inf',     'Inf',     'Inf',     'Inf',     'Inf',     'Inf',     ],
            }
        # Technology/energt carrier database
        data['te_data'] = {
            # Technology name
            'name': ['bpgt_dk0','bpgt_de0','bpgt_no0','bpgt_dk0','bpgt_de0','bpgt_no0','bpgt_dk0','bpgt_de0','bpgt_no0',
                     'wind_dk0','wind_de0','wind_no0','sopv_dk0','sopv_de0','sopv_no0',],
            # Energy carrier
            'ener': ['elec',    'elec',    'elec',    'chea',    'chea',    'chea',    'ngas',    'ngas',    'ngas',    
                     'elec',    'elec',    'elec',    'elec',    'elec',    'elec',],
            # Efficiency by energy carrier, share of total energy input
            # Negative means energy input, positive means energy output
            'effe': [0.45,      0.45,      0.45,      0.55,      0.55,      0.55,      -1.00,     -1.00,     -1.00,      
                     1.00,      1.00,      1.00,      1.00,      1.00,      1.00,      ],
            }

        return data
    
    def testdata(self):
        e = pandas.DataFrame(data=
            { 'ener': ['elec','ngas','h2pr'],
              'time': ['hour','year','week'], })
        e.set_index('ener', inplace=True)
        t = pandas.DataFrame(data=
            { 'tech': ['ccgt','e2h2','ngas','batt','expt' ],
              'type': ['trfm','trfm','trfm','stor','trms'], 
              'area': ['dk_0','dk_0','no_0','dk_0','se_0'], })
        t.set_index('tech', inplace=True)
        te= pandas.DataFrame(data=
            { 'tech': ['ccgt','ccgt','e2h2','e2h2','ngas','batt','expt',],
              'ener': ['ngas','elec','elec','h2pr','ngas','elec','elec',], 
              'effe': [-1.00, 0.550, -1.00, 0.700, 1.000, 0.970, 0.965, ]})
        te.set_index(['tech','ener'], inplace=True)
        te_full = (te.join(t, on='tech')).join(e, on='ener')
        te_full.reset_index(inplace=True)
        te_full.loc[(te_full['type']=='trfm') & (te_full['area']=='dk_0')].tech.tolist()
        
