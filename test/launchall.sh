#!/bin/bash

# DO NOT SOURCE! IT MAY KILL YOUR SHELL!

DO_DRYRUN=false

TAG_DATA="run2_data"
TAG_MC="run2_mc"

SCRIPT_DIRECTORY="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
JSON_LUMI="$SCRIPT_DIRECTORY/../data/Cert_294927-306462_13TeV_PromptReco_Collisions17_JSON.txt"

if [ ! -f "$JSON_LUMI" ]; then
  echo "The JSON lumi mask '$JSON_LUMI' does not exist";
  exit 1;
fi

if [ $DO_DRYRUN = true ]; then
  export DRYRUN="--dryrun";
else
  export DRYRUN="";
fi

if [ -z "$1" ]; then
  echo "You must supply file containing the list of samples (one sample per line) as an argument to the script";
  exit 2;
fi

if [ ! -f "$1" ]; then
  echo "File '$1' does not exist!"
  exit 3;
fi

# Saving absolute path
export DATASET_FILE=$1
if [[ ! "$DATASET_FILE" =~ ^/ ]]; then
  export DATASET_FILE="$PWD/$DATASET_FILE";
  echo "Full path to the dataset file: $DATASET_FILE";
fi

echo "Checking if crab is available ..."
CRAB_AVAILABLE=$(which crab 2>/dev/null)
if [ -z "$CRAB_AVAILABLE" ]; then
  echo "crab not available! please do: source /cvmfs/cms.cern.ch/crab3/crab.sh"
  exit 4;
fi

echo "Checking if VOMS is available ..."
VOMS_PROXY_AVAILABLE=$(which voms-proxy-info 2>/dev/null)
if [ -z "$VOMS_PROXY_AVAILABLE" ]; then
  echo "VOMS proxy not available! please do: source /cvmfs/grid.cern.ch/glite/etc/profile.d/setup-ui-example.sh";
  exit 5;
fi

echo "Checking if VOMS is open long enough ..."
export MIN_HOURSLEFT=72
export MIN_TIMELEFT=$((3600 * $MIN_HOURSLEFT))
VOMS_PROXY_TIMELEFT=$(voms-proxy-info --timeleft)
if [ "$VOMS_PROXY_TIMELEFT" -lt "$MIN_TIMELEFT" ]; then
  echo "Less than $MIN_HOURSLEFT hours left for the proxy to be open: $VOMS_PROXY_TIMELEFT seconds";
  echo "Please update your proxy: voms-proxy-init -voms cms -valid 192:00";
  exit 6;
fi

export DATASET_PATTERN="^/(.*)/(.*)/[0-9A-Za-z]+$"
declare -A DATA_CATEGORIES=([SingleElectron]= [SingleMuon]= [Tau]= [DoubleEG]= [DoubleMuon]= [MuonEG]=)

echo "Generating the skeleton configuration file for CRAB submission"

#export AUTOCOND_DATA=$(python -c "from Configuration.AlCa.autoCond import autoCond; print(autoCond['$TAG_DATA'])")
#export AUTOCOND_MC=$(python -c "from Configuration.AlCa.autoCond import autoCond; print(autoCond['$TAG_MC'])")

# recommended: https://twiki.cern.ch/twiki/bin/view/CMSPublic/SWGuideFrontierConditions#Global_Tags_for_2017_Nov_re_reco
export AUTOCOND_DATA="94X_dataRun2_ReReco_EOY17_v2"
# recommended: https://twiki.cern.ch/twiki/bin/view/CMSPublic/SWGuideFrontierConditions#Global_Tags_for_RunIIFall17DRStd
export AUTOCOND_MC="94X_mc2017_realistic_v10"

if [ -z "$AUTOCOND_DATA" ]; then
  echo "Could not deduce the acutal global tag for the data";
  exit 7;
fi

if [ -z "$AUTOCOND_MC" ]; then
  echo "Could not deduce the acutal global tag for the MC";
  exit 8;
fi

export CUSTOMISE_COMMANDS="process.MessageLogger.cerr.FwkReport.reportEvery = 1000\\n\
                           process.source.fileNames = []\\n"

# for data
cmsDriver.py nanoAOD -s NANO --data --eventcontent NANOAOD --datatier NANOAOD           \
  --conditions $AUTOCOND_DATA --era Run2_2017 --no_exec --fileout=tree.root --number=-1 \
  --python_filename="$SCRIPT_DIRECTORY/nanoAOD_data.py"                                 \
  --customise_commands="$CUSTOMISE_COMMANDS" --lumiToProcess="$JSON_LUMI"

# for MC
cmsDriver.py nanoAOD -s NANO --mc --eventcontent NANOAODSIM --datatier NANOAODSIM     \
  --conditions $AUTOCOND_MC --era Run2_2017 --no_exec --fileout=tree.root --number=-1 \
  --python_filename="$SCRIPT_DIRECTORY/nanoAOD_mc.py"                                 \
  --customise_commands="$CUSTOMISE_COMMANDS"

echo "Submitting jobs ..."
cat $DATASET_FILE | while read LINE; do
  export DATASET=$(echo $LINE | awk '{print $1}');
  unset DATASET_CATEGORY;
  unset IS_DATA;

  if [ -z "$DATASET" ]; then
    continue; # it's an empty line, skip silently
  fi

  if [[ ! "$DATASET" =~ $DATASET_PATTERN ]]; then
    echo "Not a valid sample: '$DATASET'";
    continue;
  else
    export DATASET_CATEGORY="${BASH_REMATCH[1]}";
  fi

  if [ -z "$DATASET_CATEGORY" ]; then
    echo "Could not find the dataset category for: '$DATASET'";
    continue;
  fi

  if [[ ${DATA_CATEGORIES[$DATASET_CATEGORY]-X} == ${DATA_CATEGORIES[$DATASET_CATEGORY]} ]]; then
    export IS_DATA=1;
    echo "Found data sample: $DATASET";
  else
    export IS_DATA=0;
    echo "Found MC   sample: $DATASET";
  fi
  crab submit $DRYRUN --config="$SCRIPT_DIRECTORY/nano_cfg_env.py" --wait
done
