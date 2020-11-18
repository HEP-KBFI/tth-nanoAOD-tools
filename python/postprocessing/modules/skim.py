import ROOT
import os
ROOT.PyConfig.IgnoreCommandLineOptions = True

from PhysicsTools.NanoAODTools.postprocessing.framework.eventloop import Module

class Skimmer(Module):
    def __init__(self, rle_file):
        self.rle_file = rle_file
        self.rles = {}

    def beginJob(self):
        if not os.path.isfile(self.rle_file):
            raise RuntimeError("No such file")
        with open(self.rle_file, 'r') as rle_file:
            for line in rle_file:
                run, lumi, evt = [ int(rle) for rle in line.strip().split(':') ]
                if run not in self.rles:
                    self.rles[run] = {}
                if lumi not in self.rles[run]:
                    self.rles[run][lumi] = []
                assert(evt not in self.rles[run][lumi])
                self.rles[run][lumi].append(evt)

    def endJob(self):
        pass

    def beginFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
        pass

    def endFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
        pass

    def analyze(self, event):
        run = int(getattr(event, 'run'))
        lumi = int(getattr(event, 'luminosityBlock'))
        evt = int(getattr(event, 'event'))
        if run not in self.rles:
            return False
        if lumi not in self.rles[run]:
            return False
        if evt not in self.rles[run][lumi]:
            return False
        return True

skimmer = lambda path: Skimmer(path)
