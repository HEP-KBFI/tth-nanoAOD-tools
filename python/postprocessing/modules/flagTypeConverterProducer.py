import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True

from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import Collection, Object
from PhysicsTools.NanoAODTools.postprocessing.framework.eventloop import Module

class flagTypeConverterProducer(Module):

    def __init__(self):
        self.branchNames = [
          'Flag_ecalBadCalibFilterV2',
        ]

    def getOutputBranchName(self, branchName):
      return '%s_bool' % branchName

    def beginJob(self):
        pass

    def endJob(self):
        pass

    def beginFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
        self.out = wrappedOutputTree
        for branchName in self.branchNames:
          self.out.branch(self.getOutputBranchName(branchName),  "O") # "O" means Bool_t

    def endFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
        pass

    def analyze(self, event):
        for branchName in self.branchNames:
          self.out.fillBranch(self.getOutputBranchName(branchName), bool(getattr(event, branchName)))

        return True

# provide this variable as the 2nd argument to the import option for the nano_postproc.py script
flagTypeConverter = lambda : flagTypeConverterProducer()
