import unittest

from inputdata import PyMorelInputData
from output import PyMorelOutput
from model import PyMorelModel

# INTRODUCTION
#
# Note: These tests are integration tests aiming for success rather than unit test.
# ToDo: Create framework for checking for bad user data and do unit test on that

# USAGE: Run the tests from a prompt in the base pymorel directory
#        using the command:> python -m unittest discover
#        This will run all tests in the subfolder 'pymorel/tests'

# This input dict is in the format needed by PyMorelInputData.load_from_dict()
# Base model structure: 1 region, 1 technology, 1 energy carrier, 1 asset
I_1r1e1a1w4h = {
    'r_data':   {'rgio': ['dk_0'],},        # Region data
    'e_data':   {'ener': ['elec'],          # Energy carrier data
                 'tfrq': ['hour']},
    'er_data':  {'ener': ['elec'],          # Region data by energy carrier
                 'rgio': ['dk_0'],
                 'lFin': [1],               # Effect (energy per second)
                 'vFin': ['uniform'], },
    'a_data':   {'asst': ['sopv_dk0'],      # Asset data
                 'role': ['prim'],
                 'rgio': ['dk_0'],
                 'dest': [''],
                 'cstC': [2000],
                 'cstF': [20],
                 'cstV': [0],
                 'vAva': ['sol_DK'], },
    'ae_data':  {'asst': ['sopv_dk0'],      # Asset / energy carrier data
                 'ener': ['elec'],
                 'effi': [1.000], },
    'ay_data':  {'asst': ['sopv_dk0'],      # Asset / year data
                 'year': ['y2020',],
                 'iniC': [1000,],           # Effect (energy per second)
                 'maxC': [1000,], },        # Effect (energy per second)
    'w_data':   {'week':     ['w001',],},                           # Weeks
    'h_data':   {'hour':     ['h003','h009','h015','h021',], },     # Hours
    'wh_data':  {'week':     ['w001','w001','w001','w001',],        # Week/hour data
                 'hour':     ['h003','h009','h015','h021',],        # e.g. time variation
                 'uniform':  [1,      1,       1,     1],
                 'sol_DK':   [0,      0.9,     1,     0],
                 'varElec':  [0.5,    0.8,     1,     0.6],}
}

I_1r2e2a1w4h = {
    'r_data':   {'rgio': ['dk_0'],},
    'e_data':   {'ener': ['elec','heat'],
                 'tfrq': ['hour','hour']},
    'er_data':  {'ener': ['elec','heat'],
                 'rgio': ['dk_0','dk_0'],
                 'lFin': [1,      1],
                 'vFin': ['uniform','uniform'], },
    'a_data':   {'asst': ['sopv_dk0','hpmp_dk0'],
                 'role': ['prim','tfrm'],
                 'rgio': ['dk_0','dk_0'],
                 'dest': ['',    ''],
                 'cstC': [2000,   2000],
                 'cstF': [20,     30],
                 'cstV': [0,      2],
                 'vAva': ['sol_DK','uniform'], },
    'ae_data':  {'asst': ['sopv_dk0','hpmp_dk0','hpmp_dk0'],
                 'ener': ['elec',    'elec',    'heat'],
                 'effi': [1.000,     -1.000,    3.000], },
    'ay_data':  {'asst': ['sopv_dk0', 'hpmp_dk0'],
                 'year': ['y2020',    'y2020'],
                 'iniC': [1000,       1000],
                 'maxC': [1000,       1000], },
    'w_data':   {'week':     ['w001',],},
    'h_data':   {'hour':     ['h003','h009','h015','h021',], },
    'wh_data':  {'week':     ['w001','w001','w001','w001',],
                 'hour':     ['h003','h009','h015','h021',],
                 'uniform':  [1,      1,       1,     1],
                 'sol_DK':   [0,      0.9,     1,     0],
                 'varElec':  [0.5,    0.8,     1,     0.6],}
}


def run_with_dict(d):
    """Run PyMorel with inputdata dict d, return PyMorelOutput."""
    pymorel_inputdata = PyMorelInputData()
    pymorel_inputdata.load_data_from_dict(d)
    pymorel_model = PyMorelModel(pymorel_inputdata)
    pymorel_model.solve()
    return PyMorelOutput(pymorel_model)


class Test1Region1Energy1asset(unittest.TestCase):

    def test_1r1e1a1w4h(self):
        """1 Region, 1 Energy Carrier, 1 Asset, 1 Week, 4 hours."""
        print('Testing 1 region, 1 energy carrier, 1 asset, 4 hours')
        self.output = run_with_dict(I_1r1e1a1w4h)
        bal_h = self.output.balance_h
        # First check final consumption - INPUT_DICT say 1MW, so (annual) final
        # consumption should be -1*365.25*24/1000 GWh
        fcon = bal_h.query("rgio == 'dk_0' and ener == 'elec' and role == 'fcon'").engy.sum()
        self.assertEqual(fcon,-365.25*24)
        # Then check primary energy consumption, should be equal to minus fcon
        prim = bal_h.query("rgio == 'dk_0' and ener == 'elec' and role == 'prim'").engy.sum()
        self.assertEqual(prim,-fcon)

    def test_1r2e2a1w4h(self):
        """1 Region, 2 Energy Carriers, 2 Assets, 1 Week, 4 hours."""
        # We add heat as energy carrier and a heat pump as asset
        print('Testing 1 region, 1 energy carrier, 1 asset, 4 hours')
        self.output = run_with_dict(I_1r2e2a1w4h)
        bal_h = self.output.balance_h
        print(bal_h)
        # First check final consumption - INPUT_DICT say 1MW, so (annual) final
        # consumption should be -1*365.25*24/1000 GWh
        fcon_e = bal_h.query("rgio == 'dk_0' and ener == 'elec' and role == 'fcon'").engy.sum()
        # Heat is also 1MW all hours of year
        self.assertEqual(fcon_e,-365.25*24)
        fcon_h = bal_h.query("rgio == 'dk_0' and ener == 'elec' and role == 'fcon'").engy.sum()
        self.assertEqual(fcon_h,-365.25*24)
        # Transformation outputs elec = fcon_h
        tfrm_h = bal_h.query("rgio == 'dk_0' and ener == 'heat' and role == 'tfrm'").engy.sum()
        self.assertEqual(round(tfrm_h,6),round(365.25*24,6))
        # Transformation inputs elec = fcon_h/3 as ae_data (COP) is set to 300%
        tfrm_e = bal_h.query("rgio == 'dk_0' and ener == 'elec' and role == 'tfrm'").engy.sum()
        self.assertEqual(tfrm_e,-tfrm_h/3)
        # Then check primary energy consumption, should be equal to minus fcon_e + fcon_h/3
        prim = bal_h.query("rgio == 'dk_0' and ener == 'elec' and role == 'prim'").engy.sum()
        self.assertEqual(round(prim,6),round(-fcon_e-fcon_h/3,6))
