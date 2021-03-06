import ROOT
import os.path, re
ROOT.PyConfig.IgnoreCommandLineOptions = True

from PhysicsTools.NanoAODTools.postprocessing.framework.eventloop import Module

class rleProducer(Module):

    def __init__(self):
        self.run_nr = 0
        self.run_brName = "run"
        self.ls_brName = "luminosityBlock"
        self.evt_brName = "event"
        self.max_event = 250
        self.current_event_idx = 0
        self.run_rgxKey = 'idx'
        self.inputFile_rgx = re.compile(r'^tree_(?P<{}>\d+)(_.*)?.root$'.format(self.run_rgxKey))

    def endJob(self):
        pass

    def beginFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
        self.out = wrappedOutputTree
        self.out.branch(self.run_brName, "i")
        self.out.branch(self.ls_brName, "i")
        self.out.branch(self.evt_brName, "l")

        inputFile_baseName = os.path.basename(inputFile.GetName())
        inputFile_rgxMatch = self.inputFile_rgx.match(inputFile_baseName)
        if not inputFile_rgxMatch:
            raise RuntimeError("Invalid file given: %s" % inputFile_baseName)
        self.run_nr = int(inputFile_rgxMatch.group(self.run_rgxKey))
        print("Extracted {} as the new run number frmo file name {}".format(self.run_nr, inputFile_baseName))

    def endFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
        pass

    def analyze(self, event):
        ls_nr = int(self.current_event_idx / self.max_event)
        evt_nr = self.current_event_idx % self.max_event
        self.out.fillBranch(self.run_brName, self.run_nr)
        self.out.fillBranch(self.ls_brName, ls_nr)
        self.out.fillBranch(self.evt_brName, evt_nr)
        self.current_event_idx += 1

        return True

# provide this variable as the 2nd argument to the import option for the nano_postproc.py script
rle = lambda :rleProducer()
