from tthAnalysis.NanoAODTools.postprocessing.modules.genParticleProducer import genAll
from tthAnalysis.NanoAODTools.postprocessing.modules.genMatchCollectionProducer import genMatchCollection
from tthAnalysis.NanoAODTools.postprocessing.modules.lepJetVarProducer import lepJetVarBTagAll_2016, lepJetVarBTagAll_2017, lepJetVarBTagAll_2018
from tthAnalysis.NanoAODTools.postprocessing.modules.genHiggsDecayModeProducer import genHiggsDecayMode
from tthAnalysis.NanoAODTools.postprocessing.modules.tauIDLogProducer import tauIDLog
from tthAnalysis.NanoAODTools.postprocessing.modules.absIsoProducer import absIso
from tthAnalysis.NanoAODTools.postprocessing.modules.jetIdxProducer import jetIdx
from tthAnalysis.NanoAODTools.postprocessing.modules.diHiggsVarProducer import diHiggsVar_2016, diHiggsVar_2017, diHiggsVar_2018
from tthAnalysis.NanoAODTools.postprocessing.modules.btagSFProducer_explicitBranchNames import btagSF_deep_2016, btagSF_deepFlav_2016, btagSF_csvv2_2016, btagSF_cmva_2016, \
                                                                                               btagSF_deep_2017, btagSF_deepFlav_2017, btagSF_csvv2_2017,                   \
                                                                                               btagSF_deep_2018, btagSF_deepFlav_2018
from tthAnalysis.NanoAODTools.postprocessing.modules.eventCountHistogramProducer import eventCountHistogram
from tthAnalysis.NanoAODTools.postprocessing.modules.countHistogramProducer import countHistogramAll
from tthAnalysis.NanoAODTools.postprocessing.modules.binnedEventCountProducer import binnedEventCounter
from tthAnalysis.NanoAODTools.postprocessing.modules.trigObjMatcherProducer import trigObjMatcher
from tthAnalysis.NanoAODTools.postprocessing.modules.puHistogramProducer import puHist2016, puHist2017, puHist2018
from tthAnalysis.NanoAODTools.postprocessing.modules.egammaIdProducer import egammaId
from PhysicsTools.NanoAODTools.postprocessing.modules.common.puWeightProducer import puWeight2016, puWeight2017, puWeight2018
from PhysicsTools.NanoAODTools.postprocessing.modules.jme.jetmetHelperRun2 import createJMECorrector

jetmetUncertainties2016All = createJMECorrector(dataYear = 2016, jesUncert = "All")
jetmetUncertainties2017All = createJMECorrector(dataYear = 2017, jesUncert = "All")
jetmetUncertainties2018All = createJMECorrector(dataYear = 2018, jesUncert = "All")
