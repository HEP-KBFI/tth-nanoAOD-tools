import ROOT
import numpy as np

ROOT.PyConfig.IgnoreCommandLineOptions = True

from PhysicsTools.NanoAODTools.postprocessing.framework.eventloop import Module

class countHistogramProducer(Module):

  def __init__(self, era, selection):
    self.era                = era
    self.puWeightName       = 'puWeight'
    self.puWeightName_up    = '%sUp' % self.puWeightName
    self.puWeightName_down  = '%sDown' % self.puWeightName
    self.genWeightName      = 'genWeight'
    self.lheTHXWeightName   = 'LHEWeight_rwgt_12' # Corresponds to SM in THQ/THW samples
    self.LHEPdfWeightName   = 'LHEPdfWeight'
    self.LHEScaleWeightName = 'LHEScaleWeight'
    self.nLHEPdfWeight      = 101
    self.nLHEScaleWeight    = 9

    self.histograms = {
      'Count'                      : { 'bins' : 1, 'min' :  0.,  'max' : 2.,  'title' : 'sum(1)',                                        },
      'CountWeighted'              : { 'bins' : 3, 'min' : -0.5, 'max' : 2.5, 'title' : 'sum(sgn(gen) * PU(central,up,down) * LHE(tH))', },
      'CountFullWeighted'          : { 'bins' : 3, 'min' : -0.5, 'max' : 2.5, 'title' : 'sum(gen * PU(central,up,down) * LHE(tH))',      },
      'CountWeightedNoPU'          : { 'bins' : 1, 'min' :  0.,  'max' : 2.,  'title' : 'sum(sgn(gen) * LHE(th))',                       },
      'CountFullWeightedNoPU'      : { 'bins' : 1, 'min' :  0.,  'max' : 2.,  'title' : 'sum(gen * LHE(th))',                            },
      'CountPosWeight'             : { 'bins' : 1, 'min' :  0.,  'max' : 2.,  'title' : 'sum(gen > 0)',                                  },
      'CountNegWeight'             : { 'bins' : 1, 'min' :  0.,  'max' : 2.,  'title' : 'sum(gen < 0)',                                  },
      'CountWeightedLHEWeightPdf'  : {
        'bins'  : self.nLHEPdfWeight,
        'min'   : -0.5,
        'max'   : self.nLHEPdfWeight - 0.5,
        'title' : 'sum(sgn(gen) * PU(central) * LHE(th) * LHE(pdf))',
      },
      'CountWeightedLHEWeightPdfNoPU': {
        'bins'  : self.nLHEPdfWeight,
        'min'   : -0.5,
        'max'   : self.nLHEPdfWeight - 0.5,
        'title' : 'sum(sgn(gen) * LHE(th) * LHE(pdf))',
      },
      'CountFullWeightedLHEWeightPdf'  : {
        'bins'  : self.nLHEPdfWeight,
        'min'   : -0.5,
        'max'   : self.nLHEPdfWeight - 0.5,
        'title' : 'sum(gen * PU(central) * LHE(th) * LHE(pdf))',
      },
      'CountFullWeightedLHEWeightPdfNoPU': {
        'bins'  : self.nLHEPdfWeight,
        'min'   : -0.5,
        'max'   : self.nLHEPdfWeight - 0.5,
        'title' : 'sum(gen * LHE(th) * LHE(pdf))',
      },
      'CountWeightedLHEWeightScale': {
        'bins'  : self.nLHEScaleWeight,
        'min'   : -0.5,
        'max'   : self.nLHEScaleWeight - 0.5,
        'title' : 'sum(sgn(gen) * PU(central) * LHE(th) * LHE(scale))',
      },
      'CountWeightedLHEWeightScaleNoPU': {
        'bins'  : self.nLHEScaleWeight,
        'min'   : -0.5,
        'max'   : self.nLHEScaleWeight - 0.5,
        'title' : 'sum(sgn(gen) * LHE(th) * LHE(scale))',
      },
      'CountFullWeightedLHEWeightScale': {
        'bins'  : self.nLHEScaleWeight,
        'min'   : -0.5,
        'max'   : self.nLHEScaleWeight - 0.5,
        'title' : 'sum(gen * PU(central) * LHE(th) * LHE(scale))',
      },
      'CountFullWeightedLHEWeightScaleNoPU': {
        'bins'  : self.nLHEScaleWeight,
        'min'   : -0.5,
        'max'   : self.nLHEScaleWeight - 0.5,
        'title' : 'sum(gen * LHE(th) * LHE(scale))',
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

        if hasattr(event, self.lheTHXWeightName):
          lheTHXWeight = getattr(event, self.lheTHXWeightName)
        else:
          if not self.isPrinted[self.lheTHXWeightName]:
            self.isPrinted[self.lheTHXWeightName] = True
            print('Missing branch: %s' % self.lheTHXWeightName)
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
  'CountWeightedNoPU',
  'CountFullWeighted',
  'CountFullWeightedNoPU',
  'CountPosWeight',
  'CountNegWeight',
  'CountWeightedLHEWeightPdf',
  'CountWeightedLHEWeightPdfNoPU',
  'CountFullWeightedLHEWeightPdf',
  'CountFullWeightedLHEWeightPdfNoPU',
  'CountWeightedLHEWeightScale',
  'CountWeightedLHEWeightScaleNoPU',
  'CountFullWeightedLHEWeightScale',
  'CountFullWeightedLHEWeightScaleNoPU',
]

# provide this variable as the 2nd argument to the import option for the nano_postproc.py script
countHistogramAll_2016                                 = lambda : countHistogramProducer('2016', all_histograms)
countHistogramCount_2016                               = lambda : countHistogramProducer('2016', ['Count'])
countHistogramCountWeighted_2016                       = lambda : countHistogramProducer('2016', ['CountWeighted'])
countHistogramCountWeightedNoPU_2016                   = lambda : countHistogramProducer('2016', ['CountWeightedNoPU'])
countHistogramCountFullWeighted_2016                   = lambda : countHistogramProducer('2016', ['CountFullWeighted'])
countHistogramCountFullWeightedNoPU_2016               = lambda : countHistogramProducer('2016', ['CountFullWeightedNoPU'])
countHistogramCountPosWeight_2016                      = lambda : countHistogramProducer('2016', ['CountPosWeight'])
countHistogramCountNegWeight_2016                      = lambda : countHistogramProducer('2016', ['CountNegWeight'])
countHistogramCountWeightedLHEWeightPdf_2016           = lambda : countHistogramProducer('2016', ['CountWeightedLHEWeightPdf'])
countHistogramCountWeightedLHEWeightPdfNoPU_2016       = lambda : countHistogramProducer('2016', ['CountWeightedLHEWeightPdfNoPU'])
countHistogramCountFullWeightedLHEWeightPdf_2016       = lambda : countHistogramProducer('2016', ['CountFullWeightedLHEWeightPdf'])
countHistogramCountFullWeightedLHEWeightPdfNoPU_2016   = lambda : countHistogramProducer('2016', ['CountFullWeightedLHEWeightPdfNoPU'])
countHistogramCountWeightedLHEWeightScale_2016         = lambda : countHistogramProducer('2016', ['CountWeightedLHEWeightScale'])
countHistogramCountWeightedLHEWeightScaleNoPU_2016     = lambda : countHistogramProducer('2016', ['CountWeightedLHEWeightScaleNoPU'])
countHistogramCountFullWeightedLHEWeightScale_2016     = lambda : countHistogramProducer('2016', ['CountFullWeightedLHEWeightScale'])
countHistogramCountFullWeightedLHEWeightScaleNoPU_2016 = lambda : countHistogramProducer('2016', ['CountFullWeightedLHEWeightScaleNoPU'])

countHistogramAll_2017                                 = lambda : countHistogramProducer('2017', all_histograms)
countHistogramCount_2017                               = lambda : countHistogramProducer('2017', ['Count'])
countHistogramCountWeighted_2017                       = lambda : countHistogramProducer('2017', ['CountWeighted'])
countHistogramCountWeightedNoPU_2017                   = lambda : countHistogramProducer('2017', ['CountWeightedNoPU'])
countHistogramCountFullWeighted_2017                   = lambda : countHistogramProducer('2017', ['CountFullWeighted'])
countHistogramCountFullWeightedNoPU_2017               = lambda : countHistogramProducer('2017', ['CountFullWeightedNoPU'])
countHistogramCountPosWeight_2017                      = lambda : countHistogramProducer('2017', ['CountPosWeight'])
countHistogramCountNegWeight_2017                      = lambda : countHistogramProducer('2017', ['CountNegWeight'])
countHistogramCountWeightedLHEWeightPdf_2017           = lambda : countHistogramProducer('2017', ['CountWeightedLHEWeightPdf'])
countHistogramCountWeightedLHEWeightPdfNoPU_2017       = lambda : countHistogramProducer('2017', ['CountWeightedLHEWeightPdfNoPU'])
countHistogramCountFullWeightedLHEWeightPdf_2017       = lambda : countHistogramProducer('2017', ['CountFullWeightedLHEWeightPdf'])
countHistogramCountFullWeightedLHEWeightPdfNoPU_2017   = lambda : countHistogramProducer('2017', ['CountFullWeightedLHEWeightPdfNoPU'])
countHistogramCountWeightedLHEWeightScale_2017         = lambda : countHistogramProducer('2017', ['CountWeightedLHEWeightScale'])
countHistogramCountWeightedLHEWeightScaleNoPU_2017     = lambda : countHistogramProducer('2017', ['CountWeightedLHEWeightScaleNoPU'])
countHistogramCountFullWeightedLHEWeightScale_2017     = lambda : countHistogramProducer('2017', ['CountFullWeightedLHEWeightScale'])
countHistogramCountFullWeightedLHEWeightScaleNoPU_2017 = lambda : countHistogramProducer('2017', ['CountFullWeightedLHEWeightScaleNoPU'])
