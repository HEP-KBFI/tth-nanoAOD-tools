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

At the time of writing it seems that each module can only be executed separately and not all-in-one shot.
This means that every time we want to add branch(es) to the nanoAOD Ntuple, we have to create a new file.
The output file name is created by appending `_Skim` to the basename of the input file.

```bash
cd $CMSSW_BASE/src/PhysicsTools/NanoAODTools
export NANOAOD_OUTPUT_DIR=~/sandbox/nanoAODs # or any other directory you prefer
mkdir -p $NANOAOD_OUTPUT_DIR

#  add lepton-to-jet variables jetPtRatio and jetBtagCSV
./scripts/nano_postproc.py -I tthAnalysis.NanoAODTools.postprocessing.modules.lepJetVarProducer lepJetVar                 $NANOAOD_OUTPUT_DIR ../NanoAOD/test/nano.root

# pull out stable generator level electrons and muons to a new branch
./scripts/nano_postproc.py -I tthAnalysis.NanoAODTools.postprocessing.modules.genLepMerger genLepMerger                   $NANOAOD_OUTPUT_DIR $NANOAOD_OUTPUT_DIR/nano_Skim.root

# add Higgs decay mode at generator level
./scripts/nano_postproc.py -I tthAnalysis.NanoAODTools.postprocessing.modules.genHiggsDecayModeProducer genHiggsDecayMode $NANOAOD_OUTPUT_DIR $NANOAOD_OUTPUT_DIR/nano_Skim_Skim.root

# add b-tagging scale factors
./scripts/nano_postproc.py -I PhysicsTools.NanoAODTools.postprocessing.modules.btv.btagSFProducer btagSF                  $NANOAOD_OUTPUT_DIR $NANOAOD_OUTPUT_DIR/nano_Skim_Skim_Skim.root

# add pile-up weights
./scripts/nano_postproc.py -I PhysicsTools.NanoAODTools.postprocessing.examples.puWeightProducer puWeight                 $NANOAOD_OUTPUT_DIR $NANOAOD_OUTPUT_DIR/nano_Skim_Skim_Skim_Skim.root

# add JECs
./scripts/nano_postproc.py -I PhysicsTools.NanoAODTools.postprocessing.modules.jme.jecUncertainties jecUncertAll_cpp      $NANOAOD_OUTPUT_DIR $NANOAOD_OUTPUT_DIR/nano_Skim_Skim_Skim_Skim_Skim.root

# the final output file will be at:
ls -l $NANOAOD_OUTPUT_DIR $NANOAOD_OUTPUT_DIR/nano_Skim_Skim_Skim_Skim_Skim_Skim.root
```

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
