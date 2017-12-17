#!/bin/bash

# DO NOT SOURCE! IT MAY KILL YOUR SHELL!

if [ -z "$1" ]; then
  echo "You must supply file containing the list of samples (one sample per line) as an argument to the script";
  exit 1;
fi

if [ ! -f "$1" ]; then
  echo "File '$f' does not exist!"
  exit 2;
fi

echo "Checking if crab is available ..."
CRAB_AVAILABLE=$(which crab 2>/dev/null)
if [ -z "$CRAB_AVAILABLE" ]; then
  echo "crab not available! please do: source /cvmfs/cms.cern.ch/crab3/crab.sh"
  exit 3;
fi

echo "Checking if VOMS is available ..."
VOMS_PROXY_AVAILABLE=$(which voms-proxy-info 2>/dev/null)
if [ -z "$VOMS_PROXY_AVAILABLE" ]; then
  echo "VOMS proxy not available! please do: source /cvmfs/grid.cern.ch/glite/etc/profile.d/setup-ui-example.sh";
  exit 4;
fi

echo "Checking if VOMS is open long enough ..."
export MIN_HOURSLEFT=72
export MIN_TIMELEFT=$((3600 * $MIN_HOURSLEFT))
VOMS_PROXY_TIMELEFT=$(voms-proxy-info --timeleft)
if [ "$VOMS_PROXY_TIMELEFT" -lt "$MIN_TIMELEFT" ]; then
  echo "Less than $MIN_HOURSLEFT hours left for the proxy to be open: $VOMS_PROXY_TIMELEFT seconds";
  echo "Please update your proxy: voms-proxy-init -voms cms -valid 192:00";
  exit 1;
fi

echo "Submitting jobs ..."
for f in `cat $1`; do
  export DATASET=$f
  echo "Found sample: $DATASET"
  #crab submit --dryrun --config=nano_cfg_env.py --wait
done
