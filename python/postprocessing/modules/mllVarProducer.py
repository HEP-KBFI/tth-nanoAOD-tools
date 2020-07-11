import ROOT

ROOT.PyConfig.IgnoreCommandLineOptions = True

from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import Collection
from PhysicsTools.NanoAODTools.postprocessing.framework.eventloop import Module

class mllVarProducer(Module):

    def __init__(self, mode):
        modes = {
            'wzto3lnu'          : { 'idxs' : [ 2, 3 ], 'min_mll' : -1. },
            'wzto3lnu_mllmin01' : { 'idxs' : [ 4, 5 ], 'min_mll' :  4. },
        }
        if mode not in modes:
            raise ValueError("No such mode available: %s" % mode)
        choice = modes[mode]
        leptonIdxs = choice['idxs']
        self.minCollectionSize = max(leptonIdxs) + 1
        self.firstLeptonIdx = leptonIdxs[0]
        self.secondLeptonIdx = leptonIdxs[1]
        self.lhePartName = 'LHEPart'
        self.mllBranchName = 'LHE_mll'
        self.min_mll = choice['min_mll']

    def beginJob(self):
        pass

    def endJob(self):
        pass

    def beginFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
        self.out = wrappedOutputTree
        self.out.branch(self.mllBranchName, "F")

    def endFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
        pass

    def analyze(self, event):

        lheParts = Collection(event, self.lhePartName)
        if len(lheParts) < self.minCollectionSize:
            raise RuntimeError("Expected at least %d LHE particles, got only %d" % (self.minCollectionSize, len(lheParts)))

        firstLHEPart = lheParts[self.firstLeptonIdx]
        secondLHEPart = lheParts[self.secondLeptonIdx]
        if firstLHEPart.pdgId != -secondLHEPart.pdgId:
            raise RuntimeError("Incompatible PDG IDs detected: %d and %d" % (firstLHEPart.pdgId, secondLHEPart.pdgId))

        lep1 = ROOT.TLorentzVector()
        lep1.SetPtEtaPhiM(firstLHEPart.pt, firstLHEPart.eta, firstLHEPart.phi, firstLHEPart.mass)
        lep2 = ROOT.TLorentzVector()
        lep2.SetPtEtaPhiM(secondLHEPart.pt, secondLHEPart.eta, secondLHEPart.phi, secondLHEPart.mass)
        lepSum = lep1 + lep2
        mll = lepSum.M()
        assert(mll > 0.)

        self.out.fillBranch(self.mllBranchName, mll)

        return (self.min_mll > 0. and mll >= self.min_mll) or self.min_mll < 0.


# provide this variable as the 2nd argument to the import option for the nano_postproc.py script
mllWZTo3LNu          = lambda: mllVarProducer(mode = 'wzto3lnu')
mllWZTo3LNu_mllmin01 = lambda: mllVarProducer(mode = 'wzto3lnu_mllmin01')
