# tth-nanoAOD-tools
Postprocessing scripts to add branches specific to ttH analysis to nanoAOD Ntuples.

## Setup

```bash
# set up the CMSSW environment
source /cvmfs/cms.cern.ch/cmsset_default.sh # !! or .csh
export SCRAM_ARCH=slc6_amd64_gcc630 # !! or setenv SCRAM_ARCH slc6_amd64_gcc630
cmsrel CMSSW_9_4_0_pre3
cd CMSSW_9_4_0_pre3/src/
cmsenv

# clone necessary repositories
git cms-merge-topic cms-nanoAOD:master
git clone https://github.com/cms-nanoAOD/nanoAOD-tools.git     $CMSSW_BASE/src/PhysicsTools/NanoAODTools
git clone https://github.com/HEP-KBFI/tth-nanoAOD-tools        $CMSSW_BASE/src/tthAnalysis/NanoAODTools

# compile the thing
cd $CMSSW_BASE/src
scram b -j 18
```

At the time of writing it's not clear if the masses of generator-level particles will be added to the standard nanoAOD solution or not ([link](https://github.com/cms-nanoAOD/cmssw/issues/51) to the discussion).
Currently, we go with the easy route and add the branch ourselves.
This can be achieved by adding one more line to `$CMSSW_BASE/src/PhysicsTools/NanoAOD/python/genparticles_cff.py`:

```python
mass = Var("mass",float,precision=8),
```

to the `genParticleTable` variable.

## Generate an example nanoAOD file

```bash
cd $CMSSW_BASE/src/PhysicsTools/NanoAOD/test
cmsRun nano_cfg.py                           # probably change the paths to the input files
```

## How to run the post-processing steps:

The output file name is created by appending `_Skim` to the basename of the input file.

```bash
cd $CMSSW_BASE/src/PhysicsTools/NanoAODTools
export NANOAOD_OUTPUT_DIR=~/sandbox/nanoAODs # or any other directory you prefer
mkdir -p $NANOAOD_OUTPUT_DIR

#  add the missing branches
./scripts/nano_postproc.py -I tthAnalysis.NanoAODTools.postprocessing.tthModules \
  genLepMerger,genHiggsDecayMode,lepJetVar,btagSF,puWeight,jecUncertAll_cpp \
  $NANOAOD_OUTPUT_DIR ../NanoAOD/test/nano.root

# the final output file will be at:
ls -l $NANOAOD_OUTPUT_DIR/nano_Skim.root
```

If you want to add more modules then you must add the relevant import statements to `$CMSSW_BASE/src/tthAnalysis/NanoAODTools/python/postprocessing/tthModules.py` and recompile the NanoAODTools packages in `PhysicsTools` and `tthAnalysis` in order for the changes to take effect.

## TODO

1. Module for computing MET systematic uncertainties ([pull request](https://github.com/cms-nanoAOD/nanoAOD-tools/pull/24) currently open);
2. ECAL variables (eleDEta, eleDPhi, eleooEmooP) missing (but it might be the case that they'll be replaced with a single bit flag indicating whether a given lepton passes the ECAL cuts or not);
3. Compute corr_JECUp and corr_JECDown from the branches generated with jecUncertainties module
4. Compute miniIsoCharged and miniIsoNeutral for leptons from miniPFRelIso_all and miniPFRelIso_chg
5. Fallback tau ID variables idCI3hit and isoCI3hit missing
6. tH event weights lheWeightSM missing
7. Use charge of the generator-level hadronic tau instead of pdgID?
8. Add charge to the generator-level particles

The rest of the branches used in the [tth-htt analysis](https://github.com/HEP-KBFI/tth-htt/tree/nanoAOD) need to be renamed where necessary.

## Links

1. Official tool for post-processing the nanoAOD Ntuples: https://github.com/cms-nanoAOD/nanoAOD-tools
2. nanoAOD fork of CMSSW (relevant addition): https://github.com/cms-nanoAOD/cmssw/tree/master/PhysicsTools/NanoAOD
