import FWCore.ParameterSet.Config as cms
from Configuration.StandardSequences.Eras import eras
from Configuration.AlCa.autoCond import autoCond

import os

if 'IS_DATA' not in os.environ:
  raise ValueError("$IS_DATA not defined")

is_data = bool(int(os.environ['IS_DATA']))
print("Using {mc_or_data} settings for sample {sample_name}".format(
  mc_or_data  = "data" if is_data else "MC  ",
  sample_name = os.environ['DATASET'],
))

process = cms.Process('NANO', eras.Run2_2017,eras.run2_nanoAOD_92X)
process.load("FWCore.MessageLogger.MessageLogger_cfi")
process.load("Configuration.StandardSequences.GeometryDB_cff")
process.load("Configuration.StandardSequences.FrontierConditions_GlobalTag_cff")
process.load('Configuration.StandardSequences.Services_cff')

process.GlobalTag.globaltag                      = autoCond['run2_data'] if is_data else autoCond['phase1_2017_realistic']
process.options                                  = cms.untracked.PSet(wantSummary = cms.untracked.bool(True))
process.MessageLogger.cerr.FwkReport.reportEvery = 1000
process.maxEvents                                = cms.untracked.PSet(input = cms.untracked.int32(10000))
process.source                                   = cms.Source("PoolSource", fileNames = cms.untracked.vstring())
process.source.fileNames                         = []
process.load("PhysicsTools.NanoAOD.nano_cff")

process.RandomNumberGeneratorService = cms.Service("RandomNumberGeneratorService",
    calibratedPatElectrons = cms.PSet(
      initialSeed = cms.untracked.uint32(81),
      engineName  = cms.untracked.string('TRandom3'),
    ),
    calibratedPatPhotons = cms.PSet(
      initialSeed = cms.untracked.uint32(81),
      engineName  = cms.untracked.string('TRandom3'),
    ),
)
process.nanoPath                    = cms.Path(process.nanoSequence) if is_data else cms.Path(process.nanoSequenceMC)
process.calibratedPatElectrons.isMC = cms.bool(True)
process.calibratedPatPhotons.isMC   = cms.bool(True)

process.out = cms.OutputModule("NanoAODOutputModule",
    fileName       = cms.untracked.string('tree.root'),
    outputCommands = process.NanoAODEDMEventContent.outputCommands,
)
process.end = cms.EndPath(process.out)
