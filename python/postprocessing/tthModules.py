from tthAnalysis.NanoAODTools.postprocessing.modules.genParticleProducer import genAll
from tthAnalysis.NanoAODTools.postprocessing.modules.genMatchCollectionProducer import genMatchCollection
from tthAnalysis.NanoAODTools.postprocessing.modules.lepJetVarProducer import lepJetVarBTagAll_2016, lepJetVarBTagAll_2017, lepJetVarBTagAll_2018
from tthAnalysis.NanoAODTools.postprocessing.modules.genHiggsDecayModeProducer import genHiggsDecayMode
from tthAnalysis.NanoAODTools.postprocessing.modules.tauIDLogProducer import tauIDLog
from tthAnalysis.NanoAODTools.postprocessing.modules.absIsoProducer import absIso
from tthAnalysis.NanoAODTools.postprocessing.modules.jetIdxProducer import jetIdx, jetAK4LSLooseIdx
from tthAnalysis.NanoAODTools.postprocessing.modules.diHiggsVarProducer import diHiggsVar_2016, diHiggsVar_2017, diHiggsVar_2018
from tthAnalysis.NanoAODTools.postprocessing.modules.btagSFProducer_explicitBranchNames import *
from tthAnalysis.NanoAODTools.postprocessing.modules.eventCountHistogramProducer import eventCountHistogram
from tthAnalysis.NanoAODTools.postprocessing.modules.countHistogramProducer import countHistogramAll, countHistogramAllCompTopRwgt
from tthAnalysis.NanoAODTools.postprocessing.modules.binnedEventCountProducer import binnedEventCounter
from tthAnalysis.NanoAODTools.postprocessing.modules.trigObjMatcherProducer import trigObjMatcher
from tthAnalysis.NanoAODTools.postprocessing.modules.puHistogramProducer import puHist2016, puHist2017, puHist2018
from tthAnalysis.NanoAODTools.postprocessing.modules.egammaIdProducer import egammaId
from PhysicsTools.NanoAODTools.postprocessing.modules.common.puWeightProducer import puWeight2016, puWeight2017, puWeight2018
from PhysicsTools.NanoAODTools.postprocessing.modules.jme.jetmetHelperRun2 import createJMECorrector

jetmetUncertainties2016All = createJMECorrector(dataYear = 2016, jesUncert = "All")
jetmetUncertainties2017All = createJMECorrector(dataYear = 2017, jesUncert = "All", metBranchName = "MET")
jetmetUncertainties2018All = createJMECorrector(dataYear = 2018, jesUncert = "All")

fatjetUncertainties2016Total = createJMECorrector(dataYear = 2016, jesUncert = "Total", jetType = "AK8PFPuppi")
fatjetUncertainties2017Total = createJMECorrector(dataYear = 2017, jesUncert = "Total", jetType = "AK8PFPuppi")
fatjetUncertainties2018Total = createJMECorrector(dataYear = 2018, jesUncert = "Total", jetType = "AK8PFPuppi")

jetmetAK4LSLooseUncertainties2016Total = createJMECorrector(dataYear = 2016, jesUncert = "Total", jetType = "AK4LSLoosePFchs")
jetmetAK4LSLooseUncertainties2017Total = createJMECorrector(dataYear = 2017, jesUncert = "Total", jetType = "AK4LSLoosePFchs", metBranchName = "MET")
jetmetAK4LSLooseUncertainties2018Total = createJMECorrector(dataYear = 2018, jesUncert = "Total", jetType = "AK4LSLoosePFchs")

fatjetAK8LSLooseUncertainties2016Total = createJMECorrector(dataYear = 2016, jesUncert = "Total", jetType = "AK8LSLoosePFPuppi")
fatjetAK8LSLooseUncertainties2017Total = createJMECorrector(dataYear = 2017, jesUncert = "Total", jetType = "AK8LSLoosePFPuppi")
fatjetAK8LSLooseUncertainties2018Total = createJMECorrector(dataYear = 2018, jesUncert = "Total", jetType = "AK8LSLoosePFPuppi")