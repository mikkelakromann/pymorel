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

        # Sets
        self.sets = {
            'e': [],    # Energy carriers
            'a': [],    # Areas
            't': [],    # Technologies
            'tth': [],  # Hourly transformation technologies
            'txh': [],  # Hourly transmission technologies 
            'tsh': [],  # Hourly storage technologies
            'tc': [],   # Technologies for which investment is allowed
        }
        self.sets['e'] = data['e_data']['ener']
        self.sets['a'] = data['a_data']['area']
        self.sets['t'] = data['t_data']['tech']
        for t_row in self.t_data:
            self.sets['tth'] = t_dk+t_no+t_de 
            self.sets['txh'] = ['x_dk_no','x_dk_de']
            self.sets['tsh'] = []
            self.sets['tc'] = []


        self.sets['w'] = ['w01']
        self.sets['h'] = ['h03','h09','h15','h21','h27','h33','h39','h45']


        # Selector helps with adding only necessary constraints and variables
        # to the equations
        self.selector_dict = {
            'e_is_hourly': {},      # Hourly markets
            'TIh_in_ea': {},        # Technologies operating in market
            'XXh_into_ea': {},      # Transmission into market
            'XXh_from_ea': {},      # Transmission from market
            'SS_in_ea': {},         # Storage in market
            }
        

        # Utility dict: technology: area
        tech_area = zip(self.t_data['tech'].to_list(),self.t_data['area'].to_list())
        # Utility dict: technology: list of energy carriers
        tech_ener = {}
        for t_row in self.t_data:
            tech_ener[t_row['tech']] = []
        for te_row in self.te_data:
            tech_ener[te_row['tech']].append(te_row['ener'])
            
            
        # Set up dicts for selectors
        for e in self.sets['e']:
            for a in self.sets['a']:
                self.selector_dict['TIh_in_ea'][e,a] = False
                self.selector_dict['XXh_into_ea'][e,a]= False
                self.selector_dict['XXh_from_ea'][e,a]= False
                self.selector_dict['SS_in_ea'][e,a]= False

        # Is the energy carrier traded on an hourly market?
        for e_row in self.e_data:
            if e_row['time'] == 'hourly':
                self.selector_dict['e_is_hourly'][e_row['ener']] =  True
                th_ea[e_row['tech']]
            else:
                self.selector_dict['e_is_hourly'][e_row['ener']] =  False  

        


        self.selector_dict['TIh_in_ea'] = { 
            ('ele','dk0'): True, ('ele','de0'): True, ('ele','no0'): True }
        # Is there import of energy carrrier into the area?
        self.selector_dict['XXh_into_ea'] = { 
            ('ele','dk0'): True, ('ele','de0'): True, ('ele','no0'): True }
        # Is there export of energy carrrier from the area?
        self.selector_dict['XXh_from_ea'] = { 
            ('ele','dk0'): True, ('ele','de0'): True, ('ele','no0'): True }
        # Is there storage of energy carrier in the area?
        self.selector_dict['SS_in_ea'] = {
            ('ele','dk0'): False, ('ele','de0'): False, ('ele','no0'): False }
        
        # subsets helps by quickly returning subsets for constraint building
        self.conditionalsets = {}
        # Return subset of all technologies generating energy carrier in area
        self.conditionalsets['tth_in_ea'] = { 
            ('ele','dk0'): t_dk, ('ele','no0'): t_no, ('ele','de0'): t_de }
        self.conditionalsets['x1_into_ea'] = { 
            ('ele','dk0'): [], ('ele','no0'): ['x_dk_no'], ('ele','de0'): ['x_dk_de'], }
        self.conditionalsets['x2_into_ea'] = { 
            ('ele','dk0'): ['x_dk_no','x_dk_de'], ('ele','no0'): [], ('ele','de0'): [], }
        self.conditionalsets['x2_from_ea'] = { 
            ('ele','dk0'): [], ('ele','no0'): ['x_dk_no'], ('ele','de0'): ['x_dk_de'], }
        self.conditionalsets['x1_from_ea'] = { 
            ('ele','dk0'): ['x_dk_no','x_dk_de'], ('ele','no0'): [], ('ele','de0'): [], }
        self.conditionalsets['tsh_in_ea'] = { 
            ('ele','dk0'): [], ('ele','no0'): [], ('ele','de0'): [], }

        # Parameters
        self.para = {}
        # Transformation efficiency
        self.para['eff_TIe'] = { 
            ('ele','gas_dk0'): 0.55, ('ele','gas_no0'): 0.55, ('ele','gas_de0'): 0.55, 
            ('ele','wnd_dk0'): 1.00, ('ele','wnd_no0'): 1.00, ('ele','wnd_de0'): 1.00, 
            ('ele','sol_dk0'): 1.00, ('ele','sol_no0'): 1.00, ('ele','sol_de0'): 1.00, }
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
            # Total efficiency
            'teff': [0.95,      0.95,      0.95,      1.00,      1.00,      1.00,      1.00,      1.00,      1.00,      ],
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
            # Energy carrier's share of output (positive number) or input (negative number)
            # Inputs (if any) must sum over carriers to -1 per technology, outputs to +1
            'shre': [0.45,      0.45,      0.45,      0.55,      0.55,      0.55,      -1.00,     -1.00,     -1.00,      
                     1.00,      1.00,      1.00,      1.00,      1.00,      1.00,      ],
            }

        return data