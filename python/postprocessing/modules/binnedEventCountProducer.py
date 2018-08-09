import ROOT
import numpy as np
import collections
import ast
import array

ROOT.PyConfig.IgnoreCommandLineOptions = True

from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import Collection
from PhysicsTools.NanoAODTools.postprocessing.framework.eventloop import Module

class binnedEventCountProducer(Module):

  def __init__(self, outFn, x_var, x_binning, y_var = '', y_binning = [], mll_binning = []):
    self.outFn = outFn
    self.x_var = x_var
    self.x_binning = self.assign_list(x_binning)
    self.y_var = y_var
    self.y_binning = self.assign_list(y_binning)
    self.mll_binning = self.assign_list(mll_binning)

    print('x-var = %s; binning = %s' % (self.x_var, str(self.x_binning)))
    print('y-var = %s; binning = %s' % (self.y_var, str(self.y_binning)))
    print('mll binning = %s' % str(self.mll_binning))
    print('Is 2D? %s' % str(bool(self.y_var)))
    print('Bin by mll? %s' % str(bool(self.mll_binning)))

    assert(self.x_var and self.x_binning)
    assert((self.y_var and self.y_binning) or (not self.y_var and not self.y_binning))
    assert(len(self.mll_binning) in [0, 2])
    assert(self.outFn.endswith('.root'))

    self.is2D = self.x_var != '' and self.y_var != ''
    assert(self.x_var != self.y_var)

    self.x_binning_arr = array.array('d', self.x_binning)
    self.y_binning_arr = array.array('d', self.y_binning) if self.is2D else None

    self.required_nLHEWeightScale = 9

    self.brName_genWeight       = 'genWeight'
    self.brName_puWeight        = 'puWeight'
    self.brName_puWeightUp      = '%sUp' % self.brName_puWeight
    self.brName_puWeightDown    = '%sDown' % self.brName_puWeight
    self.brName_LHEScaleWeight  = 'LHEScaleWeight'
    self.brName_nLHEScaleWeight = 'n%s' % self.brName_LHEScaleWeight
    self.brName_LHEPart         = 'LHEPart'

    self.histograms = collections.OrderedDict()

    self.count_keys = collections.OrderedDict([
      ('Count',                               { 'nbins' :                             1, 'title' : 'sum(1)',                                   }),
      ('CountFullWeighted',                   { 'nbins' :                             3, 'title' : 'sum(gen * PU(central,up,down))',           }),
      ('CountWeighted',                       { 'nbins' :                             3, 'title' : 'sum(sgn(gen) * PU(central,up,down))',      }),
      ('CountFullWeightedNoPU',               { 'nbins' :                             1, 'title' : 'sum(gen)',                                 }),
      ('CountPosWeight',                      { 'nbins' :                             1, 'title' : 'sum(gen > 0)'                              }),
      ('CountNegWeight',                      { 'nbins' :                             1, 'title' : 'sum(gen < 0)'                              }),
      ('CountWeightedNoPU',                   { 'nbins' :                             1, 'title' : 'sum(sgn(gen))',                            }),
      ('CountWeightedLHEWeightScale',         { 'nbins' : self.required_nLHEWeightScale, 'title' : 'sum(sgn(gen) * PU(central) * LHE(scale))', }),
      ('CountWeightedLHEWeightScaleNoPU',     { 'nbins' : self.required_nLHEWeightScale, 'title' : 'sum(sgn(gen) * LHE(scale))',               }),
      ('CountFullWeightedLHEWeightScale',     { 'nbins' : self.required_nLHEWeightScale, 'title' : 'sum(gen * PU(central) * LHE(scale))',      }),
      ('CountFullWeightedLHEWeightScaleNoPU', { 'nbins' : self.required_nLHEWeightScale, 'title' : 'sum(gen * LHE(scale))',                    }),
    ])

  def assign_list(self, val, sort = True):
    val_arrayed = []
    if type(val) == list:
      val_arrayed = val
    elif type(val) == str:
      val_arrayed = ast.literal_eval(val.replace('|', ','))
    else:
      raise ValueError('Cannot convert to list: %s' % str(val))
    if sort:
      return list(sorted(val_arrayed))
    return val_arrayed

  def clip(self, value, min_val = -10., max_val = 10.):
    return min(max(value, min_val), max_val)

  def get_mll_str(self, val):
    if val < self.mll_binning[0]:
      return 'lt%s' % str(int(self.mll_binning[0]))
    elif self.mll_binning[0] <= val < self.mll_binning[1]:
      return '%sto%s' % (str(int(self.mll_binning[0])), str(int(self.mll_binning[1])))
    elif val >= self.mll_binning[1]:
      return 'gt%s' % (str(int(self.mll_binning[1])))
    else:
      raise RuntimeError('Unexpected value: %f (%s)' % (val, self.mll_binning))

  def create_histogram(self, key, title):
    if self.is2D:
      self.histograms[key] = ROOT.TH2D(
        key, title,
        len(self.x_binning_arr) - 1, self.x_binning_arr,
        len(self.y_binning_arr) - 1, self.y_binning_arr
      )
      for bin_idx in range(len(self.x_binning_arr) - 1):
        self.histograms[key].GetXaxis().SetBinLabel(
          bin_idx + 1,
          '%d <= %s < %d' % (
            self.x_binning_arr[bin_idx], self.x_var, self.x_binning_arr[bin_idx + 1]
          )
        )
      for bin_idx in range(len(self.y_binning_arr) - 1):
        self.histograms[key].GetYaxis().SetBinLabel(
          bin_idx + 1,
          '%d <= %s < %d' % (
            self.y_binning_arr[bin_idx], self.y_var, self.y_binning_arr[bin_idx + 1]
          )
        )
      self.histograms[key].SetXTitle(self.x_var)
      self.histograms[key].SetYTitle(self.y_var)
    else:
      self.histograms[key] = ROOT.TH1D(key, title, len(self.x_binning_arr) - 1, self.x_binning_arr)
      for bin_idx in range(len(self.x_binning_arr) - 1):
        self.histograms[key].GetXaxis().SetBinLabel(
          bin_idx + 1,
          '%d <= %s < %d' % (
            self.x_binning_arr[bin_idx], self.x_var, self.x_binning_arr[bin_idx + 1]
          )
        )
      self.histograms[key].SetXTitle(self.x_var)


  def beginJob(self):
    if self.mll_binning:
      assert(len(self.mll_binning) == 2)
      for val in [self.mll_binning[0] - 1., (self.mll_binning[0] + self.mll_binning[1]) / 2., self.mll_binning[1] + 1]:
        for count_key, count_settings in self.count_keys.items():
          for histogram_idx in range(count_settings['nbins']):
            mll_str = self.get_mll_str(val)
            key = '%s_%d_%s' % (count_key, histogram_idx, mll_str)
            title = count_settings['title']
            if count_settings['nbins'] > 1:
              title += ' [bin = %d]' % histogram_idx
            title += ' (mll %s)' % mll_str
            self.create_histogram(key, title)
    else:
      for count_key, count_settings in self.count_keys.items():
        for histogram_idx in range(count_settings['nbins']):
          key = '%s_%d' % (count_key, histogram_idx)
          title = count_settings['title']
          if count_settings['nbins'] > 1:
            title += ' [bin = %d]' % histogram_idx
          self.create_histogram(key, title)

  def endJob(self):
    pass

  def beginFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
    self.out = wrappedOutputTree

  def endFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
    outputFile = ROOT.TFile.Open(self.outFn, 'recreate')
    outputFile.cd()
    for histogram in self.histograms.values():
      histogram.Write()
    outputFile.Close()

  def analyze(self, event):
    if self.mll_binning:
      invmass = []
      pdgIds = []
      LHEPart_collection = Collection(event, self.brName_LHEPart)
      for LHEPart in LHEPart_collection:
        if abs(LHEPart.pdgId) in [ 11, 13, 15 ]:
          lv = ROOT.TLorentzVector()
          lv.SetPtEtaPhiM(LHEPart.pt, LHEPart.eta, LHEPart.phi, LHEPart.mass)
          invmass.append(lv)
          pdgIds.append(LHEPart.pdgId)
      if len(invmass) != 2 or sum(pdgIds) != 0:
        print(
          'Warning: event %s does not contain two LHE leptons' % \
          ':'.join(map(lambda x: str(getattr(event, x)), [ 'run', 'luminosityBlock', 'event' ]))
        )
        return True
      mll = (invmass[0] + invmass[1]).M()
      suffix = suffix = '_%s' % self.get_mll_str(mll)
    else:
      suffix = ''

    genWeight    = getattr(event, self.brName_genWeight)
    puWeight     = getattr(event, self.brName_puWeight)
    puWeightUp   = getattr(event, self.brName_puWeightUp)
    puWeightDown = getattr(event, self.brName_puWeightDown)

    nLHEScaleWeight = getattr(event, self.brName_nLHEScaleWeight)
    if(nLHEScaleWeight != self.required_nLHEWeightScale):
      print(
        'Warning: event %s does not contain exactly %d LHE scale weights' % (
          ':'.join(map(lambda x: str(getattr(event, x)), [ 'run', 'luminosityBlock', 'event' ])),
          self.required_nLHEWeightScale
        )
      )
      return True
    LHEScaleWeight = map(self.clip, getattr(event, self.brName_LHEScaleWeight))

    genWeight_sign = np.sign(genWeight)

    counts = {
      'Count_0'                 : 1.,
      'CountWeighted_0'         : genWeight_sign * puWeight,
      'CountWeighted_1'         : genWeight_sign * puWeightUp,
      'CountWeighted_2'         : genWeight_sign * puWeightDown,
      'CountFullWeighted_0'     : genWeight * puWeight,
      'CountFullWeighted_1'     : genWeight * puWeightUp,
      'CountFullWeighted_2'     : genWeight * puWeightDown,
      'CountWeightedNoPU_0'     : genWeight_sign,
      'CountFullWeightedNoPU_0' : genWeight,
      'CountPosWeight_0'        : genWeight * (genWeight_sign > 0),
      'CountNegWeight_0'        : genWeight * (genWeight_sign < 0),
    }
    for i in range(nLHEScaleWeight):
      counts['CountWeightedLHEWeightScale_%d'         % i] = genWeight_sign * puWeight * LHEScaleWeight[i]
      counts['CountWeightedLHEWeightScaleNoPU_%d'     % i] = genWeight_sign            * LHEScaleWeight[i]
      counts['CountFullWeightedLHEWeightScale_%d'     % i] = genWeight      * puWeight * LHEScaleWeight[i]
      counts['CountFullWeightedLHEWeightScaleNoPU_%d' % i] = genWeight                 * LHEScaleWeight[i]

    x_val = float(getattr(event, self.x_var))
    y_val = float(getattr(event, self.y_var)) if self.is2D else None
    for count_key in counts:
      key = count_key + suffix
      evtWeight = counts[count_key]
      if self.is2D:
        self.histograms[key].Fill(x_val, y_val, evtWeight)
      else:
        self.histograms[key].Fill(x_val, evtWeight)

    return True

# provide this variable as the 2nd argument to the import option for the nano_postproc.py script
binnedEventCounter = lambda outFn, x_var, x_binning, y_var, y_binning, mll_binning: \
   binnedEventCountProducer(outFn, x_var, x_binning, y_var, y_binning, mll_binning)
