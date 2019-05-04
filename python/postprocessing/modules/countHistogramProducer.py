import ROOT
import numpy as np

ROOT.PyConfig.IgnoreCommandLineOptions = True

from PhysicsTools.NanoAODTools.postprocessing.framework.eventloop import Module

class countHistogramProducer(Module):

  def __init__(self, selection):
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
    self.lheTHXSMWeightIndex     = 11 # 12th value
    self.LHEPdfWeightName        = 'LHEPdfWeight'
    self.LHEScaleWeightName      = 'LHEScaleWeight'
    self.nLHEPdfWeight           = 101
    self.nLHEScaleWeight         = 9

    self.histograms = {
      'Count'                             : { 'bins' : 1, 'min' :  0.,  'max' : 2.,  'title' : 'sum(1)',                                                         },
      'CountWeighted'                     : { 'bins' : 3, 'min' : -0.5, 'max' : 2.5, 'title' : 'sum(sgn(gen) * PU(central,up,down) * LHE(tH))',                  },
      'CountWeightedL1PrefireNom'         : { 'bins' : 3, 'min' : -0.5, 'max' : 2.5, 'title' : 'sum(sgn(gen) * PU(central,up,down) * LHE(tH) * L1Prefire(nom))', },
      'CountWeightedL1Prefire'            : { 'bins' : 3, 'min' : -0.5, 'max' : 2.5, 'title' : 'sum(sgn(gen) * PU(central) * LHE(tH) * L1Prefire(nom,up,down))', },
      'CountFullWeighted'                 : { 'bins' : 3, 'min' : -0.5, 'max' : 2.5, 'title' : 'sum(gen * PU(central,up,down) * LHE(tH))',                       },
      'CountFullWeightedL1PrefireNom'     : { 'bins' : 3, 'min' : -0.5, 'max' : 2.5, 'title' : 'sum(gen * PU(central,up,down) * LHE(tH) * L1Prefire(nom))',      },
      'CountFullWeightedL1Prefire'        : { 'bins' : 3, 'min' : -0.5, 'max' : 2.5, 'title' : 'sum(gen * PU(central) * LHE(tH) * L1Prefire(nom,up,down))',      },
      'CountWeightedNoPU'                 : { 'bins' : 1, 'min' :  0.,  'max' : 2.,  'title' : 'sum(sgn(gen) * LHE(th))',                                        },
      'CountWeightedNoPUL1PrefireNom'     : { 'bins' : 1, 'min' :  0.,  'max' : 2.,  'title' : 'sum(sgn(gen) * LHE(th) * L1Prefire(nom))',                       },
      'CountFullWeightedNoPU'             : { 'bins' : 1, 'min' :  0.,  'max' : 2.,  'title' : 'sum(gen * LHE(th))',                                             },
      'CountFullWeightedNoPUL1PrefireNom' : { 'bins' : 1, 'min' :  0.,  'max' : 2.,  'title' : 'sum(gen * LHE(th)) * L1Prefire(nom)',                            },
      'CountPosWeight'                    : { 'bins' : 1, 'min' :  0.,  'max' : 2.,  'title' : 'sum(gen > 0)',                                                   },
      'CountNegWeight'                    : { 'bins' : 1, 'min' :  0.,  'max' : 2.,  'title' : 'sum(gen < 0)',                                                   },
      'CountWeightedLHEWeightPdf' : {
        'bins'  : self.nLHEPdfWeight,
        'min'   : -0.5,
        'max'   : self.nLHEPdfWeight - 0.5,
        'title' : 'sum(sgn(gen) * PU(central) * LHE(th) * LHE(pdf))',
      },
      'CountWeightedLHEWeightPdfL1PrefireNom' : {
        'bins'  : self.nLHEPdfWeight,
        'min'   : -0.5,
        'max'   : self.nLHEPdfWeight - 0.5,
        'title' : 'sum(sgn(gen) * PU(central) * LHE(th) * LHE(pdf) * L1Prefire(nom))',
      },
      'CountWeightedLHEWeightPdfNoPU': {
        'bins'  : self.nLHEPdfWeight,
        'min'   : -0.5,
        'max'   : self.nLHEPdfWeight - 0.5,
        'title' : 'sum(sgn(gen) * LHE(th) * LHE(pdf))',
      },
      'CountWeightedLHEWeightPdfNoPUL1PrefireNom' : {
        'bins'  : self.nLHEPdfWeight,
        'min'   : -0.5,
        'max'   : self.nLHEPdfWeight - 0.5,
        'title' : 'sum(sgn(gen) * LHE(th) * LHE(pdf) * L1Prefire(nom))',
      },
      'CountFullWeightedLHEWeightPdf' : {
        'bins'  : self.nLHEPdfWeight,
        'min'   : -0.5,
        'max'   : self.nLHEPdfWeight - 0.5,
        'title' : 'sum(gen * PU(central) * LHE(th) * LHE(pdf))',
      },
      'CountFullWeightedLHEWeightPdfL1PrefireNom' : {
        'bins'  : self.nLHEPdfWeight,
        'min'   : -0.5,
        'max'   : self.nLHEPdfWeight - 0.5,
        'title' : 'sum(gen * PU(central) * LHE(th) * LHE(pdf) * L1Prefire(nom))',
      },
      'CountFullWeightedLHEWeightPdfNoPU' : {
        'bins'  : self.nLHEPdfWeight,
        'min'   : -0.5,
        'max'   : self.nLHEPdfWeight - 0.5,
        'title' : 'sum(gen * LHE(th) * LHE(pdf))',
      },
      'CountFullWeightedLHEWeightPdfNoPUL1PrefireNom' : {
        'bins'  : self.nLHEPdfWeight,
        'min'   : -0.5,
        'max'   : self.nLHEPdfWeight - 0.5,
        'title' : 'sum(gen * LHE(th) * LHE(pdf) * L1Prefire(nom))',
      },
      'CountWeightedLHEWeightScale' : {
        'bins'  : self.nLHEScaleWeight,
        'min'   : -0.5,
        'max'   : self.nLHEScaleWeight - 0.5,
        'title' : 'sum(sgn(gen) * PU(central) * LHE(th) * LHE(scale))',
      },
      'CountWeightedLHEWeightScaleL1PrefireNom' : {
        'bins'  : self.nLHEScaleWeight,
        'min'   : -0.5,
        'max'   : self.nLHEScaleWeight - 0.5,
        'title' : 'sum(sgn(gen) * PU(central) * LHE(th) * LHE(scale) * L1Prefire(nom))',
      },
      'CountWeightedLHEWeightScaleNoPU' : {
        'bins'  : self.nLHEScaleWeight,
        'min'   : -0.5,
        'max'   : self.nLHEScaleWeight - 0.5,
        'title' : 'sum(sgn(gen) * LHE(th) * LHE(scale))',
      },
      'CountWeightedLHEWeightScaleNoPUL1PrefireNom' : {
        'bins': self.nLHEScaleWeight,
        'min': -0.5,
        'max': self.nLHEScaleWeight - 0.5,
        'title': 'sum(sgn(gen) * LHE(th) * LHE(scale) * L1Prefire(nom))',
      },
      'CountFullWeightedLHEWeightScale' : {
        'bins'  : self.nLHEScaleWeight,
        'min'   : -0.5,
        'max'   : self.nLHEScaleWeight - 0.5,
        'title' : 'sum(gen * PU(central) * LHE(th) * LHE(scale))',
      },
      'CountFullWeightedLHEWeightScaleL1PrefireNom' : {
        'bins'  : self.nLHEScaleWeight,
        'min'   : -0.5,
        'max'   : self.nLHEScaleWeight - 0.5,
        'title' : 'sum(gen * PU(central) * LHE(th) * LHE(scale) * L1Prefire(nom))',
      },
      'CountFullWeightedLHEWeightScaleNoPU' : {
        'bins'  : self.nLHEScaleWeight,
        'min'   : -0.5,
        'max'   : self.nLHEScaleWeight - 0.5,
        'title' : 'sum(gen * LHE(th) * LHE(scale))',
      },
      'CountFullWeightedLHEWeightScaleNoPUL1PrefireNom': {
        'bins'  : self.nLHEScaleWeight,
        'min'   : -0.5,
        'max'   : self.nLHEScaleWeight - 0.5,
        'title' : 'sum(gen * LHE(th) * LHE(scale) * L1Prefire(nom))',
      },
    }

    for histogramName in selection:
      if histogramName not in self.histograms:
        raise ValueError("Invalid histogram requested: %s" % histogramName)
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

        has_lhe = False
        if hasattr(event, self.lheTHXWeightCountName) and hasattr(event, self.lheTHXWeightName):
          nofLheTHXWeights = getattr(event, self.lheTHXWeightCountName)
          if self.lheTHXSMWeightIndex < nofLheTHXWeights:
            lheTHXWeightArr = getattr(event, self.lheTHXWeightName)
            lheTHXWeight = lheTHXWeightArr[self.lheTHXSMWeightIndex]
            has_lhe = True
        if not has_lhe:
          if not self.isPrinted[self.lheTHXWeightName]:
            self.isPrinted[self.lheTHXWeightName] = True
            print('Missing or unfilled branch: %s' % self.lheTHXWeightName)
          lheTHXWeight = 1.

        puWeight = getattr(event, self.puWeightName)
        puWeight_up = getattr(event, self.puWeightName_up)
        puWeight_down = getattr(event, self.puWeightName_down)

        if 'histogram' in self.histograms['CountWeighted']:
          if not self.isInitialized(['CountWeighted']):
            self.initHistograms(['CountWeighted'])
          self.histograms['CountWeighted']['histogram'].Fill(0., genWeight_sign * puWeight * lheTHXWeight)
          self.histograms['CountWeighted']['histogram'].Fill(1., genWeight_sign * puWeight_up * lheTHXWeight)
          self.histograms['CountWeighted']['histogram'].Fill(2., genWeight_sign * puWeight_down * lheTHXWeight)

        if 'histogram' in self.histograms['CountFullWeighted']:
          if not self.isInitialized(['CountFullWeighted']):
            self.initHistograms(['CountFullWeighted'])
          self.histograms['CountFullWeighted']['histogram'].Fill(0., genWeight * puWeight * lheTHXWeight)
          self.histograms['CountFullWeighted']['histogram'].Fill(1., genWeight * puWeight_up * lheTHXWeight)
          self.histograms['CountFullWeighted']['histogram'].Fill(2., genWeight * puWeight_down * lheTHXWeight)

        if 'histogram' in self.histograms['CountWeightedNoPU']:
          if not self.isInitialized(['CountWeightedNoPU']):
            self.initHistograms(['CountWeightedNoPU'])
          self.histograms['CountWeightedNoPU']['histogram'].Fill(0., genWeight_sign * lheTHXWeight)

        if 'histogram' in self.histograms['CountFullWeightedNoPU']:
          if not self.isInitialized(['CountFullWeightedNoPU']):
            self.initHistograms(['CountFullWeightedNoPU'])
          self.histograms['CountFullWeightedNoPU']['histogram'].Fill(0., genWeight * lheTHXWeight)
        
        if has_l1Prefire:
          if 'histogram' in self.histograms['CountWeightedL1PrefireNom']:
            if not self.isInitialized(['CountWeightedL1PrefireNom']):
              self.initHistograms(['CountWeightedL1PrefireNom'])
            self.histograms['CountWeightedL1PrefireNom']['histogram'].Fill(0., genWeight_sign * puWeight * lheTHXWeight * l1_nom)
            self.histograms['CountWeightedL1PrefireNom']['histogram'].Fill(1., genWeight_sign * puWeight_up * lheTHXWeight * l1_nom)
            self.histograms['CountWeightedL1PrefireNom']['histogram'].Fill(2., genWeight_sign * puWeight_down * lheTHXWeight * l1_nom)
          
          if 'histogram' in self.histograms['CountWeightedL1Prefire']:
            if not self.isInitialized(['CountWeightedL1Prefire']):
              self.initHistograms(['CountWeightedL1Prefire'])
            self.histograms['CountWeightedL1Prefire']['histogram'].Fill(0., genWeight_sign * puWeight * lheTHXWeight * l1_nom)
            self.histograms['CountWeightedL1Prefire']['histogram'].Fill(1., genWeight_sign * puWeight * lheTHXWeight * l1_up)
            self.histograms['CountWeightedL1Prefire']['histogram'].Fill(2., genWeight_sign * puWeight * lheTHXWeight * l1_down)
          
          if 'histogram' in self.histograms['CountFullWeightedL1PrefireNom']:
            if not self.isInitialized(['CountFullWeightedL1PrefireNom']):
              self.initHistograms(['CountFullWeightedL1PrefireNom'])
            self.histograms['CountFullWeightedL1PrefireNom']['histogram'].Fill(0., genWeight * puWeight * lheTHXWeight * l1_nom)
            self.histograms['CountFullWeightedL1PrefireNom']['histogram'].Fill(1., genWeight * puWeight_up * lheTHXWeight * l1_nom)
            self.histograms['CountFullWeightedL1PrefireNom']['histogram'].Fill(2., genWeight * puWeight_down * lheTHXWeight * l1_nom)

          if 'histogram' in self.histograms['CountFullWeightedL1Prefire']:
            if not self.isInitialized(['CountFullWeightedL1Prefire']):
              self.initHistograms(['CountFullWeightedL1Prefire'])
            self.histograms['CountFullWeightedL1Prefire']['histogram'].Fill(0., genWeight * puWeight * lheTHXWeight * l1_nom)
            self.histograms['CountFullWeightedL1Prefire']['histogram'].Fill(1., genWeight * puWeight * lheTHXWeight * l1_up)
            self.histograms['CountFullWeightedL1Prefire']['histogram'].Fill(2., genWeight * puWeight * lheTHXWeight * l1_down)
          
          if 'histogram' in self.histograms['CountWeightedNoPUL1PrefireNom']:
            if not self.isInitialized(['CountWeightedNoPUL1PrefireNom']):
              self.initHistograms(['CountWeightedNoPUL1PrefireNom'])
            self.histograms['CountWeightedNoPUL1PrefireNom']['histogram'].Fill(0., genWeight_sign * lheTHXWeight * l1_nom)
          
          if 'histogram' in self.histograms['CountFullWeightedNoPUL1PrefireNom']:
            if not self.isInitialized(['CountFullWeightedNoPUL1PrefireNom']):
              self.initHistograms(['CountFullWeightedNoPUL1PrefireNom'])
            self.histograms['CountFullWeightedNoPUL1PrefireNom']['histogram'].Fill(0., genWeight * lheTHXWeight * l1_nom)

        if hasattr(event, self.LHEPdfWeightName):
          LHEPdfWeight = getattr(event, self.LHEPdfWeightName)

          if len(LHEPdfWeight) != self.nLHEPdfWeight:
            print(
              "WARNING: The length of '%s' array (= %i) does not match to the expected length of %i" % \
              (self.LHEPdfWeightName, len(LHEPdfWeight), self.nLHEPdfWeight)
            )
            self.nLHEPdfWeight = len(LHEPdfWeight)

          if 'histogram' in self.histograms['CountWeightedLHEWeightPdf']:
            if not self.isInitialized(['CountWeightedLHEWeightPdf']):
              self.initHistograms(['CountWeightedLHEWeightPdf'], self.nLHEPdfWeight)
            for lhe_pdf_idx in range(self.nLHEPdfWeight):
              self.histograms['CountWeightedLHEWeightPdf']['histogram'].Fill(
                float(lhe_pdf_idx), genWeight_sign * puWeight * lheTHXWeight * self.clip(LHEPdfWeight[lhe_pdf_idx])
              )
          if 'histogram' in self.histograms['CountFullWeightedLHEWeightPdf']:
            if not self.isInitialized(['CountFullWeightedLHEWeightPdf']):
              self.initHistograms(['CountFullWeightedLHEWeightPdf'], self.nLHEPdfWeight)
            for lhe_pdf_idx in range(self.nLHEPdfWeight):
              self.histograms['CountFullWeightedLHEWeightPdf']['histogram'].Fill(
                float(lhe_pdf_idx), genWeight * puWeight * lheTHXWeight * self.clip(LHEPdfWeight[lhe_pdf_idx])
              )

          if 'histogram' in self.histograms['CountWeightedLHEWeightPdfNoPU']:
            if not self.isInitialized(['CountWeightedLHEWeightPdfNoPU']):
              self.initHistograms(['CountWeightedLHEWeightPdfNoPU'], self.nLHEPdfWeight)
            for lhe_pdf_idx in range(self.nLHEPdfWeight):
              self.histograms['CountWeightedLHEWeightPdfNoPU']['histogram'].Fill(
                float(lhe_pdf_idx), genWeight_sign * lheTHXWeight * self.clip(LHEPdfWeight[lhe_pdf_idx])
              )
          if 'histogram' in self.histograms['CountFullWeightedLHEWeightPdfNoPU']:
            if not self.isInitialized(['CountFullWeightedLHEWeightPdfNoPU']):
              self.initHistograms(['CountFullWeightedLHEWeightPdfNoPU'], self.nLHEPdfWeight)
            for lhe_pdf_idx in range(self.nLHEPdfWeight):
              self.histograms['CountFullWeightedLHEWeightPdfNoPU']['histogram'].Fill(
                float(lhe_pdf_idx), genWeight * lheTHXWeight * self.clip(LHEPdfWeight[lhe_pdf_idx])
              )
          
          if has_l1Prefire:
            if 'histogram' in self.histograms['CountWeightedLHEWeightPdfL1PrefireNom']:
              if not self.isInitialized(['CountWeightedLHEWeightPdfL1PrefireNom']):
                self.initHistograms(['CountWeightedLHEWeightPdfL1PrefireNom'], self.nLHEPdfWeight)
              for lhe_pdf_idx in range(self.nLHEPdfWeight):
                self.histograms['CountWeightedLHEWeightPdfL1PrefireNom']['histogram'].Fill(
                  float(lhe_pdf_idx), genWeight_sign * puWeight * lheTHXWeight * l1_nom * self.clip(LHEPdfWeight[lhe_pdf_idx])
                )
            if 'histogram' in self.histograms['CountFullWeightedLHEWeightPdfL1PrefireNom']:
              if not self.isInitialized(['CountFullWeightedLHEWeightPdfL1PrefireNom']):
                self.initHistograms(['CountFullWeightedLHEWeightPdfL1PrefireNom'], self.nLHEPdfWeight)
              for lhe_pdf_idx in range(self.nLHEPdfWeight):
                self.histograms['CountFullWeightedLHEWeightPdfL1PrefireNom']['histogram'].Fill(
                  float(lhe_pdf_idx), genWeight * puWeight * lheTHXWeight * l1_nom * self.clip(LHEPdfWeight[lhe_pdf_idx])
                )

            if 'histogram' in self.histograms['CountWeightedLHEWeightPdfNoPUL1PrefireNom']:
              if not self.isInitialized(['CountWeightedLHEWeightPdfNoPUL1PrefireNom']):
                self.initHistograms(['CountWeightedLHEWeightPdfNoPUL1PrefireNom'], self.nLHEPdfWeight)
              for lhe_pdf_idx in range(self.nLHEPdfWeight):
                self.histograms['CountWeightedLHEWeightPdfNoPUL1PrefireNom']['histogram'].Fill(
                  float(lhe_pdf_idx), genWeight_sign * lheTHXWeight * l1_nom * self.clip(LHEPdfWeight[lhe_pdf_idx])
                )
            if 'histogram' in self.histograms['CountFullWeightedLHEWeightPdfNoPUL1PrefireNom']:
              if not self.isInitialized(['CountFullWeightedLHEWeightPdfNoPUL1PrefireNom']):
                self.initHistograms(['CountFullWeightedLHEWeightPdfNoPUL1PrefireNom'], self.nLHEPdfWeight)
              for lhe_pdf_idx in range(self.nLHEPdfWeight):
                self.histograms['CountFullWeightedLHEWeightPdfNoPUL1PrefireNom']['histogram'].Fill(
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

          if 'histogram' in self.histograms['CountWeightedLHEWeightScale']:
            if not self.isInitialized(['CountWeightedLHEWeightScale']):
              self.initHistograms(['CountWeightedLHEWeightScale'], self.nLHEScaleWeight)
            for lhe_scale_idx in range(self.nLHEScaleWeight):
              self.histograms['CountWeightedLHEWeightScale']['histogram'].Fill(
                float(lhe_scale_idx), genWeight_sign * puWeight * lheTHXWeight * self.clip(LHEScaleWeight[lhe_scale_idx])
              )
          if 'histogram' in self.histograms['CountFullWeightedLHEWeightScale']:
            if not self.isInitialized(['CountFullWeightedLHEWeightScale']):
              self.initHistograms(['CountFullWeightedLHEWeightScale'], self.nLHEScaleWeight)
            for lhe_scale_idx in range(self.nLHEScaleWeight):
              self.histograms['CountFullWeightedLHEWeightScale']['histogram'].Fill(
                float(lhe_scale_idx), genWeight * puWeight * lheTHXWeight * self.clip(LHEScaleWeight[lhe_scale_idx])
              )

          if 'histogram' in self.histograms['CountWeightedLHEWeightScaleNoPU']:
            if not self.isInitialized(['CountWeightedLHEWeightScaleNoPU']):
              self.initHistograms(['CountWeightedLHEWeightScaleNoPU'], self.nLHEScaleWeight)
            for lhe_scale_idx in range(self.nLHEScaleWeight):
              self.histograms['CountWeightedLHEWeightScaleNoPU']['histogram'].Fill(
                float(lhe_scale_idx), genWeight_sign * lheTHXWeight * self.clip(LHEScaleWeight[lhe_scale_idx])
              )
          if 'histogram' in self.histograms['CountFullWeightedLHEWeightScaleNoPU']:
            if not self.isInitialized(['CountFullWeightedLHEWeightScaleNoPU']):
              self.initHistograms(['CountFullWeightedLHEWeightScaleNoPU'], self.nLHEScaleWeight)
            for lhe_scale_idx in range(self.nLHEScaleWeight):
              self.histograms['CountFullWeightedLHEWeightScaleNoPU']['histogram'].Fill(
                float(lhe_scale_idx), genWeight * lheTHXWeight * self.clip(LHEScaleWeight[lhe_scale_idx])
              )
          
          if has_l1Prefire:
            if 'histogram' in self.histograms['CountWeightedLHEWeightScaleL1PrefireNom']:
              if not self.isInitialized(['CountWeightedLHEWeightScaleL1PrefireNom']):
                self.initHistograms(['CountWeightedLHEWeightScaleL1PrefireNom'], self.nLHEScaleWeight)
              for lhe_scale_idx in range(self.nLHEScaleWeight):
                self.histograms['CountWeightedLHEWeightScaleL1PrefireNom']['histogram'].Fill(
                  float(lhe_scale_idx), genWeight_sign * puWeight * lheTHXWeight * l1_nom * self.clip(LHEScaleWeight[lhe_scale_idx])
                )
            if 'histogram' in self.histograms['CountFullWeightedLHEWeightScaleL1PrefireNom']:
              if not self.isInitialized(['CountFullWeightedLHEWeightScaleL1PrefireNom']):
                self.initHistograms(['CountFullWeightedLHEWeightScaleL1PrefireNom'], self.nLHEScaleWeight)
              for lhe_scale_idx in range(self.nLHEScaleWeight):
                self.histograms['CountFullWeightedLHEWeightScaleL1PrefireNom']['histogram'].Fill(
                  float(lhe_scale_idx), genWeight * puWeight * lheTHXWeight * l1_nom * self.clip(LHEScaleWeight[lhe_scale_idx])
                )

            if 'histogram' in self.histograms['CountWeightedLHEWeightScaleNoPUL1PrefireNom']:
              if not self.isInitialized(['CountWeightedLHEWeightScaleNoPUL1PrefireNom']):
                self.initHistograms(['CountWeightedLHEWeightScaleNoPUL1PrefireNom'], self.nLHEScaleWeight)
              for lhe_scale_idx in range(self.nLHEScaleWeight):
                self.histograms['CountWeightedLHEWeightScaleNoPUL1PrefireNom']['histogram'].Fill(
                  float(lhe_scale_idx), genWeight_sign * lheTHXWeight * l1_nom * self.clip(LHEScaleWeight[lhe_scale_idx])
                )
            if 'histogram' in self.histograms['CountFullWeightedLHEWeightScaleNoPUL1PrefireNom']:
              if not self.isInitialized(['CountFullWeightedLHEWeightScaleNoPUL1PrefireNom']):
                self.initHistograms(['CountFullWeightedLHEWeightScaleNoPUL1PrefireNom'], self.nLHEScaleWeight)
              for lhe_scale_idx in range(self.nLHEScaleWeight):
                self.histograms['CountFullWeightedLHEWeightScaleNoPUL1PrefireNom']['histogram'].Fill(
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

all_histograms = [
  'Count',
  'CountWeighted',
  'CountWeightedL1PrefireNom',
  'CountWeightedL1Prefire',
  'CountWeightedNoPU',
  'CountWeightedNoPUL1PrefireNom',
  'CountFullWeighted',
  'CountFullWeightedL1PrefireNom',
  'CountFullWeightedL1Prefire',
  'CountFullWeightedNoPU',
  'CountFullWeightedNoPUL1PrefireNom',
  'CountPosWeight',
  'CountNegWeight',
  'CountWeightedLHEWeightPdf',
  'CountWeightedLHEWeightPdfL1PrefireNom',
  'CountWeightedLHEWeightPdfNoPU',
  'CountWeightedLHEWeightPdfNoPUL1PrefireNom',
  'CountFullWeightedLHEWeightPdf',
  'CountFullWeightedLHEWeightPdfL1PrefireNom',
  'CountFullWeightedLHEWeightPdfNoPU',
  'CountFullWeightedLHEWeightPdfNoPUL1PrefireNom',
  'CountWeightedLHEWeightScale',
  'CountWeightedLHEWeightScaleL1PrefireNom',
  'CountWeightedLHEWeightScaleNoPU',
  'CountWeightedLHEWeightScaleNoPUL1PrefireNom',
  'CountFullWeightedLHEWeightScale',
  'CountFullWeightedLHEWeightScaleL1PrefireNom',
  'CountFullWeightedLHEWeightScaleNoPU',
  'CountFullWeightedLHEWeightScaleNoPUL1PrefireNom',
]

# provide this variable as the 2nd argument to the import option for the nano_postproc.py script
countHistogramAll = lambda : countHistogramProducer(all_histograms)
