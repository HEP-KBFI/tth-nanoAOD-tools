import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True

from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import Collection
from PhysicsTools.NanoAODTools.postprocessing.framework.eventloop import Module

# Possible values of the decay modes in case the event has one Higgs boson:
#      3 H -> s sbar
#      4 H -> c cbar
#      5 H -> b bbar
#     13 H -> mu+ mu-
#     15 H -> tau+ tau-
#     21 H -> glu glu
#     22 H -> gamma gamma
#     23 H -> Z Z
#     24 H -> W+ W-
# 220023 H -> Z gamma
#
# Possible values of the decay modes in case the event has two Higgs bosons and HH -> 4tau/2V2tau/4V and V = W or Z:
#       15 H -> tau+ tau- tau+ tau-
#       23 H -> Z Z Z Z
#       24 H -> W+ W- W+ W-
# 15000023 H -> tau+ tau- Z Z
# 15000024 H -> tau+ tau- W+ W-
# 23000024 H -> Z Z W+ W-
#
# Possible values of the decay modes in case the event has two Higgs bosons and HH -> bbVV and V = W or Z:
# 5000023 H -> b bbar Z Z
# 5000024 H -> b bbar W+ W-

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

    higgses = sorted(set(map(lambda genPartPair: genPartPair[0], filter(
      lambda genPart:
        genPart[1].pdgId == 25 and \
        (genParticles[genPart[1].genPartIdxMother].pdgId != 25 if genPart[1].genPartIdxMother >= 0 else True),
      enumerate(genParticles)
    ))))
    nofHiggs = len(higgses)

    decayModeVals = []
    if 0 < nofHiggs < 3:
      for idxHiggs in range(nofHiggs):
        higgs_daus = [  ]
        higgs_idx = higgses[idxHiggs]
        while True:
          for idx, genPart in enumerate(genParticles):
            if genPart.genPartIdxMother == higgs_idx:
              if genPart.pdgId == 25:
                higgs_idx = idx
                break
              else:
                higgs_daus.append(idx)
          if len(higgs_daus) == 2:
            break
        higgs_daus_pdgId = list(sorted(set(map(lambda idx: abs(genParticles[idx].pdgId), higgs_daus)), reverse = True))
        decayModeVal = sum(map(lambda pdgId: pdgId[1] * 10**(4 * pdgId[0]), enumerate(higgs_daus_pdgId)))
        decayModeVals.append(decayModeVal)

    genHiggsDecayModeVal = sum(map(
      lambda decMode: decMode[1] * 10**(6 * decMode[0]), enumerate(sorted(set(decayModeVals), reverse = True))
    ))

    self.out.fillBranch(self.genHiggsDecayModeName, genHiggsDecayModeVal)
    return True

# provide this variable as the 2nd argument to the import option for the nano_postproc.py script
genHiggsDecayMode = lambda : genHiggsDecayModeProducer()
