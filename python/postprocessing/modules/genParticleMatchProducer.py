import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True

from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import Collection
from PhysicsTools.NanoAODTools.postprocessing.framework.eventloop import Module

from tthAnalysis.NanoAODTools.postprocessing.modules.genParticleProducer import MassTable, GenPartAux

import collections

def getDefaultValue(genVar):
  if genVar in [ 'status', 'statusFlags' ]:
    return -1
  elif genVar in [ 'pdgId', 'charge' ]:
    return 0
  else:
    return 0.

class genParticleMatchProducer(Module):
  def __init__(self):
    self.massTable = MassTable()
    self.genPartBr = 'GenPart'

    self.muBr = 'Muon'
    self.elBr = 'Electron'
    self.taBr = 'Tau'
    self.jtBr = 'Jet'

    self.genLepBr = 'genLepton'
    self.genTauBr = 'genTau'
    self.genPhoBr = 'genPhoton'
    self.genJetBr = 'genJet'

    self.genVars = collections.OrderedDict([
      ('pt',          'F'),
      ('eta',         'F'),
      ('phi',         'F'),
      ('mass',        'F'),
      ('pdgId',       'I'),
      ('charge',      'I'),
      ('status',      'I'),
      ('statusFlags', 'I'),
    ])

  def beginJob(self):
    pass

  def endJob(self):
    pass

  def beginFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
    self.out = wrappedOutputTree
    for recoObjBr in [ self.muBr, self.elBr, self.taBr ]: #, self.jtBr ]:
      for genObjBr in [ self.genLepBr ]:#, self.genTauBr, self.genPhoBr, self.genJetBr ]:
        for genVar in self.genVars:
          self.out.branch('_'.join([ recoObjBr, genObjBr, genVar ]), self.genVars[genVar], lenVar = 'n{}'.format(recoObjBr))

  def endFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
    pass

  def analyze(self, event):
    genParticles  = {
      idx : GenPartAux(part, idx, self.massTable)
      for idx, part in enumerate(Collection(event, self.genPartBr))
    }
    genOut = {}
    for recoObjBr in [ self.muBr, self.elBr, self.taBr ]:#, self.jtBr ]:
      genOut[recoObjBr] = {}
      for genObjBr in [ self.genLepBr, self.genTauBr, self.genPhoBr, self.genJetBr ]:
        genOut[recoObjBr][genObjBr] = []

    for recoObjBr in [ self.muBr, self.elBr, self.taBr ]:
      recoObjs = Collection(event, recoObjBr)

      for recoObj in recoObjs:
        if recoObj.genPartIdx >= 0:
          genPart = genParticles[recoObj.genPartIdx]
          if abs(genPart.pdgId) in [ 11, 13 ]:
            genOut[recoObjBr][self.genLepBr].append(genPart)
          else:
            genOut[recoObjBr][self.genLepBr].append(None)
        else:
          genOut[recoObjBr][self.genLepBr].append(None)

    for recoObjBr in [self.muBr, self.elBr, self.taBr ]:#, self.jtBr]:
      for genObjBr in [self.genLepBr ]:#, self.genTauBr, self.genPhoBr, self.genJetBr]:
        genOutArr = genOut[recoObjBr][genObjBr]
        for genVar in self.genVars:
          genVarArr = map(lambda genObj: getattr(genObj, genVar) if genObj is not None else getDefaultValue(genVar), genOutArr)
          self.out.fillBranch('_'.join([ recoObjBr, genObjBr, genVar ]), genVarArr)

    return True

genParticleMatcher = lambda : genParticleMatchProducer()
