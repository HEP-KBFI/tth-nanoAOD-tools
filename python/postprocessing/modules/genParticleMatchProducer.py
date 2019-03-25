import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True

from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import Collection
from PhysicsTools.NanoAODTools.postprocessing.framework.eventloop import Module

from tthAnalysis.NanoAODTools.postprocessing.modules.genParticleProducer import MassTable, GenPartAux

import collections
import logging

class GenPartAuxAug(GenPartAux):
  def __init__(self, genPart, idx, massTable):
    super(self.__class__, self).__init__(genPart, idx, massTable)
    self.genPartFlav = 0

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
    self.genPartFlav      = 0
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
  elif genVar in [ 'pdgId', 'charge', 'genPartFlav' ]:
    return 0
  else:
    return 0.

class genParticleMatchProducer(Module):
  def __init__(self):
    self.massTable = MassTable()

    self.genPartBr    = 'GenPart'
    self.genPartJetBr = 'GenJet'

    self.muBr = 'Muon'
    self.elBr = 'Electron'
    self.taBr = 'Tau'
    self.jtBr = 'Jet'

    self.genLepBr = 'genLepton'
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
      ('genPartFlav', 'b'),
    ])

  def beginJob(self):
    pass

  def endJob(self):
    pass

  def beginFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
    self.out = wrappedOutputTree
    for recoObjBr in [ self.muBr, self.elBr, self.taBr, self.jtBr ]:
      for genObjBr in [ self.genLepBr, self.genPhoBr, self.genJetBr ]:

        if recoObjBr != self.elBr and genObjBr == self.genPhoBr:
          # match gen photons only to reco electrons
          continue
        if recoObjBr == self.jtBr and genObjBr != self.genJetBr:
          # match reco jets only to gen jets
          continue

        for genVar in self.genVars:
          self.out.branch('_'.join([ recoObjBr, genObjBr, genVar ]), self.genVars[genVar], lenVar = 'n{}'.format(recoObjBr))

  def endFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
    pass

  def analyze(self, event):

    # read the collections
    genParticles  = {
      idx : GenPartAuxAug(part, idx, self.massTable)
      for idx, part in enumerate(Collection(event, self.genPartBr))
    }
    genJets = {
      idx : GenJetAux(part, idx)
      for idx, part in enumerate(Collection(event, self.genPartJetBr))
    }
    jets = Collection(event, self.jtBr)

    # construct output arrays
    genOut = {}
    for recoObjBr in [ self.muBr, self.elBr, self.taBr, self.jtBr ]:
      genOut[recoObjBr] = {}
      for genObjBr in [ self.genLepBr, self.genPhoBr, self.genJetBr ]:

        if recoObjBr != self.elBr and genObjBr == self.genPhoBr:
          # match gen photons only to reco electrons
          continue
        if recoObjBr == self.jtBr and genObjBr != self.genJetBr:
          # match reco jets only to gen jets
          continue

        genOut[recoObjBr][genObjBr] = []

    # perform index-based gen matching for electrons, muons and taus to gen leptons, jets (and photons)
    for recoObjBr in [ self.muBr, self.elBr, self.taBr ]:
      recoObjs = Collection(event, recoObjBr)

      for recoObj in recoObjs:

        # matching to gen leptons (and photons)
        if recoObj.genPartIdx >= 0 and recoObj.genPartIdx < len(genParticles):
          genPart = genParticles[recoObj.genPartIdx]
          genPart.genPartFlav = recoObj.genPartFlav

          if abs(genPart.pdgId) in [ 11, 13 ]:
            genOut[recoObjBr][self.genLepBr].append(genPart)
          else:
            genOut[recoObjBr][self.genLepBr].append(None)

          if recoObjBr == self.elBr:
            # gen photons are matched only to electrons
            if abs(genPart.pdgId) == 22:
              genOut[recoObjBr][self.genPhoBr].append(genPart)
            else:
              genOut[recoObjBr][self.genPhoBr].append(None)

        else:
          genOut[recoObjBr][self.genLepBr].append(None)
          if recoObjBr == self.elBr:
            # gen photons are matched only to electrons
            genOut[recoObjBr][self.genPhoBr].append(None)

        # matching to gen jets
        if recoObj.jetIdx >= 0 and recoObj.jetIdx < len(jets):
          jet = jets[recoObj.jetIdx]

          if jet.genJetIdx >= 0 and jet.genJetIdx < len(genJets):
            genOut[recoObjBr][self.genJetBr].append(genJets[jet.genJetIdx])
          else:
            genOut[recoObjBr][self.genJetBr].append(None)
        else:
          genOut[recoObjBr][self.genJetBr].append(None)

    # match gen jets to reco jets
    for jet in jets:
      if jet.genJetIdx >= 0 and jet.genJetIdx < len(genJets):
        genOut[self.jtBr][self.genJetBr].append(genJets[jet.genJetIdx])
      else:
        genOut[self.jtBr][self.genJetBr].append(None)

    # save the results
    for recoObjBr in [ self.muBr, self.elBr, self.taBr, self.jtBr ]:
      for genObjBr in [ self.genLepBr, self.genPhoBr, self.genJetBr ]:

        if recoObjBr != self.elBr and genObjBr == self.genPhoBr:
          # match gen photons only to reco electrons
          continue
        if recoObjBr == self.jtBr and genObjBr != self.genJetBr:
          # match reco jets only to gen jets
          continue

        genOutArr = genOut[recoObjBr][genObjBr]
        for genVar in self.genVars:
          genVarArr = map(lambda genObj: getattr(genObj, genVar) if genObj is not None else getDefaultValue(genVar), genOutArr)
          self.out.fillBranch('_'.join([ recoObjBr, genObjBr, genVar ]), genVarArr)

    return True

genParticleMatcher = lambda : genParticleMatchProducer()
