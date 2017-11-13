import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True

from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import Collection
from PhysicsTools.NanoAODTools.postprocessing.framework.eventloop import Module

'''This module adds missing branches which will be hopefully soon available
'''

class missingProducer(Module):

  def __init__(self):
    self.eleBranch = "Electron"
    self.eleDEta = "%s_%s" % (self.eleBranch, "eleDEta") # deltaEtaSuperClusterTrackAtVtx
    self.eleDPhi = "%s_%s" % (self.eleBranch, "eleDPhi") # deltaPhiSuperClusterTrackAtVtx
    self.nele    = "n%s" % self.eleBranch

  def beginJob(self):
    pass

  def endJob(self):
    pass

  def beginFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
    self.out = wrappedOutputTree
    self.out.branch(self.eleDEta, "F", lenVar = self.nele)
    self.out.branch(self.eleDPhi, "F", lenVar = self.nele)

  def endFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
    pass

  def analyze(self, event):
    eles = Collection(event, self.eleBranch)
    self.out.fillBranch(self.eleDEta, [0.] * len(eles))
    self.out.fillBranch(self.eleDPhi, [0.] * len(eles))
    return True

# provide this variable as the 2nd argument to the import option for the nano_postproc.py script
missing = lambda : missingProducer()
