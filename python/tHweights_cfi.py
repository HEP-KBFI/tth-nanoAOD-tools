import FWCore.ParameterSet.Config as cms

KV_NORM = 1.0

def get_tHq_sf(kt_over_kv, kv):
  return 1.0 if kt_over_kv == 1.0 and kv == 1.0 else kv**2 * (2.63 * kt_over_kv**2 + 3.588 - 5.21 * kt_over_kv)

def get_tHW_sf(kt_over_kv, kv):
  return 1.0 if kt_over_kv == 1.0 and kv == 1.0 else kv**2 * (2.91 * kt_over_kv**2 + 2.31 - 4.22 * kt_over_kv)

def get_ttH_sf(kt_over_kv, kv):
  return 1.0

tHweights = cms.VPSet(
  cms.PSet(kt = cms.double(-1.0),  kv = cms.double(1.0), idx = cms.int32(-1)), # the default (i.e. no weight)
  # 16 weights
  cms.PSet(kt = cms.double(-3.0),  kv = cms.double(1.0), idx = cms.int32(0)),
  cms.PSet(kt = cms.double(-2.0),  kv = cms.double(1.0), idx = cms.int32(1)),
  cms.PSet(kt = cms.double(-1.5),  kv = cms.double(1.0), idx = cms.int32(2)),
  cms.PSet(kt = cms.double(-1.25), kv = cms.double(1.0), idx = cms.int32(3)),
  cms.PSet(kt = cms.double(-0.75), kv = cms.double(1.0), idx = cms.int32(4)),
  cms.PSet(kt = cms.double(-0.5),  kv = cms.double(1.0), idx = cms.int32(5)),
  cms.PSet(kt = cms.double(-0.25), kv = cms.double(1.0), idx = cms.int32(6)),
  cms.PSet(kt = cms.double(0.0),   kv = cms.double(1.0), idx = cms.int32(7)),
  cms.PSet(kt = cms.double(0.25),  kv = cms.double(1.0), idx = cms.int32(8)),
  cms.PSet(kt = cms.double(0.5),   kv = cms.double(1.0), idx = cms.int32(9)),
  cms.PSet(kt = cms.double(0.75),  kv = cms.double(1.0), idx = cms.int32(10)),
  cms.PSet(kt = cms.double(1.0),   kv = cms.double(1.0), idx = cms.int32(11)),
  cms.PSet(kt = cms.double(1.25),  kv = cms.double(1.0), idx = cms.int32(12)),
  cms.PSet(kt = cms.double(1.5),   kv = cms.double(1.0), idx = cms.int32(13)),
  cms.PSet(kt = cms.double(2.0),   kv = cms.double(1.0), idx = cms.int32(14)),
  cms.PSet(kt = cms.double(3.0),   kv = cms.double(1.0), idx = cms.int32(15)),
  # 17 weights in total - 7 redundant weights -> 10 weights
  #cms.PSet(kt = cms.double(-3.0),  kv = cms.double(1.5), idx = cms.int32(16)), # has the same kt / kv as idx 1
  cms.PSet(kt = cms.double(-2.0),  kv = cms.double(1.5), idx = cms.int32(17)),
  #cms.PSet(kt = cms.double(-1.5),  kv = cms.double(1.5), idx = cms.int32(18)), # has the same kt / kv as idx -1
  cms.PSet(kt = cms.double(-1.25), kv = cms.double(1.5), idx = cms.int32(19)),
  cms.PSet(kt = cms.double(-1.0),  kv = cms.double(1.5), idx = cms.int32(20)),
  #cms.PSet(kt = cms.double(-0.75), kv = cms.double(1.5), idx = cms.int32(21)), # has the same kt / kv as idx 4
  cms.PSet(kt = cms.double(-0.5),  kv = cms.double(1.5), idx = cms.int32(22)),
  cms.PSet(kt = cms.double(-0.25), kv = cms.double(1.5), idx = cms.int32(23)),
  #cms.PSet(kt = cms.double(0.0),   kv = cms.double(1.5), idx = cms.int32(24)), # has the same kt / kv as idx 7
  cms.PSet(kt = cms.double(0.25),  kv = cms.double(1.5), idx = cms.int32(25)),
  cms.PSet(kt = cms.double(0.5),   kv = cms.double(1.5), idx = cms.int32(26)),
  #cms.PSet(kt = cms.double(0.75),  kv = cms.double(1.5), idx = cms.int32(27)), # has the same kt / kv as idx 10
  cms.PSet(kt = cms.double(1.0),   kv = cms.double(1.5), idx = cms.int32(28)),
  cms.PSet(kt = cms.double(1.25),  kv = cms.double(1.5), idx = cms.int32(29)),
  #cms.PSet(kt = cms.double(1.5),   kv = cms.double(1.5), idx = cms.int32(30)), # has the same kt / kv as idx 11
  cms.PSet(kt = cms.double(2.0),   kv = cms.double(1.5), idx = cms.int32(31)),
  #cms.PSet(kt = cms.double(3.0),   kv = cms.double(1.5), idx = cms.int32(32)), # has the same kt / kv as idx 14
  # 17 weights in total - 11 redundant weights -> 6 weights
  cms.PSet(kt = cms.double(-3.0),  kv = cms.double(0.5), idx = cms.int32(33)),
  cms.PSet(kt = cms.double(-2.0),  kv = cms.double(0.5), idx = cms.int32(34)),
  #cms.PSet(kt = cms.double(-1.5),  kv = cms.double(0.5), idx = cms.int32(35)), # has the same kt / kv as idx 0
  cms.PSet(kt = cms.double(-1.25), kv = cms.double(0.5), idx = cms.int32(36)),
  #cms.PSet(kt = cms.double(-1.0),  kv = cms.double(0.5), idx = cms.int32(37)), # has the same kt / kv as idx 1
  #cms.PSet(kt = cms.double(-0.75), kv = cms.double(0.5), idx = cms.int32(38)), # has the same kt / kv as idx 2
  #cms.PSet(kt = cms.double(-0.5),  kv = cms.double(0.5), idx = cms.int32(39)), # has the same kt / kv as idx -1
  #cms.PSet(kt = cms.double(-0.25), kv = cms.double(0.5), idx = cms.int32(40)), # has the same kt / kv as idx 5
  #cms.PSet(kt = cms.double(0.0),   kv = cms.double(0.5), idx = cms.int32(41)), # has the same kt / kv as idx 7
  #cms.PSet(kt = cms.double(0.25),  kv = cms.double(0.5), idx = cms.int32(42)), # has the same kt / kv as idx 9
  #cms.PSet(kt = cms.double(0.5),   kv = cms.double(0.5), idx = cms.int32(43)), # has the same kt / kv as idx 11
  #cms.PSet(kt = cms.double(0.75),  kv = cms.double(0.5), idx = cms.int32(44)), # has the same kt / kv as idx 13
  #cms.PSet(kt = cms.double(1.0),   kv = cms.double(0.5), idx = cms.int32(45)), # has the same kt / kv as idx 14
  cms.PSet(kt = cms.double(1.25),  kv = cms.double(0.5), idx = cms.int32(46)),
  #cms.PSet(kt = cms.double(1.5),   kv = cms.double(0.5), idx = cms.int32(47)), # has the same kt / kv as idx 15
  cms.PSet(kt = cms.double(2.0),   kv = cms.double(0.5), idx = cms.int32(48)),
  cms.PSet(kt = cms.double(3.0),   kv = cms.double(0.5), idx = cms.int32(49)),
  # verdict: 16 + 10 + 6 = 32 pairs of kt and kv with unique kt / kv ratio
)

for tHweight in tHweights:
  kt = tHweight.kt.value()
  kv = tHweight.kv.value()
  kt_over_kv = kt / kv
  tHweight.xs_tHq = cms.double(get_tHq_sf(kt_over_kv, KV_NORM))
  tHweight.xs_tHW = cms.double(get_tHW_sf(kt_over_kv, KV_NORM))
  tHweight.xs_ttH = cms.double(get_ttH_sf(kt_over_kv, KV_NORM))

# final choice (determined by the indices to the reweighting branch)
thIdxs = [ coupling.idx.value() for coupling in tHweights ]

def find_tHweight(tHweights, idx):
  requried_entry = [ entry for entry in tHweights if entry.idx.value() == idx ]
  if len(requried_entry) == 0:
    raise RuntimeError("No weights found for index: %d" % idx)
  elif len(requried_entry) > 1:
    raise RuntimeError("Multiple weights found for index %d" % idx)
  return requried_entry[0]
