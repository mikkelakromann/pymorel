import pandas


class PyMorelOutput():
    """Class for organising output from PyMorel model."""

    def __init__(self,pymorel_model):
        """Initialise output object."""
        self.model = pymorel_model.model        # Pyomo model object
        self.input = pymorel_model.data         # PyMorel input data object
        self.read_hourly_variables()
        self.set_balances()

    def read_hourly_variables(self):
        """Read model variables into dataframes."""
        Ph = pandas.DataFrame.from_dict(self.model.Ph.extract_values(), orient='index', columns=['level'])
        Th = pandas.DataFrame.from_dict(self.model.Th.extract_values(), orient='index', columns=['level'])
        Xh = pandas.DataFrame.from_dict(self.model.Xh.extract_values(), orient='index', columns=['level'])
        Ih = pandas.DataFrame.from_dict(self.model.Ih.extract_values(), orient='index', columns=['level'])
        Sh = pandas.DataFrame.from_dict(self.model.Sh.extract_values(), orient='index', columns=['level'])
        Dh = pandas.DataFrame.from_dict(self.model.Dh.extract_values(), orient='index', columns=['level'])
        Vh = pandas.DataFrame.from_dict(self.model.Vh.extract_values(), orient='index', columns=['level'])

        # Add variable name for later use when these tables are concatenated
        Ph['var'] = 'Ph'
        Th['var'] = 'Th'
        Xh['var'] = 'Xh'
        Ih['var'] = 'Ih'
        Sh['var'] = 'Sh'
        Dh['var'] = 'Dh'
        Vh['var'] = 'Vh'

        # Create hourly activity dataframe with all values from hourly variables
        activity_h = pandas.concat([Ph,Th,Xh,Ih,Sh,Dh,Vh])
        # Unpack the index tuple of (tech, week, hour) to separate columns
        activity_h['asst'], activity_h['week'], activity_h['hour'] = zip(*activity_h.index)
        # Merge energy carrier and efficiency on technologies
        activity_h = activity_h.merge(self.input.ae[['asst','ener','effi']], on='asst')
        # Merge region into act_h
        activity_h = activity_h.merge(self.input.a[['asst','role','rgio','dest']], on='asst')

        # Add data to Fh (m.fin_h[e,r,w,h]) which are not present since final consumption are not assets
        Fh = pandas.DataFrame.from_dict(self.model.fin_h.extract_values(), orient='index', columns=['level'])
#        Fh = pandas.DataFrane(['level','var','ener','rgio','week','hour','role','asst','dest','effi',])
        Fh['var'] = 'Fh'
        Fh['asst'] = 'demand'
        Fh['week'] = ''
        Fh['hour'] = ''
        Fh['ener'] = ''
        Fh['effi'] = -1
        Fh['role'] = 'fcon'
        Fh['rgio'] = ''
        Fh['dest'] = ''
        Fh['ener'], Fh['rgio'], Fh['week'], Fh['hour'] = zip(*Fh.index)
        Fh.reset_index(drop=True, inplace=True)
        activity_h = pandas.concat([activity_h,Fh])

        # Calculate effect and energy for each variable
        activity_h['efct'] = activity_h['effi']*activity_h['level']
        weight = 1 + 0*365.25*24/(len(self.model.H)*len(self.model.H))
        scale_engy = 1000
        activity_h['engy'] = activity_h['efct'] * weight / scale_engy
        self.activity_h = activity_h

    def set_balances(self):
        """Calculate energy balance tables from activity tables"""

        balance_h = self.activity_h[['rgio','role','ener','engy']].groupby(['rgio','role','ener']).sum()
        balance_h_ener = pandas.pivot_table(self.activity_h, values='engy', index=['rgio','role'], columns=['ener'])
        print(balance_h)
        print(balance_h_ener)
