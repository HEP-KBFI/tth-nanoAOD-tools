import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True

from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import Collection
from PhysicsTools.NanoAODTools.postprocessing.framework.eventloop import Module

class genLeptonCollectionMerger(Module):

  def __init__(self):
    self.branchBaseName = "GenLep"
    self.genLeptonBranches = {
      "pt"    : "F",
      "eta"   : "F",
      "phi"   : "F",
      "mass"  : "F",
      "pdgId" : "I",
    }
    self.branchLenName = "n%s" % self.branchBaseName

  def beginJob(self):
    pass

  def endJob(self):
    pass

  def beginFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
    self.out = wrappedOutputTree
    for branchName, branchType in self.genLeptonBranches.items():
      self.out.branch(
        "%s_%s" % (self.branchBaseName, branchName),
        branchType,
        lenVar = self.branchLenName
      )

  def endFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
    pass

  def analyze(self, event):
    genParticles = Collection(event, "GenPart")
    genLepton_arr = filter(
      lambda genPart: abs(genPart.pdgId) in [11, 13] and genPart.status == 1,
      genParticles
    )

    for branchName, branchType in self.genLeptonBranches.items():
      self.out.fillBranch(
        "%s_%s" % (self.branchBaseName, branchName),
        map(lambda genPart: getattr(genPart, branchName), genLepton_arr)
      )
    return True

# provide this variable as the 2nd argument to the import option for the nano_postproc.py script
genLepMerger = lambda : genLeptonCollectionMerger()
