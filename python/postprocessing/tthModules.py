from tthAnalysis.NanoAODTools.postprocessing.modules.genParticleProducer import genAll
from tthAnalysis.NanoAODTools.postprocessing.modules.genMatchCollectionProducer import genMatchCollection
from tthAnalysis.NanoAODTools.postprocessing.modules.lepJetVarProducer import lepJetVarBTagAll_2016, lepJetVarBTagAll_2017, lepJetVarBTagAll_2018
from tthAnalysis.NanoAODTools.postprocessing.modules.genHiggsDecayModeProducer import genHiggsDecayMode
from tthAnalysis.NanoAODTools.postprocessing.modules.tauIDLogProducer import tauIDLog
from tthAnalysis.NanoAODTools.postprocessing.modules.absIsoProducer import absIso
from tthAnalysis.NanoAODTools.postprocessing.modules.jetIdxProducer import jetIdx, jetAK4LSLooseIdx
from tthAnalysis.NanoAODTools.postprocessing.modules.diHiggsVarProducer import diHiggsVar_2016, diHiggsVar_2017, diHiggsVar_2018
from tthAnalysis.NanoAODTools.postprocessing.modules.mllVarProducer import mllWZTo3LNu, mllWZTo3LNu_mllmin01
from tthAnalysis.NanoAODTools.postprocessing.modules.btagSFProducer_explicitBranchNames import *
from tthAnalysis.NanoAODTools.postprocessing.modules.eventCountHistogramProducer import eventCountHistogram
from tthAnalysis.NanoAODTools.postprocessing.modules.countHistogramProducer import *
from tthAnalysis.NanoAODTools.postprocessing.modules.subjetBtagCounter import *
from tthAnalysis.NanoAODTools.postprocessing.modules.binnedEventCountProducer import binnedEventCounter
from tthAnalysis.NanoAODTools.postprocessing.modules.trigObjMatcherProducer import trigObjMatcher
from tthAnalysis.NanoAODTools.postprocessing.modules.puHistogramProducer import puHist2016, puHist2017, puHist2018
from tthAnalysis.NanoAODTools.postprocessing.modules.egammaIdProducer import egammaId
from tthAnalysis.NanoAODTools.postprocessing.modules.btagSFRatioFinder import *
from tthAnalysis.NanoAODTools.postprocessing.modules.rleProducer import rle
from PhysicsTools.NanoAODTools.postprocessing.modules.common.puWeightProducer import puWeight2016, puWeight2017, puWeight2018
from PhysicsTools.NanoAODTools.postprocessing.modules.jme.jetmetHelperRun2 import createJMECorrector

jetmetUncertainties2016Merged = createJMECorrector(dataYear = 2016, jesUncert = "Merged")
jetmetUncertainties2017Merged = createJMECorrector(dataYear = 2017, jesUncert = "Merged", metBranchName = "MET")
jetmetUncertainties2018Merged = createJMECorrector(dataYear = 2018, jesUncert = "Merged", applyHEMfix = True)

fatjetUncertainties2016Total = createJMECorrector(dataYear = 2016, jesUncert = "Total", jetType = "AK8PFPuppi", splitJER = False)
fatjetUncertainties2017Total = createJMECorrector(dataYear = 2017, jesUncert = "Total", jetType = "AK8PFPuppi", splitJER = False)
fatjetUncertainties2018Total = createJMECorrector(dataYear = 2018, jesUncert = "Total", jetType = "AK8PFPuppi", applyHEMfix = True, splitJER = False)

fatjetUncertainties2016Merged = createJMECorrector(dataYear = 2016, jesUncert = "Merged", jetType = "AK8PFPuppi", splitJER = False)
fatjetUncertainties2017Merged = createJMECorrector(dataYear = 2017, jesUncert = "Merged", jetType = "AK8PFPuppi", splitJER = False)
fatjetUncertainties2018Merged = createJMECorrector(dataYear = 2018, jesUncert = "Merged", jetType = "AK8PFPuppi", applyHEMfix = True, splitJER = False)

jetmetAK4LSLooseUncertainties2016Total = createJMECorrector(dataYear = 2016, jesUncert = "Merged", jetType = "AK4LSLoosePFchs")
jetmetAK4LSLooseUncertainties2017Total = createJMECorrector(dataYear = 2017, jesUncert = "Merged", jetType = "AK4LSLoosePFchs", metBranchName = "MET")
jetmetAK4LSLooseUncertainties2018Total = createJMECorrector(dataYear = 2018, jesUncert = "Merged", jetType = "AK4LSLoosePFchs", applyHEMfix = True)

fatjetAK8LSLooseUncertainties2016Total = createJMECorrector(dataYear = 2016, jesUncert = "Total", jetType = "AK8LSLoosePFPuppi", splitJER = False)
fatjetAK8LSLooseUncertainties2017Total = createJMECorrector(dataYear = 2017, jesUncert = "Total", jetType = "AK8LSLoosePFPuppi", splitJER = False)
fatjetAK8LSLooseUncertainties2018Total = createJMECorrector(dataYear = 2018, jesUncert = "Total", jetType = "AK8LSLoosePFPuppi", applyHEMfix = True, splitJER = False)

fatjetAK8LSLooseUncertainties2016Merged = createJMECorrector(dataYear = 2016, jesUncert = "Merged", jetType = "AK8LSLoosePFPuppi", splitJER = False)
fatjetAK8LSLooseUncertainties2017Merged = createJMECorrector(dataYear = 2017, jesUncert = "Merged", jetType = "AK8LSLoosePFPuppi", splitJER = False)
fatjetAK8LSLooseUncertainties2018Merged = createJMECorrector(dataYear = 2018, jesUncert = "Merged", jetType = "AK8LSLoosePFPuppi", applyHEMfix = True, splitJER = False)
