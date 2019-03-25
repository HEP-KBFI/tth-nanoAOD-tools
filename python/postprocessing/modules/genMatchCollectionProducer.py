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

class genMatchCollectionProducer(Module):
  def __init__(self):
    self.massTable = MassTable()

    self.genPartBr    = 'GenPart'
    self.genPartJetBr = 'GenJet'

    self.muBr = 'Muon'
    self.elBr = 'Electron'
    self.taBr = 'Tau'
    self.jtBr = 'Jet'

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
      if recoObjBr != self.jtBr:
        genCollectionName = '{}GenMatch'.format(recoObjBr)
        genCollectionLenName = 'n{}'.format(genCollectionName)
        self.out.branch(genCollectionLenName, 'i')
        for genVar in self.genVars:
          self.out.branch('{}_{}'.format(genCollectionName, genVar), self.genVars[genVar], lenVar = genCollectionLenName)
        self.out.branch('{}_genMatchIdx'.format(recoObjBr), 'I', lenVar = 'n{}'.format(recoObjBr))

      genJetCollectionName = '{}GenJetMatch'.format(recoObjBr)
      genJetCollectionLenName = 'n{}'.format(genJetCollectionName)
      self.out.branch(genJetCollectionLenName, 'i')
      for genVar in self.genVars:
        self.out.branch('{}_{}'.format(genJetCollectionName, genVar), self.genVars[genVar], lenVar = genJetCollectionLenName)
      self.out.branch('{}_genJetMatchIdx'.format(recoObjBr), 'I', lenVar = 'n{}'.format(recoObjBr))

  def endFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
    pass

  def analyze(self, event):

    # read the collections
    genParts = {
      idx : GenPartAuxAug(part, idx, self.massTable)
      for idx, part in enumerate(Collection(event, self.genPartBr))
    }
    genJets = {
      idx: GenJetAux(part, idx)
      for idx, part in enumerate(Collection(event, self.genPartJetBr))
    }
    jets = Collection(event, self.jtBr)

    jets_len = len(jets)

    recoGenMatches    = { recoObjBr : [] for recoObjBr in [ self.muBr, self.elBr, self.taBr            ] }
    recoGenJetMatches = { recoObjBr : [] for recoObjBr in [ self.muBr, self.elBr, self.taBr, self.jtBr ] }

    genMatchIdxs    = { recoObjBr : [] for recoObjBr in [ self.muBr, self.elBr, self.taBr            ] }
    genJetMatchIdxs = { recoObjBr : [] for recoObjBr in [ self.muBr, self.elBr, self.taBr, self.jtBr ] }

    for recoObjBr in [ self.muBr, self.elBr, self.taBr ]:
      recoCollection = Collection(event, recoObjBr)
      nof_genMatches = 0
      nof_genJetMatches = 0

      for recoObj in recoCollection:
        if recoObj.genPartIdx in genParts:
          genPart = genParts[recoObj.genPartIdx]
          genPart.genPartFlav = recoObj.genPartFlav
          recoGenMatches[recoObjBr].append(genPart)
          genMatchIdxs[recoObjBr].append(nof_genMatches)
          nof_genMatches += 1
        else:
          genMatchIdxs[recoObjBr].append(-1)

        if recoObj.jetIdx >= 0 and recoObj.jetIdx < jets_len:
          jetMatch_genJetIdx = jets[recoObj.jetIdx].genJetIdx
          if jetMatch_genJetIdx in genJets:
            recoGenJetMatches[recoObjBr].append(genJets[jetMatch_genJetIdx])
            genJetMatchIdxs[recoObjBr].append(nof_genJetMatches)
            nof_genJetMatches += 1
          else:
            genJetMatchIdxs[recoObjBr].append(-1)
        else:
          genJetMatchIdxs[recoObjBr].append(-1)

    nof_genJetMatches = 0
    for jet in jets:
      if jet.genJetIdx in genJets:
        recoGenJetMatches[self.jtBr].append(genJets[jet.genJetIdx])
        genJetMatchIdxs[self.jtBr].append(nof_genJetMatches)
        nof_genJetMatches += 1
      else:
        genJetMatchIdxs[self.jtBr].append(-1)
    
    for recoObjBr in [ self.muBr, self.elBr, self.taBr, self.jtBr ]:
      if recoObjBr != self.jtBr:
        genCollectionName = '{}GenMatch'.format(recoObjBr)
        for genVar in self.genVars:
          genVarArr = map(lambda genObj: getattr(genObj, genVar), recoGenMatches[recoObjBr])
          self.out.fillBranch('{}_{}'.format(genCollectionName, genVar), genVarArr)
        self.out.fillBranch('{}_genMatchIdx'.format(recoObjBr), genMatchIdxs[recoObjBr])

      genJetCollectionName = '{}GenJetMatch'.format(recoObjBr)
      for genVar in self.genVars:
        genVarArr = map(lambda genObj: getattr(genObj, genVar), recoGenJetMatches[recoObjBr])
        self.out.fillBranch('{}_{}'.format(genJetCollectionName, genVar), genVarArr)
      self.out.fillBranch('{}_genJetMatchIdx'.format(recoObjBr), genJetMatchIdxs[recoObjBr])

    return True

genMatchCollection = lambda : genMatchCollectionProducer()
