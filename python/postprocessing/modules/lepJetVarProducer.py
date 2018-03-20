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

    def __init__(self, btagAlgos):
        # define lepton and jet branches and branch used to access energy densitity rho
        # (the latter is needed to compute L1 jet energy corrections)
        self.electronBranchName = "Electron"
        self.muonBranchName     = "Muon"
        self.leptonBranchNames = [ self.electronBranchName, self.muonBranchName ]
        self.jetBranchName = "Jet"
        self.rhoBranchName = "fixedGridRhoFastjetAll"

        # fail as early as possible
        self.btagAlgos = btagAlgos
        self.btagAlgoMap = {
          'csvv2' : 'btagCSVV2',
          'deep'  : 'btagDeepB',
          'cmva'  : 'btagCMVA',
        }
        for btagAlgo in self.btagAlgos:
          if btagAlgo not in self.btagAlgoMap:
            raise ValueError("Invalid b-tagging algorithm: %s" % btagAlgo)

        self.nLepton_branchNames = { leptonBranchName : "n%s" % leptonBranchName for leptonBranchName in self.leptonBranchNames }
        self.jetPtRatio_branchNames = { leptonBranchName : "%s_jetPtRatio" % (leptonBranchName) for leptonBranchName in self.leptonBranchNames }
        self.jetPtRelv2_branchNames = { leptonBranchName : "%s_jetPtRelv2" % (leptonBranchName) for leptonBranchName in self.leptonBranchNames }
        self.jetBtagCSVV2_cut_branchNames = { leptonBranchName : '%s_btagCSVV2_cut' % (leptonBranchName) for leptonBranchName in self.leptonBranchNames }

        self.jetBtagDiscr_branchNames = { leptonBranchName : {
            btagAlgo : "%s_jetBtag_%s" % (leptonBranchName, btagAlgo) for btagAlgo in self.btagAlgos
          } for leptonBranchName in self.leptonBranchNames }

        # define txt file with L1 jet energy corrections
        # (downloaded from https://twiki.cern.ch/twiki/bin/view/CMS/JECDataMC )
        self.l1corrInputFilePath = os.environ['CMSSW_BASE'] + "/src/tthAnalysis/NanoAODTools/data/"
        self.l1corrInputFileName = "Fall17_17Nov2017_V4_MC_L1FastJet_AK4PFchs.txt"

        # load libraries for accessing jet energy corrections from txt files
        for library in [ "libCondFormatsJetMETObjects" ]:
            if library not in ROOT.gSystem.GetLibraries():
                print("Load Library '%s'" % library.replace("lib", ""))
                ROOT.gSystem.Load(library)

    def beginJob(self):
        # initialize L1 jet energy corrections
        # (cf. https://twiki.cern.ch/twiki/bin/view/CMSPublic/WorkBookJetEnergyCorrections#OffsetJEC )
        print("Loading L1 jet energy corrections from file '%s'" % os.path.join(self.l1corrInputFilePath, self.l1corrInputFileName))
        self.l1corrParams = ROOT.JetCorrectorParameters(os.path.join(self.l1corrInputFilePath, self.l1corrInputFileName))
        v_l1corrParams = getattr(ROOT, 'vector<JetCorrectorParameters>')()
        v_l1corrParams.push_back(self.l1corrParams)
        self.l1corr = ROOT.FactorizedJetCorrector(v_l1corrParams)

    def endJob(self):
        pass

    def beginFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
        self.out = wrappedOutputTree
        for leptonBranchName in self.leptonBranchNames:
            self.out.branch(self.jetPtRatio_branchNames[leptonBranchName], "F", lenVar = self.nLepton_branchNames[leptonBranchName])
            self.out.branch(self.jetPtRelv2_branchNames[leptonBranchName], "F", lenVar = self.nLepton_branchNames[leptonBranchName])
            self.out.branch(self.jetBtagCSVV2_cut_branchNames[leptonBranchName], "I", lenVar = self.nLepton_branchNames[leptonBranchName])

            for btagAlgo in self.jetBtagDiscr_branchNames[leptonBranchName]:
              self.out.branch(self.jetBtagDiscr_branchNames[leptonBranchName][btagAlgo], "F", lenVar = self.nLepton_branchNames[leptonBranchName])

    def endFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
        pass

    def jetLepAwareJEC(self, lepton, jet, rho, isElectron):
        corrFactor = (1. - jet.rawFactor)
        jet_rawPt = corrFactor*jet.pt

        lepton_pt_uncorr = (lepton.pt / lepton.eCorr) if isElectron else lepton.pt
        p4l = ROOT.TLorentzVector()
        p4l.SetPtEtaPhiM(lepton_pt_uncorr, lepton.eta, lepton.phi, lepton.mass)

        if ((jet_rawPt - lepton_pt_uncorr) < 1e-4):
            return p4l

        p4j = ROOT.TLorentzVector()
        p4j.SetPtEtaPhiM(jet.pt, jet.eta, jet.phi, jet.mass)

        self.l1corr.setJetPt(jet_rawPt)
        self.l1corr.setJetEta(jet.eta)
        self.l1corr.setJetA(jet.area)
        self.l1corr.setRho(rho)
        l1corrFactor = self.l1corr.getCorrection()

        p4j_lepAware = (p4j * corrFactor - p4l * (1. / l1corrFactor)) * (1. / corrFactor) + p4l
        return p4j_lepAware

    def getPtRatio(self, lepton, jet, rho, isElectron):
        p4j_lepAware = self.jetLepAwareJEC(lepton, jet, rho, isElectron)
        lepton_pt_uncorr = (lepton.pt / lepton.eCorr) if isElectron else lepton.pt
        return min(lepton_pt_uncorr / max(1., p4j_lepAware.Pt()), 1.5)

    def getPtRelv2(self, lepton, jet, rho, isElectron):
        lepton_pt_uncorr = (lepton.pt / lepton.eCorr) if isElectron else lepton.pt
        p4l = ROOT.TLorentzVector()
        p4l.SetPtEtaPhiM(lepton_pt_uncorr, lepton.eta, lepton.phi, lepton.mass)

        p4j_lepAware = self.jetLepAwareJEC(lepton, jet, rho, isElectron)
        p4j_minu_p4l = p4j_lepAware - p4l

        return 0. if p4j_minu_p4l.Rho() < 1e-4 else p4l.Perp(p4j_minu_p4l.Vect())

    def analyze(self, event):
        jets = Collection(event, self.jetBranchName)

        rho = getattr(event, self.rhoBranchName)

        for leptonBranchName in self.leptonBranchNames:
            leptons = Collection(event, leptonBranchName)

            leptons_jetPtRatio = []
            leptons_jetPtRelv2 = []
            leptons_jetBtagDiscr = { btagAlgo : [] for btagAlgo in self.btagAlgos }
            leptons_jetBtagCSVV2_cut = []

            pairs = matchObjectCollection(leptons, jets)
            for lepton in leptons:
                jet = pairs[lepton]
                if jet is None:
                    leptons_jetPtRatio.append(-1.)
                    leptons_jetPtRelv2.append(-1.)
                    leptons_jetBtagCSVV2_cut.append(0)
                    for btagAlgo in self.btagAlgos:
                      leptons_jetBtagDiscr[btagAlgo].append(-1.)
                else:
                    leptons_jetPtRatio.append(self.getPtRatio(lepton, jet, rho, leptonBranchName == self.electronBranchName))
                    leptons_jetPtRelv2.append(self.getPtRelv2(lepton, jet, rho, leptonBranchName == self.electronBranchName))
                    leptons_jet_btagCSVV2_value = getattr(jet, self.btagAlgoMap['csvv2'])
                    if leptons_jet_btagCSVV2_value < 0.3: # optimized WP from 2016 analysis
                        leptons_jetBtagCSVV2_cut.append(1)
                    elif 0.3 <= leptons_jet_btagCSVV2_value < 0.8484: # old medium WP
                        leptons_jetBtagCSVV2_cut.append(2)
                    else:
                        leptons_jetBtagCSVV2_cut.append(3)

                    for btagAlgo in self.btagAlgos:
                      leptons_jetBtagDiscr[btagAlgo].append(getattr(jet, self.btagAlgoMap[btagAlgo]))

            self.out.fillBranch(self.jetPtRatio_branchNames[leptonBranchName],       leptons_jetPtRatio)
            self.out.fillBranch(self.jetPtRelv2_branchNames[leptonBranchName],       leptons_jetPtRelv2)
            self.out.fillBranch(self.jetBtagCSVV2_cut_branchNames[leptonBranchName], leptons_jetBtagCSVV2_cut)

            for btagAlgo in self.btagAlgos:
              self.out.fillBranch(self.jetBtagDiscr_branchNames[leptonBranchName][btagAlgo], leptons_jetBtagDiscr[btagAlgo])

        return True

# provide this variable as the 2nd argument to the import option for the nano_postproc.py script

lepJetVarBTagAll   = lambda : lepJetVarProducer(["csvv2", "deep", "cmva"])
lepJetVarBTagCSVv2 = lambda : lepJetVarProducer(["csvv2"])
lepJetVarBTagDeep  = lambda : lepJetVarProducer(["deep"])
lepJetVarBTagCMVA  = lambda : lepJetVarProducer(["cmva"])
