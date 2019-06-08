import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True

from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import Collection
from PhysicsTools.NanoAODTools.postprocessing.framework.eventloop import Module

def get_p4(higgs):
  higgs_p4 = ROOT.TLorentzVector()
  higgs_p4.SetPtEtaPhiM(higgs.pt, higgs.eta, higgs.phi, higgs.mass)
  return higgs_p4

def get_p4_pair(higgsArr):
  return get_p4(higgsArr[0]), get_p4(higgsArr[1])

class diHiggsVarProducer(Module):

  def __init__(self, use_gen = True, use_lhe = True):
    self.use_gen = use_gen
    self.use_lhe = use_lhe
    assert(self.use_gen or self.use_lhe)

    mHH_name = "mHH"
    cosThetaStar_name = "cosThetaStar"
    gen_suffix = "gen"
    lhe_suffix = "lhe"

    self.mHH_genName = "{}_{}".format(mHH_name, gen_suffix)
    self.cosThetaStar_genName = "{}_{}".format(cosThetaStar_name, gen_suffix)
    self.mHH_lheName = "{}_{}".format(mHH_name, lhe_suffix)
    self.cosThetaStar_lheName = "{}_{}".format(cosThetaStar_name, lhe_suffix)

  def beginJob(self):
    pass

  def endJob(self):
    pass

  def beginFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
    self.out = wrappedOutputTree
    if self.use_gen:
      self.out.branch(self.mHH_genName, "F")
      self.out.branch(self.cosThetaStar_genName, "F")
    if self.use_lhe:
      self.out.branch(self.mHH_lheName, "F")
      self.out.branch(self.cosThetaStar_lheName, "F")

  def endFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
    pass

  def analyze(self, event):

    mHH_gen, cosThetaStar_gen = -1., -2.
    if self.use_gen:
      genParticles = Collection(event, "GenPart")
      higgses_gen = sorted(
        filter(
          lambda genPart:
            genPart.pdgId == 25 and \
            (genParticles[genPart.genPartIdxMother].pdgId != 25 if genPart.genPartIdxMother >= 0 else True),
          genParticles
        ),
        key = lambda genHiggs: genHiggs.pt,
        reverse = True
      )
      nofHiggs_gen = len(higgses_gen)

      if nofHiggs_gen == 2:
        genHiggs_lead_p4, genHiggs_sublead_p4 = get_p4_pair(higgses_gen)
        mHH_gen = (genHiggs_lead_p4 + genHiggs_sublead_p4).M()
        cosThetaStar_gen = genHiggs_lead_p4.CosTheta()

    mHH_lhe, cosThetaStar_lhe = -1., -2.
    if self.use_lhe:
      lheParticles = Collection(event, "LHEPart")
      higgses_lhe = sorted(
        filter(lambda lhePart: lhePart.pdgId == 25, lheParticles),
        key = lambda lheHiggs: get_p4(lheHiggs).E(),  # sort by energy b/c pT is the same
        reverse = True
      )
      nofHiggs_lhe = len(higgses_lhe)

      if nofHiggs_lhe == 2:
        lheHiggs_lead_p4, lheHiggs_sublead_p4 = get_p4_pair(higgses_lhe)
        mHH_lhe = (lheHiggs_lead_p4 + lheHiggs_sublead_p4).M()
        cosThetaStar_lhe = lheHiggs_lead_p4.CosTheta()

    if self.use_gen:
      self.out.fillBranch(self.mHH_genName, mHH_gen)
      self.out.fillBranch(self.cosThetaStar_genName, cosThetaStar_gen)

    if self.use_lhe:
      self.out.fillBranch(self.mHH_lheName, mHH_lhe)
      self.out.fillBranch(self.cosThetaStar_lheName, cosThetaStar_lhe)

    return True

# provide this variable as the 2nd argument to the import option for the nano_postproc.py script
diHiggsVar = lambda : diHiggsVarProducer()
