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
git clone https://github.com/cms-nanoAOD/nanoAOD-tools.git $CMSSW_BASE/src/PhysicsTools/NanoAODTools
git clone https://github.com/HEP-KBFI/tth-nanoAOD-tools    $CMSSW_BASE/src/tthAnalysis/NanoAODTools

# compile the thing
cd $CMSSW_BASE/src
scram b -j 18
```

## Generate an example nanoAOD file

```bash
cd $CMSSW_BASE/src/PhysicsTools/NanoAOD/test
cmsRun nano_cfg.py                           # probably change the paths to the input files
```

## How to run the post-processing steps:

The output file name is created by appending a suffix to the basename of the input file, specified by the option `-s`.

```bash
cd $CMSSW_BASE/src/PhysicsTools/NanoAODTools
export NANOAOD_OUTPUT_DIR=~/sandbox/nanoAODs # or any other directory you prefer
mkdir -p $NANOAOD_OUTPUT_DIR
# original size: 22M (8096 events -> 2.8 kB / event)

# NB! exclude jetmetUncertainties unless the PR https://github.com/cms-nanoAOD/nanoAOD-tools/pull/24
#     has not been merged yet (or if you haven't applied the path yourself)
./scripts/nano_postproc.py -s _i -I tthAnalysis.NanoAODTools.postprocessing.tthModules                    \
  genHiggsDecayMode,lepJetVarBTagAll,genLepton,btagSF,puWeight,jecUncert_cpp,jetmetUncertainties,tauIDLog \
  $NANOAOD_OUTPUT_DIR ../NanoAOD/test/nano.root
# time (11.7 ms / event)
# real    1m35.279s
# user    1m26.909s
# sys     0m5.622s
# new size: 16M (1.9 kB / event)
# (computing all gen lvl particles by replacing genLepton with genAll adds another 15 seconds and 2 MB)

# remove unused branches (cannot remove the branches we're working with, hence the 2nd command)
./scripts/nano_postproc.py -s i -I tthAnalysis.NanoAODTools.postprocessing.tthModules countHistogramAll \
  -b $CMSSW_BASE/src/tthAnalysis/NanoAODTools/data/keep_or_drop.txt                                     \
  $NANOAOD_OUTPUT_DIR $NANOAOD_OUTPUT_DIR/nano_i.root
# time (2 ms / event)
# real    0m16.521s
# user    0m14.140s
# sys     0m0.606s
# new size: 8.5M (1 kB / event)
# (with genAll the final size is 11MB and additional 2 seconds)

# the final output file will be at:
ls -l $NANOAOD_OUTPUT_DIR/nano_ii.root

# final statistics:
# time it takes to process a single event: 13.7 ms (< 1 day / 150 PCs / 1B events*) or w/ genAll 15.7 ms
# amount of bytes taken by one event:      1 kB (60% reduction; 1GB / 1B events*) or w/ genAll 1.4 kB
# * 2016 VHbb Ntuples have 4B events, but the events are preselected
```

If you want to add more modules then you must add the relevant import statements to `$CMSSW_BASE/src/tthAnalysis/NanoAODTools/python/postprocessing/tthModules.py` and recompile the NanoAODTools packages in `PhysicsTools` and `tthAnalysis` in order for the changes to take effect.

## TODO

1. Module for computing MET systematic uncertainties ([pull request](https://github.com/cms-nanoAOD/nanoAOD-tools/pull/24) currently open);
1. ECAL variables (eleDEta, eleDPhi) missing (but it might be the case that they'll be replaced with a single bit flag indicating whether a given lepton passes the ECAL cuts or not);
1. Fallback tau ID variables idCI3hit and isoCI3hit (and their respective raw values) missing
1. tH event weights lheWeightSM missing

The rest of the branches used in the [tth-htt analysis](https://github.com/HEP-KBFI/tth-htt/tree/nanoAOD) need to be renamed where necessary, or recomputed (such as JECDown, JECUp, miniIsoCharged and miniIsoNeutral; we don't do this computation here as we would need to loop over the events again because it is not possible to read the variables that are created within the event loop).

## Links

1. Official tool for post-processing the nanoAOD Ntuples: https://github.com/cms-nanoAOD/nanoAOD-tools
1. nanoAOD fork of CMSSW (complementary): https://github.com/cms-nanoAOD/cmssw/tree/master/PhysicsTools/NanoAOD
