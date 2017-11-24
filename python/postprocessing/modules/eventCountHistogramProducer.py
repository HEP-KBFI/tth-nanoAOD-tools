import ROOT
import array
ROOT.PyConfig.IgnoreCommandLineOptions = True

from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import Collection
from PhysicsTools.NanoAODTools.postprocessing.framework.eventloop import Module

class eventCountHistogramProducer(Module):

  def __init__(self):
    self.runTreeName = 'Runs'
    self.count = {
      'branchIn'  : 'genEventCount',
      'branchArr' : array.array('L', [0]), # Long64_t
      'histoOut'  : 'Count',
    }
    self.countWeighted = {
      'branchIn'  : 'genEventSumw',
      'branchArr' : array.array('d', [0.]), # Double_t
      'histoOut'  : 'CountWeighted',
    }
    self.countTypes = [ self.count, self.countWeighted ]

  def beginJob(self):
    pass

  def endJob(self):
    pass

  def beginFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
    runTree = inputFile.Get(self.runTreeName)
    if not runTree:
      raise ValueError('No such object in file %s: %s' % (inputFile.GetName(), self.runTreeName))

    runTree_branches = [br.GetName() for br in runTree.GetListOfBranches()]
    for countType in self.countTypes:
      if countType['branchIn'] not in runTree_branches:
        raise ValueError("No branch named '%s' in tree '%s'" % (countType['branchIn'], self.runTreeName))

      runTree.SetBranchAddress(countType['branchIn'], countType['branchArr'])
      countType['histogram'] = ROOT.TH1F(countType['histoOut'], countType['histoOut'], 1, 0., 2.)

    nofEntries = runTree.GetEntries()
    for idx in range(nofEntries):
      runTree.GetEntry(idx)
      for countType in self.countTypes:
        countType['histogram'].Fill(1, countType['branchArr'][0])

    outputFile.cd()
    for countType in self.countTypes:
      countType['histogram'].Write()

  def endFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
    pass

  def analyze(self, event):
    return True

# provide this variable as the 2nd argument to the import option for the nano_postproc.py script
eventCountHistogram = lambda : eventCountHistogramProducer()
