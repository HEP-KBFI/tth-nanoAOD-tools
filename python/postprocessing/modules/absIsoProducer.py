import math
import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True

from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import Collection
from PhysicsTools.NanoAODTools.postprocessing.framework.eventloop import Module

def get_allIsoBranchNames(relBrNeu):
  relBrAll = relBrNeu.replace('_neu', '_all')
  relBrChg = relBrNeu.replace('_neu', '_chg')
  absBrNeu = relBrNeu.replace('Rel', 'Abs')
  absBrAll = relBrAll.replace('Rel', 'Abs')
  absBrChg = relBrChg.replace('Rel', 'Abs')

  return (relBrAll, relBrChg, relBrNeu, absBrAll, absBrChg, absBrNeu)

class absIsoProducer(Module):

  def __init__(self):
    self.elBr_base = "Electron"
    self.muBr_base = "Muon"
    self.elCorr = "eCorr"

    self.relBranches_all = [
      "miniPFRelIso_all",
      "pfRelIso03_all",
    ]
    self.relBranches_chg = [
      "miniPFRelIso_chg",
      "pfRelIso03_chg",
    ]
    self.relBranches_neu = list(map(lambda brName: brName.replace('_chg', '_neu'), self.relBranches_chg))

  def beginJob(self):
    pass

  def endJob(self):
    pass

  def beginFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
    self.out = wrappedOutputTree
    for lepBr in [self.elBr_base, self.muBr_base]:
      for relBrNeu in self.relBranches_neu:
        allBrNames = get_allIsoBranchNames(relBrNeu)
        for brName in allBrNames:
          self.out.branch("%s_%s" % (lepBr, brName), "F", lenVar = "n%s" % lepBr)

  def endFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
    pass

  def analyze(self, event):
    for lepBr_base in [self.elBr_base, self.muBr_base]:
      leps = Collection(event, lepBr_base)
      isElectron = lepBr_base == self.elBr_base
      ptCorrFactors = [getattr(lep, self.elCorr) for lep in leps] if isElectron else ([1.] * len(leps))
      ptCorrs = [pt / ptCorrFactor for pt, ptCorrFactor in zip([lep.pt for lep in leps], ptCorrFactors)]

      for relBrNeu in self.relBranches_neu:

        allBrNames = get_allIsoBranchNames(relBrNeu)
        relBrAll, relBrChg, relBrNeu, absBrAll, absBrChg, absBrNeu = allBrNames

        relAlls = map(lambda lep: getattr(lep, relBrAll), leps)
        relChgs = map(lambda lep: getattr(lep, relBrChg), leps)
        relNeus = [relAll - relChg for relAll, relChg in zip(relAlls, relChgs)]

        absAlls = [relAll * ptCorr for relAll, ptCorr in zip(relAlls, ptCorrs)]
        absChgs = [relChg * ptCorr for relChg, ptCorr in zip(relChgs, ptCorrs)]
        absNeus = [relNeu * ptCorr for relNeu, ptCorr in zip(relNeus, ptCorrs)]

        for brName, isoArr in zip(allBrNames, [relAlls, relChgs, relNeus, absAlls, absChgs, absNeus]):
          self.out.fillBranch("%s_%s" % (lepBr_base, brName), isoArr)

    return True

# provide this variable as the 2nd argument to the import option for the nano_postproc.py script
absIso = lambda : absIsoProducer()
