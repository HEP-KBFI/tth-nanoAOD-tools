# tth-nanoAOD-tools
Postprocessing scripts to add branches specific to ttH analysis to nanoAOD Ntuples.

## Setup

```bash
# set up the CMSSW environment
source /cvmfs/cms.cern.ch/cmsset_default.sh # !! or .csh
export SCRAM_ARCH=slc6_amd64_gcc630 # !! or setenv SCRAM_ARCH slc6_amd64_gcc630
cmsrel CMSSW_9_4_4
cd CMSSW_9_4_4/src/
cmsenv

# clone necessary repositories
git cms-merge-topic cms-nanoAOD:master
git clone https://github.com/HEP-KBFI/nanoAOD-tools.git     $CMSSW_BASE/src/PhysicsTools/NanoAODTools
git clone https://github.com/HEP-KBFI/tth-nanoAOD-tools.git $CMSSW_BASE/src/tthAnalysis/NanoAODTools

# compile the thing
cd $CMSSW_BASE/src
scram b -j 16
```

## Generate an example nanoAOD file

```bash
cd $CMSSW_BASE/src/PhysicsTools/NanoAOD/test
cmsRun nano_cfg.py                           # probably change the paths to the input files
```

## How to run the post-processing steps:

The output file name is created by appending a suffix to the basename of the input file, specified by the option `-s`.

```bash
export NANOAOD_OUTPUT_DIR=~/sandbox/nanoAODs # or any other directory you prefer
mkdir -p $NANOAOD_OUTPUT_DIR

# choose an era between 2016 and 2017
ERA=2017

# if running on 2017 MC, you need to set these variables in order to evaluate PU weights
PILEUP=/some/path/to/a/file/containing/pu/histograms.root
SAMPLE_NAME=effectively_histogram_name

# decide which modules you need to run
NANO_MODULES_DATA="lepJetVarBTagAll_$ERA,absIso,tauIDLog_$ERA,jetSubstructureObservablesHTTv2,trigObjMatcher"
NANO_MODULES_MC="$NANO_MODULES_DATA,genHiggsDecayMode,genAll,puWeight_$ERA($PILEUP;$SAMPLE_NAME),jetmetUncertainties$ERA,btagSF_csvv2_$ERA"
if [ "$ERA" = "2016" ]; then
  NANO_MODULES_MC="$NANO_MODULES_MC,btagSF_cmva_$ERA";
elif [ "$ERA" == "2017" ]; then
  NANO_MODULES_MC="$NANO_MODULES_MC,btagSF_deep_$ERA";
fi
NANO_MODULES=NANO_MODULES_MC

nano_postproc.py -s _i -I tthAnalysis.NanoAODTools.postprocessing.tthModules $NANO_MODULES \
  $NANOAOD_OUTPUT_DIR ../NanoAOD/test/nano.root

# remove unused branches (cannot remove the branches we're working with, hence the 2nd command)
nano_postproc.py -s i -I tthAnalysis.NanoAODTools.postprocessing.tthModules countHistogramAll_$ERA \
  -b $CMSSW_BASE/src/tthAnalysis/NanoAODTools/data/keep_or_drop.txt                           \
  $NANOAOD_OUTPUT_DIR $NANOAOD_OUTPUT_DIR/nano_i.root

# the final output file will be at:
ls -l $NANOAOD_OUTPUT_DIR/nano_ii.root
```

If you want to add more modules then you must add the relevant import statements to `$CMSSW_BASE/src/tthAnalysis/NanoAODTools/python/postprocessing/tthModules.py` and recompile the NanoAODTools packages in `PhysicsTools` and `tthAnalysis` in order for the changes to take effect.

## TODO

1. tH event weights lheWeightSM missing (but we dont have any 94X tH samples)

The rest of the branches used in the [tth-htt analysis](https://github.com/HEP-KBFI/tth-htt/tree/nanoAOD) need to be renamed where necessary, or recomputed (such as JECDown, JECUp, miniIsoCharged and miniIsoNeutral; we don't do this computation here as we would need to loop over the events again because it is not possible to read the variables that are created within the event loop).

## Links

1. Official tool for post-processing the nanoAOD Ntuples: https://github.com/cms-nanoAOD/nanoAOD-tools
1. nanoAOD fork of CMSSW (complementary): https://github.com/cms-nanoAOD/cmssw/tree/master/PhysicsTools/NanoAOD
1. Our own nanoAOD-tools fork: https://github.com/HEP-KBFI/nanoAOD-tools
1. Our own fork of the CMSSW FW, based off the official nanoAOD fork: https://github.com/HEP-KBFI/cmssw
