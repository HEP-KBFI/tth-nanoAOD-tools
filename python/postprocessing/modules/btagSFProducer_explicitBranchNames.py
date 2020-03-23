from PhysicsTools.NanoAODTools.postprocessing.modules.btv.btagSFProducer import btagSFProducer

#NOTE assumes FullSim; no support for FastSim implemented, yet

class btagSFProducer_explicitBranchNames(btagSFProducer):
  def __init__(self, era, algo, jetName = 'Jet', verbose = 0):
    btagSFProducer.__init__(self, era, algo, None, verbose, jetName)

    self.branchName_prefix       = "%s_btagSF_%s" % (self.jetCollectionName, self.algo)
    self.branchName_shape_prefix = '%s_shape'      % self.branchName_prefix

    self.branchNames_central_and_systs = {}
    for central_or_syst in self.central_and_systs:
      if central_or_syst == "central":
        self.branchNames_central_and_systs[central_or_syst] = self.branchName_prefix
      else:
        self.branchNames_central_and_systs[central_or_syst] = "%s_%s" % (self.branchName_prefix, central_or_syst)

    self.branchNames_central_and_systs_shape_corr = {}
    for central_or_syst in self.central_and_systs_shape_corr:
      if central_or_syst == "central":
        self.branchNames_central_and_systs_shape_corr[central_or_syst] = self.branchName_shape_prefix
      else:
        self.branchNames_central_and_systs_shape_corr[central_or_syst] = "%s_%s" % (self.branchName_shape_prefix, central_or_syst)

btagSF_deep_2018     = lambda : btagSFProducer_explicitBranchNames('2018', 'deepcsv')
btagSF_deepFlav_2018 = lambda : btagSFProducer_explicitBranchNames('2018', 'deepjet')

btagSF_deep_2017     = lambda : btagSFProducer_explicitBranchNames('2017', 'deepcsv')
btagSF_deepFlav_2017 = lambda : btagSFProducer_explicitBranchNames('2017', 'deepjet')
btagSF_csvv2_2017    = lambda : btagSFProducer_explicitBranchNames('2017', 'csvv2') # legacy

btagSF_deep_2016_TuneCP5     = lambda : btagSFProducer_explicitBranchNames('2016_TuneCP5', 'deepcsv')
btagSF_deepFlav_2016_TuneCP5 = lambda : btagSFProducer_explicitBranchNames('2016_TuneCP5', 'deepjet')
btagSF_deep_2016             = lambda : btagSFProducer_explicitBranchNames('2016',         'deepcsv')
btagSF_deepFlav_2016         = lambda : btagSFProducer_explicitBranchNames('2016',         'deepjet')
btagSF_csvv2_2016            = lambda : btagSFProducer_explicitBranchNames('2016',         'csvv2') # legacy
btagSF_cmva_2016             = lambda : btagSFProducer_explicitBranchNames('2016',         'cmva') # legacy

btagSF_deep_2018_LSLoose     = lambda : btagSFProducer_explicitBranchNames('2018', 'deepcsv', 'JetAK4LSLoose')
btagSF_deepFlav_2018_LSLoose = lambda : btagSFProducer_explicitBranchNames('2018', 'deepjet', 'JetAK4LSLoose')

btagSF_deep_2017_LSLoose     = lambda : btagSFProducer_explicitBranchNames('2017', 'deepcsv', 'JetAK4LSLoose')
btagSF_deepFlav_2017_LSLoose = lambda : btagSFProducer_explicitBranchNames('2017', 'deepjet', 'JetAK4LSLoose')
btagSF_csvv2_2017_LSLoose    = lambda : btagSFProducer_explicitBranchNames('2017', 'csvv2', 'JetAK4LSLoose') # legacy

btagSF_deep_2016_TuneCP5_LSLoose     = lambda : btagSFProducer_explicitBranchNames('2016_TuneCP5', 'deepcsv', 'JetAK4LSLoose')
btagSF_deepFlav_2016_TuneCP5_LSLoose = lambda : btagSFProducer_explicitBranchNames('2016_TuneCP5', 'deepjet', 'JetAK4LSLoose')
btagSF_deep_2016_LSLoose             = lambda : btagSFProducer_explicitBranchNames('2016',         'deepcsv', 'JetAK4LSLoose')
btagSF_deepFlav_2016_LSLoose         = lambda : btagSFProducer_explicitBranchNames('2016',         'deepjet', 'JetAK4LSLoose')
btagSF_csvv2_2016_LSLoose            = lambda : btagSFProducer_explicitBranchNames('2016',         'csvv2', 'JetAK4LSLoose') # legacy
btagSF_cmva_2016_LSLoose             = lambda : btagSFProducer_explicitBranchNames('2016',         'cmva', 'JetAK4LSLoose') # legacy

btagSF_deep_2018_subjet = lambda: btagSFProducer_explicitBranchNames('2018', 'deepcsv', 'SubJet')
btagSF_deep_2017_subjet = lambda: btagSFProducer_explicitBranchNames('2017', 'deepcsv', 'SubJet')
btagSF_deep_2016_subjet = lambda: btagSFProducer_explicitBranchNames('2016', 'deepcsv', 'SubJet')

btagSF_deep_2018_subjet_LSLoose = lambda: btagSFProducer_explicitBranchNames('2018', 'deepcsv', 'SubJetAK8LSLoose')
btagSF_deep_2017_subjet_LSLoose = lambda: btagSFProducer_explicitBranchNames('2017', 'deepcsv', 'SubJetAK8LSLoose')
btagSF_deep_2016_subjet_LSLoose = lambda: btagSFProducer_explicitBranchNames('2016', 'deepcsv', 'SubJetAK8LSLoose')
