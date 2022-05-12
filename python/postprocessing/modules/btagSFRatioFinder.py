import ROOT
import math, os, array, collections
from functools import reduce
ROOT.PyConfig.IgnoreCommandLineOptions = True

from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import Collection, Object
from PhysicsTools.NanoAODTools.postprocessing.framework.eventloop import Module
from PhysicsTools.NanoAODTools.postprocessing.tools import deltaR

from tthAnalysis.NanoAODTools.postprocessing.modules.countHistogramProducer import clip_genWeight

class btagSFRatioFinder(Module):

    def __init__(self, era, outputFn, histName, ref_genWeight, applySLcuts = False):
        self.jetBranchName = "Jet"
        self.muonBranchName = "Muon"
        self.electronBranchName = "Electron"
        self.tauBranchName = "Tau"
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
        btagTightCuts = { 2016 : 0.7221, 2017 : 0.7489, 2018 : 0.7264 }
        self.btagLooseCut = btagLooseCuts[self.era]
        self.btagMediumCut = btagMediumCuts[self.era]
        self.btagTightCut = btagTightCuts[self.era]

        self.mu_wp = 0.50
        self.ele_wp = 0.30

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
                btag_name = '{}_{}'.format(shift.lower(), jes.replace('JES', 'jes'))
                self.branchMap[jes_key] = { 'pt' : jes_pt, 'btag' : btag_name }

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

        self.applySLcuts = applySLcuts
        self.triggerList_ele = {
            2016 : [ 'HLT_Ele25_eta2p1_WPTight_Gsf', 'HLT_Ele27_WPTight_Gsf', 'HLT_Ele27_eta2p1_WPLoose_Gsf' ],
            2017 : [ 'HLT_Ele32_WPTight_Gsf', 'HLT_Ele35_WPTight_Gsf' ],
            2018 : [ 'HLT_Ele32_WPTight_Gsf' ],
        }
        self.triggerList_mu = {
            2016 : [ 'HLT_IsoMu22_eta2p1', 'HLT_IsoMu22', 'HLT_IsoMu24', 'HLT_IsoTkMu22_eta2p1', 'HLT_IsoTkMu24', 'HLT_IsoTkMu22', ],
            2017 : [ 'HLT_IsoMu24', 'HLT_IsoMu27' ],
            2018 : [ 'HLT_IsoMu24', 'HLT_IsoMu27' ],
        }
        self.triggers_ele = self.triggerList_ele[self.era]
        self.triggers_mu = self.triggerList_mu[self.era]
        self.pt_ele = 32.
        self.pt_mu = 25.

    def beginJob(self):
        pass

    def endJob(self):
        pass

    def getHistKey(self, sysKey):
        return '{}_{}'.format(self.histName, sysKey)

    def get_p4(self, obj):
        p4 = ROOT.TLorentzVector()
        p4.SetPtEtaPhiM(obj.pt, obj.eta, obj.phi, obj.mass)
        return p4

    def check_lowMassVeto(self, leps):
        is_lowmll = False
        for lepi in range(len(leps)):
            for lepj in range(lepi - 1):
                mll = (self.get_p4(leps[lepi]) + self.get_p4(leps[lepj])).M()
                if mll < 12.:
                    is_lowmll = True
                    break
        return is_lowmll

    def check_zveto(self, leps):
        is_zveto = False
        for lepi in range(len(leps)):
            for lepj in range(lepi - 1):
                mll = (self.get_p4(leps[lepi]) + self.get_p4(leps[lepj])).M()
                if leps[lepi].charge * leps[lepj].charge < 0 and abs(mll - 90.) < 10.:
                    is_zveto = True
                    break
        return is_zveto

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
                       muon.jetPtRatio >= 1. / 1.8 and
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
               self.hlt_cut(ele) and \
               (
                   ele.assocJetBtag_DeepJet <= self.btagMediumCut if ele.mvaTTH > self.ele_wp else (
                           ele.assocJetBtag_DeepJet <= self.btagTightCut and
                           ele.jetPtRatio >= 1. / 1.7 and
                           ele.mvaFall17V2noIso_WP90
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

    def select_tau(self, tau):
        return tau.pt > 20. and \
               abs(tau.eta) < 2.3 and \
               abs(tau.dz) < 0.2 and \
               tau.idDeepTau2017v2VSjet_log >= 5 and \
               tau.idDeepTau2017v2VSmu_log > 0 and \
               tau.idDeepTau2017v2VSe_log > 0

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

        if self.applySLcuts:
            # 1 tight lepton + trigger fired
            lep_fakeable = list(sorted(
                muons_sel + eles_sel,
                key = lambda lep: self.cone_pt(lep, self.ele_wp if abs(lep.pdgId) != 13 else self.mu_wp),
                reverse = True
            ))
            if not lep_fakeable:
                return False
            lep_lead = lep_fakeable[0]
            if abs(lep_lead.pdgId) == 11:
                if lep_lead.mvaTTH < self.ele_wp or \
                   self.cone_pt(lep_lead, self.ele_wp) < self.pt_ele or \
                   not any(bool(getattr(event, hlt_path)) for hlt_path in self.triggers_ele):
                    return False
            elif abs(lep_lead.pdgId) == 13:
                if lep_lead.mvaTTH < self.mu_wp or \
                   self.cone_pt(lep_lead, self.mu_wp) < self.pt_mu or \
                   not any(bool(getattr(event, hlt_path)) for hlt_path in self.triggers_mu):
                    return False
            else:
                assert(False)
            # no more than 1 tight lepton
            lep_tight = [ lep for lep in lep_fakeable if lep.mvaTTH >= (self.ele_wp if abs(lep.pdgId) == 11 else self.mu_wp) ]
            if len(lep_tight) > 1:
                return False
            assert(len(lep_tight) == 1)
            # low mass resonance veto
            eles_loose_uncleaned = [ ele for ele in eles if self.preselect_ele(ele, []) ]
            if self.check_lowMassVeto(eles_loose_uncleaned + muons_loose):
                return False
            # Z veto
            eles_loose = [ ele for ele in eles_loose_uncleaned if not self.overlaps_any(ele, muons_loose, 0.3) ]
            if self.check_zveto(eles_loose) or self.check_zveto(muons_loose):
                return False
            # tau veto
            taus = Collection(event, self.tauBranchName)
            taus_tight = [ tau for tau in taus if self.select_tau(tau) ]
            if taus_tight:
                return False

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
btagSFRatioSL2016 = lambda outputFn, histName, ref_genWeight: btagSFRatioFinder(2016, outputFn, histName, ref_genWeight, True)
btagSFRatioSL2017 = lambda outputFn, histName, ref_genWeight: btagSFRatioFinder(2017, outputFn, histName, ref_genWeight, True)
btagSFRatioSL2018 = lambda outputFn, histName, ref_genWeight: btagSFRatioFinder(2018, outputFn, histName, ref_genWeight, True)
