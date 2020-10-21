import ROOT
import math, os, array, collections
from functools import reduce
ROOT.PyConfig.IgnoreCommandLineOptions = True

from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import Collection, Object
from PhysicsTools.NanoAODTools.postprocessing.framework.eventloop import Module
from PhysicsTools.NanoAODTools.postprocessing.tools import deltaR

from tthAnalysis.NanoAODTools.postprocessing.modules.countHistogramProducer import clip_genWeight

class btagSFRatioFinder(Module):

    def __init__(self, era, outputFn, histName, ref_genWeight):
        self.jetBranchName = "Jet"
        self.muonBranchName = "Muon"
        self.electronBranchName = "Electron"
        self.genWeightBranchName = "genWeight"
        self.puWeightBranchName = "puWeight"
        self.puWeightBranchNameUp = "puWeightUp"
        self.puWeightBranchNameDown = "puWeightDown"
        self.l1prefireWeightBranchName = "L1PreFiringWeight_Nom"
        self.l1prefireWeightBranchNameUp = "L1PreFiringWeight_Up"
        self.l1prefireWeightBranchNameDown = "L1PreFiringWeight_Dn"
        self.topPtRwgtBranchName = "topPtRwgt_Quadratic"
        self.era = era
        self.out = None
        self.outputFileName = outputFn
        self.hists_woBtag = collections.OrderedDict()
        self.hists_wBtag = collections.OrderedDict()
        self.histName = histName
        self.njets = 16
        self.njets_array = array.array('f', list(range(self.njets)))
        self.jetIdCut = 1 if self.era == 2016 else 2
        self.ref_genWeight = abs(float(ref_genWeight))
        assert(self.ref_genWeight > 0.)

        btagLooseCuts  = { 2016 : 0.0614, 2017 : 0.0521, 2018 : 0.0494 }
        btagMediumCuts = { 2016 : 0.3093, 2017 : 0.3033, 2018 : 0.2770 }
        self.btagLooseCut = btagLooseCuts[self.era]
        self.btagMediumCut = btagMediumCuts[self.era]

        self.mu_wp = 0.85
        self.ele_wp = 0.80

        self.btagSF_branch = 'btagSF_deepjet_shape'
        self.branchMap = collections.OrderedDict([
            ( 'none',    { 'pt' : '',             'btag' : '' } ),
            ( 'central', { 'pt' : 'nom',          'btag' : '' } ),
            ( 'JESUp',   { 'pt' : 'jesTotalUp',   'btag' : 'up_jes'   } ),
            ( 'JESDown', { 'pt' : 'jesTotalDown', 'btag' : 'down_jes' } ),
            ( 'JERUp',   { 'pt' : 'jerUp',        'btag' : '' }),
            ( 'JERDown', { 'pt' : 'jerDown',      'btag' : '' }),
        ])
        btag_list = collections.OrderedDict([
            ('HF', 'hf'), ('HFStats1', 'hfstats1'), ('HFStats2', 'hfstats2'),
            ('LF', 'lf'), ('LFStats1', 'lfstats1'), ('LFStats2', 'lfstats2'),
            ('cErr1', 'cferr1'),
            ('cErr2', 'cferr2'),
        ])
        for btag_sys in btag_list:
            for shift in [ 'Up', 'Down' ]:
                sys_key = '{}{}'.format(btag_sys, shift)
                btag_branch = '{}_{}'.format(shift.lower(), btag_list[btag_sys])
                assert(sys_key not in self.branchMap)
                self.branchMap[sys_key] = { 'pt' : 'nom', 'btag' : btag_branch }
        jes_list = [
            'JESAbsolute', 'JESAbsolute_{}'.format(self.era), 'JESBBEC1', 'JESBBEC1_{}'.format(era),
            'JESEC2', 'JESEC2_{}'.format(era), 'JESFlavorQCD', 'JESHF', 'JESHF_{}'.format(era),
            'JESRelativeBal', 'JESRelativeSample_{}'.format(era),
        ]
        for jes in jes_list:
            for shift in [ 'Up', 'Down' ]:
                jes_key = '{}{}'.format(jes, shift)
                jes_pt = jes_key.replace('JES', 'jes')
                assert(jes_key not in self.branchMap)
                self.branchMap[jes_key] = { 'pt' : jes_pt, 'btag' : '' }

        jer_list = [ 'JERBarrel', 'JEREndcap1' ]
        self.jer_keys = []
        for jer in jer_list:
            for shift in [ 'Up', 'Down' ]:
                jer_key = '{}{}'.format(jer, shift)
                assert(jer_key not in self.branchMap)
                self.branchMap[jer_key] = { 'pt' : 'jer{}'.format(shift), 'btag' : '' }
                self.jer_keys.append(jer_key)

        nonJet_sysList = [ 'pileup', 'l1PreFire', 'topPtReweighting' ]
        for nonJet_sys in nonJet_sysList:
            for shift in [ 'Up', 'Down' ]:
                sys_key = '{}{}'.format(nonJet_sys, shift)
                assert(sys_key not in self.branchMap)
                self.branchMap[sys_key] = { 'pt' : 'nom', 'btag' : '' }

        self.useFakeable = True
        self.useGenWeightSignOnly = False

    def beginJob(self):
        pass

    def endJob(self):
        pass

    def getHistKey(self, sysKey):
        return '{}_{}'.format(self.histName, sysKey)

    def overlaps_any(self, obj, refcollection, coneSize):
        has_overlap = False
        for refobj in refcollection:
            if deltaR(obj.eta, obj.phi, refobj.eta, refobj.phi) < coneSize:
                has_overlap = True
                break
        return has_overlap

    def preselect_mu(self, muon):
        return muon.pt >= 5. and \
               abs(muon.eta) <= 2.4 and \
               abs(muon.dxy) <= 0.05 and \
               abs(muon.dz) <= 0.1 and \
               muon.miniPFRelIso_all <= 0.4 and \
               muon.sip3d <= 8.

    def preselect_ele(self, ele, muons):
        return ele.pt >= 7. and \
               abs(ele.eta) <= 2.5 and \
               abs(ele.dxy) <= 0.05 and \
               abs(ele.dz) < 0.1 and \
               ele.miniPFRelIso_all <= 0.4 and \
               ele.sip3d <= 8. and \
               ele.mvaFall17V2noIso_WPL and \
               ele.lostHits <= 1 and \
               not self.overlaps_any(ele, muons, 0.3)

    def preselect_jet(self, jet):
        return abs(jet.eta) <= 2.4 and jet.jetId >= self.jetIdCut

    def cone_pt(self, lep, wp):
        return lep.pt * (1. if lep.mvaTTH >= wp else 0.9 / lep.jetPtRatio)

    def btag_cut(self, muon):
        jetpt = muon.pt * 0.9 / muon.jetPtRatio
        btagWP = min(max(0., jetpt - 20.) / 25., 1.)
        return btagWP * self.btagLooseCut + (1. - btagWP) * self.btagMediumCut

    def fakeableselect_mu(self, muon):
        return self.preselect_mu(muon) and \
               self.cone_pt(muon, self.mu_wp) >= 10. and \
               muon.assocJetBtag_DeepJet <= self.btagMediumCut and \
               (
                   True if muon.mvaTTH > self.mu_wp else (
                       muon.jetPtRatio >= 2. / 3 and
                       muon.assocJetBtag_DeepJet <= self.btag_cut(muon)
                   )
               )

    def hlt_cut(self, ele):
        sieie_cut = 0.011 if abs(ele.eta) <= 1.479 else 0.030
        return ele.hoe <= 0.10 and ele.eInvMinusPInv >= -0.04 and ele.sieie <= sieie_cut

    def fakeableselect_ele(self, ele, muons):
        return self.preselect_ele(ele, muons) and \
               self.cone_pt(ele, self.ele_wp) >= 10. and \
               ele.lostHits == 0 and \
               ele.convVeto and \
               ele.assocJetBtag_DeepJet <= self.btagMediumCut and \
               self.hlt_cut(ele) and \
               (
                   True if ele.mvaTTH > self.ele_wp else (
                           ele.jetPtRatio >= 1. / 1.7 and
                           ele.mvaFall17V2noIso_WP80
                   )
               )

    def select_mu(self, muon):
        return self.fakeableselect_mu(muon) if self.useFakeable else self.preselect_mu(muon)

    def select_ele(self, ele, muons):
        return self.fakeableselect_ele(ele, muons) if self.useFakeable else self.preselect_ele(ele, muons)

    def select_jet(self, jet, sysKey):
        if sysKey not in self.jer_keys:
            pt_branch = 'pt_{}'.format(self.branchMap[sysKey]['pt']) if self.branchMap[sysKey]['pt'] else 'pt'
        else:
            absEta = abs(jet.eta)
            pt_branch = self.branchMap['central']['pt']
            if absEta < 1.93:
                if sysKey == 'JERBarrelUp':
                    pt_branch = 'jerUp'
                elif sysKey == 'JERBarrelDown':
                    pt_branch = 'jerDown'
            elif absEta < 2.5:
                if sysKey == 'JEREndcap1Up':
                    pt_branch = 'jerUp'
                elif sysKey == 'JEREndcap1Down':
                    pt_branch = 'jerDown'
            pt_branch = 'pt_{}'.format(pt_branch)
        jet_pt = getattr(jet, pt_branch)
        return jet_pt >= 25.

    def beginFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
        for sysKey in self.branchMap:
            histKey = self.getHistKey(sysKey)
            assert(histKey not in self.hists_woBtag)
            assert(histKey not in self.hists_wBtag)
            histName_woBtag = '{}_woBtag{}'.format(self.histName, '_{}'.format(sysKey) if sysKey != 'none' else '')
            histName_wBtag = '{}_wBtag{}'.format(self.histName, '_{}'.format(sysKey) if sysKey != 'none' else '')
            self.hists_woBtag[histKey] = ROOT.TH1D(histName_woBtag, histName_woBtag, len(self.njets_array) - 1, self.njets_array)
            self.hists_wBtag[histKey] = ROOT.TH1D(histName_wBtag, histName_wBtag, len(self.njets_array) - 1, self.njets_array)
            self.hists_woBtag[histKey].Sumw2()
            self.hists_wBtag[histKey].Sumw2()

    def endFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
        self.out = ROOT.TFile.Open(self.outputFileName, 'recreate')
        self.out.cd()
        for sysKey in self.branchMap:
            histKey = self.getHistKey(sysKey)
            self.hists_woBtag[histKey].Write()
            self.hists_wBtag[histKey].Write()
        self.out.Close()

    def analyze(self, event):
        jets = Collection(event, self.jetBranchName)
        muons = Collection(event, self.muonBranchName)
        eles = Collection(event, self.electronBranchName)

        genWeight = clip_genWeight(getattr(event, self.genWeightBranchName), self.ref_genWeight)
        genWeight_sign = 1. if genWeight > 0. else -1.

        muons_loose = [ mu for mu in muons if self.preselect_mu(mu) ]
        muons_sel = [ mu for mu in muons_loose if self.select_mu(mu) ]
        eles_sel = [ ele for ele in eles if self.select_ele(ele, muons_loose) ]
        jet_idxs_overlap_mu = [ mu.jetIdx for mu in muons_sel if mu.jetIdx >= 0 ]
        jet_idxs_overlap_ele = [ ele.jetIdx for ele in eles_sel if ele.jetIdx >= 0 ]
        jet_idxs_overlap = list(sorted(set(jet_idxs_overlap_mu) | set(jet_idxs_overlap_ele)))
        jets_cleaned = [ jet for jet in jets if jet.jetIdx not in jet_idxs_overlap and self.preselect_jet(jet) ]

        for sysKey in self.branchMap:
            if sysKey == 'pileupUp':
                puWeight = getattr(event, self.puWeightBranchNameUp)
            elif sysKey == 'pileupDown':
                puWeight = getattr(event, self.puWeightBranchNameDown)
            else:
                puWeight = getattr(event, self.puWeightBranchName)
            l1PrefiringWeight = 1.
            if self.era != 2018:
                if sysKey == 'l1PreFireUp':
                    l1PrefiringWeight = getattr(event, self.l1prefireWeightBranchNameUp)
                if sysKey == 'l1PreFireDown':
                    l1PrefiringWeight = getattr(event, self.l1prefireWeightBranchNameDown)
                else:
                    l1PrefiringWeight = getattr(event, self.l1prefireWeightBranchName)
            topPtRwgt = 1.
            if hasattr(event, self.topPtRwgtBranchName):
                topPtRwgt = getattr(event, self.topPtRwgtBranchName)
                if sysKey == 'topPtReweightingUp':
                    topPtRwgt *= topPtRwgt
                elif sysKey == 'topPtReweightingDown':
                    topPtRwgt = 1.
                else:
                    pass
            nominalWeight = genWeight_sign if self.useGenWeightSignOnly else genWeight
            nominalWeight *= puWeight * l1PrefiringWeight * topPtRwgt

            btag_branch = '{}_{}'.format(self.btagSF_branch, self.branchMap[sysKey]['btag']) if self.branchMap[sysKey]['btag'] else self.btagSF_branch

            jets_loose = [ jet for jet in jets_cleaned if self.select_jet(jet, sysKey) ]
            njets_sel = min(len(jets_loose), self.njets - 1)
            btagSFs = [ getattr(jet, btag_branch) for jet in jets_loose ]
            btagWeight = reduce(lambda x, y: x * y, btagSFs, 1.)
            nominalWeight_times_btagWeight = nominalWeight * btagWeight

            histKey = self.getHistKey(sysKey)
            self.hists_woBtag[histKey].Fill(njets_sel, nominalWeight)
            self.hists_wBtag[histKey].Fill(njets_sel, nominalWeight_times_btagWeight)
        return True

# provide this variable as the 2nd argument to the import option for the nano_postproc.py script
btagSFRatio2016 = lambda outputFn, histName, ref_genWeight: btagSFRatioFinder(2016, outputFn, histName, ref_genWeight)
btagSFRatio2017 = lambda outputFn, histName, ref_genWeight: btagSFRatioFinder(2017, outputFn, histName, ref_genWeight)
btagSFRatio2018 = lambda outputFn, histName, ref_genWeight: btagSFRatioFinder(2018, outputFn, histName, ref_genWeight)
