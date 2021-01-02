import pandas


class PyMorelOutput():
    """Class for organising output from PyMorel model."""

    def __init__(self,pymorel_model):
        """Initialise output object."""
        self.model = pymorel_model.model        # Pyomo model object
        self.input = pymorel_model.data         # PyMorel input data object
        self.read_hourly_variables()

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
        act_h = pandas.concat([Ph,Th,Xh,Ih,Sh,Dh,Vh])
        # Unpack the index tuple of (tech, week, hour) to separate columns
        act_h['asst'], act_h['week'], act_h['hour'] = zip(*act_h.index)
        # Merge energy carrier and efficiency on technologies
        act_h = act_h.merge(self.input.ae[['asst','ener','effi']], on='asst')
        # Merge region into act_h
        act_h = act_h.merge(self.input.a[['asst','role','regn','dest']], on='asst')

        # Add data to Fh (m.fin_h[e,r,w,h]) which are not present since final consumption are not assets
        Fh = pandas.DataFrame.from_dict(self.model.fin_h.extract_values(), orient='index', columns=['level'])
#        Fh = pandas.DataFrane(['level','var','ener','regn','week','hour','role','asst','dest','effi',])
        Fh['var'] = 'Fh'
        Fh['asst'] = 'demand'
        Fh['week'] = ''
        Fh['hour'] = ''
        Fh['ener'] = ''
        Fh['effi'] = -1
        Fh['role'] = 'fcon'
        Fh['regn'] = ''
        Fh['dest'] = ''
        Fh['ener'], Fh['regn'], Fh['week'], Fh['hour'] = zip(*Fh.index)
        Fh.reset_index(drop=True, inplace=True)
        pandas.set_option('display.max_rows', 10)
        act_h = pandas.concat([act_h,Fh])
        print(Fh)


        # Calculate effect
        act_h['efct'] = act_h['effi']*act_h['level']
        weight = 1 + 0*365.25*24/(len(self.model.H)*len(self.model.H))
        scale_engy = 1000
        act_h['engy'] = act_h['efct'] * weight / scale_engy
        print(act_h)
#        temp_bal_y = act_h[['regn','role','ener','engy']].groupby(['regn','role','ener']).sum()
        bal_y = pandas.pivot_table(act_h, values='engy', index=['regn','role'], columns=['ener'], aggfunc=sum)
        print(bal_y)

