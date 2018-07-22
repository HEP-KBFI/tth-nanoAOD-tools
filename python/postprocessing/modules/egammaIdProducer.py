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
        self.mvaSpring16_branchName = "%s_mvaSpring16" % self.electronBranchName

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
        self.out.branch(self.mvaSpring16_branchName, "O", lenVar = self.electronLenBranchName) # "O" means Bool_t

    def endFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
        pass

    def analyze(self, event):
        electrons = Collection(event, self.electronBranchName)
        mvaSpring16_arr = [ ]
        for electron in electrons:
            idxBin = self.get_absEtaIdx(electron)
            if electron.pt <= 10.:
                mvaRawPOG = getattr(electron, self.mvaSpring16HZZ_branchName)
                mvaRawPOGCut = self.min_mvaRawPOG_vlow[idxBin]
            else:
                mvaRawPOG = getattr(electron, self.mvaSpring16GP_branchName)
                a = self.min_mvaRawPOG_low[idxBin]
                b = self.min_mvaRawPOG_high[idxBin]
                c = (a - b) / 10.
                mvaRawPOGCut = min(a, max(b, a - c * (electron.pt - 15.))) # warning: the _high WP must be looser than the _low one
            mvaSpring16 = mvaRawPOG >= mvaRawPOGCut
            mvaSpring16_arr.append(mvaSpring16)
        self.out.fillBranch(self.mvaSpring16_branchName, mvaSpring16_arr)

        return True

# provide this variable as the 2nd argument to the import option for the nano_postproc.py script
egammaId   = lambda : egammaIdProducer()
