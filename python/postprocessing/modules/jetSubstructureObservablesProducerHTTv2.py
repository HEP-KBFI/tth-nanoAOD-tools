import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True

from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import Collection
from PhysicsTools.NanoAODTools.postprocessing.framework.eventloop import Module
from PhysicsTools.NanoAODTools.postprocessing.tools import deltaR

class jetSubstructureObservablesProducerHTTv2(Module):

  def __init__(self):
    self.jetCollectionCA15 = "FatjetCA15"
    self.jetCollectionHTTv2 = "HTTV2"
    
  def beginJob(self):
    pass

  def endJob(self):
    pass

  def beginFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
    self.out = wrappedOutputTree
    self.out.branch(self.jetCollectionHTTv2 + "_tau1", "F", lenVar = "n" + self.jetCollectionHTTv2)
    self.out.branch(self.jetCollectionHTTv2 + "_tau2", "F", lenVar = "n" + self.jetCollectionHTTv2)
    self.out.branch(self.jetCollectionHTTv2 + "_tau3", "F", lenVar = "n" + self.jetCollectionHTTv2)
        
  def endFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
    pass

  def analyze(self, event):
    jetsCA15  = Collection(event, self.jetCollectionCA15)
    jetsHTTv2 = Collection(event, self.jetCollectionHTTv2)

    print "<jetSubstructureObservablesProducerHTTv2::analyze>: #%s jets = %i, #%s jets = %i" % (self.jetCollectionHTTv2, len(jetsHTTv2), self.jetCollectionCA15, len(jetsCA15))

    tau1Val = []
    tau2Val = []
    tau3Val = []
    for jetHTTv2_idx, jetHTTv2 in enumerate(jetsHTTv2):
        print "%s jet #%i: pT = %1.2f, eta = %1.2f, phi = %1.2f, mass = %1.2f" % \
          (self.jetCollectionHTTv2, jetHTTv2_idx, jetHTTv2.pt, jetHTTv2.eta, jetHTTv2.phi, jetHTTv2.mass)
        tau1 = -1.
        tau2 = -1.
        tau3 = -1.
        dRmin = 1.e+3
        for jetCA15_idx, jetCA15 in enumerate(jetsCA15):
            dR = deltaR(jetHTTv2, jetCA15)
            if dR < 0.75 and dR < dRmin:
                tau1 = jetCA15.tau1
                tau2 = jetCA15.tau2
                tau3 = jetCA15.tau3
                dRmin = dR
                print "matched to %s jet #%i: pT = %1.2f, eta = %1.2f, phi = %1.2f, mass = %1.2f (dR = %1.2f)" % \
                  (self.jetCollectionCA15, jetCA15_idx, jetCA15.pt, jetCA15.eta, jetCA15.phi, jetCA15.mass, dR)
        print " setting tau1 = %1.2f, tau2 = %1.2f, tau3 = %1.2f" % (tau1, tau2, tau3)
        tau1Val.append(tau1)
        tau2Val.append(tau2)
        tau3Val.append(tau3)

    self.out.fillBranch(self.jetCollectionHTTv2 + "_tau1", tau1Val)
    self.out.fillBranch(self.jetCollectionHTTv2 + "_tau2", tau2Val)
    self.out.fillBranch(self.jetCollectionHTTv2 + "_tau3", tau3Val)
    
    return True

# provide this variable as the 2nd argument to the import option for the nano_postproc.py script
jetSubstructureObservablesHTTv2 = lambda : jetSubstructureObservablesProducerHTTv2()
