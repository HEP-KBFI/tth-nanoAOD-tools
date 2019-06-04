import FWCore.ParameterSet.Config as cms

def get_tHq_sf(kt, kv):
  return 1.0 if kt == 1.0 and kv == 1.0 else 2.63 * kt * kt + 3.588 * kv * kv - 5.21 * kt * kv

def get_tHW_sf(kt, kv):
  return 1.0 if kt == 1.0 and kv == 1.0 else 2.91 * kt * kt + 2.31 * kv * kv - 4.22 * kt * kv

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
  # 17 weights
  cms.PSet(kt = cms.double(-3.0),  kv = cms.double(1.5), idx = cms.int32(16)),
  cms.PSet(kt = cms.double(-2.0),  kv = cms.double(1.5), idx = cms.int32(17)),
  cms.PSet(kt = cms.double(-1.5),  kv = cms.double(1.5), idx = cms.int32(18)),
  cms.PSet(kt = cms.double(-1.25), kv = cms.double(1.5), idx = cms.int32(19)),
  cms.PSet(kt = cms.double(-1.0),  kv = cms.double(1.5), idx = cms.int32(20)),
  cms.PSet(kt = cms.double(-0.75), kv = cms.double(1.5), idx = cms.int32(21)),
  cms.PSet(kt = cms.double(-0.5),  kv = cms.double(1.5), idx = cms.int32(22)),
  cms.PSet(kt = cms.double(-0.25), kv = cms.double(1.5), idx = cms.int32(23)),
  cms.PSet(kt = cms.double(0.0),   kv = cms.double(1.5), idx = cms.int32(24)),
  cms.PSet(kt = cms.double(0.25),  kv = cms.double(1.5), idx = cms.int32(25)),
  cms.PSet(kt = cms.double(0.5),   kv = cms.double(1.5), idx = cms.int32(26)),
  cms.PSet(kt = cms.double(0.75),  kv = cms.double(1.5), idx = cms.int32(27)),
  cms.PSet(kt = cms.double(1.0),   kv = cms.double(1.5), idx = cms.int32(28)),
  cms.PSet(kt = cms.double(1.25),  kv = cms.double(1.5), idx = cms.int32(29)),
  cms.PSet(kt = cms.double(1.5),   kv = cms.double(1.5), idx = cms.int32(30)),
  cms.PSet(kt = cms.double(2.0),   kv = cms.double(1.5), idx = cms.int32(31)),
  cms.PSet(kt = cms.double(3.0),   kv = cms.double(1.5), idx = cms.int32(32)),
  # 17 weights
  cms.PSet(kt = cms.double(-3.0),  kv = cms.double(0.5), idx = cms.int32(33)),
  cms.PSet(kt = cms.double(-2.0),  kv = cms.double(0.5), idx = cms.int32(34)),
  cms.PSet(kt = cms.double(-1.5),  kv = cms.double(0.5), idx = cms.int32(35)),
  cms.PSet(kt = cms.double(-1.25), kv = cms.double(0.5), idx = cms.int32(36)),
  cms.PSet(kt = cms.double(-1.0),  kv = cms.double(0.5), idx = cms.int32(37)),
  cms.PSet(kt = cms.double(-0.75), kv = cms.double(0.5), idx = cms.int32(38)),
  cms.PSet(kt = cms.double(-0.5),  kv = cms.double(0.5), idx = cms.int32(39)),
  cms.PSet(kt = cms.double(-0.25), kv = cms.double(0.5), idx = cms.int32(40)),
  cms.PSet(kt = cms.double(0.0),   kv = cms.double(0.5), idx = cms.int32(41)),
  cms.PSet(kt = cms.double(0.25),  kv = cms.double(0.5), idx = cms.int32(42)),
  cms.PSet(kt = cms.double(0.5),   kv = cms.double(0.5), idx = cms.int32(43)),
  cms.PSet(kt = cms.double(0.75),  kv = cms.double(0.5), idx = cms.int32(44)),
  cms.PSet(kt = cms.double(1.0),   kv = cms.double(0.5), idx = cms.int32(45)),
  cms.PSet(kt = cms.double(1.25),  kv = cms.double(0.5), idx = cms.int32(46)),
  cms.PSet(kt = cms.double(1.5),   kv = cms.double(0.5), idx = cms.int32(47)),
  cms.PSet(kt = cms.double(2.0),   kv = cms.double(0.5), idx = cms.int32(48)),
  cms.PSet(kt = cms.double(3.0),   kv = cms.double(0.5), idx = cms.int32(49)),
)

for tHweight in tHweights:
  tHweight.xs_tHq = cms.double(get_tHq_sf(tHweight.kt.value(), tHweight.kv.value()))
  tHweight.xs_tHW = cms.double(get_tHW_sf(tHweight.kt.value(), tHweight.kv.value()))
