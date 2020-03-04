import ROOT
import numpy as np
import collections

ROOT.PyConfig.IgnoreCommandLineOptions = True

from PhysicsTools.NanoAODTools.postprocessing.framework.eventloop import Module
from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import Collection

from tthAnalysis.NanoAODTools.tHweights_cfi import thIdxs

class countHistogramProducer(Module):

  def __init__(self, compTopRwgt = False):
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

    self.ISR_down_idx = 0
    self.FSR_down_idx = 1
    self.ISR_up_idx = 2
    self.FSR_up_idx = 3

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
      # ('CountPosWeight', {
      #   'bins'  : 1,
      #   'min'   : 0.,
      #   'max'   : 2.,
      #   'title' : 'sum(gen > 0)',
      # }),
      # ('CountNegWeight', {
      #   'bins'  : 1,
      #   'min'   : 0.,
      #   'max'   : 2.,
      #   'title' : 'sum(gen < 0)',
      # }),
    ])
    self.lheTHXSMWeightIndices = thIdxs
    self.topPtRwgtLabels = [ "" ]
    self.topPtRwgtTitles = [ "" ]
    if self.compTopRwgt:
      self.topPtRwgtLabels.extend([ "TopPtRwgtSF", "TopPtRwgtSFSquared" ])
      self.topPtRwgtTitles.extend([ "* top-pT", "* top-pT^2" ])

    for topPtRwgtIdx, topPtRwgtLabel in enumerate(self.topPtRwgtLabels):
      for lheTHXSMWeightIndex in self.lheTHXSMWeightIndices:
        do_tH = lheTHXSMWeightIndex >= 0
        insert_title = self.topPtRwgtTitles[topPtRwgtIdx]
        insert_title += ("* LHE(tH %d)" % lheTHXSMWeightIndex) if do_tH else ""
        insert_name = topPtRwgtLabel
        insert_name += ("_rwgt%d" % lheTHXSMWeightIndex) if do_tH else ""
        self.histograms.update([
          ('CountWeighted{}'.format(insert_name), {
            'bins'  : 3,
            'min'   : -0.5,
            'max'   : 2.5,
            'title' : 'sum(sgn(gen) * PU(central,up,down){})'.format(insert_title),
          }),
          ('CountWeightedL1PrefireNom{}'.format(insert_name), {
            'bins'  : 3,
            'min'   : -0.5,
            'max'   : 2.5,
            'title' : 'sum(sgn(gen) * PU(central,up,down){} * L1Prefire(nom))'.format(insert_title),
          }),
          ('CountWeightedL1Prefire{}'.format(insert_name), {
            'bins'  : 3,
            'min'   : -0.5,
            'max'   : 2.5,
            'title' : 'sum(sgn(gen) * PU(central){} * L1Prefire(nom,up,down))'.format(insert_title),
          }),
          # ('CountFullWeighted{}'.format(insert_name), {
          #   'bins'  : 3,
          #   'min'   : -0.5,
          #   'max'   : 2.5,
          #   'title' : 'sum(gen * PU(central,up,down){})'.format(insert_title),
          # }),
          # ('CountFullWeightedL1PrefireNom{}'.format(insert_name), {
          #   'bins'  : 3,
          #   'min'   : -0.5,
          #   'max'   : 2.5,
          #   'title' : 'sum(gen * PU(central,up,down){} * L1Prefire(nom))'.format(insert_title),
          # }),
          # ('CountFullWeightedL1Prefire{}'.format(insert_name), {
          #   'bins'  : 3,
          #   'min'   : -0.5,
          #   'max'   : 2.5,
          #   'title' : 'sum(gen * PU(central){} * L1Prefire(nom,up,down))'.format(insert_title),
          # }),
          # ('CountWeightedNoPU{}'.format(insert_name), {
          #   'bins'  : 1,
          #   'min'   : 0.,
          #   'max'   : 2.,
          #   'title' : 'sum(sgn(gen){})'.format(insert_title),
          # }),
          # ('CountWeightedNoPUL1PrefireNom{}'.format(insert_name), {
          #   'bins'  : 1,
          #   'min'   : 0.,
          #   'max'   : 2.,
          #   'title' : 'sum(sgn(gen){} * L1Prefire(nom))'.format(insert_title),
          # }),
          # ('CountFullWeightedNoPU{}'.format(insert_name), {
          #   'bins'  : 1,
          #   'min'   : 0.,
          #   'max'   : 2.,
          #   'title' : 'sum(gen{})'.format(insert_title),
          # }),
          # ('CountFullWeightedNoPUL1PrefireNom{}'.format(insert_name), {
          #   'bins'  : 1,
          #   'min'   : 0.,
          #   'max'   : 2.,
          #   'title' : 'sum(gen{} * L1Prefire(nom))'.format(insert_title),
          # }),
          ('CountWeightedLHEWeightPdf{}'.format(insert_name), {
            'bins'  : self.nLHEPdfWeight,
            'min'   : -0.5,
            'max'   : self.nLHEPdfWeight - 0.5,
            'title' : 'sum(sgn(gen) * PU(central){} * LHE(pdf))'.format(insert_title),
          }),
          ('CountWeightedLHEWeightPdfL1PrefireNom{}'.format(insert_name), {
            'bins'  : self.nLHEPdfWeight,
            'min'   : -0.5,
            'max'   : self.nLHEPdfWeight - 0.5,
            'title' : 'sum(sgn(gen) * PU(central){} * LHE(pdf) * L1Prefire(nom))'.format(insert_title),
          }),
          # ('CountWeightedLHEWeightPdfNoPU{}'.format(insert_name), {
          #   'bins'  : self.nLHEPdfWeight,
          #   'min'   : -0.5,
          #   'max'   : self.nLHEPdfWeight - 0.5,
          #   'title' : 'sum(sgn(gen){} * LHE(pdf))'.format(insert_title),
          # }),
          # ('CountWeightedLHEWeightPdfNoPUL1PrefireNom{}'.format(insert_name), {
          #   'bins'  : self.nLHEPdfWeight,
          #   'min'   : -0.5,
          #   'max'   : self.nLHEPdfWeight - 0.5,
          #   'title' : 'sum(sgn(gen){} * LHE(pdf) * L1Prefire(nom))'.format(insert_title),
          # }),
          # ('CountFullWeightedLHEWeightPdf{}'.format(insert_name), {
          #   'bins'  : self.nLHEPdfWeight,
          #   'min'   : -0.5,
          #   'max'   : self.nLHEPdfWeight - 0.5,
          #   'title' : 'sum(gen * PU(central){} * LHE(pdf))'.format(insert_title),
          # }),
          # ('CountFullWeightedLHEWeightPdfL1PrefireNom{}'.format(insert_name), {
          #   'bins'  : self.nLHEPdfWeight,
          #   'min'   : -0.5,
          #   'max'   : self.nLHEPdfWeight - 0.5,
          #   'title' : 'sum(gen * PU(central){} * LHE(pdf) * L1Prefire(nom))'.format(insert_title),
          # }),
          # ('CountFullWeightedLHEWeightPdfNoPU{}'.format(insert_name), {
          #   'bins'  : self.nLHEPdfWeight,
          #   'min'   : -0.5,
          #   'max'   : self.nLHEPdfWeight - 0.5,
          #   'title' : 'sum(gen{} * LHE(pdf))'.format(insert_title),
          # }),
          # ('CountFullWeightedLHEWeightPdfNoPUL1PrefireNom{}'.format(insert_name), {
          #   'bins'  : self.nLHEPdfWeight,
          #   'min'   : -0.5,
          #   'max'   : self.nLHEPdfWeight - 0.5,
          #   'title' : 'sum(gen{} * LHE(pdf) * L1Prefire(nom))'.format(insert_title),
          # }),
          ('CountWeightedLHEWeightScale{}'.format(insert_name), {
            'bins'  : self.nLHEScaleWeight,
            'min'   : -0.5,
            'max'   : self.nLHEScaleWeight - 0.5,
            'title' : 'sum(sgn(gen) * PU(central){} * LHE(scale))'.format(insert_title),
          }),
          ('CountWeightedLHEWeightScaleL1PrefireNom{}'.format(insert_name), {
            'bins'  : self.nLHEScaleWeight,
            'min'   : -0.5,
            'max'   : self.nLHEScaleWeight - 0.5,
            'title' : 'sum(sgn(gen) * PU(central){} * LHE(scale) * L1Prefire(nom))'.format(insert_title),
          }),
          # ('CountWeightedLHEWeightScaleNoPU{}'.format(insert_name), {
          #   'bins'  : self.nLHEScaleWeight,
          #   'min'   : -0.5,
          #   'max'   : self.nLHEScaleWeight - 0.5,
          #   'title' : 'sum(sgn(gen){} * LHE(scale))'.format(insert_title),
          # }),
          # ('CountWeightedLHEWeightScaleNoPUL1PrefireNom{}'.format(insert_name), {
          #   'bins': self.nLHEScaleWeight,
          #   'min': -0.5,
          #   'max': self.nLHEScaleWeight - 0.5,
          #   'title': 'sum(sgn(gen){} * LHE(scale) * L1Prefire(nom))'.format(insert_title),
          # }),
          # ('CountFullWeightedLHEWeightScale{}'.format(insert_name), {
          #   'bins'  : self.nLHEScaleWeight,
          #   'min'   : -0.5,
          #   'max'   : self.nLHEScaleWeight - 0.5,
          #   'title' : 'sum(gen * PU(central){} * LHE(scale))'.format(insert_title),
          # }),
          # ('CountFullWeightedLHEWeightScaleL1PrefireNom{}'.format(insert_name), {
          #   'bins'  : self.nLHEScaleWeight,
          #   'min'   : -0.5,
          #   'max'   : self.nLHEScaleWeight - 0.5,
          #   'title' : 'sum(gen * PU(central){} * LHE(scale) * L1Prefire(nom))'.format(insert_title),
          # }),
          # ('CountFullWeightedLHEWeightScaleNoPU{}'.format(insert_name), {
          #   'bins'  : self.nLHEScaleWeight,
          #   'min'   : -0.5,
          #   'max'   : self.nLHEScaleWeight - 0.5,
          #   'title' : 'sum(gen{} * LHE(scale))'.format(insert_title),
          # }),
          # ('CountFullWeightedLHEWeightScaleNoPUL1PrefireNom{}'.format(insert_name), {
          #   'bins'  : self.nLHEScaleWeight,
          #   'min'   : -0.5,
          #   'max'   : self.nLHEScaleWeight - 0.5,
          #   'title' : 'sum(gen{} * LHE(scale) * L1Prefire(nom))'.format(insert_title),
          # }),
          ('CountWeightedLHEEnvelope{}'.format(insert_name), {
            'bins'  : self.nLHEEnvelope,
            'min'   : -0.5,
            'max'   : self.nLHEEnvelope - 0.5,
            'title' : 'sum(sgn(gen) * PU(central){} * LHE(envelope up, down))'.format(insert_title),
          }),
          ('CountWeightedLHEEnvelopeL1PrefireNom{}'.format(insert_name), {
            'bins'  : self.nLHEEnvelope,
            'min'   : -0.5,
            'max'   : self.nLHEEnvelope - 0.5,
            'title' : 'sum(sgn(gen) * PU(central){} * LHE(envelope up, down) * L1Prefire(nom))'.format(insert_title),
          }),
          ('CountWeightedPSWeight{}'.format(insert_name), {
            'bins': self.nPSweight,
            'min': -0.5,
            'max': self.nPSweight - 0.5,
            'title': 'sum(sgn(gen) * PU(central){} * PS(ISR/FSR/both up, ISR/FSR/both down))'.format(insert_title),
          }),
          ('CountWeightedPSWeightL1PrefireNom{}'.format(insert_name), {
            'bins': self.nPSweight,
            'min': -0.5,
            'max': self.nPSweight - 0.5,
            'title': 'sum(sgn(gen) * PU(central){} * PS(ISR/FSR/both up, ISR/FSR/both down) * L1Prefire(nom))'.format(insert_title),
          }),
          # the PS weights may not average to 1 because of incorrect normalization, see
          # https://hypernews.cern.ch/HyperNews/CMS/get/physTools/3709.html
          # https://github.com/cms-nanoAOD/cmssw/issues/381
          ('CountWeightedPSWeightOriginalXWGTUP{}'.format(insert_name), {
            'bins': self.nPSweight,
            'min': -0.5,
            'max': self.nPSweight - 0.5,
            'title': 'sum(sgn(gen) * PU(central){} * PS(ISR/FSR/both up, ISR/FSR/both down) * LHE(nom))'.format(insert_title),
          }),
          ('CountWeightedPSWeightOriginalXWGTUPL1PrefireNom{}'.format(insert_name), {
            'bins': self.nPSweight,
            'min': -0.5,
            'max': self.nPSweight - 0.5,
            'title': 'sum(sgn(gen) * PU(central){} * PS(ISR/FSR/both up, ISR/FSR/both down) * L1Prefire(nom) * LHE(nom))'.format(
              insert_title),
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

  def getTopRwgtSF(self, genTops):
    # https://twiki.cern.ch/twiki/bin/view/CMS/TopPtReweighting#Use_case_3_ttbar_MC_is_used_to_m
    assert(genTops)
    assert(len(genTops) == 2)
    assert(genTops[0].pdgId * genTops[1].pdgId < 0)
    genTop_pos_idx = 0 if genTops[0].pdgId > 0 else 1
    genTop_neg_idx = 1 - genTop_pos_idx
    genTop_pos_pt = genTops[genTop_pos_idx].pt
    genTop_neg_pt = genTops[genTop_neg_idx].pt
    genTop_pt_avg = (genTop_pos_pt + genTop_neg_pt) / 2.
    a =  0.0615
    b = -0.0005
    return np.exp(a + b * genTop_pt_avg)

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
      self.out.branch(self.topRwgtBranchName, "F")
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

    topRwgt = 1.
    LHEEnvelopeValues = [ 1., 1. ]
    if self.compTopRwgt:
      genTops = Collection(event, self.genTopCollectionName)
      topRwgt = self.getTopRwgtSF(genTops)

    if hasattr(event, self.genWeightName):
      genWeight = getattr(event, self.genWeightName)
      genWeight_sign = np.sign(genWeight)

      # if 'histogram' in self.histograms['CountPosWeight']:
      #   if not self.isInitialized(['CountPosWeight']):
      #     self.initHistograms(['CountPosWeight'])
      #   self.histograms['CountPosWeight']['histogram'].Fill(1, 1 if genWeight_sign > 0 else 0)
      # if 'histogram' in self.histograms['CountNegWeight']:
      #   if not self.isInitialized(['CountNegWeight']):
      #     self.initHistograms(['CountNegWeight'])
      #   self.histograms['CountNegWeight']['histogram'].Fill(1, 1 if genWeight_sign < 0 else 0)

      if hasattr(event, self.puWeightName):
        assert(hasattr(event, self.puWeightName_up))
        assert(hasattr(event, self.puWeightName_down))

        puWeight = getattr(event, self.puWeightName)
        puWeight_up = getattr(event, self.puWeightName_up)
        puWeight_down = getattr(event, self.puWeightName_down)

        for topPtRwgtIdx, topPtRwgtLabel in enumerate(self.topPtRwgtLabels):
          topSF = topRwgt**topPtRwgtIdx

          for lheTHXSMWeightIndex in self.lheTHXSMWeightIndices:
            do_tH = lheTHXSMWeightIndex >= 0
            insert_name = topPtRwgtLabel
            insert_name += ("_rwgt%d" % lheTHXSMWeightIndex) if do_tH else ""

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

            if 'histogram' in self.histograms['CountWeighted{}'.format(insert_name)]:
              if not self.isInitialized(['CountWeighted{}'.format(insert_name)]):
                self.initHistograms(['CountWeighted{}'.format(insert_name)])
              self.histograms['CountWeighted{}'.format(insert_name)]['histogram'].Fill(0., genWeight_sign * puWeight * lheTHXWeight * topSF)
              self.histograms['CountWeighted{}'.format(insert_name)]['histogram'].Fill(1., genWeight_sign * puWeight_up * lheTHXWeight * topSF)
              self.histograms['CountWeighted{}'.format(insert_name)]['histogram'].Fill(2., genWeight_sign * puWeight_down * lheTHXWeight * topSF)

            # if 'histogram' in self.histograms['CountFullWeighted{}'.format(insert_name)]:
            #   if not self.isInitialized(['CountFullWeighted{}'.format(insert_name)]):
            #     self.initHistograms(['CountFullWeighted{}'.format(insert_name)])
            #   self.histograms['CountFullWeighted{}'.format(insert_name)]['histogram'].Fill(0., genWeight * puWeight * lheTHXWeight * topSF)
            #   self.histograms['CountFullWeighted{}'.format(insert_name)]['histogram'].Fill(1., genWeight * puWeight_up * lheTHXWeight * topSF)
            #   self.histograms['CountFullWeighted{}'.format(insert_name)]['histogram'].Fill(2., genWeight * puWeight_down * lheTHXWeight * topSF)

            # if 'histogram' in self.histograms['CountWeightedNoPU{}'.format(insert_name)]:
            #   if not self.isInitialized(['CountWeightedNoPU{}'.format(insert_name)]):
            #     self.initHistograms(['CountWeightedNoPU{}'.format(insert_name)])
            #   self.histograms['CountWeightedNoPU{}'.format(insert_name)]['histogram'].Fill(0., genWeight_sign * lheTHXWeight * topSF)

            # if 'histogram' in self.histograms['CountFullWeightedNoPU{}'.format(insert_name)]:
            #   if not self.isInitialized(['CountFullWeightedNoPU{}'.format(insert_name)]):
            #     self.initHistograms(['CountFullWeightedNoPU{}'.format(insert_name)])
            #   self.histograms['CountFullWeightedNoPU{}'.format(insert_name)]['histogram'].Fill(0., genWeight * lheTHXWeight * topSF)

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

              # if 'histogram' in self.histograms['CountFullWeightedL1PrefireNom{}'.format(insert_name)]:
              #   if not self.isInitialized(['CountFullWeightedL1PrefireNom{}'.format(insert_name)]):
              #     self.initHistograms(['CountFullWeightedL1PrefireNom{}'.format(insert_name)])
              #   self.histograms['CountFullWeightedL1PrefireNom{}'.format(insert_name)]['histogram'].Fill(0., genWeight * puWeight * lheTHXWeight * l1_nom * topSF)
              #   self.histograms['CountFullWeightedL1PrefireNom{}'.format(insert_name)]['histogram'].Fill(1., genWeight * puWeight_up * lheTHXWeight * l1_nom * topSF)
              #   self.histograms['CountFullWeightedL1PrefireNom{}'.format(insert_name)]['histogram'].Fill(2., genWeight * puWeight_down * lheTHXWeight * l1_nom * topSF)
              #
              # if 'histogram' in self.histograms['CountFullWeightedL1Prefire{}'.format(insert_name)]:
              #   if not self.isInitialized(['CountFullWeightedL1Prefire{}'.format(insert_name)]):
              #     self.initHistograms(['CountFullWeightedL1Prefire{}'.format(insert_name)])
              #   self.histograms['CountFullWeightedL1Prefire{}'.format(insert_name)]['histogram'].Fill(0., genWeight * puWeight * lheTHXWeight * l1_nom * topSF)
              #   self.histograms['CountFullWeightedL1Prefire{}'.format(insert_name)]['histogram'].Fill(1., genWeight * puWeight * lheTHXWeight * l1_up * topSF)
              #   self.histograms['CountFullWeightedL1Prefire{}'.format(insert_name)]['histogram'].Fill(2., genWeight * puWeight * lheTHXWeight * l1_down * topSF)

              # if 'histogram' in self.histograms['CountWeightedNoPUL1PrefireNom{}'.format(insert_name)]:
              #   if not self.isInitialized(['CountWeightedNoPUL1PrefireNom{}'.format(insert_name)]):
              #     self.initHistograms(['CountWeightedNoPUL1PrefireNom{}'.format(insert_name)])
              #   self.histograms['CountWeightedNoPUL1PrefireNom{}'.format(insert_name)]['histogram'].Fill(0., genWeight_sign * lheTHXWeight * l1_nom * topSF)

              # if 'histogram' in self.histograms['CountFullWeightedNoPUL1PrefireNom{}'.format(insert_name)]:
              #   if not self.isInitialized(['CountFullWeightedNoPUL1PrefireNom{}'.format(insert_name)]):
              #     self.initHistograms(['CountFullWeightedNoPUL1PrefireNom{}'.format(insert_name)])
              #   self.histograms['CountFullWeightedNoPUL1PrefireNom{}'.format(insert_name)]['histogram'].Fill(0., genWeight * lheTHXWeight * l1_nom * topSF)

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
              # if 'histogram' in self.histograms['CountFullWeightedLHEWeightPdf{}'.format(insert_name)]:
              #   if not self.isInitialized(['CountFullWeightedLHEWeightPdf{}'.format(insert_name)]):
              #     self.initHistograms(['CountFullWeightedLHEWeightPdf{}'.format(insert_name)], self.nLHEPdfWeight)
              #   for lhe_pdf_idx in range(self.nLHEPdfWeight):
              #     self.histograms['CountFullWeightedLHEWeightPdf{}'.format(insert_name)]['histogram'].Fill(
              #       float(lhe_pdf_idx), genWeight * puWeight * lheTHXWeight * self.clip(LHEPdfWeight[lhe_pdf_idx]) * topSF
              #     )

              # if 'histogram' in self.histograms['CountWeightedLHEWeightPdfNoPU{}'.format(insert_name)]:
              #   if not self.isInitialized(['CountWeightedLHEWeightPdfNoPU{}'.format(insert_name)]):
              #     self.initHistograms(['CountWeightedLHEWeightPdfNoPU{}'.format(insert_name)], self.nLHEPdfWeight)
              #   for lhe_pdf_idx in range(self.nLHEPdfWeight):
              #     self.histograms['CountWeightedLHEWeightPdfNoPU{}'.format(insert_name)]['histogram'].Fill(
              #       float(lhe_pdf_idx), genWeight_sign * lheTHXWeight * self.clip(LHEPdfWeight[lhe_pdf_idx]) * topSF
              #     )
              # if 'histogram' in self.histograms['CountFullWeightedLHEWeightPdfNoPU{}'.format(insert_name)]:
              #   if not self.isInitialized(['CountFullWeightedLHEWeightPdfNoPU{}'.format(insert_name)]):
              #     self.initHistograms(['CountFullWeightedLHEWeightPdfNoPU{}'.format(insert_name)], self.nLHEPdfWeight)
              #   for lhe_pdf_idx in range(self.nLHEPdfWeight):
              #     self.histograms['CountFullWeightedLHEWeightPdfNoPU{}'.format(insert_name)]['histogram'].Fill(
              #       float(lhe_pdf_idx), genWeight * lheTHXWeight * self.clip(LHEPdfWeight[lhe_pdf_idx]) * topSF
              #     )

              if has_l1Prefire:
                if 'histogram' in self.histograms['CountWeightedLHEWeightPdfL1PrefireNom{}'.format(insert_name)]:
                  if not self.isInitialized(['CountWeightedLHEWeightPdfL1PrefireNom{}'.format(insert_name)]):
                    self.initHistograms(['CountWeightedLHEWeightPdfL1PrefireNom{}'.format(insert_name)], self.nLHEPdfWeight)
                  for lhe_pdf_idx in range(self.nLHEPdfWeight):
                    self.histograms['CountWeightedLHEWeightPdfL1PrefireNom{}'.format(insert_name)]['histogram'].Fill(
                      float(lhe_pdf_idx), genWeight_sign * puWeight * lheTHXWeight * l1_nom * self.clip(LHEPdfWeight[lhe_pdf_idx]) * topSF
                    )
                # if 'histogram' in self.histograms['CountFullWeightedLHEWeightPdfL1PrefireNom{}'.format(insert_name)]:
                #   if not self.isInitialized(['CountFullWeightedLHEWeightPdfL1PrefireNom{}'.format(insert_name)]):
                #     self.initHistograms(['CountFullWeightedLHEWeightPdfL1PrefireNom{}'.format(insert_name)], self.nLHEPdfWeight)
                #   for lhe_pdf_idx in range(self.nLHEPdfWeight):
                #     self.histograms['CountFullWeightedLHEWeightPdfL1PrefireNom{}'.format(insert_name)]['histogram'].Fill(
                #       float(lhe_pdf_idx), genWeight * puWeight * lheTHXWeight * l1_nom * self.clip(LHEPdfWeight[lhe_pdf_idx]) * topSF
                #     )

                # if 'histogram' in self.histograms['CountWeightedLHEWeightPdfNoPUL1PrefireNom{}'.format(insert_name)]:
                #   if not self.isInitialized(['CountWeightedLHEWeightPdfNoPUL1PrefireNom{}'.format(insert_name)]):
                #     self.initHistograms(['CountWeightedLHEWeightPdfNoPUL1PrefireNom{}'.format(insert_name)], self.nLHEPdfWeight)
                #   for lhe_pdf_idx in range(self.nLHEPdfWeight):
                #     self.histograms['CountWeightedLHEWeightPdfNoPUL1PrefireNom{}'.format(insert_name)]['histogram'].Fill(
                #       float(lhe_pdf_idx), genWeight_sign * lheTHXWeight * l1_nom * self.clip(LHEPdfWeight[lhe_pdf_idx]) * topSF
                #     )
                # if 'histogram' in self.histograms['CountFullWeightedLHEWeightPdfNoPUL1PrefireNom{}'.format(insert_name)]:
                #   if not self.isInitialized(['CountFullWeightedLHEWeightPdfNoPUL1PrefireNom{}'.format(insert_name)]):
                #     self.initHistograms(['CountFullWeightedLHEWeightPdfNoPUL1PrefireNom{}'.format(insert_name)], self.nLHEPdfWeight)
                #   for lhe_pdf_idx in range(self.nLHEPdfWeight):
                #     self.histograms['CountFullWeightedLHEWeightPdfNoPUL1PrefireNom{}'.format(insert_name)]['histogram'].Fill(
                #       float(lhe_pdf_idx), genWeight * lheTHXWeight * l1_nom * self.clip(LHEPdfWeight[lhe_pdf_idx]) * topSF
                #     )

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
              # if 'histogram' in self.histograms['CountFullWeightedLHEWeightScale{}'.format(insert_name)]:
              #   if not self.isInitialized(['CountFullWeightedLHEWeightScale{}'.format(insert_name)]):
              #     self.initHistograms(['CountFullWeightedLHEWeightScale{}'.format(insert_name)], self.nLHEScaleWeight)
              #   for lhe_scale_idx in range(self.nLHEScaleWeight):
              #     self.histograms['CountFullWeightedLHEWeightScale{}'.format(insert_name)]['histogram'].Fill(
              #       float(lhe_scale_idx), genWeight * puWeight * lheTHXWeight * self.clip(LHEScaleWeight[lhe_scale_idx]) * topSF
              #     )

              # if 'histogram' in self.histograms['CountWeightedLHEWeightScaleNoPU{}'.format(insert_name)]:
              #   if not self.isInitialized(['CountWeightedLHEWeightScaleNoPU{}'.format(insert_name)]):
              #     self.initHistograms(['CountWeightedLHEWeightScaleNoPU{}'.format(insert_name)], self.nLHEScaleWeight)
              #   for lhe_scale_idx in range(self.nLHEScaleWeight):
              #     self.histograms['CountWeightedLHEWeightScaleNoPU{}'.format(insert_name)]['histogram'].Fill(
              #       float(lhe_scale_idx), genWeight_sign * lheTHXWeight * self.clip(LHEScaleWeight[lhe_scale_idx]) * topSF
              #     )
              # if 'histogram' in self.histograms['CountFullWeightedLHEWeightScaleNoPU{}'.format(insert_name)]:
              #   if not self.isInitialized(['CountFullWeightedLHEWeightScaleNoPU{}'.format(insert_name)]):
              #     self.initHistograms(['CountFullWeightedLHEWeightScaleNoPU{}'.format(insert_name)], self.nLHEScaleWeight)
              #   for lhe_scale_idx in range(self.nLHEScaleWeight):
              #     self.histograms['CountFullWeightedLHEWeightScaleNoPU{}'.format(insert_name)]['histogram'].Fill(
              #       float(lhe_scale_idx), genWeight * lheTHXWeight * self.clip(LHEScaleWeight[lhe_scale_idx]) * topSF
              #     )

              if has_l1Prefire:
                if 'histogram' in self.histograms['CountWeightedLHEWeightScaleL1PrefireNom{}'.format(insert_name)]:
                  if not self.isInitialized(['CountWeightedLHEWeightScaleL1PrefireNom{}'.format(insert_name)]):
                    self.initHistograms(['CountWeightedLHEWeightScaleL1PrefireNom{}'.format(insert_name)], self.nLHEScaleWeight)
                  for lhe_scale_idx in range(self.nLHEScaleWeight):
                    self.histograms['CountWeightedLHEWeightScaleL1PrefireNom{}'.format(insert_name)]['histogram'].Fill(
                      float(lhe_scale_idx), genWeight_sign * puWeight * lheTHXWeight * l1_nom * self.clip(LHEScaleWeight[lhe_scale_idx]) * topSF
                    )
                # if 'histogram' in self.histograms['CountFullWeightedLHEWeightScaleL1PrefireNom{}'.format(insert_name)]:
                #   if not self.isInitialized(['CountFullWeightedLHEWeightScaleL1PrefireNom{}'.format(insert_name)]):
                #     self.initHistograms(['CountFullWeightedLHEWeightScaleL1PrefireNom{}'.format(insert_name)], self.nLHEScaleWeight)
                #   for lhe_scale_idx in range(self.nLHEScaleWeight):
                #     self.histograms['CountFullWeightedLHEWeightScaleL1PrefireNom{}'.format(insert_name)]['histogram'].Fill(
                #       float(lhe_scale_idx), genWeight * puWeight * lheTHXWeight * l1_nom * self.clip(LHEScaleWeight[lhe_scale_idx]) * topSF
                #     )

                # if 'histogram' in self.histograms['CountWeightedLHEWeightScaleNoPUL1PrefireNom{}'.format(insert_name)]:
                #   if not self.isInitialized(['CountWeightedLHEWeightScaleNoPUL1PrefireNom{}'.format(insert_name)]):
                #     self.initHistograms(['CountWeightedLHEWeightScaleNoPUL1PrefireNom{}'.format(insert_name)], self.nLHEScaleWeight)
                #   for lhe_scale_idx in range(self.nLHEScaleWeight):
                #     self.histograms['CountWeightedLHEWeightScaleNoPUL1PrefireNom{}'.format(insert_name)]['histogram'].Fill(
                #       float(lhe_scale_idx), genWeight_sign * lheTHXWeight * l1_nom * self.clip(LHEScaleWeight[lhe_scale_idx]) * topSF
                #     )
                # if 'histogram' in self.histograms['CountFullWeightedLHEWeightScaleNoPUL1PrefireNom{}'.format(insert_name)]:
                #   if not self.isInitialized(['CountFullWeightedLHEWeightScaleNoPUL1PrefireNom{}'.format(insert_name)]):
                #     self.initHistograms(['CountFullWeightedLHEWeightScaleNoPUL1PrefireNom{}'.format(insert_name)], self.nLHEScaleWeight)
                #   for lhe_scale_idx in range(self.nLHEScaleWeight):
                #     self.histograms['CountFullWeightedLHEWeightScaleNoPUL1PrefireNom{}'.format(insert_name)]['histogram'].Fill(
                #       float(lhe_scale_idx), genWeight * lheTHXWeight * l1_nom * self.clip(LHEScaleWeight[lhe_scale_idx]) * topSF
                #     )
              
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

    if self.compTopRwgt:
      self.out.fillBranch(self.topRwgtBranchName, topRwgt)
    if self.compLHEEnvelope:
      self.out.fillBranch(self.LHEEnvelopeNameUp, LHEEnvelopeValues[0])
      self.out.fillBranch(self.LHEEnvelopeNameDown, LHEEnvelopeValues[1])

    return True

# provide this variable as the 2nd argument to the import option for the nano_postproc.py script
countHistogramAll            = lambda: countHistogramProducer(False)
countHistogramAllCompTopRwgt = lambda: countHistogramProducer(True)
