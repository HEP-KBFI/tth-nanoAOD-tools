from tthAnalysis.NanoAODTools.postprocessing.modules.genParticleProducer import genAll
from tthAnalysis.NanoAODTools.postprocessing.modules.lepJetVarProducer import *
from tthAnalysis.NanoAODTools.postprocessing.modules.genHiggsDecayModeProducer import genHiggsDecayMode
from tthAnalysis.NanoAODTools.postprocessing.modules.tauIDLogProducer import tauIDLog_2016, tauIDLog_2017
from tthAnalysis.NanoAODTools.postprocessing.modules.absIsoProducer import absIso
from tthAnalysis.NanoAODTools.postprocessing.modules.btagSFProducer_explicitBranchNames import btagSF_csvv2_2016, btagSF_cmva_2016, btagSF_csvv2_2017, btagSF_deep_2017
from tthAnalysis.NanoAODTools.postprocessing.modules.eventCountHistogramProducer import eventCountHistogram
from tthAnalysis.NanoAODTools.postprocessing.modules.countHistogramProducer import countHistogramAll_2016, countHistogramAll_2017
from tthAnalysis.NanoAODTools.postprocessing.modules.jetSubstructureObservablesProducerHTTv2 import jetSubstructureObservablesHTTv2
from tthAnalysis.NanoAODTools.postprocessing.modules.trigObjMatcherProducer import trigObjMatcher
from tthAnalysis.NanoAODTools.postprocessing.modules.puHistogramProducer import puHist2016, puHist2017
from PhysicsTools.NanoAODTools.postprocessing.modules.common.puWeightProducer import puWeight as puWeight_2016
from PhysicsTools.NanoAODTools.postprocessing.modules.common.puWeightProducer import puWeight2017 as puWeight_2017
from PhysicsTools.NanoAODTools.postprocessing.modules.jme.jetmetUncertainties import jetmetUncertainties2016, jetmetUncertainties2017
