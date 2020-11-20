import ROOT
import numpy as np
import collections

ROOT.PyConfig.IgnoreCommandLineOptions = True

from PhysicsTools.NanoAODTools.postprocessing.framework.eventloop import Module
from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import Collection

from tthAnalysis.NanoAODTools.tHweights_cfi import thIdxs

class countHistogramProducer(Module):

  def __init__(self, compTopRwgt, compHTXS, category = ''):
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
    self.nLHEEnvelope_required   = self.nLHEScaleWeight
    self.LHEEnvelopeIdxs         = [ 0, 1, 3, 5, 7, 8 ] # 0/8 muR & muF down/up, 1/7 muR down/up, 3/5 muF down/up
    self.compLHEEnvelope         = False
    self.compTopRwgt             = compTopRwgt
    self.topRwgtBranchName       = "topPtRwgt"
    self.genTopCollectionName    = "GenTop"
    self.compHTXS                = compHTXS
    self.htxsBrancBasehName      = "HTXS_Higgs"
    self.htxsPtBranchName        = "%s_pt" % self.htxsBrancBasehName
    self.htxsEtaBranchName       = "%s_y" % self.htxsBrancBasehName
    self.htxsBranchName          = "HTXS_stage1_2_cat_pTjet30GeV"
    self.category                = category

    self.ISR_down_idx = 0
    self.FSR_down_idx = 1
    self.ISR_up_idx = 2
    self.FSR_up_idx = 3

    self.topPtRwgtChoices = [ "TOP16011", "Linear", "Quadratic", "HighPt" ]

    self.htxs = None
    if self.compHTXS:
      assert(self.category in [ 'ttH', 'ggH', 'qqH', 'VH' ])
      if self.category == 'ttH':
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
      else:
        htxs_ggH = collections.OrderedDict([
          ("GG2H_FWDH", lambda id: id == 100),
          ("GG2H_PTH_200_300", lambda id: id == 101),
          ("GG2H_PTH_300_450", lambda id: id == 102),
          ("GG2H_PTH_450_650", lambda id: id == 103),
          ("GG2H_PTH_GT650",   lambda id: id == 104),
          ("GG2H_0J_PTH_0_10", lambda id: id == 105),
          ("GG2H_0J_PTH_GT10", lambda id: id == 106),
          ("GG2H_1J_PTH_0_60", lambda id: id == 107),
          ("GG2H_1J_PTH_60_120", lambda id: id == 108),
          ("GG2H_1J_PTH_120_200", lambda id: id == 109),
          ("GG2H_GE2J_MJJ_0_350_PTH_0_60", lambda id: id == 110),
          ("GG2H_GE2J_MJJ_0_350_PTH_60_120", lambda id: id == 111),
          ("GG2H_GE2J_MJJ_0_350_PTH_120_200", lambda id: id == 112),
          ("GG2H_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_0_25", lambda id: id == 113),
          ("GG2H_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_GT25", lambda id: id == 114),
          ("GG2H_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_0_25", lambda id: id == 115),
          ("GG2H_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_GT25", lambda id: id == 116),
        ])
        htxs_qqH = collections.OrderedDict([
          ("QQ2HQQ_FWDH", lambda id: id == 200),
          ("QQ2HQQ_0J", lambda id: id == 201),
          ("QQ2HQQ_1J", lambda id: id == 202),
          ("QQ2HQQ_GE2J_MJJ_0_60", lambda id: id == 203),
          ("QQ2HQQ_GE2J_MJJ_60_120", lambda id: id == 204),
          ("QQ2HQQ_GE2J_MJJ_120_350", lambda id: id == 205),
          ("QQ2HQQ_GE2J_MJJ_GT350_PTH_GT200", lambda id: id == 206),
          ("QQ2HQQ_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_0_25", lambda id: id == 207),
          ("QQ2HQQ_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_GT25", lambda id: id == 208),
          ("QQ2HQQ_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_0_25", lambda id: id == 209),
          ("QQ2HQQ_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_GT25", lambda id: id == 210),
        ])
        htxs_wh = collections.OrderedDict([
          ("QQ2HLNU_FWDH", lambda id: id == 300),
          ("QQ2HLNU_PTV_0_75", lambda id: id == 301),
          ("QQ2HLNU_PTV_75_150", lambda id: id == 302),
          ("QQ2HLNU_PTV_150_250_0J", lambda id: id == 303),
          ("QQ2HLNU_PTV_150_250_GE1J", lambda id: id == 304),
          ("QQ2HLNU_PTV_GT250", lambda id: id == 305),
        ])
        htxs_zh = collections.OrderedDict([
          ("QQ2HLL_FWDH", lambda id: id == 400),
          ("QQ2HLL_PTV_0_75", lambda id: id == 401),
          ("QQ2HLL_PTV_75_150", lambda id: id == 402),
          ("QQ2HLL_PTV_150_250_0J", lambda id: id == 403),
          ("QQ2HLL_PTV_150_250_GE1J", lambda id: id == 404),
          ("QQ2HLL_PTV_GT250", lambda id: id == 405),
        ])
        htxs_gg2Hll = collections.OrderedDict([
          ("GG2HLL_FWDH", lambda id: id == 500),
          ("GG2HLL_PTV_0_75", lambda id: id == 501),
          ("GG2HLL_PTV_75_150", lambda id: id == 502),
          ("GG2HLL_PTV_150_250_0J", lambda id: id == 503),
          ("GG2HLL_PTV_150_250_GE1J", lambda id: id == 504),
          ("GG2HLL_PTV_GT250", lambda id: id == 505),
        ])
        self.htxs = collections.OrderedDict()
        if self.category == 'ggH':
          self.htxs.update(htxs_ggH)
        elif self.category == 'qqH':
          self.htxs.update(htxs_qqH)
        elif self.category == 'VH':
          self.htxs.update(htxs_qqH)
          self.htxs.update(htxs_wh)
          self.htxs.update(htxs_zh)
        else:
          assert(False)

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

    self.htxs_binning = [ "" ]
    if self.compHTXS:
      self.htxs_binning.extend(list(self.htxs.keys()))

    for topPtRwgtIdx, topPtRwgtLabel in enumerate(self.topPtRwgtLabels):
      for lheTHXSMWeightIndex in self.lheTHXSMWeightIndices:
        for htxs_bin in self.htxs_binning:
          do_tH = lheTHXSMWeightIndex >= 0
          insert_title = self.topPtRwgtTitles[topPtRwgtIdx]
          insert_title += ("* LHE(tH %d)" % lheTHXSMWeightIndex) if do_tH else ""
          insert_name = topPtRwgtLabel
          insert_name += ("_rwgt%d" % lheTHXSMWeightIndex) if do_tH else ""
          suffix_title = ""

          if htxs_bin:
            insert_name_empty = not bool(insert_name)
            insert_name += "_%s" % htxs_bin
            htxs_bin_name = htxs_bin.replace('pt', 'Higgs pt ').replace('to', '-').replace('Gt', '> ').replace('fwd', 'forward Higgs') \
                            if self.category == 'ttH'  else htxs_bin
            suffix_title += " (%s)" % htxs_bin_name
            if insert_name_empty:
              self.histograms.update([
                ('Count{}'.format(insert_name), {
                  'bins'  : 1,
                  'min'   : 0.,
                  'max'   : 2.,
                  'title' : 'sum(1) {}'.format(suffix_title),
                })
              ])

          self.histograms.update([
            ('CountWeighted{}'.format(insert_name), {
              'bins'  : 3,
              'min'   : -0.5,
              'max'   : 2.5,
              'title' : 'sum(sgn(gen) * PU(central,up,down){}) {}'.format(insert_title, suffix_title),
            }),
            ('CountWeightedL1PrefireNom{}'.format(insert_name), {
              'bins'  : 3,
              'min'   : -0.5,
              'max'   : 2.5,
              'title' : 'sum(sgn(gen) * PU(central,up,down){} * L1Prefire(nom)) {}'.format(insert_title, suffix_title),
            }),
            ('CountWeightedL1Prefire{}'.format(insert_name), {
              'bins'  : 3,
              'min'   : -0.5,
              'max'   : 2.5,
              'title' : 'sum(sgn(gen) * PU(central){} * L1Prefire(nom,up,down)) {}'.format(insert_title, suffix_title),
            }),
            ('CountWeightedLHEWeightPdf{}'.format(insert_name), {
              'bins'  : self.nLHEPdfWeight,
              'min'   : -0.5,
              'max'   : self.nLHEPdfWeight - 0.5,
              'title' : 'sum(sgn(gen) * PU(central){} * LHE(pdf)) {}'.format(insert_title, suffix_title),
            }),
            ('CountWeightedLHEWeightPdfL1PrefireNom{}'.format(insert_name), {
              'bins'  : self.nLHEPdfWeight,
              'min'   : -0.5,
              'max'   : self.nLHEPdfWeight - 0.5,
              'title' : 'sum(sgn(gen) * PU(central){} * LHE(pdf) * L1Prefire(nom)) {}'.format(insert_title, suffix_title),
            }),
            ('CountWeightedLHEWeightScale{}'.format(insert_name), {
              'bins'  : self.nLHEScaleWeight,
              'min'   : -0.5,
              'max'   : self.nLHEScaleWeight - 0.5,
              'title' : 'sum(sgn(gen) * PU(central){} * LHE(scale)) {}'.format(insert_title, suffix_title),
            }),
            ('CountWeightedLHEWeightScaleL1PrefireNom{}'.format(insert_name), {
              'bins'  : self.nLHEScaleWeight,
              'min'   : -0.5,
              'max'   : self.nLHEScaleWeight - 0.5,
              'title' : 'sum(sgn(gen) * PU(central){} * LHE(scale) * L1Prefire(nom)) {}'.format(insert_title, suffix_title),
            }),
            ('CountWeightedLHEEnvelope{}'.format(insert_name), {
              'bins'  : self.nLHEEnvelope,
              'min'   : -0.5,
              'max'   : self.nLHEEnvelope - 0.5,
              'title' : 'sum(sgn(gen) * PU(central){} * LHE(envelope up, down)) {}'.format(insert_title, suffix_title),
            }),
            ('CountWeightedLHEEnvelopeL1PrefireNom{}'.format(insert_name), {
              'bins'  : self.nLHEEnvelope,
              'min'   : -0.5,
              'max'   : self.nLHEEnvelope - 0.5,
              'title' : 'sum(sgn(gen) * PU(central){} * LHE(envelope up, down) * L1Prefire(nom)) {}'.format(insert_title, suffix_title),
            }),
            ('CountWeightedPSWeight{}'.format(insert_name), {
              'bins': self.nPSweight,
              'min': -0.5,
              'max': self.nPSweight - 0.5,
              'title': 'sum(sgn(gen) * PU(central){} * PS(ISR/FSR/both up, ISR/FSR/both down)) {}'.format(insert_title, suffix_title),
            }),
            ('CountWeightedPSWeightL1PrefireNom{}'.format(insert_name), {
              'bins': self.nPSweight,
              'min': -0.5,
              'max': self.nPSweight - 0.5,
              'title': 'sum(sgn(gen) * PU(central){} * PS(ISR/FSR/both up, ISR/FSR/both down) * L1Prefire(nom)) {}'.format(insert_title, suffix_title),
            }),
            # the PS weights may not average to 1 because of incorrect normalization, see
            # https://hypernews.cern.ch/HyperNews/CMS/get/physTools/3709.html
            # https://github.com/cms-nanoAOD/cmssw/issues/381
            ('CountWeightedPSWeightOriginalXWGTUP{}'.format(insert_name), {
              'bins': self.nPSweight,
              'min': -0.5,
              'max': self.nPSweight - 0.5,
              'title': 'sum(sgn(gen) * PU(central){} * PS(ISR/FSR/both up, ISR/FSR/both down) * LHE(nom)) {}'.format(insert_title, suffix_title),
            }),
            ('CountWeightedPSWeightOriginalXWGTUPL1PrefireNom{}'.format(insert_name), {
              'bins': self.nPSweight,
              'min': -0.5,
              'max': self.nPSweight - 0.5,
              'title': 'sum(sgn(gen) * PU(central){} * PS(ISR/FSR/both up, ISR/FSR/both down) * L1Prefire(nom) * LHE(nom)) {}'.format(
                insert_title, suffix_title),
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
      if histogramName == 'Count' or histogramName.startswith('Count_'):
        histogramParams['histogram'] = ROOT.TH1I(
          histogramName, histogramParams['title'],
          histogramParams['bins'], histogramParams['min'], histogramParams['max']
        )
      else:
        histogramParams['histogram'] = ROOT.TH1F(
          histogramName, histogramParams['title'],
          histogramParams['bins'], histogramParams['min'], histogramParams['max']
        )

  def clip(self, value, min_val = -10., max_val = 10.):
    return min(max(value, min_val), max_val)

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

  def getLHEEnvelope(self, LHEScaleWeight):
    if len(LHEScaleWeight) != self.nLHEEnvelope_required:
      return (1., 1.)
    LHEEnvelopeValues = [ self.clip(LHEScaleWeight[lhe_idx]) for lhe_idx in self.LHEEnvelopeIdxs ]
    return [ max(LHEEnvelopeValues), min(LHEEnvelopeValues) ]

  def beginJob(self):
    pass

  def endJob(self):
    pass

  def beginFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
    self.out = wrappedOutputTree
    if self.compTopRwgt:
      for choice in self.topPtRwgtChoices:
        self.out.branch("{}_{}".format(self.topRwgtBranchName, choice), "F")
    inputTreeBranchNames = [ branch.GetName() for branch in inputTree.GetListOfBranches() ]
    if self.LHEScaleWeightName in inputTreeBranchNames:
      self.compLHEEnvelope = True
    if self.compLHEEnvelope:
      print("Computing LHE envelope weights")
      self.out.branch(self.LHEEnvelopeNameUp,   "F")
      self.out.branch(self.LHEEnvelopeNameDown, "F")
    else:
      print("NOT computing LHE envelope weights")

  def endFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
    outputFile.cd()

    for histogramName in self.histograms:
      if 'histogram' in self.histograms[histogramName] and \
         self.histograms[histogramName]['histogram'] != None:
        self.histograms[histogramName]['histogram'].Write()

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

    htxs_val = -1
    htxs_selected = False
    for htxs_bin in self.htxs_binning:

      if htxs_bin:
        assert(self.compHTXS)
        assert(htxs_bin in self.htxs)
        if self.category == 'ttH':
          if not hasattr(event, self.htxsPtBranchName):
            raise RuntimeError("No such branch: %s" % self.htxsPtBranchName)
          if not hasattr(event, self.htxsEtaBranchName):
            raise RuntimeError("No such branch: %s" % self.htxsEtaBranchName)
          htxs_pt = getattr(event, self.htxsPtBranchName)
          htxs_eta = getattr(event, self.htxsEtaBranchName)
          if not self.htxs[htxs_bin](htxs_pt, htxs_eta):
            continue
        else:
          if htxs_val < 0:
            if not hasattr(event, self.htxsBranchName):
              raise RuntimeError("No such branch: %s" % self.htxsBranchName)
            htxs_val = getattr(event, self.htxsBranchName)
          if not self.htxs[htxs_bin](htxs_val):
            continue
        htxs_selected = True

        if 'histogram' in self.histograms['Count_{}'.format(htxs_bin)]:
          if not self.isInitialized(['Count_{}'.format(htxs_bin)]):
            self.initHistograms(['Count_{}'.format(htxs_bin)])
          self.histograms['Count_{}'.format(htxs_bin)]['histogram'].Fill(1, 1)

      if hasattr(event, self.genWeightName):
        genWeight = getattr(event, self.genWeightName)
        genWeight_sign = np.sign(genWeight)

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

              if htxs_bin:
                insert_name = "%s_%s" % (insert_name_common, htxs_bin)
              else:
                insert_name = insert_name_common

              if 'histogram' in self.histograms['CountWeighted{}'.format(insert_name)]:
                if not self.isInitialized(['CountWeighted{}'.format(insert_name)]):
                  self.initHistograms(['CountWeighted{}'.format(insert_name)])
                self.histograms['CountWeighted{}'.format(insert_name)]['histogram'].Fill(0., genWeight_sign * puWeight * lheTHXWeight * topSF)
                self.histograms['CountWeighted{}'.format(insert_name)]['histogram'].Fill(1., genWeight_sign * puWeight_up * lheTHXWeight * topSF)
                self.histograms['CountWeighted{}'.format(insert_name)]['histogram'].Fill(2., genWeight_sign * puWeight_down * lheTHXWeight * topSF)

              if has_l1Prefire:
                if 'histogram' in self.histograms['CountWeightedL1PrefireNom{}'.format(insert_name)]:
                  if not self.isInitialized(['CountWeightedL1PrefireNom{}'.format(insert_name)]):
                    self.initHistograms(['CountWeightedL1PrefireNom{}'.format(insert_name)])
                  self.histograms['CountWeightedL1PrefireNom{}'.format(insert_name)]['histogram'].Fill(0., genWeight_sign * puWeight * lheTHXWeight * l1_nom * topSF)
                  self.histograms['CountWeightedL1PrefireNom{}'.format(insert_name)]['histogram'].Fill(1., genWeight_sign * puWeight_up * lheTHXWeight * l1_nom * topSF)
                  self.histograms['CountWeightedL1PrefireNom{}'.format(insert_name)]['histogram'].Fill(2., genWeight_sign * puWeight_down * lheTHXWeight * l1_nom * topSF)

                if 'histogram' in self.histograms['CountWeightedL1Prefire{}'.format(insert_name)]:
                  if not self.isInitialized(['CountWeightedL1Prefire{}'.format(insert_name)]):
                    self.initHistograms(['CountWeightedL1Prefire{}'.format(insert_name)])
                  self.histograms['CountWeightedL1Prefire{}'.format(insert_name)]['histogram'].Fill(0., genWeight_sign * puWeight * lheTHXWeight * l1_nom * topSF)
                  self.histograms['CountWeightedL1Prefire{}'.format(insert_name)]['histogram'].Fill(1., genWeight_sign * puWeight * lheTHXWeight * l1_up * topSF)
                  self.histograms['CountWeightedL1Prefire{}'.format(insert_name)]['histogram'].Fill(2., genWeight_sign * puWeight * lheTHXWeight * l1_down * topSF)

              if hasattr(event, self.LHEPdfWeightName):
                LHEPdfWeight = getattr(event, self.LHEPdfWeightName)

                if len(LHEPdfWeight) != self.nLHEPdfWeight:
                  print(
                    "WARNING: The length of '%s' array (= %i) does not match to the expected length of %i" % \
                    (self.LHEPdfWeightName, len(LHEPdfWeight), self.nLHEPdfWeight)
                  )
                  self.nLHEPdfWeight = len(LHEPdfWeight)

                if 'histogram' in self.histograms['CountWeightedLHEWeightPdf{}'.format(insert_name)]:
                  if not self.isInitialized(['CountWeightedLHEWeightPdf{}'.format(insert_name)]):
                    self.initHistograms(['CountWeightedLHEWeightPdf{}'.format(insert_name)], self.nLHEPdfWeight)
                  for lhe_pdf_idx in range(self.nLHEPdfWeight):
                    self.histograms['CountWeightedLHEWeightPdf{}'.format(insert_name)]['histogram'].Fill(
                      float(lhe_pdf_idx), genWeight_sign * puWeight * lheTHXWeight * self.clip(LHEPdfWeight[lhe_pdf_idx]) * topSF
                    )

                if has_l1Prefire:
                  if 'histogram' in self.histograms['CountWeightedLHEWeightPdfL1PrefireNom{}'.format(insert_name)]:
                    if not self.isInitialized(['CountWeightedLHEWeightPdfL1PrefireNom{}'.format(insert_name)]):
                      self.initHistograms(['CountWeightedLHEWeightPdfL1PrefireNom{}'.format(insert_name)], self.nLHEPdfWeight)
                    for lhe_pdf_idx in range(self.nLHEPdfWeight):
                      self.histograms['CountWeightedLHEWeightPdfL1PrefireNom{}'.format(insert_name)]['histogram'].Fill(
                        float(lhe_pdf_idx), genWeight_sign * puWeight * lheTHXWeight * l1_nom * self.clip(LHEPdfWeight[lhe_pdf_idx]) * topSF
                      )

              else:
                if not self.isPrinted[self.LHEPdfWeightName]:
                  self.isPrinted[self.LHEPdfWeightName] = True
                  print('Missing branch: %s' % self.LHEPdfWeightName)

              if hasattr(event, self.LHEScaleWeightName):
                assert(self.compLHEEnvelope)
                LHEScaleWeight = getattr(event, self.LHEScaleWeightName)
                LHEEnvelopeValues = self.getLHEEnvelope(LHEScaleWeight)

                if len(LHEScaleWeight) != self.nLHEScaleWeight:
                  print(
                    "WARNING: The length of '%s' array (= %i) does not match to the expected length of %i" % \
                    (self.LHEScaleWeightName, len(LHEScaleWeight), self.nLHEScaleWeight)
                  )
                  self.nLHEScaleWeight = len(LHEScaleWeight)

                if 'histogram' in self.histograms['CountWeightedLHEWeightScale{}'.format(insert_name)]:
                  if not self.isInitialized(['CountWeightedLHEWeightScale{}'.format(insert_name)]):
                    self.initHistograms(['CountWeightedLHEWeightScale{}'.format(insert_name)], self.nLHEScaleWeight)
                  for lhe_scale_idx in range(self.nLHEScaleWeight):
                    self.histograms['CountWeightedLHEWeightScale{}'.format(insert_name)]['histogram'].Fill(
                      float(lhe_scale_idx), genWeight_sign * puWeight * lheTHXWeight * self.clip(LHEScaleWeight[lhe_scale_idx]) * topSF
                    )

                if has_l1Prefire:
                  if 'histogram' in self.histograms['CountWeightedLHEWeightScaleL1PrefireNom{}'.format(insert_name)]:
                    if not self.isInitialized(['CountWeightedLHEWeightScaleL1PrefireNom{}'.format(insert_name)]):
                      self.initHistograms(['CountWeightedLHEWeightScaleL1PrefireNom{}'.format(insert_name)], self.nLHEScaleWeight)
                    for lhe_scale_idx in range(self.nLHEScaleWeight):
                      self.histograms['CountWeightedLHEWeightScaleL1PrefireNom{}'.format(insert_name)]['histogram'].Fill(
                        float(lhe_scale_idx), genWeight_sign * puWeight * lheTHXWeight * l1_nom * self.clip(LHEScaleWeight[lhe_scale_idx]) * topSF
                      )

                if 'histogram' in self.histograms['CountWeightedLHEEnvelope{}'.format(insert_name)]:
                  if not self.isInitialized(['CountWeightedLHEEnvelope{}'.format(insert_name)]):
                    self.initHistograms(['CountWeightedLHEEnvelope{}'.format(insert_name)], self.nLHEEnvelope)
                  for lhe_scale_idx, lhe_scale_value in enumerate(LHEEnvelopeValues):
                    self.histograms['CountWeightedLHEEnvelope{}'.format(insert_name)]['histogram'].Fill(
                      float(lhe_scale_idx), genWeight_sign * puWeight * lheTHXWeight * lhe_scale_value * topSF
                    )
                if has_l1Prefire:
                  if 'histogram' in self.histograms['CountWeightedLHEEnvelopeL1PrefireNom{}'.format(insert_name)]:
                    if not self.isInitialized(['CountWeightedLHEEnvelopeL1PrefireNom{}'.format(insert_name)]):
                      self.initHistograms(['CountWeightedLHEEnvelopeL1PrefireNom{}'.format(insert_name)], self.nLHEEnvelope)
                    for lhe_scale_idx, lhe_scale_value in enumerate(LHEEnvelopeValues):
                      self.histograms['CountWeightedLHEEnvelopeL1PrefireNom{}'.format(insert_name)]['histogram'].Fill(
                        float(lhe_scale_idx), genWeight_sign * puWeight * lheTHXWeight * l1_nom * lhe_scale_value * topSF
                      )

              else:
                if not self.isPrinted[self.LHEScaleWeightName]:
                  self.isPrinted[self.LHEScaleWeightName] = True
                  print('Missing branch: %s' % self.LHEScaleWeightName)

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

                if 'histogram' in self.histograms['CountWeightedPSWeight{}'.format(insert_name)]:
                  if not self.isInitialized(['CountWeightedPSWeight{}'.format(insert_name)]):
                    self.initHistograms(['CountWeightedPSWeight{}'.format(insert_name)], self.nPSweight)
                  for psweight_idx, psweight in enumerate(PSweights_ext):
                    self.histograms['CountWeightedPSWeight{}'.format(insert_name)]['histogram'].Fill(
                      float(psweight_idx), genWeight_sign * puWeight * lheTHXWeight * self.clip(psweight) * topSF
                    )
                if has_l1Prefire:
                  if 'histogram' in self.histograms['CountWeightedPSWeightL1PrefireNom{}'.format(insert_name)]:
                    if not self.isInitialized(['CountWeightedPSWeightL1PrefireNom{}'.format(insert_name)]):
                      self.initHistograms(['CountWeightedPSWeightL1PrefireNom{}'.format(insert_name)], self.nPSweight)
                    for psweight_idx, psweight in enumerate(PSweights_ext):
                      self.histograms['CountWeightedPSWeightL1PrefireNom{}'.format(insert_name)]['histogram'].Fill(
                        float(psweight_idx), genWeight_sign * puWeight * lheTHXWeight * l1_nom * self.clip(psweight) * topSF
                      )

                if hasattr(event, self.nominalLHEweightName):
                  lhe_nom = getattr(event, self.nominalLHEweightName)
                  if 'histogram' in self.histograms['CountWeightedPSWeightOriginalXWGTUP{}'.format(insert_name)]:
                    if not self.isInitialized(['CountWeightedPSWeightOriginalXWGTUP{}'.format(insert_name)]):
                      self.initHistograms(['CountWeightedPSWeightOriginalXWGTUP{}'.format(insert_name)], self.nPSweight)
                    for psweight_idx, psweight in enumerate(PSweights_ext):
                      self.histograms['CountWeightedPSWeightOriginalXWGTUP{}'.format(insert_name)]['histogram'].Fill(
                        float(psweight_idx), genWeight_sign * puWeight * lheTHXWeight * self.clip(psweight * lhe_nom) * topSF
                      )
                  if has_l1Prefire:
                    if 'histogram' in self.histograms['CountWeightedPSWeightOriginalXWGTUPL1PrefireNom{}'.format(insert_name)]:
                      if not self.isInitialized(['CountWeightedPSWeightOriginalXWGTUPL1PrefireNom{}'.format(insert_name)]):
                        self.initHistograms(['CountWeightedPSWeightOriginalXWGTUPL1PrefireNom{}'.format(insert_name)], self.nPSweight)
                      for psweight_idx, psweight in enumerate(PSweights_ext):
                        self.histograms['CountWeightedPSWeightOriginalXWGTUPL1PrefireNom{}'.format(insert_name)]['histogram'].Fill(
                          float(psweight_idx), genWeight_sign * puWeight * lheTHXWeight * l1_nom * self.clip(psweight * lhe_nom) * topSF
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

    if self.compHTXS and not htxs_selected:
      raise RuntimeError(
        "Event %d:%d:%d has not been selected in any of the HTXS bins because its ID is %d" % \
        (getattr(event, 'run'), getattr(event, 'luminosityBlock'), getattr(event, 'event'), htxs_val)
      )

    if self.compTopRwgt:
      for topPtRwgtIdx, choice in enumerate(self.topPtRwgtChoices):
        self.out.fillBranch("{}_{}".format(self.topRwgtBranchName, choice), topRwgt[topPtRwgtIdx])
    if self.compLHEEnvelope:
      self.out.fillBranch(self.LHEEnvelopeNameUp, LHEEnvelopeValues[0])
      self.out.fillBranch(self.LHEEnvelopeNameDown, LHEEnvelopeValues[1])

    return True

# provide this variable as the 2nd argument to the import option for the nano_postproc.py script
countHistogramAll            = lambda:          countHistogramProducer(compTopRwgt = False, compHTXS = False)
countHistogramAllCompTopRwgt = lambda:          countHistogramProducer(compTopRwgt = True,  compHTXS = False)
countHistogramAllCompHTXS    = lambda category: countHistogramProducer(compTopRwgt = False, compHTXS = True, category = category)
