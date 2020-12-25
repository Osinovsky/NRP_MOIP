from src.NRP import NextReleaseProblem
from src.util.ObjectiveSpace import ObjectiveSpace3D


nrp = NextReleaseProblem('MSWord')
nrp.premodel({})
problem = nrp.model('triple', {})

space = ObjectiveSpace3D(problem)
s, p = space.HR_sample()
print(s, p)
