from CRABClient.UserUtilities import config, getUsernameFromSiteDB

import re
import os

if 'JOB_PREFIX' not in os.environ:
  raise ValueError("$JOB_PREFIX not defined")

PREFIX = os.environ['JOB_PREFIX']
CURDIR = os.path.dirname(os.path.realpath(__file__))

if 'IS_DATA' not in os.environ:
  raise ValueError("$IS_DATA not defined")

if 'DATASET' not in os.environ:
  raise ValueError("$DATASET not defined")

if 'DATASET_PATTERN' not in os.environ:
  raise ValueError("$DATASET_PATTERN not defined")

is_data         = bool(int(os.environ['IS_DATA']))
dataset_name    = os.environ['DATASET']
dataset_pattern = os.environ['DATASET_PATTERN']
dataset_match   = re.match(dataset_pattern, dataset_name)
if not dataset_match:
  raise ValueError("Dataset '%s' did not match to pattern '%s'" % (dataset_name, dataset_pattern))

id_ = '%s_%s__%s' % (PREFIX, dataset_match.group(1), dataset_match.group(2))
requestName      = id_
outputDatasetTag = id_

if len(requestName) > 100:
  requestName_new = requestName[:90] + requestName[-10:]
  print("Changing old request name '{rqname_old}' -> '{rqname_new}'".format(
    rqname_old = requestName,
    rqname_new = requestName_new,
  ))
  requestName = requestName_new

config = config()

config.General.requestName     = requestName
config.General.workArea        = os.path.join(os.path.expanduser('~'), 'crab_projects')
config.General.transferOutputs = True
config.General.transferLogs    = True

config.JobType.pluginName = 'Analysis'
config.JobType.psetName   = os.path.join(CURDIR, 'nanoAOD_%s.py' % ("data" if is_data else "mc"))

config.Data.inputDataset     = dataset_name
config.Data.inputDBS         = 'global'
config.Data.splitting        = 'EventAwareLumiBased'
config.Data.unitsPerJob      = 50000
config.Data.outLFNDirBase    = '/store/user/%s/NanoAOD_2017' % getUsernameFromSiteDB()
config.Data.publication      = False
config.Data.outputDatasetTag = outputDatasetTag

if is_data:
  config.Data.lumiMask = os.path.join(
    CURDIR, '..', 'data', 'Cert_294927-306462_13TeV_EOY2017ReReco_Collisions17_JSON.txt'
  )

config.Site.storageSite = 'T2_EE_Estonia'
