import ROOT
import numpy as np
import collections

ROOT.PyConfig.IgnoreCommandLineOptions = True

from PhysicsTools.NanoAODTools.postprocessing.framework.eventloop import Module
from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import Collection

from tthAnalysis.NanoAODTools.tHweights_cfi import thIdxs

REF_GENWEIGHT_LIMIT = 3

def clip(value, min_val = -10., max_val = 10.):
  return min(max(value, min_val), max_val)

def clip_genWeight(genWeight, ref_genWeight):
    assert(ref_genWeight > 0.)
    max_val = REF_GENWEIGHT_LIMIT * ref_genWeight
    min_val = -max_val
    return clip(genWeight, min_val = min_val, max_val = max_val)

class countHistogramProducer(Module):

  def __init__(self, outputFileName, process_name, refGenWeight, compTopRwgt, compHTXS, splitByLHENjet, splitByLHEHT):
    self.puWeightName            = 'puWeight'
    self.puWeightName_up         = '%sUp' % self.puWeightName
    self.puWeightName_down       = '%sDown' % self.puWeightName
    self.l1PrefireWeightName     = 'L1PreFiringWeight'
    self.l1PrefireWeightNomName  = '%s_Nom' % self.l1PrefireWeightName
    self.l1PrefireWeightUpName   = '%s_Up' % self.l1PrefireWeightName
    self.l1PrefireWeightDownName = '%s_Dn' % self.l1PrefireWeightName
    self.genWeightName           = 'genWeight'
    self.PSWeightName            = 'PSWeight'
    self.PSWeightCountName       = 'n%s' % self.PSWeightName
    self.nPSWeight_required      = 4 # ISR down, FSR down, ISR up, FSR up
    self.nPSweight               = self.nPSWeight_required + 2 # ISR+FSR up & down (envelope)
    self.nominalLHEweightName    = 'LHEWeight_originalXWGTUP'
    self.lheTHXWeightName        = 'LHEReweightingWeight'
    self.lheTHXWeightCountName   = 'n%s' % self.lheTHXWeightName
    self.LHEPdfWeightName        = 'LHEPdfWeight'
    self.LHEScaleWeightName      = 'LHEScaleWeight'
    self.LHEEnvelopeName         = 'LHEEnvelopeWeight'
    self.LHEEnvelopeNameUp       = '%sUp' % self.LHEEnvelopeName
    self.LHEEnvelopeNameDown     = '%sDown' % self.LHEEnvelopeName
    self.nLHEPdfWeight           = 101
    self.nLHEScaleWeight         = 9
    self.nLHEEnvelope            = 2
    self.LHEEnvelopeIdxs         = {
      9 : [ 0, 1, 3, 5, 7, 8 ], # 0/8 muR & muF down/up, 1/7 muR down/up, 3/5 muF down/up
      8 : [ 0, 1, 3, 4, 6, 7 ], # same as 9, but the 5th weight (muR = muF = 1) is omitted
    }
    self.compLHEEnvelope         = False
    self.compTopRwgt             = compTopRwgt
    self.topRwgtBranchName       = "topPtRwgt"
    self.genTopCollectionName    = "GenTop"
    self.compHTXS                = compHTXS
    self.splitByLHENjet          = splitByLHENjet
    self.splitByLHEHT            = splitByLHEHT
    self.htxsBranchName          = "HTXS_Higgs"
    self.htxsPtBranchName        = "%s_pt" % self.htxsBranchName
    self.htxsEtaBranchName       = "%s_y" % self.htxsBranchName
    self.LHENjetsBranchName      = "LHE_Njets"
    self.LHEHTBranchName         = "LHE_HT"
    self.ref_genWeight           = abs(float(refGenWeight))
    self.process_name            = process_name
    self.outputFileName          = outputFileName
    self.out                     = None

    if self.compHTXS and (self.splitByLHENjet or self.splitByLHEHT):
      raise ValueError("Cannot enable HTXS binning and LHE binning simultanteously")

    self.ISR_down_idx = 0
    self.FSR_down_idx = 1
    self.ISR_up_idx = 2
    self.FSR_up_idx = 3

    self.topPtRwgtChoices = [ "TOP16011", "Linear", "Quadratic", "HighPt" ]

    self.useFullGenWeight = [ False, True ]

    self.htxs = collections.OrderedDict([
      ("fwd",         lambda pt, eta: abs(eta) >= 2.5                     ),
      ("pt0to60",     lambda pt, eta: abs(eta) < 2.5 and         pt <  60.),
      ("pt60to120",   lambda pt, eta: abs(eta) < 2.5 and  60. <= pt < 120.),
      ("pt120to200",  lambda pt, eta: abs(eta) < 2.5 and 120. <= pt < 200.),
      ("pt200to300",  lambda pt, eta: abs(eta) < 2.5 and 200. <= pt < 300.),
      ("ptGt300",     lambda pt, eta: abs(eta) < 2.5 and 300. <= pt       ),
      ("pt300to450",  lambda pt, eta: abs(eta) < 2.5 and 300. <= pt < 450.),
      ("ptGt450",     lambda pt, eta: abs(eta) < 2.5 and 450. <= pt       ),
    ])

    self.lheNjets = collections.OrderedDict([
      ("LHENjet0", lambda lheNjet: lheNjet == 0),
      ("LHENjet1", lambda lheNjet: lheNjet == 1),
      ("LHENjet2", lambda lheNjet: lheNjet == 2),
      ("LHENjet3", lambda lheNjet: lheNjet == 3),
      ("LHENjet4", lambda lheNjet: lheNjet == 4),
    ])
    self.lheHT = collections.OrderedDict([
      ("LHEHT0to70",      lambda lhe_HT:          lhe_HT <   70.),
      ("LHEHT70to100",    lambda lhe_HT:   70. <= lhe_HT <  100.),
      ("LHEHT100to200",   lambda lhe_HT:  100. <= lhe_HT <  200.),
      ("LHEHT200to400",   lambda lhe_HT:  200. <= lhe_HT <  400.),
      ("LHEHT400to600",   lambda lhe_HT:  400. <= lhe_HT <  600.),
      ("LHEHT600to800",   lambda lhe_HT:  600. <= lhe_HT <  800.),
      ("LHEHT800to1200",  lambda lhe_HT:  800. <= lhe_HT < 1200.),
      ("LHEHT1200to2500", lambda lhe_HT: 1200. <= lhe_HT < 2500.),
      ("LHEHT2500toInf",  lambda lhe_HT: 2500. <= lhe_HT        ),
    ])
    self.lheNjetsHT = []
    for lheNjet_key in self.lheNjets:
      for lheHT_key in self.lheHT:
        self.lheNjetsHT.append('{}_{}'.format(lheNjet_key, lheHT_key))

    if self.compTopRwgt:
      print("Computing top reweighting: %s" % self.compTopRwgt)
    else:
      print("NOT computing top reweighting: %s" % self.compTopRwgt)

    self.histograms = collections.OrderedDict([
      ('Count', {
        'bins'  : 1,
        'min'   : 0.,
        'max'   : 2.,
        'title' : 'sum(1)',
      }),
    ])
    self.lheTHXSMWeightIndices = thIdxs
    self.topPtRwgtLabels = [ "" ]
    self.topPtRwgtTitles = [ "" ]
    if self.compTopRwgt:
      for choice in self.topPtRwgtChoices:
        self.topPtRwgtLabels.extend([ "{}TopPtRwgtSF".format(choice), "{}TopPtRwgtSFSquared".format(choice) ])
        self.topPtRwgtTitles.extend([ "* top-pT({})".format(choice), "* top-pT({})^2".format(choice) ])

    self.aux_binning = [ "" ]
    if self.compHTXS:
      self.aux_binning.extend(list(self.htxs.keys()))
    elif self.splitByLHENjet and not self.splitByLHEHT:
      self.aux_binning.extend(list(self.lheNjets.keys()))
    elif self.splitByLHEHT and not self.splitByLHENjet:
      self.aux_binning.extend(list(self.lheHT.keys()))
    elif self.splitByLHENjet and self.splitByLHEHT:
      self.aux_binning.extend(self.lheNjetsHT)

    for fullGenWeight in self.useFullGenWeight:
      for topPtRwgtIdx, topPtRwgtLabel in enumerate(self.topPtRwgtLabels):
        for lheTHXSMWeightIndex in self.lheTHXSMWeightIndices:
          for aux_bin in self.aux_binning:
            do_tH = lheTHXSMWeightIndex >= 0
            insert_title = self.topPtRwgtTitles[topPtRwgtIdx]
            insert_title += ("* LHE(tH %d)" % lheTHXSMWeightIndex) if do_tH else ""
            insert_name = topPtRwgtLabel
            insert_name += ("_rwgt%d" % lheTHXSMWeightIndex) if do_tH else ""
            suffix_title = ""

            if aux_bin:
              insert_name_empty = not bool(insert_name)
              insert_name += "_%s" % aux_bin
              if self.compHTXS:
                aux_bin_name = aux_bin.replace('pt', 'Higgs pt ').replace('to', '-').replace('Gt', '> ').replace('fwd', 'forward Higgs')
              elif self.splitByLHENjet and not self.splitByLHEHT:
                aux_bin_name = 'LHENjets == {}'.format(aux_bin[-1])
              elif self.splitByLHEHT and not self.splitByLHENjet:
                aux_bin_split = aux_bin[len('LHEHT'):].split('to')
                if aux_bin_split[1] != 'Inf':
                  aux_bin_name = '{} <= LHEHT < {}'.format(*aux_bin_split)
                else:
                  aux_bin_name = 'LHEHT >= {}'.format(aux_bin_split[0])
              elif self.splitByLHENjet and self.splitByLHEHT:
                aux_bin_njet, aux_bin_ht = aux_bin.split('_')
                aux_bin_name_njet = 'LHENjets == {}'.format(aux_bin_njet[-1])
                aux_bin_split = aux_bin_ht[len('LHEHT'):].split('to')
                if aux_bin_split[1] != 'Inf':
                  aux_bin_name_ht = '{} <= LHEHT < {}'.format(*aux_bin_split)
                else:
                  aux_bin_name_ht = 'LHEHT >= {}'.format(aux_bin_split[0])
                aux_bin_name = '{} and {}'.format(aux_bin_name_njet, aux_bin_name_ht)
              else:
                assert(False)
              suffix_title += " (%s)" % aux_bin_name

              insert_name_empty_key = 'Count{}'.format(insert_name)
              if insert_name_empty and insert_name_empty_key not in self.histograms:
                self.histograms.update([
                  (insert_name_empty_key, {
                    'bins'  : 1,
                    'min'   : 0.,
                    'max'   : 2.,
                    'title' : 'sum(1) {}'.format(suffix_title),
                  })
                ])

            gen_str = "gen" if fullGenWeight else "sgn(gen)"
            prefix = "CountWeighted{}".format("Full" if fullGenWeight else "")
            self.histograms.update([
              ('{}{}'.format(prefix, insert_name), {
                'bins'  : 3,
                'min'   : -0.5,
                'max'   : 2.5,
                'title' : 'sum({} * PU(central,up,down){}) {}'.format(gen_str, insert_title, suffix_title),
              }),
              ('{}L1PrefireNom{}'.format(prefix, insert_name), {
                'bins'  : 3,
                'min'   : -0.5,
                'max'   : 2.5,
                'title' : 'sum({} * PU(central,up,down){} * L1Prefire(nom)) {}'.format(gen_str, insert_title, suffix_title),
              }),
              ('{}L1Prefire{}'.format(prefix, insert_name), {
                'bins'  : 3,
                'min'   : -0.5,
                'max'   : 2.5,
                'title' : 'sum({} * PU(central){} * L1Prefire(nom,up,down)) {}'.format(gen_str, insert_title, suffix_title),
              }),
              ('{}LHEWeightPdf{}'.format(prefix, insert_name), {
                'bins'  : self.nLHEPdfWeight,
                'min'   : -0.5,
                'max'   : self.nLHEPdfWeight - 0.5,
                'title' : 'sum({} * PU(central){} * LHE(pdf)) {}'.format(gen_str, insert_title, suffix_title),
              }),
              ('{}LHEWeightPdfL1PrefireNom{}'.format(prefix, insert_name), {
                'bins'  : self.nLHEPdfWeight,
                'min'   : -0.5,
                'max'   : self.nLHEPdfWeight - 0.5,
                'title' : 'sum({} * PU(central){} * LHE(pdf) * L1Prefire(nom)) {}'.format(gen_str, insert_title, suffix_title),
              }),
              ('{}LHEWeightScale{}'.format(prefix, insert_name), {
                'bins'  : self.nLHEScaleWeight,
                'min'   : -0.5,
                'max'   : self.nLHEScaleWeight - 0.5,
                'title' : 'sum({} * PU(central){} * LHE(scale)) {}'.format(gen_str, insert_title, suffix_title),
              }),
              ('{}LHEWeightScaleL1PrefireNom{}'.format(prefix, insert_name), {
                'bins'  : self.nLHEScaleWeight,
                'min'   : -0.5,
                'max'   : self.nLHEScaleWeight - 0.5,
                'title' : 'sum({} * PU(central){} * LHE(scale) * L1Prefire(nom)) {}'.format(gen_str, insert_title, suffix_title),
              }),
              ('{}LHEEnvelope{}'.format(prefix, insert_name), {
                'bins'  : self.nLHEEnvelope,
                'min'   : -0.5,
                'max'   : self.nLHEEnvelope - 0.5,
                'title' : 'sum({} * PU(central){} * LHE(envelope up, down)) {}'.format(gen_str, insert_title, suffix_title),
              }),
              ('{}LHEEnvelopeL1PrefireNom{}'.format(prefix, insert_name), {
                'bins'  : self.nLHEEnvelope,
                'min'   : -0.5,
                'max'   : self.nLHEEnvelope - 0.5,
                'title' : 'sum({} * PU(central){} * LHE(envelope up, down) * L1Prefire(nom)) {}'.format(gen_str, insert_title, suffix_title),
              }),
              ('{}PSWeight{}'.format(prefix, insert_name), {
                'bins': self.nPSweight,
                'min': -0.5,
                'max': self.nPSweight - 0.5,
                'title': 'sum({} * PU(central){} * PS(ISR/FSR/both up, ISR/FSR/both down)) {}'.format(gen_str, insert_title, suffix_title),
              }),
              ('{}PSWeightL1PrefireNom{}'.format(prefix, insert_name), {
                'bins': self.nPSweight,
                'min': -0.5,
                'max': self.nPSweight - 0.5,
                'title': 'sum({} * PU(central){} * PS(ISR/FSR/both up, ISR/FSR/both down) * L1Prefire(nom)) {}'.format(gen_str, insert_title, suffix_title),
              }),
              # the PS weights may not average to 1 because of incorrect normalization, see
              # https://hypernews.cern.ch/HyperNews/CMS/get/physTools/3709.html
              # https://github.com/cms-nanoAOD/cmssw/issues/381
              ('{}PSWeightOriginalXWGTUP{}'.format(prefix, insert_name), {
                'bins': self.nPSweight,
                'min': -0.5,
                'max': self.nPSweight - 0.5,
                'title': 'sum({} * PU(central){} * PS(ISR/FSR/both up, ISR/FSR/both down) * LHE(nom)) {}'.format(gen_str, insert_title, suffix_title),
              }),
              ('{}PSWeightOriginalXWGTUPL1PrefireNom{}'.format(prefix, insert_name), {
                'bins': self.nPSweight,
                'min': -0.5,
                'max': self.nPSweight - 0.5,
                'title': 'sum({} * PU(central){} * PS(ISR/FSR/both up, ISR/FSR/both down) * L1Prefire(nom) * LHE(nom)) {}'.format(gen_str, insert_title, suffix_title),
              }),
            ])

    for histogramName in self.histograms:
      self.histograms[histogramName]['histogram'] = None

    self.isPrinted = {
      branchName : False for branchName in [
        self.puWeightName, self.genWeightName, self.lheTHXWeightName, self.LHEPdfWeightName,
        self.LHEScaleWeightName, self.PSWeightCountName, self.nominalLHEweightName,
      ]
    }

  def initHistograms(self, histogramNames, nofBins = -1):
    for histogramName in histogramNames:
      assert(histogramName in self.histograms)
      histogramParams = self.histograms[histogramName]
      if nofBins >= 0 and histogramParams['bins'] != nofBins:
        histogramParams['bins'] = nofBins
        histogramParams['max'] = nofBins - 0.5
      histogram_type = ROOT.TH1I if histogramName == 'Count' or histogramName.startswith('Count_') else ROOT.TH1F
      histogramParams['histogram'] = histogram_type(
        histogramName, histogramParams['title'],
        histogramParams['bins'], histogramParams['min'], histogramParams['max']
      )

  def clip_lhe(self, value, nominal = 1., min_val = -10., max_val = 10.):
    denom = nominal if nominal != 0. else 1.
    correctiveFactor = 2. if self.nLHEScaleWeight == 8 else 1.
    return clip(value * correctiveFactor / denom, min_val, max_val)

  def isInitialized(self, histogramNames):
    return all(map(
      lambda histogramName: histogramName in self.histograms and \
                            self.histograms[histogramName]['histogram'] != None,
      histogramNames
    ))

  def compTopRwgtSF(self, genTopPt, choice):
    if choice == 'TOP16011':
      # figures from TOP-16-011
      a = 0.0615
      b = -0.0005
      genTopPt = min(genTopPt, 800.)
      return np.exp(a + b * genTopPt)
    elif choice == 'Linear':
      a = 0.058
      b = -0.000466
      genTopPt = min(genTopPt, 500.)
      return np.exp(a + b * genTopPt)
    elif choice == 'Quadratic':
      a = 0.088
      b = -0.00087
      c = 9.2e-07
      genTopPt = min(genTopPt, 472.)
      return np.exp(a + b * genTopPt + c * genTopPt**2)
    elif choice == 'HighPt':
      # CV: new parametrization that is valid up tp 3 TeV, given on slide 12 of the presentation by Dennis Roy in the Higgs PAG meeting on 12/05/2020:
      #       https://indico.cern.ch/event/904971/contributions/3857701/attachments/2036949/3410728/TopPt_20.05.12.pdf 
      a = -2.02274e-01
      b =  1.09734e-04
      c = -1.30088e-07
      d =  5.83494e+01
      e =  1.96252e+02
      genTopPt = min(genTopPt, 3000.)
      return np.exp(a + b * genTopPt + c * genTopPt**2 + d / (genTopPt + e))
    else:
      raise RuntimeError("Invalid choice: %s" % choice)
  
  def getTopRwgtSF(self, genTops, choice):
    assert(genTops)
    assert(len(genTops) == 2)
    assert(genTops[0].pdgId * genTops[1].pdgId < 0)
    assert(choice in self.topPtRwgtChoices)
    genTop_pos_idx = 0 if genTops[0].pdgId > 0 else 1
    genTop_neg_idx = 1 - genTop_pos_idx
    genTop_pos_pt = genTops[genTop_pos_idx].pt
    genTop_neg_pt = genTops[genTop_neg_idx].pt
    return np.sqrt(self.compTopRwgtSF(genTop_pos_pt, choice) * self.compTopRwgtSF(genTop_neg_pt, choice))

  def getLHENominal(self, LHEScaleWeight):
    return LHEScaleWeight[4] if len(LHEScaleWeight) == 9 else 1.

  def getLHEEnvelope(self, LHEScaleWeight):
    nof_lheScaleWeights = len(LHEScaleWeight)
    if nof_lheScaleWeights not in self.LHEEnvelopeIdxs:
      return (1., 1.)
    LHEEnvelopeValues = [ LHEScaleWeight[lhe_idx] for lhe_idx in self.LHEEnvelopeIdxs[nof_lheScaleWeights] ]
    return [ max(LHEEnvelopeValues), min(LHEEnvelopeValues) ]

  def beginJob(self):
    pass

  def endJob(self):
    pass

  def beginFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
    if wrappedOutputTree:
      self.out = wrappedOutputTree
      if self.compTopRwgt:
        for choice in self.topPtRwgtChoices:
          self.out.branch("{}_{}".format(self.topRwgtBranchName, choice), "F")
    inputTreeBranchNames = [ branch.GetName() for branch in inputTree.GetListOfBranches() ]
    if self.LHEScaleWeightName in inputTreeBranchNames:
      self.compLHEEnvelope = True
    if self.compLHEEnvelope:
      print("Computing LHE envelope weights")
      if self.out:
        self.out.branch(self.LHEEnvelopeNameUp,   "F")
        self.out.branch(self.LHEEnvelopeNameDown, "F")
    else:
      print("NOT computing LHE envelope weights")

  def endFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
    out_file = None

    if outputFile:
      outputFile.cd()
    else:
      assert(self.outputFileName)
      assert(self.process_name)
      out_file = ROOT.TFile.Open(self.outputFileName, 'recreate')
      out_dir = out_file.mkdir(self.process_name)
      out_dir.cd()

    for histogramName in self.histograms:
      if 'histogram' in self.histograms[histogramName] and \
         self.histograms[histogramName]['histogram'] != None:
        self.histograms[histogramName]['histogram'].Write()

    if out_file:
      out_file.Close()

  def analyze(self, event):
    if 'histogram' in self.histograms['Count']:
      if not self.isInitialized(['Count']):
        self.initHistograms(['Count'])
      self.histograms['Count']['histogram'].Fill(1, 1)

    has_l1Prefire = hasattr(event, self.l1PrefireWeightNomName) and \
                    hasattr(event, self.l1PrefireWeightUpName)  and \
                    hasattr(event, self.l1PrefireWeightDownName)
    if has_l1Prefire:
      l1_nom  = getattr(event, self.l1PrefireWeightNomName)
      l1_up   = getattr(event, self.l1PrefireWeightUpName)
      l1_down = getattr(event, self.l1PrefireWeightDownName)

    topRwgt = [ 1. ] * len(self.topPtRwgtChoices)
    LHEEnvelopeValues = [ 1., 1. ]
    if self.compTopRwgt:
      genTops = Collection(event, self.genTopCollectionName)
      topRwgt = [ self.getTopRwgtSF(genTops, choice) for choice in self.topPtRwgtChoices ]

    for aux_bin in self.aux_binning:

      if aux_bin:
        assert(self.compHTXS or self.splitByLHENjet or self.splitByLHEHT)
        if self.compHTXS:
          assert(aux_bin in self.htxs)
          if not hasattr(event, self.htxsPtBranchName):
            raise RuntimeError("No such branch: %s" % self.htxsPtBranchName)
          if not hasattr(event, self.htxsEtaBranchName):
            raise RuntimeError("No such branch: %s" % self.htxsEtaBranchName)
          htxs_pt = getattr(event, self.htxsPtBranchName)
          htxs_eta = getattr(event, self.htxsEtaBranchName)
          if not self.htxs[aux_bin](htxs_pt, htxs_eta):
            continue
        elif self.splitByLHENjet and not self.splitByLHEHT:
          assert(aux_bin in self.lheNjets)
          if not hasattr(event, self.LHENjetsBranchName):
            raise RuntimeError("No such branch: %s" % self.LHENjetsBranchName)
          lhe_njets = getattr(event, self.LHENjetsBranchName)
          if not self.lheNjets[aux_bin](lhe_njets):
            continue
        elif self.splitByLHEHT and not self.splitByLHENjet:
          assert(aux_bin in self.lheHT)
          if not hasattr(event, self.LHEHTBranchName):
            raise RuntimeError("No such branch: %s" % self.LHEHTBranchName)
          lhe_ht = getattr(event, self.LHEHTBranchName)
          if not self.lheHT[aux_bin](lhe_ht):
            continue
        elif self.splitByLHENjet and self.splitByLHEHT:
          assert(aux_bin in self.lheNjetsHT)
          if not hasattr(event, self.LHEHTBranchName):
            raise RuntimeError("No such branch: %s" % self.LHEHTBranchName)
          lhe_ht = getattr(event, self.LHEHTBranchName)
          if not hasattr(event, self.LHENjetsBranchName):
            raise RuntimeError("No such branch: %s" % self.LHENjetsBranchName)
          lhe_njets = getattr(event, self.LHENjetsBranchName)
          aux_bin_split = aux_bin.split('_')
          matches_lhe_njets = self.lheNjets[aux_bin_split[0]](lhe_njets)
          matches_lhe_ht = self.lheHT[aux_bin_split[1]](lhe_ht)
          matches_lhe_njets_ht = matches_lhe_njets and matches_lhe_ht
          if not matches_lhe_njets_ht:
            continue
        else:
          assert(False)

        if 'histogram' in self.histograms['Count_{}'.format(aux_bin)]:
          if not self.isInitialized(['Count_{}'.format(aux_bin)]):
            self.initHistograms(['Count_{}'.format(aux_bin)])
          self.histograms['Count_{}'.format(aux_bin)]['histogram'].Fill(1, 1)

      if hasattr(event, self.genWeightName):
        for fullGenWeight in self.useFullGenWeight:
          genWeight_full = clip_genWeight(getattr(event, self.genWeightName), self.ref_genWeight)
          genWeight_sign = np.sign(genWeight_full)
          genWeight = genWeight_full if fullGenWeight else genWeight_sign

          if hasattr(event, self.puWeightName):
            assert(hasattr(event, self.puWeightName_up))
            assert(hasattr(event, self.puWeightName_down))

            puWeight = getattr(event, self.puWeightName)
            puWeight_up = getattr(event, self.puWeightName_up)
            puWeight_down = getattr(event, self.puWeightName_down)

            for topPtRwgtIdx, topPtRwgtLabel in enumerate(self.topPtRwgtLabels):
              if self.compTopRwgt and topPtRwgtIdx > 0:
                topSF_pow = int((topPtRwgtIdx % 2) == 0) + 1
                assert(topSF_pow in [1, 2])
                topSF_idx = int((topPtRwgtIdx - 1) / 2)
                assert(topSF_idx <= len(self.topPtRwgtChoices))
                topSF = topRwgt[topSF_idx]**topSF_pow
              else:
                topSF = 1.

              for lheTHXSMWeightIndex in self.lheTHXSMWeightIndices:
                do_tH = lheTHXSMWeightIndex >= 0
                insert_name_common = topPtRwgtLabel
                insert_name_common += ("_rwgt%d" % lheTHXSMWeightIndex) if do_tH else ""

                lheTHXWeight = 1.
                has_lhe = False

                if do_tH:
                  if hasattr(event, self.lheTHXWeightCountName) and hasattr(event, self.lheTHXWeightName):
                    nofLheTHXWeights = getattr(event, self.lheTHXWeightCountName)
                    if lheTHXSMWeightIndex < nofLheTHXWeights:
                      lheTHXWeightArr = getattr(event, self.lheTHXWeightName)
                      lheTHXWeight = lheTHXWeightArr[lheTHXSMWeightIndex]
                      has_lhe = True
                  if not has_lhe:
                    if not self.isPrinted[self.lheTHXWeightName]:
                      self.isPrinted[self.lheTHXWeightName] = True
                      print('Missing or unfilled branch: %s' % self.lheTHXWeightName)

                if do_tH and not has_lhe:
                  continue

                if aux_bin:
                  insert_name = "%s_%s" % (insert_name_common, aux_bin)
                else:
                  insert_name = insert_name_common

                prefix = "CountWeighted{}".format("Full" if fullGenWeight else "")

                if 'histogram' in self.histograms['{}{}'.format(prefix, insert_name)]:
                  if not self.isInitialized(['{}{}'.format(prefix, insert_name)]):
                    self.initHistograms(['{}{}'.format(prefix, insert_name)])
                  self.histograms['{}{}'.format(prefix, insert_name)]['histogram'].Fill(0., genWeight * puWeight * lheTHXWeight * topSF)
                  self.histograms['{}{}'.format(prefix, insert_name)]['histogram'].Fill(1., genWeight * puWeight_up * lheTHXWeight * topSF)
                  self.histograms['{}{}'.format(prefix, insert_name)]['histogram'].Fill(2., genWeight * puWeight_down * lheTHXWeight * topSF)

                if has_l1Prefire:
                  if 'histogram' in self.histograms['{}L1PrefireNom{}'.format(prefix, insert_name)]:
                    if not self.isInitialized(['{}L1PrefireNom{}'.format(prefix, insert_name)]):
                      self.initHistograms(['{}L1PrefireNom{}'.format(prefix, insert_name)])
                    self.histograms['{}L1PrefireNom{}'.format(prefix, insert_name)]['histogram'].Fill(0., genWeight * puWeight * lheTHXWeight * l1_nom * topSF)
                    self.histograms['{}L1PrefireNom{}'.format(prefix, insert_name)]['histogram'].Fill(1., genWeight * puWeight_up * lheTHXWeight * l1_nom * topSF)
                    self.histograms['{}L1PrefireNom{}'.format(prefix, insert_name)]['histogram'].Fill(2., genWeight * puWeight_down * lheTHXWeight * l1_nom * topSF)

                  if 'histogram' in self.histograms['{}L1Prefire{}'.format(prefix, insert_name)]:
                    if not self.isInitialized(['{}L1Prefire{}'.format(prefix, insert_name)]):
                      self.initHistograms(['{}L1Prefire{}'.format(prefix, insert_name)])
                    self.histograms['{}L1Prefire{}'.format(prefix, insert_name)]['histogram'].Fill(0., genWeight * puWeight * lheTHXWeight * l1_nom * topSF)
                    self.histograms['{}L1Prefire{}'.format(prefix, insert_name)]['histogram'].Fill(1., genWeight * puWeight * lheTHXWeight * l1_up * topSF)
                    self.histograms['{}L1Prefire{}'.format(prefix, insert_name)]['histogram'].Fill(2., genWeight * puWeight * lheTHXWeight * l1_down * topSF)

                if hasattr(event, self.LHEScaleWeightName):
                  assert(self.compLHEEnvelope)
                  LHEScaleWeight = getattr(event, self.LHEScaleWeightName)
                  LHEEnvelopeValues = self.getLHEEnvelope(LHEScaleWeight)
                  LHENominal = self.getLHENominal(LHEScaleWeight)

                  nof_lheScaleWeight = len(LHEScaleWeight)
                  if nof_lheScaleWeight != self.nLHEScaleWeight:
                    print(
                      "WARNING: The length of '%s' array (= %i) does not match to the expected length of %i" % \
                      (self.LHEScaleWeightName, len(LHEScaleWeight), self.nLHEScaleWeight)
                    )
                    self.nLHEScaleWeight = nof_lheScaleWeight

                  if 'histogram' in self.histograms['{}LHEWeightScale{}'.format(prefix, insert_name)]:
                    if not self.isInitialized(['{}LHEWeightScale{}'.format(prefix, insert_name)]):
                      self.initHistograms(['{}LHEWeightScale{}'.format(prefix, insert_name)], self.nLHEScaleWeight)
                    for lhe_scale_idx in range(self.nLHEScaleWeight):
                      self.histograms['{}LHEWeightScale{}'.format(prefix, insert_name)]['histogram'].Fill(
                        float(lhe_scale_idx), genWeight * puWeight * lheTHXWeight * self.clip_lhe(LHEScaleWeight[lhe_scale_idx], LHENominal) * topSF
                      )

                  if has_l1Prefire:
                    if 'histogram' in self.histograms['{}LHEWeightScaleL1PrefireNom{}'.format(prefix, insert_name)]:
                      if not self.isInitialized(['{}LHEWeightScaleL1PrefireNom{}'.format(prefix, insert_name)]):
                        self.initHistograms(['{}LHEWeightScaleL1PrefireNom{}'.format(prefix, insert_name)], self.nLHEScaleWeight)
                      for lhe_scale_idx in range(self.nLHEScaleWeight):
                        self.histograms['{}LHEWeightScaleL1PrefireNom{}'.format(prefix, insert_name)]['histogram'].Fill(
                          float(lhe_scale_idx), genWeight * puWeight * lheTHXWeight * l1_nom * self.clip_lhe(LHEScaleWeight[lhe_scale_idx], LHENominal) * topSF
                        )

                  if 'histogram' in self.histograms['{}LHEEnvelope{}'.format(prefix, insert_name)]:
                    if not self.isInitialized(['{}LHEEnvelope{}'.format(prefix, insert_name)]):
                      self.initHistograms(['{}LHEEnvelope{}'.format(prefix, insert_name)], self.nLHEEnvelope)
                    for lhe_scale_idx, lhe_scale_value in enumerate(LHEEnvelopeValues):
                      self.histograms['{}LHEEnvelope{}'.format(prefix, insert_name)]['histogram'].Fill(
                        float(lhe_scale_idx), genWeight * puWeight * lheTHXWeight * self.clip_lhe(lhe_scale_value, LHENominal) * topSF
                      )
                  if has_l1Prefire:
                    if 'histogram' in self.histograms['{}LHEEnvelopeL1PrefireNom{}'.format(prefix, insert_name)]:
                      if not self.isInitialized(['{}LHEEnvelopeL1PrefireNom{}'.format(prefix, insert_name)]):
                        self.initHistograms(['{}LHEEnvelopeL1PrefireNom{}'.format(prefix, insert_name)], self.nLHEEnvelope)
                      for lhe_scale_idx, lhe_scale_value in enumerate(LHEEnvelopeValues):
                        self.histograms['{}LHEEnvelopeL1PrefireNom{}'.format(prefix, insert_name)]['histogram'].Fill(
                          float(lhe_scale_idx), genWeight * puWeight * lheTHXWeight * l1_nom * self.clip_lhe(lhe_scale_value, LHENominal) * topSF
                        )

                else:
                  if not self.isPrinted[self.LHEScaleWeightName]:
                    self.isPrinted[self.LHEScaleWeightName] = True
                    print('Missing branch: %s' % self.LHEScaleWeightName)

                if hasattr(event, self.LHEPdfWeightName):
                  LHEPdfWeight = getattr(event, self.LHEPdfWeightName)

                  if len(LHEPdfWeight) != self.nLHEPdfWeight:
                    print(
                      "WARNING: The length of '%s' array (= %i) does not match to the expected length of %i" % \
                      (self.LHEPdfWeightName, len(LHEPdfWeight), self.nLHEPdfWeight)
                    )
                    self.nLHEPdfWeight = len(LHEPdfWeight)

                  if 'histogram' in self.histograms['{}LHEWeightPdf{}'.format(prefix, insert_name)]:
                    if not self.isInitialized(['{}LHEWeightPdf{}'.format(prefix, insert_name)]):
                      self.initHistograms(['{}LHEWeightPdf{}'.format(prefix, insert_name)], self.nLHEPdfWeight)
                    for lhe_pdf_idx in range(self.nLHEPdfWeight):
                      self.histograms['{}LHEWeightPdf{}'.format(prefix, insert_name)]['histogram'].Fill(
                        float(lhe_pdf_idx), genWeight * puWeight * lheTHXWeight * self.clip_lhe(LHEPdfWeight[lhe_pdf_idx]) * topSF
                      )

                  if has_l1Prefire:
                    if 'histogram' in self.histograms['{}LHEWeightPdfL1PrefireNom{}'.format(prefix, insert_name)]:
                      if not self.isInitialized(['{}LHEWeightPdfL1PrefireNom{}'.format(prefix, insert_name)]):
                        self.initHistograms(['{}LHEWeightPdfL1PrefireNom{}'.format(prefix, insert_name)], self.nLHEPdfWeight)
                      for lhe_pdf_idx in range(self.nLHEPdfWeight):
                        self.histograms['{}LHEWeightPdfL1PrefireNom{}'.format(prefix, insert_name)]['histogram'].Fill(
                          float(lhe_pdf_idx), genWeight * puWeight * lheTHXWeight * l1_nom * self.clip_lhe(LHEPdfWeight[lhe_pdf_idx]) * topSF
                        )
                else:
                  if not self.isPrinted[self.LHEPdfWeightName]:
                    self.isPrinted[self.LHEPdfWeightName] = True
                    print('Missing branch: %s' % self.LHEPdfWeightName)

                nof_PSweight = getattr(event, self.PSWeightCountName, 0)
                if nof_PSweight == self.nPSWeight_required:
                  PSweights = getattr(event, self.PSWeightName)
                  assert(len(PSweights) == nof_PSweight)
                  # FSR and ISR may move in opposite directions -> just take min and max of the weights to build the envelope
                  PS_env_up = max([ PSweights[ps_idx] for ps_idx in range(nof_PSweight) ])
                  PS_env_down = min([ PSweights[ps_idx] for ps_idx in range(nof_PSweight) ])
                  # target: ISR/FSR/both up, ISR/FSR/both down
                  PSweights_ext = [
                    PSweights[self.ISR_up_idx],   PSweights[self.FSR_up_idx],   PS_env_up,
                    PSweights[self.ISR_down_idx], PSweights[self.FSR_down_idx], PS_env_down,
                  ]
                  assert(len(PSweights_ext) == self.nPSweight)

                  if 'histogram' in self.histograms['{}PSWeight{}'.format(prefix, insert_name)]:
                    if not self.isInitialized(['{}PSWeight{}'.format(prefix, insert_name)]):
                      self.initHistograms(['{}PSWeight{}'.format(prefix, insert_name)], self.nPSweight)
                    for psweight_idx, psweight in enumerate(PSweights_ext):
                      self.histograms['{}PSWeight{}'.format(prefix, insert_name)]['histogram'].Fill(
                        float(psweight_idx), genWeight * puWeight * lheTHXWeight * clip(psweight) * topSF
                      )
                  if has_l1Prefire:
                    if 'histogram' in self.histograms['{}PSWeightL1PrefireNom{}'.format(prefix, insert_name)]:
                      if not self.isInitialized(['{}PSWeightL1PrefireNom{}'.format(prefix, insert_name)]):
                        self.initHistograms(['{}PSWeightL1PrefireNom{}'.format(prefix, insert_name)], self.nPSweight)
                      for psweight_idx, psweight in enumerate(PSweights_ext):
                        self.histograms['{}PSWeightL1PrefireNom{}'.format(prefix, insert_name)]['histogram'].Fill(
                          float(psweight_idx), genWeight * puWeight * lheTHXWeight * l1_nom * clip(psweight) * topSF
                        )

                  if hasattr(event, self.nominalLHEweightName):
                    lhe_nom = getattr(event, self.nominalLHEweightName)
                    if 'histogram' in self.histograms['{}PSWeightOriginalXWGTUP{}'.format(prefix, insert_name)]:
                      if not self.isInitialized(['{}PSWeightOriginalXWGTUP{}'.format(prefix, insert_name)]):
                        self.initHistograms(['{}PSWeightOriginalXWGTUP{}'.format(prefix, insert_name)], self.nPSweight)
                      for psweight_idx, psweight in enumerate(PSweights_ext):
                        self.histograms['{}PSWeightOriginalXWGTUP{}'.format(prefix, insert_name)]['histogram'].Fill(
                          float(psweight_idx), genWeight * puWeight * lheTHXWeight * clip(psweight * lhe_nom) * topSF
                        )
                    if has_l1Prefire:
                      if 'histogram' in self.histograms['{}PSWeightOriginalXWGTUPL1PrefireNom{}'.format(prefix, insert_name)]:
                        if not self.isInitialized(['{}PSWeightOriginalXWGTUPL1PrefireNom{}'.format(prefix, insert_name)]):
                          self.initHistograms(['{}PSWeightOriginalXWGTUPL1PrefireNom{}'.format(prefix, insert_name)], self.nPSweight)
                        for psweight_idx, psweight in enumerate(PSweights_ext):
                          self.histograms['{}PSWeightOriginalXWGTUPL1PrefireNom{}'.format(prefix, insert_name)]['histogram'].Fill(
                            float(psweight_idx), genWeight * puWeight * lheTHXWeight * l1_nom * clip(psweight * lhe_nom) * topSF
                          )
                  else:
                    if not self.isPrinted[self.nominalLHEweightName]:
                      self.isPrinted[self.nominalLHEweightName] = True
                      print('Missing branch: %s' % self.nominalLHEweightName)

                else:
                  if not self.isPrinted[self.PSWeightCountName]:
                    self.isPrinted[self.PSWeightCountName] = True
                    print('Missing branch: %s' % self.PSWeightCountName)

        else:
          if not self.isPrinted[self.puWeightName]:
            self.isPrinted[self.puWeightName] = True
            print('Missing branch: %s' % self.puWeightName)

      else:
        if not self.isPrinted[self.genWeightName]:
          self.isPrinted[self.genWeightName] = True
          print('Missing branch: %s' % self.genWeightName)

    if self.out:
      if self.compTopRwgt:
        for topPtRwgtIdx, choice in enumerate(self.topPtRwgtChoices):
          self.out.fillBranch("{}_{}".format(self.topRwgtBranchName, choice), topRwgt[topPtRwgtIdx])
      if self.compLHEEnvelope:
        #TODO in future iterations do not clip or apply the corrective factors, do it all at the analysis level instead
        self.out.fillBranch(self.LHEEnvelopeNameUp, self.clip_lhe(LHEEnvelopeValues[0]))
        self.out.fillBranch(self.LHEEnvelopeNameDown, self.clip_lhe(LHEEnvelopeValues[1]))

    return True

# provide this variable as the 2nd argument to the import option for the nano_postproc.py script
def countHistogramAll(output_file, process_name, refGenWeight):
  return countHistogramProducer(output_file, process_name, refGenWeight, compTopRwgt = False, compHTXS = False, splitByLHENjet = False, splitByLHEHT = False)
def countHistogramAllCompTopRwgt(output_file, process_name, refGenWeight):
  return countHistogramProducer(output_file, process_name, refGenWeight, compTopRwgt = True,  compHTXS = False, splitByLHENjet = False, splitByLHEHT = False)
def countHistogramAllCompHTXS(output_file, process_name, refGenWeight):
  return countHistogramProducer(output_file, process_name, refGenWeight, compTopRwgt = False, compHTXS = True,  splitByLHENjet = False, splitByLHEHT = False)
def countHistogramAllSplitByLHENjet(output_file, process_name, refGenWeight):
  return countHistogramProducer(output_file, process_name, refGenWeight, compTopRwgt = False, compHTXS = False, splitByLHENjet = True,  splitByLHEHT = False)
def countHistogramAllSplitByLHEHT(output_file, process_name, refGenWeight):
  return countHistogramProducer(output_file, process_name, refGenWeight, compTopRwgt = False, compHTXS = False, splitByLHENjet = False, splitByLHEHT = True)
def countHistogramAllSplitByLHENjetHT(output_file, process_name, refGenWeight):
  return countHistogramProducer(output_file, process_name, refGenWeight, compTopRwgt = False, compHTXS = False, splitByLHENjet = True,  splitByLHEHT = True)
