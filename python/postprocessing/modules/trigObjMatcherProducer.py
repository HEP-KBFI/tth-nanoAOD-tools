import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True

from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import Collection
from PhysicsTools.NanoAODTools.postprocessing.framework.eventloop import Module

import math

class trigObjMatcherProducer(Module):

  def __init__(self):
    self.trigObjBranchName = 'TrigObj'
    self.muBranchName      = 'Muon'
    self.eleBranchName     = 'Electron'
    self.tauBranchName     = 'Tau'

    self.isTrigObjMatchedBranchName = 'filterBits'
    self.isTrigObjMuMatchedBranchName  = '%s_%s' % (self.muBranchName,  self.isTrigObjMatchedBranchName)
    self.isTrigObjEleMatchedBranchName = '%s_%s' % (self.eleBranchName, self.isTrigObjMatchedBranchName)
    self.isTrigObjTauMatchedBranchName = '%s_%s' % (self.tauBranchName, self.isTrigObjMatchedBranchName)

  def beginJob(self):
    pass

  def endJob(self):
    pass

  def beginFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
    self.out = wrappedOutputTree
    self.out.branch(self.isTrigObjMuMatchedBranchName,  'i', lenVar = 'n%s' % self.muBranchName)
    self.out.branch(self.isTrigObjEleMatchedBranchName, 'i', lenVar = 'n%s' % self.eleBranchName)
    self.out.branch(self.isTrigObjTauMatchedBranchName, 'i', lenVar = 'n%s' % self.tauBranchName)

  def endFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
    pass

  def is_dR_matched(self, obj1, obj2, maxDr = 5e-2):
    return math.sqrt((obj1.eta - obj2.eta)**2 + (obj1.phi - obj2.phi)**2) < maxDr

  def analyze(self, event):
    trigObjs = Collection(event, self.trigObjBranchName)
    mus      = Collection(event, self.muBranchName)
    eles     = Collection(event, self.eleBranchName)
    taus     = Collection(event, self.tauBranchName)

    mus_isMatched  = [0] * len(mus)
    eles_isMatched = [0] * len(eles)
    taus_isMatched = [0] * len(taus)

    for trigObj in trigObjs:
      trigObjID         = trigObj.id
      trigObjFilterBits = trigObj.filterBits

      if trigObjID == 13:
        for idx, mu in enumerate(mus):
          if self.is_dR_matched(trigObj, mu):
            mus_isMatched[idx] |= trigObjFilterBits

      elif trigObjID == 11:
        for idx, ele in enumerate(eles):
          if self.is_dR_matched(trigObj, ele):
            if not eles_isMatched[idx]:
              eles_isMatched[idx] |= trigObjFilterBits

      elif trigObjID == 15:
        for idx, tau in enumerate(taus):
          if self.is_dR_matched(trigObj, tau):
            taus_isMatched[idx] |= trigObjFilterBits

    self.out.fillBranch(self.isTrigObjMuMatchedBranchName,  mus_isMatched)
    self.out.fillBranch(self.isTrigObjEleMatchedBranchName, eles_isMatched)
    self.out.fillBranch(self.isTrigObjTauMatchedBranchName, taus_isMatched)
    return True

# provide this variable as the 2nd argument to the import option for the nano_postproc.py script
trigObjMatcher = lambda : trigObjMatcherProducer()
