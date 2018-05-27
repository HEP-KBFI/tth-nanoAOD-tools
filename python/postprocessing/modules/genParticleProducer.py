import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True

from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import Collection
from PhysicsTools.NanoAODTools.postprocessing.framework.eventloop import Module
import math
import logging


sign = lambda x: int(math.copysign(1, x) if x != 0 else 0)


statusFlagsMap = {
  # comments taken from:
  # DataFormats/HepMCCandidate/interface/GenParticle.h
  # PhysicsTools/HepMCCandAlgos/interface/MCTruthHelper.h
  #
  # nomenclature taken from:
  # PhysicsTools/NanoAOD/python/genparticles_cff.py
  #
  #TODO: use this map in other gen-lvl particle selectors as well
  # GenLepFromTauFromTop -> isDirectPromptTauDecayProduct &&
  #                         isDirectHardProcessTauDecayProduct &&
  #                         isLastCopy &&
  #                         ! isDirectHadronDecayProduct
  # GenLepFromTau -> isDirectTauDecayProduct (or isDirectPromptTauDecayProduct?) &&
  #                  isLastCopy &&
  #                  ! isDirectHadronDecayProduct
  #                  (&& maybe isHardProcessTauDecayProduct?)
  #
  # GenLepFromTop -> isPrompt &&
  #                  isHardProcess &&
  #                  (isLastCopy || isLastCopyBeforeFSR) &&
  #                  ! isDirectHadronDecayProduct
  #
  # Not sure if to choose (isLastCopy or isLastCopyBeforeFSR) or just isFirstCopy:
  # GenWZQuark, GenHiggsDaughters, GenVbosons
  #
  # Have no clue what exactly to require from GenTau
  #
  #
  'isPrompt'                           : 0,  # any decay product NOT coming from hadron, muon or tau decay
  'isDecayedLeptonHadron'              : 1,  # a particle coming from hadron, muon, or tau decay
                                             # (does not include resonance decays like W,Z,Higgs,top,etc)
                                             # equivalent to status 2 in the current HepMC standard
  'isTauDecayProduct'                  : 2,  # a direct or indirect tau decay product
  'isPromptTauDecayProduct'            : 3,  # a direct or indirect decay product of a prompt tau
  'isDirectTauDecayProduct'            : 4,  # a direct tau decay product
  'isDirectPromptTauDecayProduct'      : 5,  # a direct decay product from a prompt tau
  'isDirectHadronDecayProduct'         : 6,  # a direct decay product from a hadron
  'isHardProcess'                      : 7,  # part of the hard process
  'fromHardProcess'                    : 8,  # the direct descendant of a hard process particle of the same pdg id
  'isHardProcessTauDecayProduct'       : 9,  # a direct or indirect decay product of a tau from the hard process
  'isDirectHardProcessTauDecayProduct' : 10, # a direct decay product of a tau from the hard process
  'fromHardProcessBeforeFSR'           : 11, # the direct descendant of a hard process particle of the same pdg id
                                             # for outgoing particles the kinematics are those before QCD or QED FSR
  'isFirstCopy'                        : 12, # the first copy of the particle in the chain with the same pdg id
  'isLastCopy'                         : 13, # the last copy of the particle in the chain with the same pdg id
                                             # (and therefore is more likely, but not guaranteed,
                                             # to carry the final physical momentum)
  'isLastCopyBeforeFSR'                : 14, # the last copy of the particle in the chain with the same pdg id
                                             # before QED or QCD FSR (and therefore is more likely,
                                             # but not guaranteed, to carry the momentum after ISR;
                                             # only really makes sense for outgoing particles
}


class MassTable:
  def __init__(self):
    self.pdgTable = ROOT.TDatabasePDG()

  def getMass(self, mass, pdgId):
    if mass > 10. or (pdgId == 22 and mass > 1.) or abs(pdgId) == 24 or pdgId == 23:
      return mass
    else:
      genParticleInstance = self.pdgTable.GetParticle(pdgId)
      if not genParticleInstance:
        # Since most of the common low-mass particles are defined in ROOT's PDG table,
        # and that it's more than likely we don't need such generator-level information,
        # we can safely set the masses of such particles to 0 GeV
        logging.debug("Setting the mass to 0 GeV for a particle with PDG id of %d" % pdgId)
        return 0.
      return genParticleInstance.Mass()

  def getCharge(self, pdgId):
    genParticleInstance = self.pdgTable.GetParticle(pdgId)
    if not genParticleInstance:
      # It's more than likely that we don't need to know the charges of generator-level particles
      # that are not defined in ROOT's PDG id table. Therefore, we assign neutral charges to
      # these particles.
      logging.debug("Setting the charge to neutral for a particle with PDG id of %d" % pdgId)
      return 0
    return sign(genParticleInstance.Charge())


class GenPartAux:
  def __init__(self, genPart, idx, massTable):
    self.pt               = genPart.pt
    self.eta              = genPart.eta
    self.phi              = genPart.phi
    self.mass             = massTable.getMass(genPart.mass, genPart.pdgId)
    self.pdgId            = genPart.pdgId
    self.charge           = massTable.getCharge(genPart.pdgId)
    self.status           = genPart.status
    self.statusFlags      = genPart.statusFlags
    self.genPartIdxMother = genPart.genPartIdxMother
    self.idx              = idx

  def __str__(self):
    return "pt = %.3f eta = %.3f phi = %.3f mass = %.3f pdgId = %i charge = %i status = %i " \
           "statusFlags = %i mom = %i idx = %i" % \
      (self.pt, self.eta, self.phi, self.mass, self.pdgId, self.charge, self.status, \
       self.statusFlags, self.genPartIdxMother, self.idx)

  def __repr__(self):
    return self.__str__()

  def checkIf(self, condition):
    assert(condition in statusFlagsMap)
    return (self.statusFlags & (1 << statusFlagsMap[condition]) != 0)


class SelectionOptions:
  SAVE_TAU                      = 0
  SAVE_LEPTONIC_TAU             = 1
  SAVE_HADRONIC_TAU             = 2
  SAVE_LEPTON_FROM_TAU          = 3
  SAVE_LEPTONIC_NU_FROM_TAU     = 4
  SAVE_TAU_NU_FROM_LEPTONIC_TAU = 5
  SAVE_TAU_NU_FROM_HADRONIC_TAU = 6

  SAVE_TOP                               = 10
  SAVE_BQUARK_FROM_TOP                   = 11
  SAVE_LEPTON_FROM_TOP                   = 12
  SAVE_LEPTONIC_NU_FROM_TOP              = 13
  SAVE_TAU_FROM_TOP                      = 14
  SAVE_TAU_NU_FROM_TOP                   = 15
  SAVE_LEPTON_FROM_TAU_FROM_TOP          = 16
  SAVE_LEPTON_NU_FROM_TAU_FROM_TOP       = 17
  SAVE_TAU_NU_FROM_LEPTONIC_TAU_FROM_TOP = 18
  SAVE_TAU_NU_FROM_HADRONIC_TAU_FROM_TOP = 19
  SAVE_NU_FROM_TAU_FROM_TOP              = 20
  SAVE_QUARK_FROM_W_FROM_TOP             = 21


def genLeptonSelection(genParticles):
  return filter(lambda genPart: abs(genPart.pdgId) in [11, 13] and genPart.status == 1, genParticles)

def genPromptLeptonSelection(genParticles):
  return filter(
    lambda genLepton:
      genLepton.checkIf('isLastCopy') and
      not genLepton.checkIf('isDirectHadronDecayProduct') and
      (
        genLepton.checkIf('isPrompt') or
        genLepton.checkIf('isDirectPromptTauDecayProduct')
      ),
    genLeptonSelection(genParticles)
  )

def genPhotonSelection(genParticles):
  return filter(lambda genPart: genPart.pdgId == 22, genParticles)

def genPromptPhotonSelection(genParticles):
  return filter(
    lambda genPart: genPart.status == 1 and genPart.checkIf('isPrompt'),
    genPhotonSelection(genParticles)
  )

def genHiggsSelection(genParticles):
  return filter(
    lambda genPart:
      genPart.pdgId == 25 and \
      (genParticles[genPart.genPartIdxMother].pdgId != 25 if genPart.genPartIdxMother >= 0 else True),
    genParticles
  )

def genHiggsDaughtersSelection(genParticles):
  return filter(
    lambda genPart:
      genPart.pdgId != 25 and \
      (genParticles[genPart.genPartIdxMother].pdgId == 25 if genPart.genPartIdxMother >= 0 else False),
    genParticles
  )

def genWZquarkSelection(genParticles):
  return filter(
    lambda genPart:
      abs(genPart.pdgId) in [1, 2, 3, 4, 5, 6] and genPart.genPartIdxMother >= 0 and \
      abs(genParticles[genPart.genPartIdxMother].pdgId) in [23, 24],
    genParticles
  )

def genVbosonSelection(genParticles):
  return filter(
    lambda genPart:
      abs(genPart.pdgId) in [23, 24] and genPart.genPartIdxMother >= 0 and \
      genParticles[genPart.genPartIdxMother].pdgId != genPart.pdgId,
    genParticles
  )

def genNuSelection(genParticles):
  return filter(lambda genPart: abs(genPart.pdgId) in [12, 14, 16], genParticles)

def genTopSelection(genParticles, choice, enable_consistency_checks = True):
  genTopMotherMap = {}
  genWMotherMap = {}
  for genPart in genParticles:
    if abs(genPart.pdgId) == 6:
      genTopMotherMap[genPart.idx] = genPart.genPartIdxMother # daughter -> mother
    elif abs(genPart.pdgId) == 24:
      genWMotherMap[genPart.genPartIdxMother] = genPart.idx # mother -> daughter

  genTopCandidates = {}
  for genTopIdx in genTopMotherMap:
    if genTopIdx not in genTopMotherMap.values():
      genTopCandidates[genTopIdx] = []

  if choice == SelectionOptions.SAVE_TOP:
    return map(lambda genTopIdx: genParticles[genTopIdx], genTopCandidates)

  for genPart in genParticles:
    if genPart.genPartIdxMother in genTopCandidates:
      genTopCandidates[genPart.genPartIdxMother].append(genPart.idx)

  # top always decays into W + q, where q = d, s, b with b the most common one
  genBquarkFromTop               = []
  genLepsFromWfromTop            = []
  genNusFromWfromTop             = []
  genTausFromTop                 = []
  genNusTauFromTop               = []
  genLepsFromTauFromTop          = []
  genNuLepFromTauFromTop         = []
  genNuTauFromLeptonicTauFromTop = []
  genNuTauFromHadronicTauFromTop = []
  genQuarkFromWfromTop           = []

  for genTopCandidateIdx, genTopCandidateDaughterIdxs in genTopCandidates.items():
    genTopCandidate = genParticles[genTopCandidateIdx]
    if len(genTopCandidateDaughterIdxs) != 2:
      raise ValueError("Invalid number of top (%s) decay products (%s): %i" % \
        (genTopCandidate, ', '.join(map(lambda idx: genParticles[idx], genTopCandidateDaughterIdxs)), len(genTopCandidateDaughterIdxs))
      )

    genWsfromTop = [ genParticles[idx] for idx in genTopCandidateDaughterIdxs if genParticles[idx].pdgId == 24 * sign(genTopCandidate.pdgId) ]
    genQsfromTop = [ genParticles[idx] for idx in genTopCandidateDaughterIdxs if sign(genTopCandidate.pdgId) * genParticles[idx].pdgId in [1, 3, 5] ]

    if len(genWsfromTop) != 1:
      raise ValueError("Not exactly 1 W boson found from top (%s) decay: %s" % \
        (genTopCandidate, ', '.join(map(lambda idx: str(genParticles[idx]), genTopCandidateDaughterIdxs)))
      )
    if len(genQsfromTop) != 1:
      raise ValueError("Not exactly 1 quark found from top (%s) decay: %s" % \
        (genTopCandidate, ', '.join(map(lambda idx: str(genParticles[idx]), genTopCandidateDaughterIdxs)))
      )

    if abs(genQsfromTop[0].pdgId) == 5:
      genBquarkFromTop.extend(genQsfromTop)
    if choice == SelectionOptions.SAVE_BQUARK_FROM_TOP:
      continue # skip the next part

    genWfromTop = genWsfromTop[0]
    # now search for leptons and/or taus which are descendant of the W boson
    # however, the W might ,,travel'' until it decays, i.e. its immediate daughter can be a single W boson
    # that's why we have to loop over the generator level particle collection and find out which W is the last one
    # in the top decay chain
    while genWfromTop.idx in genWMotherMap:
      genWfromTop = genParticles[genWMotherMap[genWfromTop.idx]]

    # let's look at W's decay products; possibilities include:
    # 1) leptonic: W -> l vl
    # 2) tauonic:  W -> tau vtau
    # 3) hadronic: W -> q q'

    genWfromTopDaughters = filter(lambda genPart: genPart.genPartIdxMother == genWfromTop.idx, genParticles)
    if len(genWfromTopDaughters) != 2:
      raise ValueError("Invalid number (%i) of W (%s) daughters from top (%s) decay: %s" % \
        (len(genWfromTopDaughters), genWfromTop, genTopCandidate, ', '.join(map(str, genWfromTopDaughters)))
      )

    if any(map(lambda genPart: abs(genPart.pdgId) in [11, 13], genWfromTopDaughters)):
      lepsFromWfromTop = filter(lambda genPart: -sign(genWfromTop.pdgId) * genPart.pdgId in [11, 13], genWfromTopDaughters)
      if len(lepsFromWfromTop) != 1:
        raise ValueError("Inconsistent W (%s) decay products from top (%s) decay: %s" % \
          (genWfromTop, genTopCandidate, ', '.join(map(str, genWfromTopDaughters)))
        )
      genLepFromWfromTop = lepsFromWfromTop[0]
      nusLepFromWfromTop = filter(lambda genPart: genPart.pdgId != sign(genWfromTop.pdgId) * (abs(genLepFromWfromTop.pdgId) + 1), genWfromTopDaughters)
      if len(nusLepFromWfromTop) != 1:
        raise ValueError("Inconsistent W (%s) decay products from top (%s) decay: %s" % \
          (genWfromTop, genTopCandidate, ', '.join(map(str, genWfromTopDaughters)))
        )
      genLepsFromWfromTop.extend(lepsFromWfromTop)
      genNusFromWfromTop.extend(nusLepFromWfromTop)
    elif any(map(lambda genPart: abs(genPart.pdgId) == 15, genWfromTopDaughters)):
      genTausFromWfromTop   = filter(lambda genPart: genPart.pdgId == -sign(genWfromTop.pdgId) * 15, genWfromTopDaughters)
      genNusTauFromWfromTop = filter(lambda genPart: genPart.pdgId ==  sign(genWfromTop.pdgId) * 16, genWfromTopDaughters)

      if len(genTausFromWfromTop) != 1 or len(genNusTauFromWfromTop) != 1:
        raise ValueError("Inconsistent W (%s) tauonic decay products from top (%s) decay: %s" % \
          (genWfromTop, genTopCandidate, ', '.join(map(str, genWfromTopDaughters)))
        )

      genTausFromTop.extend(genTausFromWfromTop)
      genNusTauFromTop.extend(genNusTauFromWfromTop)

      if choice not in [
          SelectionOptions.SAVE_LEPTON_FROM_TAU_FROM_TOP,
          SelectionOptions.SAVE_LEPTON_NU_FROM_TAU_FROM_TOP,
          SelectionOptions.SAVE_TAU_NU_FROM_LEPTONIC_TAU_FROM_TOP,
          SelectionOptions.SAVE_TAU_NU_FROM_HADRONIC_TAU_FROM_TOP,
        ]:
        continue

      genTauFromWfromTop = genTausFromWfromTop[0]
      # let's check tau decay products from t -> Wb, W -> tau vtau
      # map all mother taus to their daughters and pick the one we chose
      genTauMotherMap = {}
      for genPart in genParticles:
        if abs(genPart.pdgId) == 15:
          genTauMotherMap[genPart.genPartIdxMother] = genPart.idx

      genTauFromWfromTop_toDecay = genTauFromWfromTop
      while genTauFromWfromTop_toDecay.idx in genTauMotherMap:
        genTauFromWfromTop_toDecay = genParticles[genTauMotherMap[genTauFromWfromTop_toDecay.idx]]

      # now check tau decay products
      tauFromWfromTopDaughters = filter(lambda genPart: genPart.genPartIdxMother == genTauFromWfromTop_toDecay.idx, genParticles)
      if any(map(lambda genPart: abs(genPart.pdgId) in [11, 13], tauFromWfromTopDaughters)):
        # leptonic tau decay, record lepton, tau neutrino and lepton neutrino
        nusTauFromTauFromWfromTop = filter(lambda genPart: genPart.pdgId == 16 * sign(genTauFromWfromTop_toDecay.pdgId), tauFromWfromTopDaughters)
        if len(nusTauFromTauFromWfromTop) != 1:
          raise ValueError("Not enough tau neutrinos in leptonic tau (%s) decay from W (%s) from top (%s): %s"\
            (genTauFromWfromTop_toDecay, genWfromTop, genTopCandidate, ', '.join(map(str, tauFromWfromTopDaughters)))
          )
        lepsFromTauFromTauFromWfromTop = filter(lambda genPart: abs(genPart.pdgId) in [11, 13], tauFromWfromTopDaughters)
        if len(lepsFromTauFromTauFromWfromTop) != 1:
          raise ValueError("Too many leptons in leptonic tau (%s) decay from W (%s) from top (%s): %s"\
            (genTauFromWfromTop_toDecay, genWfromTop, genTopCandidate, ', '.join(map(str, tauFromWfromTopDaughters)))
          )
        nusLepFromTauFromWfromTop = filter(
          lambda genPart: genPart.pdgId == -sign(lepsFromTauFromTauFromWfromTop[0].pdgId) * (abs(lepsFromTauFromTauFromWfromTop[0].pdgId) + 1),
          tauFromWfromTopDaughters
        )
        if len(nusLepFromTauFromWfromTop) != 1:
          raise ValueError("Not enough lepton neutrinos in leptonic tau (%s) decay from W (%s) from top (%s): %s"\
            (genTauFromWfromTop_toDecay, genWfromTop, genTopCandidate, ', '.join(map(str, tauFromWfromTopDaughters)))
          )
        genLepsFromTauFromTop.extend(lepsFromTauFromTauFromWfromTop)
        genNuLepFromTauFromTop.extend(nusLepFromTauFromWfromTop)
        genNuTauFromLeptonicTauFromTop.extend(nusTauFromTauFromWfromTop)
      else:
        # hadronic tau decay, record the tau neutrinos only
        nusTauFromTauFromWfromTop = filter(lambda genPart: genPart.pdgId == 16 * sign(genTauFromWfromTop_toDecay.pdgId), tauFromWfromTopDaughters)
        if len(nusTauFromTauFromWfromTop) != 1:
          raise ValueError("Invalid hadronic tau (%s) decay products from W (%s) decay in top (%s) decay: %s" % \
            (genTauFromWfromTop_toDecay, genWfromTop, genTopCandidate, ', '.join(map(str, tauFromWfromTopDaughters)))
          )
        genNuTauFromHadronicTauFromTop.extend(nusTauFromTauFromWfromTop)
    elif all(map(lambda genPart: abs(genPart.pdgId) in [1, 2, 3, 4, 5], genWfromTopDaughters)):
      # hadronic case
      if enable_consistency_checks:
        genWfromTopDaughters_pdgIdSorted = list(sorted(genWfromTopDaughters, key = lambda genPart: abs(genPart.pdgId), reverse = True))
        if not ((genWfromTopDaughters_pdgIdSorted[0].pdgId == -5 * sign(genWfromTop.pdgId) and genWfromTopDaughters_pdgIdSorted[1].pdgId ==  4 * sign(genWfromTop.pdgId)) or \
                (genWfromTopDaughters_pdgIdSorted[0].pdgId == -5 * sign(genWfromTop.pdgId) and genWfromTopDaughters_pdgIdSorted[1].pdgId ==  2 * sign(genWfromTop.pdgId)) or \
                (genWfromTopDaughters_pdgIdSorted[0].pdgId ==  4 * sign(genWfromTop.pdgId) and genWfromTopDaughters_pdgIdSorted[1].pdgId == -3 * sign(genWfromTop.pdgId)) or \
                (genWfromTopDaughters_pdgIdSorted[0].pdgId ==  4 * sign(genWfromTop.pdgId) and genWfromTopDaughters_pdgIdSorted[1].pdgId == -1 * sign(genWfromTop.pdgId)) or \
                (genWfromTopDaughters_pdgIdSorted[0].pdgId == -3 * sign(genWfromTop.pdgId) and genWfromTopDaughters_pdgIdSorted[1].pdgId ==  2 * sign(genWfromTop.pdgId)) or \
                (genWfromTopDaughters_pdgIdSorted[0].pdgId ==  2 * sign(genWfromTop.pdgId) and genWfromTopDaughters_pdgIdSorted[1].pdgId == -1 * sign(genWfromTop.pdgId))):
          raise ValueError("Invalid hadronic W (%s) decay products from top (%s): %s" % \
            (genWfromTop, genTopCandidate, ', '.join(map(str, genWfromTopDaughters)))
          )
      genQuarkFromWfromTop.extend(genWfromTopDaughters)
    else:
      raise ValueError("Invalid W (%s) daughters from top (%s) decay: %s" % \
        (genWfromTop, genTopCandidate, ', '.join(map(str, genWfromTopDaughters)))
      )

  if choice == SelectionOptions.SAVE_BQUARK_FROM_TOP:
    return genBquarkFromTop
  if choice == SelectionOptions.SAVE_LEPTON_FROM_TOP:
    return genLepsFromWfromTop
  if choice == SelectionOptions.SAVE_LEPTONIC_NU_FROM_TOP:
    return genNusFromWfromTop
  if choice == SelectionOptions.SAVE_TAU_FROM_TOP:
    return genTausFromTop
  if choice == SelectionOptions.SAVE_TAU_NU_FROM_TOP:
    return genNusTauFromTop
  if choice == SelectionOptions.SAVE_TAU_NU_FROM_HADRONIC_TAU_FROM_TOP:
    return genNuTauFromHadronicTauFromTop
  if choice == SelectionOptions.SAVE_LEPTON_FROM_TAU_FROM_TOP:
    return genLepsFromTauFromTop
  if choice == SelectionOptions.SAVE_TAU_NU_FROM_LEPTONIC_TAU_FROM_TOP:
    return genNuTauFromLeptonicTauFromTop
  if choice == SelectionOptions.SAVE_LEPTON_NU_FROM_TAU_FROM_TOP:
    return genNuLepFromTauFromTop
  if choice == SelectionOptions.SAVE_QUARK_FROM_W_FROM_TOP:
    return genQuarkFromWfromTop

  raise ValueError("Invalid selection option: %i" % choice)

def genTauSelection(genParticles, choice, enable_consistency_checks = False):
  genTauMotherMap = {}
  for genPart in genParticles:
    if abs(genPart.pdgId) == 15:
      genTauMotherMap[genPart.idx] = genPart.genPartIdxMother

  genTauCandidates = {}
  for genTauIdx in genTauMotherMap:
    if genTauIdx not in genTauMotherMap.values():
      genTauCandidates[genTauIdx] = { 'daughters' : [], 'isLeptonic' : False }

  for genPart in genParticles:
    if genPart.genPartIdxMother in genTauCandidates:
      genTauCandidates[genPart.genPartIdxMother]['daughters'].append(genPart)
      genTauCandidates[genPart.genPartIdxMother]['isLeptonic'] = genTauCandidates[genPart.genPartIdxMother]['isLeptonic'] or \
                                                                 abs(genPart.pdgId) in [11, 13]

  # assert that the decay products of the leptonic taus are consistent
  if enable_consistency_checks:
    for genTauIdx in genTauCandidates:
      if genTauCandidates[genTauIdx]['isLeptonic']:
        genTauCurrent   = genParticles[genTauIdx]
        genTauDaughters = genTauCandidates[genTauIdx]['daughters']

        if len(genTauDaughters) != 3:
          raise ValueError("Not enough daughters in leptonic tau (%s) decay: %s" % \
            (genTauCurrent, ', '.join(map(str, genTauDaughters)))
          )
        genTauDaughterLep   = None
        genTauDaughterNuLep = None
        genTauDaughterNuTau = None
        for daughter in genTauDaughters:
          if abs(daughter.pdgId) in [11, 13]:
            genTauDaughterLep = daughter
          elif abs(daughter.pdgId) in [12, 14]:
            genTauDaughterNuLep = daughter
          elif abs(daughter.pdgId) == 16:
            genTauDaughterNuTau = daughter

        if genTauDaughterNuLep.pdgId is None:
          raise ValueError("Could not find lepton nu from leptonic tau (%s) decay (daughters: %s)" % \
            (genTauCurrent, ', '.join(map(str, genTauDaughters)))
          )
        if genTauDaughterNuTau.pdgId is None:
          raise ValueError("Could not find tau nu from leptonic tau (%s) decay (daughters: %s)" % \
            (genTauCurrent, ', '.join(map(str, genTauDaughters)))
          )

        if sign(genTauCurrent.pdgId) != sign(genTauDaughterLep.pdgId):
          raise ValueError("Wrong signs in tau (%s) and lepton charges (%s)" % (genTauCurrent, genTauDaughterLep))
        if sign(genTauDaughterLep.pdgId) * (abs(genTauDaughterLep.pdgId) + 1) != -genTauDaughterNuLep.pdgId:
          raise ValueError("Inconsistent pdgIds b/w lepton (%s) and lepton nu (%s) in leptonic tau decay" % \
            (genTauDaughterLep, genTauDaughterNuLep)
          )

  if choice == SelectionOptions.SAVE_TAU:
    return map(lambda genTauIdx: genParticles[genTauIdx], genTauCandidates)
  elif choice in [
      SelectionOptions.SAVE_HADRONIC_TAU,
      SelectionOptions.SAVE_TAU_NU_FROM_HADRONIC_TAU,
    ]:
    genHadronicTauIdxs = filter(lambda genTauIdx: not genTauCandidates[genTauIdx]['isLeptonic'], genTauCandidates)
    if choice == SelectionOptions.SAVE_HADRONIC_TAU:
      return map(lambda genLeptonicTauIdx: genParticles[genLeptonicTauIdx], genHadronicTauIdxs)

    genHadronicTauDaughterArrays = map(
      lambda genLeptonicTauIdx: genTauCandidates[genLeptonicTauIdx]['daughters'], genHadronicTauIdxs
    )
    genNusTauFromHadTaus = []
    for genHadronicTauDaughters in genHadronicTauDaughterArrays:
      for genHadronicTauDaughter in genHadronicTauDaughters:
        if abs(genHadronicTauDaughter.pdgId) == 16:
          genNusTauFromHadTaus.append(genHadronicTauDaughter)
    if choice == SelectionOptions.SAVE_TAU_NU_FROM_HADRONIC_TAU:
      return genNusTauFromHadTaus
  elif choice in [
      SelectionOptions.SAVE_LEPTONIC_TAU,
      SelectionOptions.SAVE_LEPTON_FROM_TAU,
      SelectionOptions.SAVE_LEPTONIC_NU_FROM_TAU,
      SelectionOptions.SAVE_TAU_NU_FROM_LEPTONIC_TAU,
    ]:
    genLeptonicTauIdxs = filter(lambda genTauIdx: genTauCandidates[genTauIdx]['isLeptonic'], genTauCandidates)
    if choice == SelectionOptions.SAVE_LEPTONIC_TAU:
      return map(lambda genLeptonicTauIdx: genParticles[genLeptonicTauIdx], genLeptonicTauIdxs)

    genLeptonicTauDaughterArrays = map(
      lambda genLeptonicTauIdx: genTauCandidates[genLeptonicTauIdx]['daughters'], genLeptonicTauIdxs
    )
    genLeptonsFromTaus, genNusLepFromTaus, genNusTauFromLepTaus = [], [], []
    for genLeptonicTauDaughters in genLeptonicTauDaughterArrays:
      for genLeptonicTauDaughter in genLeptonicTauDaughters:
        if abs(genLeptonicTauDaughter.pdgId) in [11, 13]:
          genLeptonsFromTaus.append(genLeptonicTauDaughter)
        elif abs(genLeptonicTauDaughter.pdgId) in [12, 14]:
          genNusLepFromTaus.append(genLeptonicTauDaughter)
        elif abs(genLeptonicTauDaughter.pdgId) == 16:
          genNusTauFromLepTaus.append(genLeptonicTauDaughter)

    if choice == SelectionOptions.SAVE_LEPTON_FROM_TAU:
      return genLeptonsFromTaus
    if choice == SelectionOptions.SAVE_LEPTONIC_NU_FROM_TAU:
      return genNusLepFromTaus
    if choice == SelectionOptions.SAVE_TAU_NU_FROM_LEPTONIC_TAU:
      return genNusTauFromLepTaus
  else:
    raise ValueError("Choice %i not implemented" % choice)


class genParticleProducer(Module):

  def __init__(self, genEntry, verbose = False):
    self.massTable = MassTable()
    self.branchLenNames  = {}
    self.selections      = {}
    self.branchBaseNames = []

    self.genBranches = {
        "pt"          : "F",
        "eta"         : "F",
        "phi"         : "F",
        "mass"        : "F",
        "pdgId"       : "I",
        "charge"      : "I",
        "status"      : "I",
        "statusFlags" : "I",
      }

    for branchBaseName, selection in genEntry.items():
      self.branchBaseNames.append(branchBaseName)
      self.selections[branchBaseName]     = selection
      self.branchLenNames[branchBaseName] = "n%s" % branchBaseName

    if verbose:
      logging.getLogger().setLevel(logging.DEBUG)

  def beginJob(self):
    pass

  def endJob(self):
    pass

  def beginFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
    self.out = wrappedOutputTree
    for branchBaseName in self.branchBaseNames:
      for branchName, branchType in self.genBranches.items():
        self.out.branch(
          "%s_%s" % (branchBaseName, branchName),
          branchType,
          lenVar = self.branchLenNames[branchBaseName]
        )

  def endFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
    pass

  def analyze(self, event):
    genParticles  = map(lambda genPartIdx: GenPartAux(genPartIdx[1], genPartIdx[0], self.massTable), enumerate(Collection(event, "GenPart")))

    for branchBaseName in self.branchBaseNames:
      gen_arr = self.selections[branchBaseName](genParticles)
      gen_arr = list(sorted(gen_arr, key = lambda genPart: genPart.pt, reverse = True)) # sort by pT
      for branchName, branchType in self.genBranches.items():
        self.out.fillBranch(
          "%s_%s" % (branchBaseName, branchName),
          map(lambda genPart: getattr(genPart, branchName), gen_arr)
        )
    return True


genLeptonEntry                      = ("GenLep",                         genPromptLeptonSelection)
genLeptonAllEntry                   = ("GenLepAll",                      genLeptonSelection)
genPromptPhotonEntry                = ("GenPhoton",                      genPromptPhotonSelection)
genPhotonAllEntry                   = ("GenPhotonAll",                   genPhotonSelection)
genHiggsEntry                       = ("GenHiggs",                       genHiggsSelection)
genHiggsDaughtersEntry              = ("GenHiggsDaughters",              genHiggsDaughtersSelection)
genNuEntry                          = ("GenNu",                          genNuSelection)
genWZquarkEntry                     = ("GenWZQuark",                     genWZquarkSelection)
genVbosonEntry                      = ("GenVbosons",                     genVbosonSelection)
genTauEntry                         = ("GenTau",                         (lambda genParticles : genTauSelection(genParticles, SelectionOptions.SAVE_TAU)))
genLeptonicTauEntry                 = ("GenLeptonicTau",                 (lambda genParticles : genTauSelection(genParticles, SelectionOptions.SAVE_LEPTONIC_TAU)))
genHadronicTauEntry                 = ("GenHadronicTau",                 (lambda genParticles : genTauSelection(genParticles, SelectionOptions.SAVE_HADRONIC_TAU)))
genLepFromTauEntry                  = ("GenLepFromTau",                  (lambda genParticles : genTauSelection(genParticles, SelectionOptions.SAVE_LEPTON_FROM_TAU)))
genNuLepFromTauEntry                = ("GenNuLepFromTau",                (lambda genParticles : genTauSelection(genParticles, SelectionOptions.SAVE_LEPTONIC_NU_FROM_TAU)))
genNuTauFromLeptonicTauEntry        = ("GenNuTauFromLeptonicTau",        (lambda genParticles : genTauSelection(genParticles, SelectionOptions.SAVE_TAU_NU_FROM_LEPTONIC_TAU)))
genNuTauFromHadronicTauEntry        = ("GenNuTauFromHadronicTau",        (lambda genParticles : genTauSelection(genParticles, SelectionOptions.SAVE_TAU_NU_FROM_HADRONIC_TAU)))
genTopEntry                         = ("GenTop",                         (lambda genParticles : genTopSelection(genParticles, SelectionOptions.SAVE_TOP)))
genLepFromTopEntry                  = ("GenLepFromTop",                  (lambda genParticles : genTopSelection(genParticles, SelectionOptions.SAVE_LEPTON_FROM_TOP)))
genNuFromTopEntry                   = ("GenNuFromTop",                   (lambda genParticles : genTopSelection(genParticles, SelectionOptions.SAVE_LEPTONIC_NU_FROM_TOP)))
genTauFromTopEntry                  = ("GenTauFromTop",                  (lambda genParticles : genTopSelection(genParticles, SelectionOptions.SAVE_TAU_FROM_TOP)))
genNuTauFromTopEntry                = ("GenNuTauFromTop",                (lambda genParticles : genTopSelection(genParticles, SelectionOptions.SAVE_TAU_NU_FROM_TOP)))
genNuFromHadronicTauFromTopEntry    = ("GenNuFromHadronicTauFromTop",    (lambda genParticles : genTopSelection(genParticles, SelectionOptions.SAVE_TAU_NU_FROM_HADRONIC_TAU_FROM_TOP)))
genNuFromLeptonicTauFromTopEntry    = ("GenNuFromLeptonicTauFromTop",    (lambda genParticles : genTopSelection(genParticles, SelectionOptions.SAVE_TAU_NU_FROM_LEPTONIC_TAU_FROM_TOP)))
genNuTauFromLeptonicTauFromTopEntry = ("GenNuTauFromLeptonicTauFromTop", (lambda genParticles : genTopSelection(genParticles, SelectionOptions.SAVE_LEPTON_NU_FROM_TAU_FROM_TOP)))
genLepFromTauFromTopEntry           = ("GenLepFromTauFromTop",           (lambda genParticles : genTopSelection(genParticles, SelectionOptions.SAVE_LEPTON_FROM_TAU_FROM_TOP)))
genQuarkFromTopEntry                = ("GenQuarkFromTop",                (lambda genParticles : genTopSelection(genParticles, SelectionOptions.SAVE_QUARK_FROM_W_FROM_TOP)))
genBQuarkFromTopEntry               = ("GenBQuarkFromTop",               (lambda genParticles : genTopSelection(genParticles, SelectionOptions.SAVE_BQUARK_FROM_TOP)))

# provide these variables as the 2nd arguments to the import option for the nano_postproc.py script
genLepton                      = lambda : genParticleProducer(dict([genLeptonEntry]))                      # all prompt stable leptons
genLeptonAll                   = lambda : genParticleProducer(dict([genLeptonAllEntry]))                   # all stable leptons
genPromptPhoton                = lambda : genParticleProducer(dict([genPromptPhotonEntry]))                # stable prompt photons
genPhotonAll                   = lambda : genParticleProducer(dict([genPhotonAllEntry]))                   # all photons
genHiggs                       = lambda : genParticleProducer(dict([genHiggsEntry]))                       # all Higgs (first in the decay chain)
genHiggsDaughters              = lambda : genParticleProducer(dict([genHiggsDaughtersEntry]))              # all Higgs daughters
genTau                         = lambda : genParticleProducer(dict([genTauEntry]))                         # all taus
genNu                          = lambda : genParticleProducer(dict([genNuEntry]))                          # all neutrinos
genWZquark                     = lambda : genParticleProducer(dict([genWZquarkEntry]))                     # all quarks coming from W or Z decay
genVboson                      = lambda : genParticleProducer(dict([genVbosonEntry]))                      # all W and Z bosons (first in the decay chain)
genLeptonicTau                 = lambda : genParticleProducer(dict([genLeptonicTauEntry]))                 # only taus (tau(l)) decaying leptonically: tau(l) -> l vl vtau
genHadronicTau                 = lambda : genParticleProducer(dict([genHadronicTauEntry]))                 # only taus (tau(h)) decaying hadronically: tau(h) -> tauh vtau (NB! NOT RECONSTRUCTED GEN HAD TAU!)
genLepFromTau                  = lambda : genParticleProducer(dict([genLepFromTauEntry]))                  # only leptons (l) coming from tau decay: tau -> l vl vtau
genNuLepFromTau                = lambda : genParticleProducer(dict([genNuLepFromTauEntry]))                # only lepton neutrinos (vl) coming from tau decay: tau -> l vl vtau
genNuTauFromLeptonicTau        = lambda : genParticleProducer(dict([genNuTauFromLeptonicTauEntry]))        # only tau neutrinos (vtau) coming from leptonic tau decay: tau -> l vl vtau
genNuTauFromHadronicTau        = lambda : genParticleProducer(dict([genNuTauFromHadronicTauEntry]))        # only tau neutrinos (vtau) coming from hadronic tau decay: tau -> tauh vtau
genTop                         = lambda : genParticleProducer(dict([genTopEntry]))                         # all tops
genLepFromTop                  = lambda : genParticleProducer(dict([genLepFromTopEntry]))                  # only leptons (l) from t -> W b, W -> l vl decay
genNuFromTop                   = lambda : genParticleProducer(dict([genNuFromTopEntry]))                   # only lepton neutrinos (vl) from t -> W b, W -> l vl decay
genTauFromTop                  = lambda : genParticleProducer(dict([genTauFromTopEntry]))                  # only taus (tau) from t -> W b, W -> tau vtau decay
genNuTauFromTop                = lambda : genParticleProducer(dict([genNuTauFromTopEntry]))                # only tau neutrinos (vtau) from t -> W b, W -> tau vtau decay
genNuFromHadronicTauFromTop    = lambda : genParticleProducer(dict([genNuFromHadronicTauFromTopEntry]))    # only tau neutrinos (vtau2) from t -> W b, W -> tau vtau, tau -> tauh vtau2 decay
genNuFromLeptonicTauFromTop    = lambda : genParticleProducer(dict([genNuFromLeptonicTauFromTopEntry]))    # only tau neutrinos (vtau2) from t -> W b, W -> tau vtau, tau -> l vl vtau2 decay
genNuTauFromLeptonicTauFromTop = lambda : genParticleProducer(dict([genNuTauFromLeptonicTauFromTopEntry])) # only lepton neutrinos (vl) from t -> W b, W -> tau vtau, tau -> l vl vtau2 decay
genLepFromTauFromTop           = lambda : genParticleProducer(dict([genLepFromTauFromTopEntry]))           # only leptons (l) from t -> W b, W -> tau vtau, tau -> l vl vtau2 decay
genQuarkFromTop                = lambda : genParticleProducer(dict([genQuarkFromTopEntry]))                # only quarks (q, q') from t -> W b, W -> q q' decay
genBQuarkFromTop               = lambda : genParticleProducer(dict([genBQuarkFromTopEntry]))               # only b-quarks (b) from t -> W b

genAll = lambda : genParticleProducer(dict([
    genLeptonEntry,
    genLeptonAllEntry,
    genPromptPhotonEntry,
    genPhotonAllEntry,
    genHiggsEntry,
    genHiggsDaughtersEntry,
    genNuEntry,
    genWZquarkEntry,
    genVbosonEntry,
    genTauEntry,
    genLeptonicTauEntry,
    genHadronicTauEntry,
    genLepFromTauEntry,
    genNuLepFromTauEntry,
    genNuTauFromLeptonicTauEntry,
    genNuTauFromHadronicTauEntry,
    genTopEntry,
    genLepFromTopEntry,
    genNuFromTopEntry,
    genTauFromTopEntry,
    genNuTauFromTopEntry,
    genNuFromHadronicTauFromTopEntry,
    genNuFromLeptonicTauFromTopEntry,
    genNuTauFromLeptonicTauFromTopEntry,
    genLepFromTauFromTopEntry,
    genQuarkFromTopEntry,
    genBQuarkFromTopEntry,
  ]))
