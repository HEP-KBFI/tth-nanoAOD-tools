import ROOT
import numpy as np
import array
import collections
ROOT.PyConfig.IgnoreCommandLineOptions = True

from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import Collection, Object
from PhysicsTools.NanoAODTools.postprocessing.framework.eventloop import Module
from PhysicsTools.NanoAODTools.postprocessing.tools import deltaR

class SubJetBtagCounter(Module):

    def __init__(self, era, outputFn, histName):
        self.subJetBranchName = "SubJet"
        self.genQuarkBranchNames = [ "GenQuarkFromTop", "GenBQuarkFromTop", "GenWZQuark", "GenHiggsDaughters" ]
        self.genWeightBranchName = "genWeight"
        self.era = era
        self.out = None
        self.outputFileName = outputFn
        self.hists = collections.OrderedDict()
        self.histName = histName
        self.btag_minPt = 30.
        self.btag_maxAbsEta = 2.5
        self.match_dR = 0.4
        self.flavors = [ 0, 4, 5 ]
        self.binning = {
            'fine' : {
                'pt' : array.array('f', list(np.arange(30, 1010, 10))),
                'eta' : array.array('f', list(np.arange(0, 2.51, 0.01))),
            },
            'coarse' : {
                'pt': array.array('f', list(np.arange(0, 1200, 200))),
                'eta': array.array('f', list(np.arange(0, 3.0, 0.5))),
            },
        }
        self.total_label = 'total'

        btagWPs = {
            2016 : { 'l' : 0.2217, 'm' : 0.6321 }, # https://twiki.cern.ch/twiki/bin/viewauth/CMS/BtagRecommendation2016Legacy
            2017 : { 'l' : 0.1522, 'm' : 0.4941 }, # https://twiki.cern.ch/twiki/bin/viewauth/CMS/BtagRecommendation94X
            2018 : { 'l' : 0.1241, 'm' : 0.4184 }, # https://twiki.cern.ch/twiki/bin/viewauth/CMS/BtagRecommendation102X
        }
        self.btagWP = btagWPs[self.era]

    def beginJob(self):
        pass

    def endJob(self):
        pass

    def getHistKey(self, binning, flavor, btagWP = 'total'):
        return '{}_{}_{}'.format(binning, flavor, btagWP)

    def beginFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
        for binning in self.binning:
            pt_binning = self.binning[binning]['pt']
            eta_binning = self.binning[binning]['eta']
            for flavor in self.flavors:
                histKeys = []
                for is_total in [ True, False ]:
                    if is_total:
                        histKeys.append(self.getHistKey(binning, flavor))
                    else:
                        for btagWP in self.btagWP:
                            histKeys.append(self.getHistKey(binning, flavor, btagWP))
                for histKey in histKeys:
                    assert(histKey not in self.hists)
                    self.hists[histKey] = ROOT.TH2D(
                        histKey, histKey, len(pt_binning) - 1, pt_binning, len(eta_binning) - 1, eta_binning,
                    )
                    self.hists[histKey].Sumw2()
                    if binning != 'fine':
                        self.hists[histKey].SetOption('col text')
                    else:
                        self.hists[histKey].SetOption('col')

    def endFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
        self.out = ROOT.TFile.Open(self.outputFileName, 'recreate')
        self.out.cd()
        for histKey in self.hists:
            self.hists[histKey].Write()
        self.out.Close()

    def analyze(self, event):
        subjets = Collection(event, self.subJetBranchName)
        genquarks_filtered = []
        for genquark_branchName in self.genQuarkBranchNames:
            genquarks = Collection(event, genquark_branchName)
            for genquark in genquarks:
                if not (0 < abs(genquark.pdgId) < 6):
                    continue
                has_match = False
                for genquark_filtered in genquarks_filtered:
                    if deltaR(genquark.eta, genquark.phi, genquark_filtered.eta, genquark_filtered.phi) < 1e-2:
                        has_match = True
                        break
                if not has_match:
                    genquarks_filtered.append(genquark)
        genquarks_sorted = list(sorted(genquarks_filtered, key = lambda genquark: genquark.pt, reverse = True))

        genquarks_matched = []
        for subjet in subjets:
            if not (subjet.pt > self.btag_minPt and abs(subjet.eta) < self.btag_maxAbsEta):
                continue
            subjet_flavor = 0 # assume light flavor if no match
            min_dr = 1e3
            match_idx = -1
            for genquark_idx, genquark in enumerate(genquarks_sorted):
                if genquark_idx in genquarks_matched:
                    # genquark already matched
                    continue
                dr = deltaR(subjet.eta, subjet.phi, genquark.eta, genquark.phi)
                if dr < self.match_dR and dr < min_dr:
                    min_dr = dr
                    match_idx = genquark_idx
            if match_idx >= 0:
                genquarks_matched.append(match_idx)
                subjet_flavor = abs(genquarks_sorted[match_idx].pdgId)
            if subjet_flavor < 4:
                subjet_flavor = 0
            assert(subjet_flavor in self.flavors)
            subjet_pt = subjet.pt
            subjet_absEta = abs(subjet.eta)
            subjet_btag = subjet.btagDeepB

            for binning in self.binning:
                histKey_total = self.getHistKey(binning, subjet_flavor)
                self.hists[histKey_total].Fill(subjet_pt, subjet_absEta)
                for btagWP in self.btagWP:
                    if subjet_btag >= self.btagWP[btagWP]:
                        histKey = self.getHistKey(binning, subjet_flavor, btagWP)
                        self.hists[histKey].Fill(subjet_pt, subjet_absEta)

        return True

# provide this variable as the 2nd argument to the import option for the nano_postproc.py script
subJetBtagCounter2016 = lambda outputFn, histName, ref_genWeight: SubJetBtagCounter(2016, outputFn, histName)
subJetBtagCounter2017 = lambda outputFn, histName, ref_genWeight: SubJetBtagCounter(2017, outputFn, histName)
subJetBtagCounter2018 = lambda outputFn, histName, ref_genWeight: SubJetBtagCounter(2018, outputFn, histName)
