# tth-nanoAOD-tools
Postprocessing scripts to add branches specific to ttH analysis to nanoAOD Ntuples.

## Setup

```bash
# set up the CMSSW environment
source /cvmfs/cms.cern.ch/cmsset_default.sh
export SCRAM_ARCH=slc6_amd64_gcc700
cmsrel CMSSW_10_2_10
cd $_/src/
cmsenv

# set up our CMSSW fork
git init
git config core.sparseCheckout true
echo -e 'PhysicsTools/NanoAOD/*\n' > .git/info/sparse-checkout
git remote add origin https://github.com/HEP-KBFI/cmssw.git
git fetch origin
git checkout master-102x
git pull

# (optional) clone additional code that is used during NanoAOD production
git clone https://github.com/HEP-KBFI/tth-nanoAOD.git $CMSSW_BASE/src/tthAnalysis/NanoAOD

# clone repositories needed for NanoAOD post-processing
git clone https://github.com/HEP-KBFI/nanoAOD-tools.git     $CMSSW_BASE/src/PhysicsTools/NanoAODTools
git clone https://github.com/HEP-KBFI/tth-nanoAOD-tools.git $CMSSW_BASE/src/tthAnalysis/NanoAODTools

# compile the thing
cd $CMSSW_BASE/src
scram b -j 8
```

## Generate an example nanoAOD file (optional)

Here's how to generate config file for NanoAOD production with 2017 reMiniAODv2 conditions for 10 events from ttH MC that we use in the synchronization:
```bash
launchall_nanoaod.sh -e 2017v2 -j sync -g -n 10

export NANOAOD_OUTPUT_DIR=~/sandbox/nanoAODs # or any other directory you prefer
mkdir -p $NANOAOD_OUTPUT_DIR
cd $NANOAOD_OUTPUT_DIR

# produce the Ntuple
cmsRun $CMSSW_BASE/src/tthAnalysis/NanoAOD/test/cfgs/nano_sync_RunIIFall17MiniAODv2_cfg.py &> out.log

# (output is in $NANOAOD_OUTPUT_DIR/tree.root)
```

## How to run the post-processing steps:

The output file name is created by appending a suffix to the basename of the input file, specified by the option `-s`.

```bash
# cd $NANOAOD_OUTPUT_DIR in case you already haven't

# choose an era between 2016, 2017 and 2018
ERA=2017

# when running on MC, you need to set these variables in order to evaluate PU weights
# this file can be produced w/ e.g.
# https://github.com/HEP-KBFI/tth-htt/blob/master/scripts/puHistogramProducer.sh
PILEUP=/some/path/to/a/file/containing/pu/histograms.root
SAMPLE_NAME=effectively_histogram_name

# set up modules for data and MC
NANO_MODULES_DATA="absIso,tauIDLog,jetSubstructureObservablesHTTv2,trigObjMatcher"
NANO_MODULES_MC="$NANO_MODULES_DATA,genHiggsDecayMode,genAll,puWeight${ERA}($PILEUP;$SAMPLE_NAME),\
jetmetUncertainties${ERA},btagSF_deep_${ERA},btagSF_deepFlav_${ERA}"

if [ "$ERA" = "2016" ]; then
  NANO_MODULES_DATA="$NANO_MODULES_DATA,egammaId"
  NANO_MODULES_MC="$NANO_MODULES_MC,btagSF_csvv2_${ERA},egammaId";
elif [ "$ERA" == "2017" ]; then
  NANO_MODULES_MC="$NANO_MODULES_MC,btagSF_csvv2_${ERA}";
fi

# decide which modules you need to run
NANO_MODULES=$NANO_MODULES_MC

nano_postproc.py -s _i -I tthAnalysis.NanoAODTools.postprocessing.tthModules $NANO_MODULES \
  $PWD tree.root

# remove unused branches (cannot remove the branches we're working with, hence the 2nd command)
nano_postproc.py -s i -I tthAnalysis.NanoAODTools.postprocessing.tthModules countHistogramAll \
  $PWD tree_i.root

# the final output file will be at:
ls -l $NANOAOD_OUTPUT_DIR/tree_ii.root
```

**Note** If you want to add more modules then you must add the relevant import statements to `$CMSSW_BASE/src/tthAnalysis/NanoAODTools/python/postprocessing/tthModules.py` and recompile the NanoAODTools packages in `PhysicsTools` and `tthAnalysis` in order for the changes to take effect.

Unused yet functional modules:
- `lepJetVarBTagAll_${ERA}` -- the information is already saved during NanoAOD production and is actually more accurate due to superior lepton-to-jet matching;
- `jetmetUncertainties${ERA}AK8Puppi` -- not relevant as long as we don't plan to recalibrate AK8 jets;
- `btagSF_cmva_2016` -- b-tagging discriminator deprecated since 2017;
- `flagTypeConverter`-- not relevant, unless running on `80x` datasets.

## Links

1. Official tool for post-processing the nanoAOD Ntuples: https://github.com/cms-nanoAOD/nanoAOD-tools
1. nanoAOD fork of CMSSW (complementary): https://github.com/cms-nanoAOD/cmssw/tree/master/PhysicsTools/NanoAOD
1. Our own nanoAOD-tools fork: https://github.com/HEP-KBFI/nanoAOD-tools
1. Our own fork of the CMSSW FW, based off the official nanoAOD fork: https://github.com/HEP-KBFI/cmssw
