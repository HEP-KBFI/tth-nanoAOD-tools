from CRABClient.UserUtilities import config, getUsernameFromSiteDB

import re
import os

PREFIX = 'NanoAOD_2017_v1'
CURDIR = os.path.dirname(os.path.realpath(__file__))

if 'DATASET' not in os.environ:
  raise ValueError("$DATASET not defined")

if 'DATASET_PATTERN' not in os.environ:
  raise ValueError("$DATASET_PATTERN not defined")

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
config.JobType.psetName   = os.path.join(CURDIR, 'nano_cfg.py')

config.Data.inputDataset     = dataset_name
config.Data.inputDBS         = 'global'
config.Data.splitting        = 'EventAwareLumiBased'
config.Data.unitsPerJob      = 50000
config.Data.outLFNDirBase    = '/store/user/%s/NanoAOD_2017' % getUsernameFromSiteDB()
config.Data.publication      = False
config.Data.outputDatasetTag = outputDatasetTag

config.Site.storageSite = 'T2_EE_Estonia'
