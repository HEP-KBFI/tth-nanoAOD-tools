import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True

from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import Collection
from PhysicsTools.NanoAODTools.postprocessing.framework.eventloop import Module

from tthAnalysis.NanoAODTools.postprocessing.modules.genParticleProducer import MassTable, GenPartAux

import collections

class GenJetAux:
  def __init__(self, genJet, idx):
    self.pt               = genJet.pt
    self.eta              = genJet.eta
    self.phi              = genJet.phi
    self.mass             = genJet.mass
    self.pdgId            = genJet.partonFlavour
    self.charge           = 0
    self.status           = -1
    self.statusFlags      = -1
    self.genPartIdxMother = -1
    self.idx              = idx

  def __str__(self):
    return "pt = %.3f eta = %.3f phi = %.3f mass = %.3f pdgId = %i charge = %i status = %i " \
           "statusFlags = %i mom = %i idx = %i" % \
      (self.pt, self.eta, self.phi, self.mass, self.pdgId, self.charge, self.status, \
       self.statusFlags, self.genPartIdxMother, self.idx)

  def __repr__(self):
    return self.__str__()

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

    self.genPartBr    = 'GenPart'
    self.genPartJetBr = 'GenJet'
    self.genPartTauBr = 'GenVisTau'

    self.muBr = 'Muon'
    self.elBr = 'Electron'
    self.taBr = 'Tau'
    self.jtBr = 'Jet'

    self.genLepBr = 'genLepton'
    self.genTauBr = 'genTau'
    self.genPhoBr = 'genPhoton'
    self.genJetBr = 'genJet'
    self.genOthBr = 'genOther'

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
      for genObjBr in [ self.genLepBr, self.genPhoBr, self.genOthBr, self.genJetBr ]:#, self.genTauBr, self.genJetBr ]:
        for genVar in self.genVars:
          self.out.branch('_'.join([ recoObjBr, genObjBr, genVar ]), self.genVars[genVar], lenVar = 'n{}'.format(recoObjBr))

  def endFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
    pass

  def analyze(self, event):
    genParticles  = {
      idx : GenPartAux(part, idx, self.massTable)
      for idx, part in enumerate(Collection(event, self.genPartBr))
    }
    genJets = {
      idx : GenJetAux(part, idx)
      for idx, part in enumerate(Collection(event, self.genPartJetBr))
    }
    jets = Collection(event, self.jtBr)

    genOut = {}
    for recoObjBr in [ self.muBr, self.elBr, self.taBr ]:#, self.jtBr ]:
      genOut[recoObjBr] = {}
      for genObjBr in [ self.genLepBr, self.genTauBr, self.genPhoBr, self.genJetBr, self.genOthBr ]:
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

          if abs(genPart.pdgId) == 22:
            genOut[recoObjBr][self.genPhoBr].append(genPart)
          else:
            genOut[recoObjBr][self.genPhoBr].append(None)

          if abs(genPart.pdgId) not in [ 11, 13, 22 ]:
            genOut[recoObjBr][self.genOthBr].append(genPart)
          else:
            genOut[recoObjBr][self.genOthBr].append(None)

        else:
          for genObjBr in [ self.genLepBr, self.genPhoBr, self.genOthBr ]:
            genOut[recoObjBr][genObjBr].append(None)

        if recoObj.jetIdx >= 0:
          jet = jets[recoObj.jetIdx]

          if jet.genJetIdx >= 0:
            genOut[recoObjBr][self.genJetBr].append(genJets[jet.genJetIdx])
          else:
            genOut[recoObjBr][self.genJetBr].append(None)
        else:
          genOut[recoObjBr][self.genJetBr].append(None)

    for recoObjBr in [self.muBr, self.elBr, self.taBr ]:#, self.jtBr]:
      for genObjBr in [self.genLepBr, self.genPhoBr, self.genOthBr, self.genJetBr ]:# self.genTauBr
        genOutArr = genOut[recoObjBr][genObjBr]
        for genVar in self.genVars:
          genVarArr = map(lambda genObj: getattr(genObj, genVar) if genObj is not None else getDefaultValue(genVar), genOutArr)
          self.out.fillBranch('_'.join([ recoObjBr, genObjBr, genVar ]), genVarArr)

    return True

genParticleMatcher = lambda : genParticleMatchProducer()
