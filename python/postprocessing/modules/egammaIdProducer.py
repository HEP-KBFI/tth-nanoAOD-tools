import ROOT
import math, os
ROOT.PyConfig.IgnoreCommandLineOptions = True

from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import Collection, Object
from PhysicsTools.NanoAODTools.postprocessing.framework.eventloop import Module

class egammaIdProducer(Module):

    def __init__(self):
        self.electronBranchName = "Electron"
        self.electronLenBranchName = "n%s" % self.electronBranchName
        self.mvaSpring16GP_branchName = "mvaSpring16GP"
        self.mvaSpring16HZZ_branchName = "mvaSpring16HZZ"
        self.mvaRaw_POG_branchName = "%s_mvaSpring16" % self.electronBranchName
        self.mvaID_POG_branchName = "%s_WPL" % self.mvaRaw_POG_branchName

        self.min_mvaRawPOG_vlow = [ -0.30, -0.46, -0.63 ]
        self.min_mvaRawPOG_low  = [ -0.86, -0.85, -0.81 ]
        self.min_mvaRawPOG_high = [ -0.96, -0.96, -0.95 ]
        self.binning_absEta     = [ 0.8, 1.479 ]

    def get_absEtaIdx(self, electron):
        electron_absEta = abs(electron.eta)
        if electron_absEta <= self.binning_absEta[0]:
            return 0
        elif electron_absEta <= self.binning_absEta[1]:
            return 1
        else:
            return 2

    def beginJob(self):
        pass

    def endJob(self):
        pass

    def beginFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
        self.out = wrappedOutputTree
        self.out.branch(self.mvaRaw_POG_branchName, "F", lenVar = self.electronLenBranchName)
        self.out.branch(self.mvaID_POG_branchName,  "O", lenVar = self.electronLenBranchName) # "O" means Bool_t

    def endFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
        pass

    def analyze(self, event):
        electrons = Collection(event, self.electronBranchName)
        mvaRaw_POG_arr = []
        mvaID_POG_arr = []
        for electron in electrons:
            idxBin = self.get_absEtaIdx(electron)
            if electron.pt <= 10.:
                mvaRaw_POG = getattr(electron, self.mvaSpring16HZZ_branchName)
                mvaRaw_POG_cut = self.min_mvaRawPOG_vlow[idxBin]
            else:
                mvaRaw_POG = getattr(electron, self.mvaSpring16GP_branchName)
                a = self.min_mvaRawPOG_low[idxBin]
                b = self.min_mvaRawPOG_high[idxBin]
                c = (a - b) / 10.
                mvaRaw_POG_cut = min(a, max(b, a - c * (electron.pt - 15.))) # warning: the _high WP must be looser than the _low one
            mvaID_POG = mvaRaw_POG >= mvaRaw_POG_cut
            mvaRaw_POG_arr.append(mvaRaw_POG)
            mvaID_POG_arr.append(mvaID_POG)
        assert(len(mvaRaw_POG_arr) == len(electrons))
        assert(len(mvaID_POG_arr) == len(electrons))
        self.out.fillBranch(self.mvaRaw_POG_branchName, mvaRaw_POG_arr)
        self.out.fillBranch(self.mvaID_POG_branchName, mvaID_POG_arr)

        return True

# provide this variable as the 2nd argument to the import option for the nano_postproc.py script
egammaId   = lambda : egammaIdProducer()
