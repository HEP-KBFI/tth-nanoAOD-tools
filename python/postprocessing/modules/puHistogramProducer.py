import ROOT
import os
ROOT.PyConfig.IgnoreCommandLineOptions = True

from PhysicsTools.NanoAODTools.postprocessing.framework.eventloop import Module

class puHistogramProducer(Module):
    def __init__(self, targetfile, outputFileName, targethist = "pileup", nvtx_var = "Pileup_nTrueInt"):
        self.targeth = self.loadHisto(targetfile, targethist)
        ROOT.gROOT.cd()
        self.myh = self.targeth.Clone("autoPU")
        self.myh.Reset()
        self.nvtxVar = nvtx_var
        self.outputFileName = outputFileName

    def loadHisto(self,filename,hname):
        tf = ROOT.TFile.Open(filename)
        hist = tf.Get(hname)
        hist.SetDirectory(None)
        tf.Close()
        return hist

    def beginJob(self):
        pass

    def endJob(self):
        pass

    def beginFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
        self.myh.Reset()
        ROOT.gROOT.cd()
        inputFile.Get("Events").Project("autoPU", self.nvtxVar)

        outputHistoFile = ROOT.TFile.Open(self.outputFileName, 'recreate')
        if outputHistoFile:
            outputHistoFile.cd()
            self.myh.Write()
        else:
          raise ValueError('Could not create file %s' % self.outputFileName)

    def endFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
        pass

    def analyze(self, event):
        return True

pufile_dir = "%s/src/PhysicsTools/NanoAODTools/python/postprocessing/data/pileup" % os.environ['CMSSW_BASE']
pufile_data2016 = os.path.join(pufile_dir, "PileupData_GoldenJSON_Full2016.root")
pufile_data2017 = os.path.join(pufile_dir, "PileupData_ReRecoJSON_Full2017.root")

puHist2016 = lambda outputFn: puHistogramProducer(pufile_data2016, outputFn)
puHist2017 = lambda outputFn: puHistogramProducer(pufile_data2017, outputFn)
