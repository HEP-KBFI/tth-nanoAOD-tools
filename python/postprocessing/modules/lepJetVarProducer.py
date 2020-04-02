import ROOT
import math, os
ROOT.PyConfig.IgnoreCommandLineOptions = True

from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import Collection, Object
from PhysicsTools.NanoAODTools.postprocessing.framework.eventloop import Module

class lepJetVarProducer(Module):

    def __init__(self, era, btagAlgos):
        # define lepton and jet branches and branch used to access energy densitity rho
        # (the latter is needed to compute L1 jet energy corrections)
        self.era = era
        self.electronBranchName = "Electron"
        self.muonBranchName     = "Muon"
        self.leptonBranchNames = [ self.electronBranchName, self.muonBranchName ]
        self.jetBranchName = "Jet"
        self.rhoBranchName = "fixedGridRhoFastjetAll"

        # fail as early as possible
        self.btagAlgos = btagAlgos
        self.btagAlgoMap = {
          'deep'    : 'btagDeepB',
          'deepjet' : 'btagDeepFlavB',
          'csvv2'   : 'btagCSVV2',
          'cmva'    : 'btagCMVA',
        }
        for btagAlgo in self.btagAlgos:
          if btagAlgo not in self.btagAlgoMap:
            raise ValueError("Invalid b-tagging algorithm: %s" % btagAlgo)

        self.nLepton_branchNames = { leptonBranchName : "n%s" % leptonBranchName for leptonBranchName in self.leptonBranchNames }
        self.jetPtRatio_branchNames = { leptonBranchName : "%s_assocJetPtRatio" % (leptonBranchName) for leptonBranchName in self.leptonBranchNames }
        self.jetPtRelv2_branchNames = { leptonBranchName : "%s_assocJetPtRelv2" % (leptonBranchName) for leptonBranchName in self.leptonBranchNames }

        self.jetBtagDiscr_branchNames = { leptonBranchName : {
            btagAlgo : "%s_assocJetBtag_%s" % (leptonBranchName, btagAlgo) for btagAlgo in self.btagAlgos
          } for leptonBranchName in self.leptonBranchNames }

        # define txt file with L1 jet energy corrections
        # (downloaded from https://twiki.cern.ch/twiki/bin/view/CMS/JECDataMC )
        self.l1corrInputFilePath = os.path.join(os.environ['CMSSW_BASE'], "src/PhysicsTools/NanoAODTools/data/jme")
        if self.era == '2016':
            l1corrInputDirName = "Summer16_07Aug2017_V11_MC"
        elif self.era == '2017':
          l1corrInputDirName = "Fall17_17Nov2017_V32_MC"
        elif self.era == '2018':
            l1corrInputDirName = "Autumn18_V19_MC"
        else:
          raise ValueError("Invalid era: %s" % self.era)
        self.l1corrInputFilePath = os.path.join(self.l1corrInputFilePath, l1corrInputDirName)
        self.l1corrInputFileName = "{}_L1FastJet_AK4PFchs.txt".format(l1corrInputDirName)

        # load libraries for accessing jet energy corrections from txt files
        for library in [ "libCondFormatsJetMETObjects" ]:
            if library not in ROOT.gSystem.GetLibraries():
                print("Load Library '%s'" % library.replace("lib", ""))
                ROOT.gSystem.Load(library)

    def beginJob(self):
        # initialize L1 jet energy corrections
        # (cf. https://twiki.cern.ch/twiki/bin/view/CMSPublic/WorkBookJetEnergyCorrections#OffsetJEC )
        l1corrInputFileFullPath = os.path.join(self.l1corrInputFilePath, self.l1corrInputFileName)
        print("Loading L1 jet energy corrections from file '%s'" % l1corrInputFileFullPath)
        self.l1corrParams = ROOT.JetCorrectorParameters(l1corrInputFileFullPath)
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

            for btagAlgo in self.jetBtagDiscr_branchNames[leptonBranchName]:
              self.out.branch(self.jetBtagDiscr_branchNames[leptonBranchName][btagAlgo], "F", lenVar = self.nLepton_branchNames[leptonBranchName])

    def endFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
        pass

    def getUncorrectedPt(self, lepton, isElectron):
        if isElectron:
            return lepton.pt / lepton.eCorr
        else:
            return lepton.pt

    def jetLepAwareJEC(self, lepton, jet, rho, isElectron):
        corrFactor = (1. - jet.rawFactor)
        jet_rawPt = corrFactor*jet.pt

        lepton_pt_uncorr = self.getUncorrectedPt(lepton, isElectron)
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
        lepton_pt_uncorr = self.getUncorrectedPt(lepton, isElectron)
        return min(lepton_pt_uncorr / p4j_lepAware.Pt(), 1.5)

    def getPtRelv2(self, lepton, jet, rho, isElectron):
        lepton_pt_uncorr = self.getUncorrectedPt(lepton, isElectron)
        p4l = ROOT.TLorentzVector()
        p4l.SetPtEtaPhiM(lepton_pt_uncorr, lepton.eta, lepton.phi, lepton.mass)

        p4j_lepAware = self.jetLepAwareJEC(lepton, jet, rho, isElectron)
        p4j_minu_p4l = p4j_lepAware - p4l

        return 0. if p4j_minu_p4l.Rho() < 1e-4 else p4l.Perp(p4j_minu_p4l.Vect())

    def analyze(self, event):
        jets = Collection(event, self.jetBranchName)
        njets = len(jets)
        rho = getattr(event, self.rhoBranchName)

        for leptonBranchName in self.leptonBranchNames:
            leptons = Collection(event, leptonBranchName)

            leptons_jetPtRatio = []
            leptons_jetPtRelv2 = []
            leptons_jetBtagDiscr = { btagAlgo : [] for btagAlgo in self.btagAlgos }

            for lepton in leptons:
                if lepton.jetIdx < 0 or lepton.jetIdx >= njets:
                    leptons_jetPtRatio.append(1. / (1. + lepton.pfRelIso04_all))
                    leptons_jetPtRelv2.append(-1.)
                    for btagAlgo in self.btagAlgos:
                      leptons_jetBtagDiscr[btagAlgo].append(-1.)
                else:
                    jet = jets[lepton.jetIdx]
                    leptons_jetPtRatio.append(self.getPtRatio(lepton, jet, rho, leptonBranchName == self.electronBranchName))
                    leptons_jetPtRelv2.append(self.getPtRelv2(lepton, jet, rho, leptonBranchName == self.electronBranchName))

                    for btagAlgo in self.btagAlgos:
                      leptons_jetBtagDiscr[btagAlgo].append(getattr(jet, self.btagAlgoMap[btagAlgo]))

            self.out.fillBranch(self.jetPtRatio_branchNames[leptonBranchName], leptons_jetPtRatio)
            self.out.fillBranch(self.jetPtRelv2_branchNames[leptonBranchName], leptons_jetPtRelv2)

            for btagAlgo in self.btagAlgos:
              self.out.fillBranch(self.jetBtagDiscr_branchNames[leptonBranchName][btagAlgo], leptons_jetBtagDiscr[btagAlgo])

        return True

# provide this variable as the 2nd argument to the import option for the nano_postproc.py script
lepJetVarBTagAll_2016 = lambda : lepJetVarProducer('2016', ["DeepCSV", 'DeepJet', "CSV"])
lepJetVarBTagAll_2017 = lambda : lepJetVarProducer('2017', ["DeepCSV", 'DeepJet', "CSV"])
lepJetVarBTagAll_2018 = lambda : lepJetVarProducer('2018', ["DeepCSV", 'DeepJet'])
