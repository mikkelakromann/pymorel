from inputdata import PyMorelInputData
from model import PyMorelModel
from inputdatadict import InputDataDict

pymorel_inputdata_dict = InputDataDict()
pymorel_inputdata = PyMorelInputData()
pymorel_inputdata.load_data_from_dict(pymorel_inputdata_dict.data)
pymorel_model = PyMorelModel(pymorel_inputdata)
pymorel_model.solve()
pymorel_model.report()
# pymorel_outputdata = pymorel_model.outputdata()
