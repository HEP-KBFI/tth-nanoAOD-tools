from tthAnalysis.NanoAODTools.postprocessing.modules.genParticleProducer import genAll
from tthAnalysis.NanoAODTools.postprocessing.modules.genMatchCollectionProducer import genMatchCollection
from tthAnalysis.NanoAODTools.postprocessing.modules.lepJetVarProducer import lepJetVarBTagAll_2016, lepJetVarBTagAll_2017, lepJetVarBTagAll_2018
from tthAnalysis.NanoAODTools.postprocessing.modules.genHiggsDecayModeProducer import genHiggsDecayMode
from tthAnalysis.NanoAODTools.postprocessing.modules.tauIDLogProducer import tauIDLog
from tthAnalysis.NanoAODTools.postprocessing.modules.absIsoProducer import absIso
from tthAnalysis.NanoAODTools.postprocessing.modules.jetIdxProducer import jetIdx
from tthAnalysis.NanoAODTools.postprocessing.modules.diHiggsVarProducer import diHiggsVar_2016, diHiggsVar_2017, diHiggsVar_2018
from tthAnalysis.NanoAODTools.postprocessing.modules.btagSFProducer_explicitBranchNames import *
from tthAnalysis.NanoAODTools.postprocessing.modules.eventCountHistogramProducer import eventCountHistogram
from tthAnalysis.NanoAODTools.postprocessing.modules.countHistogramProducer import countHistogramAll
from tthAnalysis.NanoAODTools.postprocessing.modules.binnedEventCountProducer import binnedEventCounter
from tthAnalysis.NanoAODTools.postprocessing.modules.trigObjMatcherProducer import trigObjMatcher
from tthAnalysis.NanoAODTools.postprocessing.modules.puHistogramProducer import puHist2016, puHist2017, puHist2018
from tthAnalysis.NanoAODTools.postprocessing.modules.egammaIdProducer import egammaId
from PhysicsTools.NanoAODTools.postprocessing.modules.common.puWeightProducer import puWeight2016, puWeight2017, puWeight2018
from PhysicsTools.NanoAODTools.postprocessing.modules.jme.jetmetUncertainties import jetmetUncertainties2016,         jetmetUncertainties2017,         jetmetUncertainties2018, \
                                                                                     jetmetUncertainties2016AK8Puppi, jetmetUncertainties2017AK8Puppi, jetmetUncertainties2018AK8Puppi
