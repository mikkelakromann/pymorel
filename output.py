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

        # For transformation variable, merge on input and output energy carriers, one row per carrier
        # print(self.input.te)
        # print(Th)

        # Create hourly activity dataframe with all values from hourly variables
        act_h = pandas.concat([Ph,Th,Xh,Ih,Sh,Dh,Vh])
        # Unpack the index tuple of (tech, week, hour) to separate columns
        act_h['asst'], act_h['week'], act_h['hour'] = zip(*act_h.index)
        # Merge energy carrier and efficiency on technologies
        act_h = act_h.merge(self.input.ae[['asst','ener','effe']], on='asst')
        # Merge region into act_h
        act_h = act_h.merge(self.input.a[['asst','role','regn','dest']], on='asst')
        # Calculate effect
        act_h['efct'] = act_h['effe']*act_h['level']
        pandas.set_option('display.max_rows', 1000)
        print(act_h)
        bal_y = act_h[['regn','role','ener','efct']].groupby(['regn','role','ener']).sum()
        print(bal_y)

