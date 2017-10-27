import ROOT
import math, os
ROOT.PyConfig.IgnoreCommandLineOptions = True

from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import Collection, Object
from PhysicsTools.NanoAODTools.postprocessing.framework.eventloop import Module

#----------------------------------------------------------------------------------------------------
# KE: global functions copied from PhysicsTools/HeppyCore/python/utils/deltar.py

def deltaPhi(p1, p2):
    '''Computes delta phi, handling periodic limit conditions.'''
    res = p1 - p2
    while res > math.pi:
        res -= 2*math.pi
    while res < -math.pi:
        res += 2*math.pi
    return res

def deltaR2(e1, p1, e2=None, p2=None):
    '''Take either 4 arguments (eta,phi, eta,phi) or two particles that have 'eta', 'phi' methods)'''
    if (e2 == None and p2 == None):
        return deltaR2(e1.eta, e1.phi, p1.eta, p1.phi)
    de = e1 - e2
    dp = deltaPhi(p1, p2)
    return de*de + dp*dp

def bestMatch(ptc, matchCollection):
    '''Return the best match to ptc in matchCollection,
    which is the closest ptc in delta R,
    together with the squared distance dR2 between ptc
    and the match.'''
    deltaR2Min = float('+inf')
    bm = None
    for match in matchCollection:
        dR2 = deltaR2(ptc, match)
        if dR2 < deltaR2Min:
            deltaR2Min = dR2
            bm = match
    return bm, deltaR2Min

def matchObjectCollection(ptcs, matchCollection, deltaRMax = 0.4, filter = lambda x,y : True):
    pairs = {}
    if len(ptcs)==0:
        return pairs
    if len(matchCollection)==0:
        return dict( list(zip(ptcs, [None]*len(ptcs))) )
    dR2Max = deltaRMax ** 2
    for ptc in ptcs:
        bm, dr2 = bestMatch( ptc, [ mob for mob in matchCollection if filter(object,mob) ] )
        if dr2 < dR2Max:
            pairs[ptc] = bm
        else:
            pairs[ptc] = None
    return pairs
#----------------------------------------------------------------------------------------------------

class lepJetVarProducer(Module):

    def __init__(self):
        # define lepton and jet branches and branch used to access energy densitity rho
        # (the latter is needed to compute L1 jet energy corrections)
        self.leptonBranchNames = [ "Electron", "Muon" ]
        self.jetBranchName = "Jet"
        self.rhoBranchName = "fixedGridRhoFastjetAll"
        
        self.btagAlgo = "csvv2"
        
        # define txt file with L1 jet energy corrections
        # (downloaded from https://twiki.cern.ch/twiki/bin/view/CMS/JECDataMC )
        self.l1corrInputFilePath = os.environ['CMSSW_BASE'] + "/src/tthAnalysis/NanoAODTools/data/"
        self.l1corrInputFileName = "Summer16_23Sep2016V4_MC_L1FastJet_AK4PFchs.txt"

        # load libraries for loading jet energy corrections from txt files
        for library in [ "libCondFormatsJetMETObjects" ]:
            if library not in ROOT.gSystem.GetLibraries():
                print "Load Library '%s'" % library.replace("lib", "")
                ROOT.gSystem.Load(library)

    def beginJob(self):
        # initialize L1 jet energy corrections
        # (cf. https://twiki.cern.ch/twiki/bin/view/CMSPublic/WorkBookJetEnergyCorrections#OffsetJEC )
        print "Loading L1 jet energy corrections from file '%s'" % os.path.join(self.l1corrInputFilePath, self.l1corrInputFileName)
        self.l1corrParams = ROOT.JetCorrectorParameters(os.path.join(self.l1corrInputFilePath, self.l1corrInputFileName))
        v_l1corrParams = getattr(ROOT, 'vector<JetCorrectorParameters>')()
        v_l1corrParams.push_back(self.l1corrParams)
        self.l1corr = ROOT.FactorizedJetCorrector(v_l1corrParams)

    def endJob(self):
        pass

    def beginFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
        self.out = wrappedOutputTree
        for leptonBranchName in self.leptonBranchNames:
            self.out.branch("%s_%s" % (leptonBranchName, "jetPtRatio"), "F", lenVar = "n%s" % leptonBranchName)
            self.out.branch("%s_%s" % (leptonBranchName, "jetBtagCSV"), "F", lenVar = "n%s" % leptonBranchName)

    def endFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
        pass

    def getPtRatio(self, lepton, jet, rho):
        jet_rawPt = (1. - jet.rawFactor)*jet.pt
        self.l1corr.setJetEta(jet.eta)
        self.l1corr.setJetPt(jet_rawPt)
        self.l1corr.setJetA(jet.area)
        self.l1corr.setRho(rho)
        jet_l1corrPt = self.l1corr.getCorrection()*jet_rawPt
        print("jet eta = %1.1f, rho = %1.1f: jet pT = %1.1f (raw), %1.1f (L1 corr), %1.1f (corr)" % (jet.eta, rho, jet_rawPt, jet_l1corrPt, jet.pt))
        if ((jet_rawPt - lepton.pt) < 1e-4): # matched to jet containing only the lepton
            return 1.
        else:
            return min(lepton.pt/max(1., ((jet_rawPt - lepton.pt*(1./(jet_l1corrPt/jet_rawPt)))*(jet.pt/jet_rawPt) + lepton.pt)), 1.5)
        
    def analyze(self, event):
        jets = Collection(event, self.jetBranchName)

        btagDiscr = None
        if self.btagAlgo == "csvv2":
            btagDiscr = "btagDeepB"
        elif self.algo == "cmva":
            btagDiscr = "btagCMVA"
        else:
            raise ValueError("ERROR: Invalid algorithm '%s'! Please choose either 'csvv2' or 'cmva'." % self.btagAlgo)

        rho = getattr(event, self.rhoBranchName)
    
        for leptonBranchName in self.leptonBranchNames:
            leptons = Collection(event, leptonBranchName)

            leptons_jetPtRatio = []
            leptons_jetBtagCSV = []

            pairs = matchObjectCollection(leptons, jets)
            for lepton in leptons:
                jet = pairs[lepton]
                if jet is None:
                    leptons_jetPtRatio.append(-1.)
                    leptons_jetBtagCSV.append(-1.)
                else:            
                    leptons_jetPtRatio.append(self.getPtRatio(lepton, jet, rho))
                    leptons_jetBtagCSV.append(getattr(jet, btagDiscr))

            self.out.fillBranch("%s_%s" % (leptonBranchName, "jetPtRatio"), leptons_jetPtRatio)
            self.out.fillBranch("%s_%s" % (leptonBranchName, "jetBtagCSV"), leptons_jetBtagCSV)

        return True

# provide this variable as the 2nd argument to the import option for the nano_postproc.py script

lepJetVar = lambda : lepJetVarProducer()
