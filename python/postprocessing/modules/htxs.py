import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True

from PhysicsTools.NanoAODTools.postprocessing.framework.eventloop import Module

import array
import os

class htxsProducer(Module):
  def __init__(self, rleFile, procName):
    self.runBr = 'run'
    self.lsBr = 'luminosityBlock'
    self.evtBr = 'event'
    self.htxsBr = 'HTXS_stage1_2_cat_pTjet30GeV'

    self.rleFile = rleFile
    self.procName = procName
    self.htxs = {}

  def beginJob(self):
    if not os.path.isfile(self.rleFile):
      raise RuntimeError("No such file: %s" % self.rleFile)
    rleFile = ROOT.TFile.Open(self.rleFile, 'read')
    procTree = rleFile.Get(self.procName)
    if not procTree:
      raise RuntimeError("No such TTree in file %s: %s" % (self.rleFile, self.procName))

    runArr = array.array('I', [0])
    lsArr = array.array('I', [0])
    evtArr = array.array('L', [0])
    htxsArr = array.array('i', [0])

    procTree.SetBranchAddress(self.runBr, runArr)
    procTree.SetBranchAddress(self.lsBr, lsArr)
    procTree.SetBranchAddress(self.evtBr, evtArr)
    procTree.SetBranchAddress(self.htxsBr, htxsArr)

    nofEntries = procTree.GetEntries()
    for evtIdx in range(nofEntries):
      procTree.GetEntry(evtIdx)

      run = runArr[0]
      ls = lsArr[0]
      evt = evtArr[0]
      htxs = htxsArr[0]

      if run not in self.htxs:
        self.htxs[run] = {}
      if ls not in self.htxs[run]:
        self.htxs[run][ls] = {}
      assert(evt not in self.htxs[run][ls])
      self.htxs[run][ls][evt] = htxs

    rleFile.Close()

  def endJob(self):
    pass

  def beginFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
    self.out = wrappedOutputTree
    self.out.branch(self.htxsBr, 'I')

  def endFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
    pass

  def analyze(self, event):
    run = getattr(event, self.runBr)
    ls = getattr(event, self.lsBr)
    evt  = getattr(event, self.evtBr)

    if run not in self.htxs:
      raise RuntimeError("Unable to find events with run nr %d" % run)
    if ls not in self.htxs[run]:
      raise RuntimeError("Unable to find events with ls nr %d" % ls)
    if evt not in self.htxs[run][ls]:
      raise RuntimeError("Unable to find events with evt nr %d" % evt)

    self.out.fillBranch(self.htxsBr, self.htxs[run][ls][evt])

    return True

htxs = lambda rleFile, procName: htxsProducer(rleFile, procName)
