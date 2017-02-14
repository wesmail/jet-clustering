#!/usr/bin/env python2
# vim:fileencoding=utf-8:ft=python

import os
import sys
import ROOT

ROOT.gROOT.SetBatch(True)
ROOT.gSystem.Load("libFWCoreFWLite.so");
ROOT.gSystem.Load("libDataFormatsFWLite.so");
ROOT.FWLiteEnabler.enable()

from DataFormats.FWLite import Events, Handle

datadir = os.path.join(os.getcwd(), 'data')

default_file = "root://eoscms.cern.ch//eos/cms/store/mc/RunIISummer16MiniAODv2/BulkGravToZZToZhadZhad_narrow_M-1800_13TeV-madgraph/MINIAODSIM/PUMoriond17_80X_mcRun2_asymptotic_2016_TrancheIV_v6-v1/60000/48313E83-C4BD-E611-9A1C-001C23BED459.root"

def process(events, n):
    label = "slimmedJetsAK8"
    jets  = Handle("std::vector<pat::Jet>")

    for e, event in enumerate(events):
        if e >= n: return

        event.getByLabel(label, jets)
        datafile = 'event%d.txt' % event.eventAuxiliary().event()

        with open(os.path.join(datadir, datafile), 'w') as f:
            f.write("# jet,constituent,eta,phi,px,py,pz,p\n")

            for j, jet in enumerate(jets.product()):
                constituents = []
                for candidate in [ jet.daughter(i) for i in range(jet.numberOfDaughters()) ]:
                    if candidate.numberOfDaughters() == 0:
                        constituents.append(candidate)
                    else:
                        cdaughters = candidate.numberOfDaughters()
                        constituents.extend([ candidate.daughter(i) for i in range(cdaughters) ])

                constituents.sort(key = lambda c:c.pt(), reverse=True)

                for i, c in enumerate(constituents):
                    pinv = 1.0 / c.p()
                    px, py, pz = pinv * c.px(), pinv * c.py(), pinv * c.pz()
                    f.write("%d,%d,%f,%f,%f,%f,%f,%f\n" % (j, i, c.eta(), c.phi(), px, py, pz, c.p()))

            f.close()

if __name__ == "__main__":
    if not os.path.exists(datadir):
        os.mkdir(datadir)

    if len(sys.argv) == 1:
        process(Events(default_file), 10)
    elif len(sys.argv) == 2:
        process(Events(default_file), int(sys.argv[1]))
    else:
        process(Events(sys.argv[1]), int(sys.argv[2]))
