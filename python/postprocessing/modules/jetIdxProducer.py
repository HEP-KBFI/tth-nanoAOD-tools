import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True

from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import Collection
from PhysicsTools.NanoAODTools.postprocessing.framework.eventloop import Module

class jetIdxProducer(Module):
  def __init__(self, jetBr = 'Jet'):
    self.jetBr = jetBr
    self.jetIdxBr = '{}_jetIdx'.format(self.jetBr)

  def beginJob(self):
    pass

  def endJob(self):
    pass

  def beginFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
    self.out = wrappedOutputTree
    self.out.branch(self.jetIdxBr, 'I', lenVar = 'n{}'.format(self.jetBr))

  def endFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
    pass

  def analyze(self, event):
    jetIdxs = list(range(len(Collection(event, self.jetBr))))
    self.out.fillBranch(self.jetIdxBr, jetIdxs)

    return True

jetIdx = lambda : jetIdxProducer()
jetAK4LSLooseIdx = lambda : jetIdxProducer(jetBr = 'JetAK4LSLoose')
