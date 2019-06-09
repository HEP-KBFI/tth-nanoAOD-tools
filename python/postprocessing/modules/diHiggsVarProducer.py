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

  def __init__(self, era, use_gen = True, use_lhe = True):
    self.use_gen = use_gen
    self.use_lhe = use_lhe
    self.era = era
    assert(self.use_gen or self.use_lhe)

    mHH_name = "mHH"
    cosThetaStar_name = "cosThetaStar"
    gen_suffix = "gen"
    lhe_suffix = "lhe"

    self.mHH_genName = "{}_{}".format(mHH_name, gen_suffix)
    self.cosThetaStar_genName = "{}_{}".format(cosThetaStar_name, gen_suffix)
    self.mHH_lheName = "{}_{}".format(mHH_name, lhe_suffix)
    self.cosThetaStar_lheName = "{}_{}".format(cosThetaStar_name, lhe_suffix)

    os.environ["MKL_NUM_THREADS"] = "1"

    self.cmssw_base = os.path.join(os.environ['CMSSW_BASE'], "src")
    self.coeffFile = os.path.join(
      self.cmssw_base, "HHStatAnalysis/AnalyticalModels/data/coefficientsByBin_extended_3M_costHHSim_19-4.txt"
    )
    assert(os.path.isfile(self.coeffFile))
    self.model = NonResonantModel()
    self.model.ReadCoefficients(self.coeffFile)

    self.scanFile = os.path.join(self.cmssw_base, "hhAnalysis/bbww/data/kl_scan.dat")
    assert(os.path.isfile(self.scanFile))

    self.denominatorFile = os.path.join(
      self.cmssw_base, "hhAnalysis/bbww/data/denominator_reweighting_bbvv_{}.root".format(era)
    )
    assert(os.path.isfile(self.denominatorFile))
    self.denominatorFilePtr = ROOT.TFile.Open(self.denominatorFile, "READ")
    assert(self.denominatorFilePtr)
    self.denominatorHistogramName = "denominator_reweighting"
    assert(self.denominatorHistogramName in [ key.GetName() for key in self.denominatorFilePtr.GetListOfKeys() ])
    self.denominatorHistogram = self.denominatorFilePtr.Get(self.denominatorHistogramName)

    self.klScan      = []
    self.ktScan      = []
    self.c2Scan      = []
    self.cgScan      = []
    self.c2gScan     = []
    self.BM_klScan   = []
    self.Norm_klScan = []

    with open(self.scanFile, 'r') as scanFileObj:
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

    self.weightBaseName = "HHWeight"
    self.BMName = "BM"
    self.scanName = "scan"

    self.nofWeightsBMName = "n{}_{}".format(self.weightBaseName, self.BMName)
    self.weightBM_genName = "{}_{}_{}".format(self.weightBaseName, self.BMName, gen_suffix)
    self.weightBM_lheName = "{}_{}_{}".format(self.weightBaseName, self.BMName, lhe_suffix)

    self.nofWeightsScanName = "n{}_{}".format(self.weightBaseName, self.scanName)
    self.weightScan_genName = "{}_{}_{}".format(self.weightBaseName, self.scanName, gen_suffix)
    self.weightScan_lheName = "{}_{}_{}".format(self.weightBaseName, self.scanName, lhe_suffix)

  def beginJob(self):
    pass

  def endJob(self):
    pass

  def beginFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
    self.out = wrappedOutputTree
    self.out.branch(self.nofWeightsBMName, "I")
    self.out.branch(self.nofWeightsScanName, "I")
    if self.use_gen:
      self.out.branch(self.mHH_genName, "F")
      self.out.branch(self.cosThetaStar_genName, "F")
      self.out.branch(self.weightBM_genName, "F", lenVar = self.nofWeightsBMName)
      self.out.branch(self.weightScan_genName, "F", lenVar = self.nofWeightsScanName)
    if self.use_lhe:
      self.out.branch(self.mHH_lheName, "F")
      self.out.branch(self.cosThetaStar_lheName, "F")
      self.out.branch(self.weightBM_lheName, "F", lenVar = self.nofWeightsBMName)
      self.out.branch(self.weightScan_lheName, "F", lenVar = self.nofWeightsScanName)

  def endFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
    self.denominatorFilePtr.Close()

  def get_denominator(self, mHH, cosThetaStar):
    mHH_bin = self.denominatorHistogram.GetXaxis().FindBin(mHH)
    cosThetaStar_bin = self.denominatorHistogram.GetYaxis().FindBin(abs(cosThetaStar))
    return self.denominatorHistogram.GetBinContent(mHH_bin, cosThetaStar_bin)

  def analyze(self, event):

    weightsBM_gen   = [ 0. * self.nofWeightsBM   ]
    weightsScan_gen = [ 0. * self.nofWeightsScan ]
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
        genHiggs_pair_p4 = genHiggs_lead_p4 + genHiggs_sublead_p4
        mHH_gen = genHiggs_pair_p4.M()

        # boost leading or subleading Higgs -- doesn't matter
        genHiggs_lead_p4.Boost(-genHiggs_pair_p4.BoostVector())
        cosThetaStar_gen = abs(genHiggs_lead_p4.CosTheta())
        denominator = self.get_denominator(mHH_gen, cosThetaStar_gen)

        weightsBM_gen = []
        for bmIdx in range(self.nofWeightsBM):
          weightBM_gen = self.model.getScaleFactor(
            mhh      = mHH_gen,
            cost     = cosThetaStar_gen,
            kl       = self.klJHEP[bmIdx],
            kt       = self.ktJHEP[bmIdx],
            c2       = 0.,
            cg       = 0.,
            c2g      = 0.,
            effSumV0 = denominator,
            Cnorm    = self.normJHEP[bmIdx],
          )
          weightsBM_gen.append(weightBM_gen)
        
        weightsScan_gen = []
        for bmIdx in range(self.nofWeightsScan):
          weightScan_gen = self.model.getScaleFactor(
            mhh      = mHH_gen,
            cost     = cosThetaStar_gen,
            kl       = self.klScan[bmIdx],
            kt       = self.ktScan[bmIdx],
            c2       = 0.,
            cg       = 0.,
            c2g      = 0.,
            effSumV0 = denominator,
            Cnorm    = self.Norm_klScan[bmIdx],
          )
          weightsScan_gen.append(weightScan_gen)

    weightsBM_lhe   = [ 0. * self.nofWeightsBM ]
    weightsScan_lhe = [ 0. * self.nofWeightsScan ]
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
        lheHiggs_pair_p4 = lheHiggs_lead_p4 + lheHiggs_sublead_p4
        mHH_lhe = lheHiggs_pair_p4.M()

        # boost leading or subleading Higgs -- doesn't matter
        lheHiggs_lead_p4.Boost(-lheHiggs_pair_p4.BoostVector())
        cosThetaStar_lhe = abs(lheHiggs_lead_p4.CosTheta())
        denominator = self.get_denominator(mHH_lhe, cosThetaStar_lhe)

        weightsBM_lhe = []
        for bmIdx in range(self.nofWeightsBM):
          weightBM_lhe = self.model.getScaleFactor(
            mhh      = mHH_lhe,
            cost     = cosThetaStar_lhe,
            kl       = self.klJHEP[bmIdx],
            kt       = self.ktJHEP[bmIdx],
            c2       = 0.,
            cg       = 0.,
            c2g      = 0.,
            effSumV0 = denominator,
            Cnorm    = self.normJHEP[bmIdx],
          )
          weightsBM_lhe.append(weightBM_lhe)
        
        weightsScan_lhe = []
        for bmIdx in range(self.nofWeightsScan):
          weightScan_lhe = self.model.getScaleFactor(
            mhh      = mHH_lhe,
            cost     = cosThetaStar_lhe,
            kl       = self.klScan[bmIdx],
            kt       = self.ktScan[bmIdx],
            c2       = 0.,
            cg       = 0.,
            c2g      = 0.,
            effSumV0 = denominator,
            Cnorm    = self.Norm_klScan[bmIdx],
          )
          weightsScan_lhe.append(weightScan_lhe)

        if self.use_gen:
          assert(len(weightsBM_gen) == len(weightsBM_lhe))
          assert(len(weightsScan_gen) == len(weightsScan_lhe))

    self.out.fillBranch(self.nofWeightsBMName, len(weightsBM_gen))
    self.out.fillBranch(self.nofWeightsScanName, len(weightsScan_gen))
    if self.use_gen:
      self.out.fillBranch(self.mHH_genName, mHH_gen)
      self.out.fillBranch(self.cosThetaStar_genName, cosThetaStar_gen)
      self.out.fillBranch(self.weightBM_genName, weightsBM_gen)
      self.out.fillBranch(self.weightScan_genName, weightsScan_gen)

    if self.use_lhe:
      self.out.fillBranch(self.mHH_lheName, mHH_lhe)
      self.out.fillBranch(self.cosThetaStar_lheName, cosThetaStar_lhe)
      self.out.fillBranch(self.weightBM_lheName, weightsBM_lhe)
      self.out.fillBranch(self.weightScan_lheName, weightsScan_lhe)

    return True

# provide this variable as the 2nd argument to the import option for the nano_postproc.py script
diHiggsVar_2016 = lambda : diHiggsVarProducer(era = "2016")
diHiggsVar_2017 = lambda : diHiggsVarProducer(era = "2017")
diHiggsVar_2018 = lambda : diHiggsVarProducer(era = "2018")
