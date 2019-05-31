import ROOT
import numpy as np
import collections

ROOT.PyConfig.IgnoreCommandLineOptions = True

from PhysicsTools.NanoAODTools.postprocessing.framework.eventloop import Module

class countHistogramProducer(Module):

  def __init__(self):
    self.puWeightName            = 'puWeight'
    self.puWeightName_up         = '%sUp' % self.puWeightName
    self.puWeightName_down       = '%sDown' % self.puWeightName
    self.l1PrefireWeightName     = 'L1PreFiringWeight'
    self.l1PrefireWeightNomName  = '%s_Nom' % self.l1PrefireWeightName
    self.l1PrefireWeightUpName   = '%s_Up' % self.l1PrefireWeightName
    self.l1PrefireWeightDownName = '%s_Dn' % self.l1PrefireWeightName
    self.genWeightName           = 'genWeight'
    self.lheTHXWeightName        = 'LHEReweightingWeight'
    self.lheTHXWeightCountName   = 'n%s' % self.lheTHXWeightName
    self.LHEPdfWeightName        = 'LHEPdfWeight'
    self.LHEScaleWeightName      = 'LHEScaleWeight'
    self.nLHEPdfWeight           = 101
    self.nLHEScaleWeight         = 9
    self.nLHEReweightingWeight   = 50

    self.histograms = collections.OrderedDict([
      ('Count', {
        'bins'  : 1,
        'min'   : 0.,
        'max'   : 2.,
        'title' : 'sum(1)',
      }),
      ('CountPosWeight', {
        'bins'  : 1,
        'min'   : 0.,
        'max'   : 2.,
        'title' : 'sum(gen > 0)',
      }),
      ('CountNegWeight', {
        'bins'  : 1,
        'min'   : 0.,
        'max'   : 2.,
        'title' : 'sum(gen < 0)',
      }),
    ])
    self.lheTHXSMWeightIndices = list(range(-1, self.nLHEReweightingWeight))

    for lheTHXSMWeightIndex in self.lheTHXSMWeightIndices:
      do_tH = lheTHXSMWeightIndex >= 0
      intert_title = ("* LHE(tH %d)" % lheTHXSMWeightIndex) if do_tH else ""
      insert_name = ("_rwgt%d" % lheTHXSMWeightIndex) if do_tH else ""
      self.histograms.update([
        ('CountWeighted{}'.format(insert_name), {
          'bins'  : 3,
          'min'   : -0.5,
          'max'   : 2.5,
          'title' : 'sum(sgn(gen) * PU(central,up,down){})'.format(intert_title),
        }),
        ('CountWeightedL1PrefireNom{}'.format(insert_name), {
          'bins'  : 3,
          'min'   : -0.5,
          'max'   : 2.5,
          'title' : 'sum(sgn(gen) * PU(central,up,down){} * L1Prefire(nom))'.format(intert_title),
        }),
        ('CountWeightedL1Prefire{}'.format(insert_name), {
          'bins'  : 3,
          'min'   : -0.5,
          'max'   : 2.5,
          'title' : 'sum(sgn(gen) * PU(central){} * L1Prefire(nom,up,down))'.format(intert_title),
        }),
        ('CountFullWeighted{}'.format(insert_name), {
          'bins'  : 3,
          'min'   : -0.5,
          'max'   : 2.5,
          'title' : 'sum(gen * PU(central,up,down){})'.format(intert_title),
        }),
        ('CountFullWeightedL1PrefireNom{}'.format(insert_name), {
          'bins'  : 3,
          'min'   : -0.5,
          'max'   : 2.5,
          'title' : 'sum(gen * PU(central,up,down){} * L1Prefire(nom))'.format(intert_title),
        }),
        ('CountFullWeightedL1Prefire{}'.format(insert_name), {
          'bins'  : 3,
          'min'   : -0.5,
          'max'   : 2.5,
          'title' : 'sum(gen * PU(central){} * L1Prefire(nom,up,down))'.format(intert_title),
        }),
        ('CountWeightedNoPU{}'.format(insert_name), {
          'bins'  : 1,
          'min'   : 0.,
          'max'   : 2.,
          'title' : 'sum(sgn(gen){})'.format(intert_title),
        }),
        ('CountWeightedNoPUL1PrefireNom{}'.format(insert_name), {
          'bins'  : 1,
          'min'   : 0.,
          'max'   : 2.,
          'title' : 'sum(sgn(gen){} * L1Prefire(nom))'.format(intert_title),
        }),
        ('CountFullWeightedNoPU{}'.format(insert_name), {
          'bins'  : 1,
          'min'   : 0.,
          'max'   : 2.,
          'title' : 'sum(gen{})'.format(intert_title),
        }),
        ('CountFullWeightedNoPUL1PrefireNom{}'.format(insert_name), {
          'bins'  : 1,
          'min'   : 0.,
          'max'   : 2.,
          'title' : 'sum(gen{} * L1Prefire(nom))'.format(intert_title),
        }),
        ('CountWeightedLHEWeightPdf{}'.format(insert_name), {
          'bins'  : self.nLHEPdfWeight,
          'min'   : -0.5,
          'max'   : self.nLHEPdfWeight - 0.5,
          'title' : 'sum(sgn(gen) * PU(central){} * LHE(pdf))'.format(intert_title),
        }),
        ('CountWeightedLHEWeightPdfL1PrefireNom{}'.format(insert_name), {
          'bins'  : self.nLHEPdfWeight,
          'min'   : -0.5,
          'max'   : self.nLHEPdfWeight - 0.5,
          'title' : 'sum(sgn(gen) * PU(central){} * LHE(pdf) * L1Prefire(nom))'.format(intert_title),
        }),
        ('CountWeightedLHEWeightPdfNoPU{}'.format(insert_name), {
          'bins'  : self.nLHEPdfWeight,
          'min'   : -0.5,
          'max'   : self.nLHEPdfWeight - 0.5,
          'title' : 'sum(sgn(gen){} * LHE(pdf))'.format(intert_title),
        }),
        ('CountWeightedLHEWeightPdfNoPUL1PrefireNom{}'.format(insert_name), {
          'bins'  : self.nLHEPdfWeight,
          'min'   : -0.5,
          'max'   : self.nLHEPdfWeight - 0.5,
          'title' : 'sum(sgn(gen){} * LHE(pdf) * L1Prefire(nom))'.format(intert_title),
        }),
        ('CountFullWeightedLHEWeightPdf{}'.format(insert_name), {
          'bins'  : self.nLHEPdfWeight,
          'min'   : -0.5,
          'max'   : self.nLHEPdfWeight - 0.5,
          'title' : 'sum(gen * PU(central){} * LHE(pdf))'.format(intert_title),
        }),
        ('CountFullWeightedLHEWeightPdfL1PrefireNom{}'.format(insert_name), {
          'bins'  : self.nLHEPdfWeight,
          'min'   : -0.5,
          'max'   : self.nLHEPdfWeight - 0.5,
          'title' : 'sum(gen * PU(central){} * LHE(pdf) * L1Prefire(nom))'.format(intert_title),
        }),
        ('CountFullWeightedLHEWeightPdfNoPU{}'.format(insert_name), {
          'bins'  : self.nLHEPdfWeight,
          'min'   : -0.5,
          'max'   : self.nLHEPdfWeight - 0.5,
          'title' : 'sum(gen{} * LHE(pdf))'.format(intert_title),
        }),
        ('CountFullWeightedLHEWeightPdfNoPUL1PrefireNom{}'.format(insert_name), {
          'bins'  : self.nLHEPdfWeight,
          'min'   : -0.5,
          'max'   : self.nLHEPdfWeight - 0.5,
          'title' : 'sum(gen{} * LHE(pdf) * L1Prefire(nom))'.format(intert_title),
        }),
        ('CountWeightedLHEWeightScale{}'.format(insert_name), {
          'bins'  : self.nLHEScaleWeight,
          'min'   : -0.5,
          'max'   : self.nLHEScaleWeight - 0.5,
          'title' : 'sum(sgn(gen) * PU(central){} * LHE(scale))'.format(intert_title),
        }),
        ('CountWeightedLHEWeightScaleL1PrefireNom{}'.format(insert_name), {
          'bins'  : self.nLHEScaleWeight,
          'min'   : -0.5,
          'max'   : self.nLHEScaleWeight - 0.5,
          'title' : 'sum(sgn(gen) * PU(central){} * LHE(scale) * L1Prefire(nom))'.format(intert_title),
        }),
        ('CountWeightedLHEWeightScaleNoPU{}'.format(insert_name), {
          'bins'  : self.nLHEScaleWeight,
          'min'   : -0.5,
          'max'   : self.nLHEScaleWeight - 0.5,
          'title' : 'sum(sgn(gen){} * LHE(scale))'.format(intert_title),
        }),
        ('CountWeightedLHEWeightScaleNoPUL1PrefireNom{}'.format(insert_name), {
          'bins': self.nLHEScaleWeight,
          'min': -0.5,
          'max': self.nLHEScaleWeight - 0.5,
          'title': 'sum(sgn(gen){} * LHE(scale) * L1Prefire(nom))'.format(intert_title),
        }),
        ('CountFullWeightedLHEWeightScale{}'.format(insert_name), {
          'bins'  : self.nLHEScaleWeight,
          'min'   : -0.5,
          'max'   : self.nLHEScaleWeight - 0.5,
          'title' : 'sum(gen * PU(central){} * LHE(scale))'.format(intert_title),
        }),
        ('CountFullWeightedLHEWeightScaleL1PrefireNom{}'.format(insert_name), {
          'bins'  : self.nLHEScaleWeight,
          'min'   : -0.5,
          'max'   : self.nLHEScaleWeight - 0.5,
          'title' : 'sum(gen * PU(central){} * LHE(scale) * L1Prefire(nom))'.format(intert_title),
        }),
        ('CountFullWeightedLHEWeightScaleNoPU{}'.format(insert_name), {
          'bins'  : self.nLHEScaleWeight,
          'min'   : -0.5,
          'max'   : self.nLHEScaleWeight - 0.5,
          'title' : 'sum(gen{} * LHE(scale))'.format(intert_title),
        }),
        ('CountFullWeightedLHEWeightScaleNoPUL1PrefireNom{}'.format(insert_name), {
          'bins'  : self.nLHEScaleWeight,
          'min'   : -0.5,
          'max'   : self.nLHEScaleWeight - 0.5,
          'title' : 'sum(gen{} * LHE(scale) * L1Prefire(nom))'.format(intert_title),
        }),
      ])

    for histogramName in self.histograms:
      self.histograms[histogramName]['histogram'] = None

    self.isPrinted = {
      branchName : False for branchName in [
        self.puWeightName, self.genWeightName, self.lheTHXWeightName,
        self.LHEPdfWeightName, self.LHEScaleWeightName,
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

  def beginJob(self):
    pass

  def endJob(self):
    pass

  def beginFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
    self.out = wrappedOutputTree

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

    if hasattr(event, self.genWeightName):
      genWeight = getattr(event, self.genWeightName)
      genWeight_sign = np.sign(genWeight)

      if 'histogram' in self.histograms['CountPosWeight']:
        if not self.isInitialized(['CountPosWeight']):
          self.initHistograms(['CountPosWeight'])
        self.histograms['CountPosWeight']['histogram'].Fill(1, 1 if genWeight_sign > 0 else 0)
      if 'histogram' in self.histograms['CountNegWeight']:
        if not self.isInitialized(['CountNegWeight']):
          self.initHistograms(['CountNegWeight'])
        self.histograms['CountNegWeight']['histogram'].Fill(1, 1 if genWeight_sign < 0 else 0)

      if hasattr(event, self.puWeightName):
        assert(hasattr(event, self.puWeightName_up))
        assert(hasattr(event, self.puWeightName_down))

        puWeight = getattr(event, self.puWeightName)
        puWeight_up = getattr(event, self.puWeightName_up)
        puWeight_down = getattr(event, self.puWeightName_down)

        for lheTHXSMWeightIndex in self.lheTHXSMWeightIndices:
          do_tH = lheTHXSMWeightIndex >= 0
          insert_name = ("_rwgt%d" % lheTHXSMWeightIndex) if do_tH else ""

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
            self.histograms['CountWeighted{}'.format(insert_name)]['histogram'].Fill(0., genWeight_sign * puWeight * lheTHXWeight)
            self.histograms['CountWeighted{}'.format(insert_name)]['histogram'].Fill(1., genWeight_sign * puWeight_up * lheTHXWeight)
            self.histograms['CountWeighted{}'.format(insert_name)]['histogram'].Fill(2., genWeight_sign * puWeight_down * lheTHXWeight)

          if 'histogram' in self.histograms['CountFullWeighted{}'.format(insert_name)]:
            if not self.isInitialized(['CountFullWeighted{}'.format(insert_name)]):
              self.initHistograms(['CountFullWeighted{}'.format(insert_name)])
            self.histograms['CountFullWeighted{}'.format(insert_name)]['histogram'].Fill(0., genWeight * puWeight * lheTHXWeight)
            self.histograms['CountFullWeighted{}'.format(insert_name)]['histogram'].Fill(1., genWeight * puWeight_up * lheTHXWeight)
            self.histograms['CountFullWeighted{}'.format(insert_name)]['histogram'].Fill(2., genWeight * puWeight_down * lheTHXWeight)

          if 'histogram' in self.histograms['CountWeightedNoPU{}'.format(insert_name)]:
            if not self.isInitialized(['CountWeightedNoPU{}'.format(insert_name)]):
              self.initHistograms(['CountWeightedNoPU{}'.format(insert_name)])
            self.histograms['CountWeightedNoPU{}'.format(insert_name)]['histogram'].Fill(0., genWeight_sign * lheTHXWeight)

          if 'histogram' in self.histograms['CountFullWeightedNoPU{}'.format(insert_name)]:
            if not self.isInitialized(['CountFullWeightedNoPU{}'.format(insert_name)]):
              self.initHistograms(['CountFullWeightedNoPU{}'.format(insert_name)])
            self.histograms['CountFullWeightedNoPU{}'.format(insert_name)]['histogram'].Fill(0., genWeight * lheTHXWeight)

          if has_l1Prefire:
            if 'histogram' in self.histograms['CountWeightedL1PrefireNom{}'.format(insert_name)]:
              if not self.isInitialized(['CountWeightedL1PrefireNom{}'.format(insert_name)]):
                self.initHistograms(['CountWeightedL1PrefireNom{}'.format(insert_name)])
              self.histograms['CountWeightedL1PrefireNom{}'.format(insert_name)]['histogram'].Fill(0., genWeight_sign * puWeight * lheTHXWeight * l1_nom)
              self.histograms['CountWeightedL1PrefireNom{}'.format(insert_name)]['histogram'].Fill(1., genWeight_sign * puWeight_up * lheTHXWeight * l1_nom)
              self.histograms['CountWeightedL1PrefireNom{}'.format(insert_name)]['histogram'].Fill(2., genWeight_sign * puWeight_down * lheTHXWeight * l1_nom)

            if 'histogram' in self.histograms['CountWeightedL1Prefire{}'.format(insert_name)]:
              if not self.isInitialized(['CountWeightedL1Prefire{}'.format(insert_name)]):
                self.initHistograms(['CountWeightedL1Prefire{}'.format(insert_name)])
              self.histograms['CountWeightedL1Prefire{}'.format(insert_name)]['histogram'].Fill(0., genWeight_sign * puWeight * lheTHXWeight * l1_nom)
              self.histograms['CountWeightedL1Prefire{}'.format(insert_name)]['histogram'].Fill(1., genWeight_sign * puWeight * lheTHXWeight * l1_up)
              self.histograms['CountWeightedL1Prefire{}'.format(insert_name)]['histogram'].Fill(2., genWeight_sign * puWeight * lheTHXWeight * l1_down)

            if 'histogram' in self.histograms['CountFullWeightedL1PrefireNom{}'.format(insert_name)]:
              if not self.isInitialized(['CountFullWeightedL1PrefireNom{}'.format(insert_name)]):
                self.initHistograms(['CountFullWeightedL1PrefireNom{}'.format(insert_name)])
              self.histograms['CountFullWeightedL1PrefireNom{}'.format(insert_name)]['histogram'].Fill(0., genWeight * puWeight * lheTHXWeight * l1_nom)
              self.histograms['CountFullWeightedL1PrefireNom{}'.format(insert_name)]['histogram'].Fill(1., genWeight * puWeight_up * lheTHXWeight * l1_nom)
              self.histograms['CountFullWeightedL1PrefireNom{}'.format(insert_name)]['histogram'].Fill(2., genWeight * puWeight_down * lheTHXWeight * l1_nom)

            if 'histogram' in self.histograms['CountFullWeightedL1Prefire{}'.format(insert_name)]:
              if not self.isInitialized(['CountFullWeightedL1Prefire{}'.format(insert_name)]):
                self.initHistograms(['CountFullWeightedL1Prefire{}'.format(insert_name)])
              self.histograms['CountFullWeightedL1Prefire{}'.format(insert_name)]['histogram'].Fill(0., genWeight * puWeight * lheTHXWeight * l1_nom)
              self.histograms['CountFullWeightedL1Prefire{}'.format(insert_name)]['histogram'].Fill(1., genWeight * puWeight * lheTHXWeight * l1_up)
              self.histograms['CountFullWeightedL1Prefire{}'.format(insert_name)]['histogram'].Fill(2., genWeight * puWeight * lheTHXWeight * l1_down)

            if 'histogram' in self.histograms['CountWeightedNoPUL1PrefireNom{}'.format(insert_name)]:
              if not self.isInitialized(['CountWeightedNoPUL1PrefireNom{}'.format(insert_name)]):
                self.initHistograms(['CountWeightedNoPUL1PrefireNom{}'.format(insert_name)])
              self.histograms['CountWeightedNoPUL1PrefireNom{}'.format(insert_name)]['histogram'].Fill(0., genWeight_sign * lheTHXWeight * l1_nom)

            if 'histogram' in self.histograms['CountFullWeightedNoPUL1PrefireNom{}'.format(insert_name)]:
              if not self.isInitialized(['CountFullWeightedNoPUL1PrefireNom{}'.format(insert_name)]):
                self.initHistograms(['CountFullWeightedNoPUL1PrefireNom{}'.format(insert_name)])
              self.histograms['CountFullWeightedNoPUL1PrefireNom{}'.format(insert_name)]['histogram'].Fill(0., genWeight * lheTHXWeight * l1_nom)

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
                  float(lhe_pdf_idx), genWeight_sign * puWeight * lheTHXWeight * self.clip(LHEPdfWeight[lhe_pdf_idx])
                )
            if 'histogram' in self.histograms['CountFullWeightedLHEWeightPdf{}'.format(insert_name)]:
              if not self.isInitialized(['CountFullWeightedLHEWeightPdf{}'.format(insert_name)]):
                self.initHistograms(['CountFullWeightedLHEWeightPdf{}'.format(insert_name)], self.nLHEPdfWeight)
              for lhe_pdf_idx in range(self.nLHEPdfWeight):
                self.histograms['CountFullWeightedLHEWeightPdf{}'.format(insert_name)]['histogram'].Fill(
                  float(lhe_pdf_idx), genWeight * puWeight * lheTHXWeight * self.clip(LHEPdfWeight[lhe_pdf_idx])
                )

            if 'histogram' in self.histograms['CountWeightedLHEWeightPdfNoPU{}'.format(insert_name)]:
              if not self.isInitialized(['CountWeightedLHEWeightPdfNoPU{}'.format(insert_name)]):
                self.initHistograms(['CountWeightedLHEWeightPdfNoPU{}'.format(insert_name)], self.nLHEPdfWeight)
              for lhe_pdf_idx in range(self.nLHEPdfWeight):
                self.histograms['CountWeightedLHEWeightPdfNoPU{}'.format(insert_name)]['histogram'].Fill(
                  float(lhe_pdf_idx), genWeight_sign * lheTHXWeight * self.clip(LHEPdfWeight[lhe_pdf_idx])
                )
            if 'histogram' in self.histograms['CountFullWeightedLHEWeightPdfNoPU{}'.format(insert_name)]:
              if not self.isInitialized(['CountFullWeightedLHEWeightPdfNoPU{}'.format(insert_name)]):
                self.initHistograms(['CountFullWeightedLHEWeightPdfNoPU{}'.format(insert_name)], self.nLHEPdfWeight)
              for lhe_pdf_idx in range(self.nLHEPdfWeight):
                self.histograms['CountFullWeightedLHEWeightPdfNoPU{}'.format(insert_name)]['histogram'].Fill(
                  float(lhe_pdf_idx), genWeight * lheTHXWeight * self.clip(LHEPdfWeight[lhe_pdf_idx])
                )

            if has_l1Prefire:
              if 'histogram' in self.histograms['CountWeightedLHEWeightPdfL1PrefireNom{}'.format(insert_name)]:
                if not self.isInitialized(['CountWeightedLHEWeightPdfL1PrefireNom{}'.format(insert_name)]):
                  self.initHistograms(['CountWeightedLHEWeightPdfL1PrefireNom{}'.format(insert_name)], self.nLHEPdfWeight)
                for lhe_pdf_idx in range(self.nLHEPdfWeight):
                  self.histograms['CountWeightedLHEWeightPdfL1PrefireNom{}'.format(insert_name)]['histogram'].Fill(
                    float(lhe_pdf_idx), genWeight_sign * puWeight * lheTHXWeight * l1_nom * self.clip(LHEPdfWeight[lhe_pdf_idx])
                  )
              if 'histogram' in self.histograms['CountFullWeightedLHEWeightPdfL1PrefireNom{}'.format(insert_name)]:
                if not self.isInitialized(['CountFullWeightedLHEWeightPdfL1PrefireNom{}'.format(insert_name)]):
                  self.initHistograms(['CountFullWeightedLHEWeightPdfL1PrefireNom{}'.format(insert_name)], self.nLHEPdfWeight)
                for lhe_pdf_idx in range(self.nLHEPdfWeight):
                  self.histograms['CountFullWeightedLHEWeightPdfL1PrefireNom{}'.format(insert_name)]['histogram'].Fill(
                    float(lhe_pdf_idx), genWeight * puWeight * lheTHXWeight * l1_nom * self.clip(LHEPdfWeight[lhe_pdf_idx])
                  )

              if 'histogram' in self.histograms['CountWeightedLHEWeightPdfNoPUL1PrefireNom{}'.format(insert_name)]:
                if not self.isInitialized(['CountWeightedLHEWeightPdfNoPUL1PrefireNom{}'.format(insert_name)]):
                  self.initHistograms(['CountWeightedLHEWeightPdfNoPUL1PrefireNom{}'.format(insert_name)], self.nLHEPdfWeight)
                for lhe_pdf_idx in range(self.nLHEPdfWeight):
                  self.histograms['CountWeightedLHEWeightPdfNoPUL1PrefireNom{}'.format(insert_name)]['histogram'].Fill(
                    float(lhe_pdf_idx), genWeight_sign * lheTHXWeight * l1_nom * self.clip(LHEPdfWeight[lhe_pdf_idx])
                  )
              if 'histogram' in self.histograms['CountFullWeightedLHEWeightPdfNoPUL1PrefireNom{}'.format(insert_name)]:
                if not self.isInitialized(['CountFullWeightedLHEWeightPdfNoPUL1PrefireNom{}'.format(insert_name)]):
                  self.initHistograms(['CountFullWeightedLHEWeightPdfNoPUL1PrefireNom{}'.format(insert_name)], self.nLHEPdfWeight)
                for lhe_pdf_idx in range(self.nLHEPdfWeight):
                  self.histograms['CountFullWeightedLHEWeightPdfNoPUL1PrefireNom{}'.format(insert_name)]['histogram'].Fill(
                    float(lhe_pdf_idx), genWeight * lheTHXWeight * l1_nom * self.clip(LHEPdfWeight[lhe_pdf_idx])
                  )

          else:
            if not self.isPrinted[self.LHEPdfWeightName]:
              self.isPrinted[self.LHEPdfWeightName] = True
              print('Missing branch: %s' % self.LHEPdfWeightName)

          if hasattr(event, self.LHEScaleWeightName):
            LHEScaleWeight = getattr(event, self.LHEScaleWeightName)

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
                  float(lhe_scale_idx), genWeight_sign * puWeight * lheTHXWeight * self.clip(LHEScaleWeight[lhe_scale_idx])
                )
            if 'histogram' in self.histograms['CountFullWeightedLHEWeightScale{}'.format(insert_name)]:
              if not self.isInitialized(['CountFullWeightedLHEWeightScale{}'.format(insert_name)]):
                self.initHistograms(['CountFullWeightedLHEWeightScale{}'.format(insert_name)], self.nLHEScaleWeight)
              for lhe_scale_idx in range(self.nLHEScaleWeight):
                self.histograms['CountFullWeightedLHEWeightScale{}'.format(insert_name)]['histogram'].Fill(
                  float(lhe_scale_idx), genWeight * puWeight * lheTHXWeight * self.clip(LHEScaleWeight[lhe_scale_idx])
                )

            if 'histogram' in self.histograms['CountWeightedLHEWeightScaleNoPU{}'.format(insert_name)]:
              if not self.isInitialized(['CountWeightedLHEWeightScaleNoPU{}'.format(insert_name)]):
                self.initHistograms(['CountWeightedLHEWeightScaleNoPU{}'.format(insert_name)], self.nLHEScaleWeight)
              for lhe_scale_idx in range(self.nLHEScaleWeight):
                self.histograms['CountWeightedLHEWeightScaleNoPU{}'.format(insert_name)]['histogram'].Fill(
                  float(lhe_scale_idx), genWeight_sign * lheTHXWeight * self.clip(LHEScaleWeight[lhe_scale_idx])
                )
            if 'histogram' in self.histograms['CountFullWeightedLHEWeightScaleNoPU{}'.format(insert_name)]:
              if not self.isInitialized(['CountFullWeightedLHEWeightScaleNoPU{}'.format(insert_name)]):
                self.initHistograms(['CountFullWeightedLHEWeightScaleNoPU{}'.format(insert_name)], self.nLHEScaleWeight)
              for lhe_scale_idx in range(self.nLHEScaleWeight):
                self.histograms['CountFullWeightedLHEWeightScaleNoPU{}'.format(insert_name)]['histogram'].Fill(
                  float(lhe_scale_idx), genWeight * lheTHXWeight * self.clip(LHEScaleWeight[lhe_scale_idx])
                )

            if has_l1Prefire:
              if 'histogram' in self.histograms['CountWeightedLHEWeightScaleL1PrefireNom{}'.format(insert_name)]:
                if not self.isInitialized(['CountWeightedLHEWeightScaleL1PrefireNom{}'.format(insert_name)]):
                  self.initHistograms(['CountWeightedLHEWeightScaleL1PrefireNom{}'.format(insert_name)], self.nLHEScaleWeight)
                for lhe_scale_idx in range(self.nLHEScaleWeight):
                  self.histograms['CountWeightedLHEWeightScaleL1PrefireNom{}'.format(insert_name)]['histogram'].Fill(
                    float(lhe_scale_idx), genWeight_sign * puWeight * lheTHXWeight * l1_nom * self.clip(LHEScaleWeight[lhe_scale_idx])
                  )
              if 'histogram' in self.histograms['CountFullWeightedLHEWeightScaleL1PrefireNom{}'.format(insert_name)]:
                if not self.isInitialized(['CountFullWeightedLHEWeightScaleL1PrefireNom{}'.format(insert_name)]):
                  self.initHistograms(['CountFullWeightedLHEWeightScaleL1PrefireNom{}'.format(insert_name)], self.nLHEScaleWeight)
                for lhe_scale_idx in range(self.nLHEScaleWeight):
                  self.histograms['CountFullWeightedLHEWeightScaleL1PrefireNom{}'.format(insert_name)]['histogram'].Fill(
                    float(lhe_scale_idx), genWeight * puWeight * lheTHXWeight * l1_nom * self.clip(LHEScaleWeight[lhe_scale_idx])
                  )

              if 'histogram' in self.histograms['CountWeightedLHEWeightScaleNoPUL1PrefireNom{}'.format(insert_name)]:
                if not self.isInitialized(['CountWeightedLHEWeightScaleNoPUL1PrefireNom{}'.format(insert_name)]):
                  self.initHistograms(['CountWeightedLHEWeightScaleNoPUL1PrefireNom{}'.format(insert_name)], self.nLHEScaleWeight)
                for lhe_scale_idx in range(self.nLHEScaleWeight):
                  self.histograms['CountWeightedLHEWeightScaleNoPUL1PrefireNom{}'.format(insert_name)]['histogram'].Fill(
                    float(lhe_scale_idx), genWeight_sign * lheTHXWeight * l1_nom * self.clip(LHEScaleWeight[lhe_scale_idx])
                  )
              if 'histogram' in self.histograms['CountFullWeightedLHEWeightScaleNoPUL1PrefireNom{}'.format(insert_name)]:
                if not self.isInitialized(['CountFullWeightedLHEWeightScaleNoPUL1PrefireNom{}'.format(insert_name)]):
                  self.initHistograms(['CountFullWeightedLHEWeightScaleNoPUL1PrefireNom{}'.format(insert_name)], self.nLHEScaleWeight)
                for lhe_scale_idx in range(self.nLHEScaleWeight):
                  self.histograms['CountFullWeightedLHEWeightScaleNoPUL1PrefireNom{}'.format(insert_name)]['histogram'].Fill(
                    float(lhe_scale_idx), genWeight * lheTHXWeight * l1_nom * self.clip(LHEScaleWeight[lhe_scale_idx])
                  )

          else:
            if not self.isPrinted[self.LHEScaleWeightName]:
              self.isPrinted[self.LHEScaleWeightName] = True
              print('Missing branch: %s' % self.LHEScaleWeightName)

      else:
        if not self.isPrinted[self.puWeightName]:
          self.isPrinted[self.puWeightName] = True
          print('Missing branch: %s' % self.puWeightName)

    else:
      if not self.isPrinted[self.genWeightName]:
        self.isPrinted[self.genWeightName] = True
        print('Missing branch: %s' % self.genWeightName)


    return True

# provide this variable as the 2nd argument to the import option for the nano_postproc.py script
countHistogramAll = lambda : countHistogramProducer()
