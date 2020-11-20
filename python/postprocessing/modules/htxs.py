import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True

from PhysicsTools.NanoAODTools.postprocessing.framework.eventloop import Module

import subprocess
import os

class htxsProducer(Module):
  def __init__(self, rleFile):
    self.runBr = 'run'
    self.lsBr = 'luminosityBlock'
    self.evtBr = 'event'
    self.htxsBr = 'HTXS_stage1_2_cat_pTjet30GeV'

    self.rleFile = rleFile
    if not os.path.isfile(self.rleFile):
      raise RuntimeError("No such file: %s" % self.rleFile)

  def beginJob(self):
    pass

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
    rle = '{}:{}:{}'.format(run, ls, evt)
    out = subprocess.check_output([ 'grep', '{} '.format(rle), self.rleFile ])
    out_split = out.strip().split()
    if len(out_split) != 2:
      raise RuntimeError("Not exactly two cols: %s" % out)
    htxs_val = int(out_split[1])

    self.out.fillBranch(self.htxsBr, htxs_val)

    return True

htxs = lambda rleFile: htxsProducer(rleFile)
