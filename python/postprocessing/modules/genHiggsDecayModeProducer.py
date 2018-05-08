import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True

from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import Collection
from PhysicsTools.NanoAODTools.postprocessing.framework.eventloop import Module

class genHiggsDecayModeProducer(Module):

  def __init__(self):
    self.genHiggsDecayModeName = "genHiggsDecayMode"

  def beginJob(self):
    pass

  def endJob(self):
    pass

  def beginFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
    self.out = wrappedOutputTree
    self.out.branch(self.genHiggsDecayModeName, "I")

  def endFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
    pass

  def analyze(self, event):
    genParticles = Collection(event, "GenPart")

    genHiggsDecayModeVal = 0
    nofHiggs = len(list(filter(
      lambda genPart:
        genPart.pdgId == 25 and \
        (genParticles[genPart.genPartIdxMother].pdgId != 25 if genPart.genPartIdxMother >= 0 else True),
      genParticles
    )))

    if nofHiggs == 1:
      h0_daus = list(filter(
        lambda genParticle: genParticle.genPartIdxMother >= 0 and \
                            genParticles[genParticle.genPartIdxMother].pdgId == 25 and \
                            genParticle.pdgId != 25,
        genParticles
      ))
      genHiggsDecayModeVal  = abs(h0_daus[0].pdgId if len(h0_daus) >= 1 else 0)
      genHiggsDecayModeVal += abs(h0_daus[1].pdgId if len(h0_daus) >= 2 and \
                                                      abs(h0_daus[0].pdgId) != abs(h0_daus[1].pdgId) else 0) * 10000

    self.out.fillBranch(self.genHiggsDecayModeName, genHiggsDecayModeVal)
    return True

# provide this variable as the 2nd argument to the import option for the nano_postproc.py script
genHiggsDecayMode = lambda : genHiggsDecayModeProducer()
