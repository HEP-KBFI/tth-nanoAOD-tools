from PhysicsTools.NanoAODTools.postprocessing.modules.btv.btagSFProducer import btagSFProducer

#NOTE assumes FullSim; no support for FastSim implemented, yet

class btagSFProducer_explicitBranchNames(btagSFProducer):
  def __init__(self, era, algo, verbose = 0):
    btagSFProducer.__init__(self, era, algo, None, verbose)

    self.branchName_prefix       = "Jet_btagSF_%s" % self.algo
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

btagSF_deep_2016     = lambda : btagSFProducer_explicitBranchNames('2016', 'deepcsv')
btagSF_deepFlav_2016 = lambda : btagSFProducer_explicitBranchNames('2016', 'deepjet')
btagSF_csvv2_2016    = lambda : btagSFProducer_explicitBranchNames('2016', 'csvv2') # legacy
btagSF_cmva_2016     = lambda : btagSFProducer_explicitBranchNames('2016', 'cmva') # legacy
