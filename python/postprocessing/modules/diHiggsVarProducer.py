import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True

from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import Collection
from PhysicsTools.NanoAODTools.postprocessing.framework.eventloop import Module

from HHStatAnalysis.AnalyticalModels.NonResonantModel import NonResonantModel

import os

def get_p4(higgs):
  higgs_p4 = ROOT.TLorentzVector()
  higgs_p4.SetPtEtaPhiM(higgs.pt, higgs.eta, higgs.phi, higgs.mass)
  return higgs_p4

def get_p4_pair(higgsArr):
  return get_p4(higgsArr[0]), get_p4(higgsArr[1])

class diHiggsVarProducer(Module):

  def __init__(self, era, use_gen = True, use_lhe = True, compute_weights = False):
    self.use_gen = use_gen
    self.use_lhe = use_lhe
    assert(self.use_gen or self.use_lhe)
    self.compute_weights = compute_weights

    if self.use_gen:
      print("Computing di-Higgs variables from generator-level Higgs bosons")
    else:
      print("NOT computing di-Higgs variables from generator-level Higgs bosons")
    if self.use_lhe:
      print("Computing di-Higgs variables from LHE parton-level Higgs bosons")
    else:
      print("NOT computing di-Higgs variables from LHE parton-level Higgs bosons")
    if self.compute_weights:
      print("Also computing the di-Higgs event-level weights")
    else:
      print("NOT computing the di-Higgs event-level weights")

    mHH_name = "mHH"
    cosThetaStar_name = "cosThetaStar"
    gen_suffix = "gen"
    lhe_suffix = "lhe"

    self.mHH_genName = "{}_{}".format(mHH_name, gen_suffix)
    self.cosThetaStar_genName = "{}_{}".format(cosThetaStar_name, gen_suffix)
    self.mHH_lheName = "{}_{}".format(mHH_name, lhe_suffix)
    self.cosThetaStar_lheName = "{}_{}".format(cosThetaStar_name, lhe_suffix)

    weightBaseName = "HHWeight"
    BMName = "BM"
    scanName = "scan"

    self.nofWeightsBMName = "n{}_{}".format(weightBaseName, BMName)
    self.weightBM_genName = "{}_{}_{}".format(weightBaseName, BMName, gen_suffix)
    self.weightBM_lheName = "{}_{}_{}".format(weightBaseName, BMName, lhe_suffix)

    self.nofWeightsScanName = "n{}_{}".format(weightBaseName, scanName)
    self.weightScan_genName = "{}_{}_{}".format(weightBaseName, scanName, gen_suffix)
    self.weightScan_lheName = "{}_{}_{}".format(weightBaseName, scanName, lhe_suffix)

    os.environ["MKL_NUM_THREADS"] = "1"

    cmssw_base = os.path.join(os.environ['CMSSW_BASE'], "src")
    coeffFile = os.path.join(
      cmssw_base, "HHStatAnalysis/AnalyticalModels/data/coefficientsByBin_extended_3M_costHHSim_19-4.txt"
    )
    self.model = None
    if self.compute_weights:
      assert (os.path.isfile(coeffFile))
      self.model = NonResonantModel()
      self.model.ReadCoefficients(coeffFile)

    denominatorHistogramName = "denominator_reweighting"
    denominatorFile = os.path.join(
      cmssw_base, "hhAnalysis/bbww/data/denominator_reweighting_bbvv_{}.root".format(era)
    )
    self.denominatorFilePtr = None
    self.denominatorHistogram = None
    if self.compute_weights:
      assert (os.path.isfile(denominatorFile))
      self.denominatorFilePtr = ROOT.TFile.Open(denominatorFile, "READ")
      assert(self.denominatorFilePtr)
      assert(denominatorHistogramName in [ key.GetName() for key in self.denominatorFilePtr.GetListOfKeys() ])
      self.denominatorHistogram = self.denominatorFilePtr.Get(denominatorHistogramName)

    scanFile = os.path.join(cmssw_base, "hhAnalysis/bbww/data/kl_scan.dat")
    self.nofWeightsScan = 0
    self.klScan      = []
    self.ktScan      = []
    self.c2Scan      = []
    self.cgScan      = []
    self.c2gScan     = []
    self.BM_klScan   = []
    self.Norm_klScan = []
    if self.compute_weights:
      assert (os.path.isfile(scanFile))
      with open(scanFile, 'r') as scanFileObj:
        for line in scanFileObj:
          line_split = line.rstrip('\n').split()
          if len(line_split) != 7:
            continue
          self.klScan.append     (float(line_split[0]))
          self.ktScan.append     (float(line_split[1]))
          self.c2Scan.append     (float(line_split[2]))
          self.cgScan.append     (float(line_split[3]))
          self.c2gScan.append    (float(line_split[4]))
          self.BM_klScan.append  (float(line_split[5]))
          self.Norm_klScan.append(float(line_split[6]))
      self.nofWeightsScan = len(self.klScan)
      assert(
        len(self.ktScan)      == self.nofWeightsScan and
        len(self.c2Scan)      == self.nofWeightsScan and
        len(self.cgScan)      == self.nofWeightsScan and
        len(self.c2gScan)     == self.nofWeightsScan and
        len(self.BM_klScan)   == self.nofWeightsScan and
        len(self.Norm_klScan) == self.nofWeightsScan
      )
      print("Using %d points to scan" % self.nofWeightsScan)

    self.nofWeightsBM = 13
    self.klJHEP   = [ 1.0,     7.5,     1.0,     1.0,    -3.5,     1.0,     2.4,     5.0,    15.0,     1.0,    10.0,     2.4,    15.0     ]
    self.ktJHEP   = [ 1.0,     1.0,     1.0,     1.0,     1.5,     1.0,     1.0,     1.0,     1.0,     1.0,     1.5,     1.0,     1.0     ]
    self.c2JHEP   = [ 0.0,    -1.0,     0.5,    -1.5,    -3.0,     0.0,     0.0,     0.0,     0.0,     1.0,    -1.0,     0.0,     1.0     ]
    self.cgJHEP   = [ 0.0,     0.0,    -0.8,     0.0,     0.0,     0.8,     0.2,     0.2,    -1.0,    -0.6,     0.0,     1.0,     0.0     ]
    self.c2gJHEP  = [ 0.0,     0.0,     0.6,    -0.8,     0.0,    -1.0,    -0.2,    -0.2,     1.0,     0.6,     0.0,    -1.0,     0.0     ]
    self.normJHEP = [ 0.99997, 0.94266, 0.71436, 0.95608, 0.97897, 0.87823, 0.95781, 1.00669, 0.92494, 0.86083, 1.00658, 0.95096, 1.00063 ]
    assert(
      len(self.klJHEP)   == self.nofWeightsBM and
      len(self.ktJHEP)   == self.nofWeightsBM and
      len(self.c2JHEP)   == self.nofWeightsBM and
      len(self.cgJHEP)   == self.nofWeightsBM and
      len(self.c2gJHEP)  == self.nofWeightsBM and
      len(self.normJHEP) == self.nofWeightsBM
    )
    print("Using %d JHEP BMs" % self.nofWeightsBM)

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
    if self.compute_weights:
      self.out.branch(self.nofWeightsBMName, "I")
      self.out.branch(self.nofWeightsScanName, "I")
      if self.use_gen:
        self.out.branch(self.weightBM_genName, "F", lenVar = self.nofWeightsBMName)
        self.out.branch(self.weightScan_genName, "F", lenVar = self.nofWeightsScanName)
      if self.use_lhe:
        self.out.branch(self.weightBM_lheName, "F", lenVar = self.nofWeightsBMName)
        self.out.branch(self.weightScan_lheName, "F", lenVar = self.nofWeightsScanName)

  def endFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
    if self.denominatorFilePtr:
      self.denominatorFilePtr.Close()

  def get_denominator(self, mHH, cosThetaStar):
    assert(self.denominatorHistogram)
    mHH_bin = self.denominatorHistogram.GetXaxis().FindBin(mHH)
    cosThetaStar_bin = self.denominatorHistogram.GetYaxis().FindBin(abs(cosThetaStar))
    return self.denominatorHistogram.GetBinContent(mHH_bin, cosThetaStar_bin)
  
  def compute(self, higgses):
    higgs_lead_p4, higgs_sublead_p4 = get_p4_pair(higgses)
    higgs_pair_p4 = higgs_lead_p4 + higgs_sublead_p4
    mHH = higgs_pair_p4.M()

    # boost leading or subleading Higgs -- doesn't matter
    higgs_lead_p4.Boost(-higgs_pair_p4.BoostVector())
    cosThetaStar = abs(higgs_lead_p4.CosTheta())
    denominator = self.get_denominator(mHH, cosThetaStar) if self.compute_weights else 1.

    weightsBM = [ 0. ] * self.nofWeightsBM
    if self.compute_weights:
      weightsBM = []
      for bmIdx in range(self.nofWeightsBM):
        weightBM = self.model.getScaleFactor(
          mhh      = mHH,
          cost     = cosThetaStar,
          kl       = self.klJHEP[bmIdx],
          kt       = self.ktJHEP[bmIdx],
          c2       = 0.,
          cg       = 0.,
          c2g      = 0.,
          effSumV0 = denominator,
          Cnorm    = self.normJHEP[bmIdx],
        )
        weightsBM.append(weightBM)

    weightsScan = [ 0. ] * self.nofWeightsScan
    if self.compute_weights:
      weightsScan = []
      for bmIdx in range(self.nofWeightsScan):
        weightScan = self.model.getScaleFactor(
          mhh      = mHH,
          cost     = cosThetaStar,
          kl       = self.klScan[bmIdx],
          kt       = self.ktScan[bmIdx],
          c2       = 0.,
          cg       = 0.,
          c2g      = 0.,
          effSumV0 = denominator,
          Cnorm    = self.Norm_klScan[bmIdx],
        )
        weightsScan.append(weightScan)

    return mHH, cosThetaStar, weightsBM, weightsScan

  def analyze(self, event):

    weightsBM_gen   = [ 0. ] * self.nofWeightsBM
    weightsScan_gen = [ 0. ] * self.nofWeightsScan
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
        mHH_gen, cosThetaStar_gen, weightsBM_gen, weightsScan_gen = self.compute(higgses_gen)
      else:
        print("Found an event that has not exactly two Higgs bosons at the generator level")

    weightsBM_lhe   = [ 0. ] * self.nofWeightsBM
    weightsScan_lhe = [ 0. ] * self.nofWeightsScan
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
        mHH_lhe, cosThetaStar_lhe, weightsBM_lhe, weightsScan_lhe = self.compute(higgses_lhe)

        if self.use_gen:
          assert(len(weightsBM_gen) == len(weightsBM_lhe))
          assert(len(weightsScan_gen) == len(weightsScan_lhe))
      else:
        print("Found an event that has not exactly two Higgs bosons at the LHE parton level")

    if self.use_gen:
      self.out.fillBranch(self.mHH_genName, mHH_gen)
      self.out.fillBranch(self.cosThetaStar_genName, cosThetaStar_gen)
    if self.use_lhe:
      self.out.fillBranch(self.mHH_lheName, mHH_lhe)
      self.out.fillBranch(self.cosThetaStar_lheName, cosThetaStar_lhe)
    if self.compute_weights:
      self.out.fillBranch(self.nofWeightsBMName, len(weightsBM_gen))
      self.out.fillBranch(self.nofWeightsScanName, len(weightsScan_gen))
      if self.use_gen:
        self.out.fillBranch(self.weightBM_genName, weightsBM_gen)
        self.out.fillBranch(self.weightScan_genName, weightsScan_gen)
      if self.use_lhe:
        self.out.fillBranch(self.weightBM_lheName, weightsBM_lhe)
        self.out.fillBranch(self.weightScan_lheName, weightsScan_lhe)

    return True

# provide this variable as the 2nd argument to the import option for the nano_postproc.py script
diHiggsVar_2016 = lambda : diHiggsVarProducer(era = "2016")
diHiggsVar_2017 = lambda : diHiggsVarProducer(era = "2017")
diHiggsVar_2018 = lambda : diHiggsVarProducer(era = "2018")
