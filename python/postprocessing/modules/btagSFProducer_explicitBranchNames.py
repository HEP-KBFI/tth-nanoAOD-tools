from PhysicsTools.NanoAODTools.postprocessing.modules.btv.btagSFProducer import btagSFProducer

btagSF_deep_2018     = lambda : btagSFProducer(era = '2018', algo = 'deepcsv')
btagSF_deepFlav_2018 = lambda : btagSFProducer(era = '2018', algo = 'deepjet')

btagSF_deep_2017     = lambda : btagSFProducer(era = '2017', algo = 'deepcsv')
btagSF_deepFlav_2017 = lambda : btagSFProducer(era = '2017', algo = 'deepjet')
btagSF_csvv2_2017    = lambda : btagSFProducer(era = '2017', algo = 'csvv2') # legacy

btagSF_deep_2016_TuneCP5     = lambda : btagSFProducer(era = '2016_TuneCP5', algo = 'deepcsv')
btagSF_deepFlav_2016_TuneCP5 = lambda : btagSFProducer(era = '2016_TuneCP5', algo = 'deepjet')
btagSF_deep_2016             = lambda : btagSFProducer(era = '2016',         algo = 'deepcsv')
btagSF_deepFlav_2016         = lambda : btagSFProducer(era = '2016',         algo = 'deepjet')
btagSF_csvv2_2016            = lambda : btagSFProducer(era = '2016',         algo = 'csvv2') # legacy
btagSF_cmva_2016             = lambda : btagSFProducer(era = '2016',         algo = 'cmva') # legacy

btagSF_deep_2018_LSLoose     = lambda : btagSFProducer(era = '2018', algo = 'deepcsv', jetCollectionName = 'JetAK4LSLoose')
btagSF_deepFlav_2018_LSLoose = lambda : btagSFProducer(era = '2018', algo = 'deepjet', jetCollectionName = 'JetAK4LSLoose')

btagSF_deep_2017_LSLoose     = lambda : btagSFProducer(era = '2017', algo = 'deepcsv', jetCollectionName = 'JetAK4LSLoose')
btagSF_deepFlav_2017_LSLoose = lambda : btagSFProducer(era = '2017', algo = 'deepjet', jetCollectionName = 'JetAK4LSLoose')
btagSF_csvv2_2017_LSLoose    = lambda : btagSFProducer(era = '2017', algo = 'csvv2',   jetCollectionName = 'JetAK4LSLoose') # legacy

btagSF_deep_2016_TuneCP5_LSLoose     = lambda : btagSFProducer(era = '2016_TuneCP5', algo = 'deepcsv', jetCollectionName = 'JetAK4LSLoose')
btagSF_deepFlav_2016_TuneCP5_LSLoose = lambda : btagSFProducer(era = '2016_TuneCP5', algo = 'deepjet', jetCollectionName = 'JetAK4LSLoose')
btagSF_deep_2016_LSLoose             = lambda : btagSFProducer(era = '2016',         algo = 'deepcsv', jetCollectionName = 'JetAK4LSLoose')
btagSF_deepFlav_2016_LSLoose         = lambda : btagSFProducer(era = '2016',         algo = 'deepjet', jetCollectionName = 'JetAK4LSLoose')
btagSF_csvv2_2016_LSLoose            = lambda : btagSFProducer(era = '2016',         algo = 'csvv2',   jetCollectionName = 'JetAK4LSLoose') # legacy
btagSF_cmva_2016_LSLoose             = lambda : btagSFProducer(era = '2016',         algo = 'cmva',    jetCollectionName = 'JetAK4LSLoose') # legacy

btagSF_deep_2018_subjet = lambda: btagSFProducer(era = '2018', algo = 'deepcsv', jetCollectionName = 'SubJet')
btagSF_deep_2017_subjet = lambda: btagSFProducer(era = '2017', algo = 'deepcsv', jetCollectionName = 'SubJet')
btagSF_deep_2016_subjet = lambda: btagSFProducer(era = '2016', algo = 'deepcsv', jetCollectionName = 'SubJet')

btagSF_deep_2018_subjet_LSLoose = lambda: btagSFProducer(era = '2018', algo = 'deepcsv', jetCollectionName = 'SubJetAK8LSLoose')
btagSF_deep_2017_subjet_LSLoose = lambda: btagSFProducer(era = '2017', algo = 'deepcsv', jetCollectionName = 'SubJetAK8LSLoose')
btagSF_deep_2016_subjet_LSLoose = lambda: btagSFProducer(era = '2016', algo = 'deepcsv', jetCollectionName = 'SubJetAK8LSLoose')
