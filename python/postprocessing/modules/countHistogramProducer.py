import ROOT
import numpy as np

ROOT.PyConfig.IgnoreCommandLineOptions = True

from PhysicsTools.NanoAODTools.postprocessing.framework.eventloop import Module

class countHistogramProducer(Module):

  def __init__(self, era, selection):
    self.era                = era
    self.puWeightName       = 'puWeight'
    self.genWeightName      = 'genWeight'
    self.LHEPdfWeightName   = 'LHEPdfWeight'
    self.LHEScaleWeightName = 'LHEScaleWeight'
    if self.era == '2016':
      self.nLHEPdfWeight = 101
    elif self.era == '2017':
      self.nLHEPdfWeight = 33
    else:
      raise ValueError('Invalid era: %s' % self.era)
    self.nLHEScaleWeight    = 9

    self.histograms = {
      'Count'                      : { 'bins' : 1, 'min' : 0., 'max' : 2., },
      'CountWeighted'              : { 'bins' : 1, 'min' : 0., 'max' : 2., },
      'CountFullWeighted'          : { 'bins' : 1, 'min' : 0., 'max' : 2., },
      'CountPosWeight'             : { 'bins' : 1, 'min' : 0., 'max' : 2., },
      'CountNegWeight'             : { 'bins' : 1, 'min' : 0., 'max' : 2., },
      'CountWeightedLHEWeightPdf'  : {
        'bins' : self.nLHEPdfWeight,
        'min'  : -0.5,
        'max'  : self.nLHEPdfWeight - 0.5,
      },
      'CountWeightedLHEWeightScale': {
        'bins' : self.nLHEScaleWeight,
        'min'  : -0.5,
        'max'  : self.nLHEScaleWeight - 0.5,
      },
    }

    for histogramName in selection:
      if histogramName not in self.histograms:
        raise ValueError("Invalid histogram requested: %s" % histogramName)
      self.histograms[histogramName]['histogram'] = None

    self.isPrinted = {
      branchName : False for branchName in [
        self.puWeightName, self.genWeightName, self.LHEPdfWeightName, self.LHEScaleWeightName
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
        histogramName, histogramName,
        histogramParams['bins'], histogramParams['min'], histogramParams['max']
      )

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
        puWeight = getattr(event, self.puWeightName)
        countFullWeight = genWeight * puWeight

        if 'histogram' in self.histograms['CountWeighted']:
          if not self.isInitialized(['CountWeighted']):
            self.initHistograms(['CountWeighted'])
          self.histograms['CountWeighted']['histogram'].Fill(1, genWeight_sign * puWeight)
        if 'histogram' in self.histograms['CountFullWeighted']:
          if not self.isInitialized(['CountFullWeighted']):
            self.initHistograms(['CountFullWeighted'])
          self.histograms['CountFullWeighted']['histogram'].Fill(1, countFullWeight)

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
                float(lhe_pdf_idx), countFullWeight * LHEPdfWeight[lhe_pdf_idx]
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
                float(lhe_scale_idx), countFullWeight * LHEScaleWeight[lhe_scale_idx]
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
  'CountFullWeighted',
  'CountPosWeight',
  'CountNegWeight',
  'CountWeightedLHEWeightPdf',
  'CountWeightedLHEWeightScale',
]

# provide this variable as the 2nd argument to the import option for the nano_postproc.py script
countHistogramAll_2016                         = lambda : countHistogramProducer('2016', all_histograms)
countHistogramCount_2016                       = lambda : countHistogramProducer('2016', ['Count'])
countHistogramCountWeighted_2016               = lambda : countHistogramProducer('2016', ['CountWeighted'])
countHistogramCountFullWeighted_2016           = lambda : countHistogramProducer('2016', ['CountFullWeighted'])
countHistogramCountPosWeight_2016              = lambda : countHistogramProducer('2016', ['CountPosWeight'])
countHistogramCountNegWeight_2016              = lambda : countHistogramProducer('2016', ['CountNegWeight'])
countHistogramCountWeightedLHEWeightPdf_2016   = lambda : countHistogramProducer('2016', ['CountWeightedLHEWeightPdf'])
countHistogramCountWeightedLHEWeightScale_2016 = lambda : countHistogramProducer('2016', ['CountWeightedLHEWeightScale'])

countHistogramAll_2017                         = lambda : countHistogramProducer('2017', all_histograms)
countHistogramCount_2017                       = lambda : countHistogramProducer('2017', ['Count'])
countHistogramCountWeighted_2017               = lambda : countHistogramProducer('2017', ['CountWeighted'])
countHistogramCountFullWeighted_2017           = lambda : countHistogramProducer('2017', ['CountFullWeighted'])
countHistogramCountPosWeight_2017              = lambda : countHistogramProducer('2017', ['CountPosWeight'])
countHistogramCountNegWeight_2017              = lambda : countHistogramProducer('2017', ['CountNegWeight'])
countHistogramCountWeightedLHEWeightPdf_2017   = lambda : countHistogramProducer('2017', ['CountWeightedLHEWeightPdf'])
countHistogramCountWeightedLHEWeightScale_2017 = lambda : countHistogramProducer('2017', ['CountWeightedLHEWeightScale'])
