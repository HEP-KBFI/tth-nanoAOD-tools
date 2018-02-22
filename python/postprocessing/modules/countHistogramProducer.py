import ROOT
import numpy as np

ROOT.PyConfig.IgnoreCommandLineOptions = True

from PhysicsTools.NanoAODTools.postprocessing.framework.eventloop import Module

class countHistogramProducer(Module):

  def __init__(self, selection):
    self.puWeightName       = 'puWeight'
    self.genWeightName      = 'genWeight'
    self.LHEPdfWeightName   = 'LHEPdfWeight'
    self.LHEScaleWeightName = 'LHEScaleWeight'
    self.nLHEPdfWeight      = 33
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
      histogramParams = self.histograms[histogramName]
      histogramParams['histogram'] = ROOT.TH1F(
        histogramName, histogramName,
        histogramParams['bins'], histogramParams['min'], histogramParams['max']
      )

  def beginJob(self):
    pass

  def endJob(self):
    pass

  def beginFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
    self.out = wrappedOutputTree
    pass

  def endFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
    outputFile.cd()

    for histogramName in self.histograms:
      if 'histogram' in self.histograms[histogramName]:
        self.histograms[histogramName]['histogram'].Write()

  def analyze(self, event):
    if 'histogram' in self.histograms['Count']:
      self.histograms['Count']['histogram'].Fill(1, 1)

    if hasattr(event, self.puWeightName) and \
       hasattr(event, self.genWeightName) and \
       hasattr(event, self.LHEPdfWeightName) and \
       hasattr(event, self.LHEScaleWeightName):

      puWeight       = getattr(event, self.puWeightName)
      genWeight      = getattr(event, self.genWeightName)
      LHEPdfWeight   = getattr(event, self.LHEPdfWeightName)
      LHEScaleWeight = getattr(event, self.LHEScaleWeightName)

      genWeight_sign  = np.sign(genWeight)
      countFullWeight = genWeight * puWeight

      if len(LHEPdfWeight) != self.nLHEPdfWeight:
        raise ValueError(
          "The length of '%s' array (= %i) does not match to the expected length of %i" % \
          (self.LHEPdfWeightName, len(LHEPdfWeight), self.nLHEPdfWeight)
        )

      if len(LHEScaleWeight) != self.nLHEScaleWeight:
        raise ValueError(
          "The length of '%s' array (= %i) does not match to the expected length of %i" % \
          (self.LHEScaleWeightName, len(LHEScaleWeight), self.nLHEScaleWeight)
        )

      if 'histogram' in self.histograms['CountWeighted']:
        self.histograms['CountWeighted']['histogram'].Fill(1, genWeight_sign * puWeight)
      if 'histogram' in self.histograms['CountFullWeighted']:
        self.histograms['CountFullWeighted']['histogram'].Fill(1, countFullWeight)
      if 'histogram' in self.histograms['CountPosWeight']:
        self.histograms['CountPosWeight']['histogram'].Fill(1, 1 if genWeight_sign > 0 else 0)
      if 'histogram' in self.histograms['CountNegWeight']:
        self.histograms['CountNegWeight']['histogram'].Fill(1, 1 if genWeight_sign < 0 else 0)
      if 'histogram' in self.histograms['CountWeightedLHEWeightPdf']:
        for lhe_pdf_idx in range(self.nLHEPdfWeight):
          self.histograms['CountWeightedLHEWeightPdf']['histogram'].Fill(
            float(lhe_pdf_idx), countFullWeight * LHEPdfWeight[lhe_pdf_idx]
          )
      if 'histogram' in self.histograms['CountWeightedLHEWeightScale']:
        for lhe_scale_idx in range(self.nLHEScaleWeight):
          self.histograms['CountWeightedLHEWeightScale']['histogram'].Fill(
            float(lhe_scale_idx), countFullWeight * LHEScaleWeight[lhe_scale_idx]
          )

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
countHistogramAll                         = lambda : countHistogramProducer(all_histograms)
countHistogramCount                       = lambda : countHistogramProducer('Count')
countHistogramCountWeighted               = lambda : countHistogramProducer('CountWeighted')
countHistogramCountFullWeighted           = lambda : countHistogramProducer('CountFullWeighted')
countHistogramCountPosWeight              = lambda : countHistogramProducer('CountPosWeight')
countHistogramCountNegWeight              = lambda : countHistogramProducer('CountNegWeight')
countHistogramCountWeightedLHEWeightPdf   = lambda : countHistogramProducer('CountWeightedLHEWeightPdf')
countHistogramCountWeightedLHEWeightScale = lambda : countHistogramProducer('CountWeightedLHEWeightScale')
