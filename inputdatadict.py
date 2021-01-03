class InputDataDict():

    def __init__(self) -> dict:
        """Provide a default dataset."""
        self.data = {}
        # Region database
        self.data['r_data'] = {
            'regn': ['dk0',     'de0',      'no0',      ],
        }
        # Energy carrier database
        self.data['e_data'] = {
            'ener': ['elec',    'dhea',     'ngas'      ],
            'tfrq': ['hourly',  'hourly',   'yearly'    ],
        }
        # Energy carrie / region database
        self.data['er_data'] = {
            'ener': ['elec',    'elec',    'elec',    'dhea',    'dhea',    'dhea',    ],
            'regn': ['dk0',     'de0',     'no0',     'dk0',     'de0',     'no0',     ],
            'lFin': [40.00,     400.0,     40.00,     0.00,      0.0,       0.00,      ],
            'vFin': ['varElec', 'varElec', 'varElec', 'varDHea', 'varDHea', 'varDHea', ],
        }
        # Asset database
        self.data['a_data'] = {
            # Asset name (duplicates as Asset set)
            'asst': ['bpgt_dk0','bpgt_de0','bpgt_no0','wind_dk0','wind_de0','wind_no0','sopv_dk0','sopv_de0','sopv_no0',],
            # Role: tfrm: transformation, tmis: transmission, stor: storage
            'role': ['tfrm',    'tfrm',    'tfrm',    'prim',    'prim',    'prim',    'prim',    'prim',    'prim',    ],
            # Region of location
            'regn': ['dk0',     'de0',     'no0',     'dk0',     'de0',     'no0',     'dk0',     'de0',     'no0',     ],
            # Destination of transmission if applicable
            'dest': ['',        '',        '',        '',        '',        '',        '',        '',        '',        ],
            # Capital expenditure, money/MW
            'cstC': [1.00,      1.00,      1.00,      2.00,      2.00,      2.00,      1.00,      1.00,      1.00,      ],
            # Fixed operational expenditure, money/MW/year
            'cstF': [50000,     50000,     50000,     50000,     50000,     50000,     25000,     25000,     25000,     ],
            # Variable operational costs, money/MWh
            'cstV': [1,         1,         1,         1,         1,         1,         0,         0,         0,         ],
            # Ratio between capacity of S and V for storaage
            'ratSV':[0,         0,         0,         0,         0,         0,         0,         0,         0,         ],
            # Ratio between capacity of D and V for storaage
            'ratDV':[0,         0,         0,         0,         0,         0,         0,         0,         0,         ],
            # Availability choice, % per hour/week/year
            'vAva': ['uniform' ,'uniform' ,'uniform' ,'wind_dk', 'wind_de', 'wind_no', 'dayonly', 'dayonly', 'dayonly', ],
        }
        # Asset/energy carrier database
        self.data['ae_data'] = {
            # Asset name
            'asst': ['bpgt_dk0','bpgt_de0','bpgt_no0','bpgt_dk0','bpgt_de0','bpgt_no0','bpgt_dk0','bpgt_de0','bpgt_no0',
                     'wind_dk0','wind_de0','wind_no0','sopv_dk0','sopv_de0','sopv_no0',],
            # Energy carrier
            'ener': ['elec',    'elec',    'elec',    'dhea',    'dhea',    'dhea',    'ngas',    'ngas',    'ngas',
                     'elec',    'elec',    'elec',    'elec',    'elec',    'elec',],
            # Efficiency by energy carrier, share of total energy input
            # Negative means energy input, positive means energy output
            'effi': [0.45,      0.45,      0.45,      0.55,      0.55,      0.55,      -1.00,     -1.00,     -1.00,
                     1.00,      1.00,      1.00,      1.00,      1.00,      1.00,      ],
        }
        # 6 hour intervals across 1 week = 4x7 = 28 hours/week
        self.data['h_data'] = {
            'hour': ['h003','h009','h015','h021','h027','h033','h039','h045','h051','h057','h063','h069',
                     'h075','h081','h087','h093','h099','h105','h111','h117','h123','h129','h135','h141',
                     'h147','h153','h159','h165',],
        }
        self.data['w_data'] = {
            'week': ['w01']
        }
        self.data['wh_data'] = {
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
        # Yearly Asset data - index: (tech,year)
        self.data['ay_data'] = {
            'asst':     ['bpgt_dk0','bpgt_de0','bpgt_no0','wind_dk0','wind_de0','wind_no0','sopv_dk0','sopv_de0','sopv_no0',],
            'year':     ['y2020',   'y2020',   'y2020',   'y2020',   'y2020',   'y2020',   'y2020',   'y2020',   'y2020',   ],
            'iniC':     [1000,      1000,      1000,      1000,      1000,      1000,      1000,      1000,      1000,      ],
            'maxC':     [1000,      1000,      1000,      1000,      1000,      1000,      1000,      1000,      1000,      ],
        }
