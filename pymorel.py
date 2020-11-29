from data import PyMorelData
from model import PyMorelModel

data = PyMorelData()
model = PyMorelModel(data)
model.solve()
model.report()
