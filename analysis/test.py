#!/usr/bin/env python3

import warnings
warnings.filterwarnings("ignore")

import awkward as ak
import uproot
import numpy as np
import glob
from coffea.nanoevents import NanoEventsFactory, DelphesSchema, BaseSchema
from coffea import hist, processor
# register our candidate behaviors
from coffea.nanoevents.methods import candidate
ak.behavior.update(candidate.behavior)

from functools import partial

from plots.helpers import makePlot2

class DelphesProcessor(processor.ProcessorABC):
    def __init__(self):
        self._accumulator = processor.dict_accumulator({
            "met": hist.Hist(
                "Events",
                hist.Cat("dataset", "Dataset"),
                hist.Bin("pt", "$p_{T}$ [GeV]", 50, 0, 500),
            ),
        })

    @property
    def accumulator(self):
        return self._accumulator

    def process(self, events):
        output = self.accumulator.identity()

        dataset = events.metadata['dataset']

        met = events.PuppiMissingET

        output["met"].fill(
            dataset=dataset,
            pt=ak.flatten(met.MET, axis=1),
        )

        return output

    def postprocess(self, accumulator):
        return accumulator

class FlatProcessor(processor.ProcessorABC):
    def __init__(self):
        self._accumulator = processor.dict_accumulator({
            "met": hist.Hist(
                "Events",
                hist.Cat("dataset", "Dataset"),
                hist.Bin("pt", "$p_{T}$ [GeV]", 75, 0, 750),
            ),
             "lead_fatjet_pt": hist.Hist(
                "Events",
                hist.Cat("dataset", "Dataset"),
                hist.Bin("pt", "$p_{T}$ [GeV]", 75, 0, 750),
            ),
            "lead_fatjet_eta": hist.Hist(
                "Events",
                hist.Cat("dataset", "Dataset"),
                hist.Bin("eta", "$\eta$", 33, -4, 4),
            ),
            "lead_fatjet_phi": hist.Hist(
                "Events",
                hist.Cat("dataset", "Dataset"),
                hist.Bin("phi", "$\phi$", 33, -4, 4),
            ),
            "lead_fatjet_mass": hist.Hist(
                "Events",
                hist.Cat("dataset", "Dataset"),
                hist.Bin("mass", "$p_{T}$ [GeV]", 50, 0, 500),
            ),
            "lead_fatjet_sdmass": hist.Hist(
                "Events",
                hist.Cat("dataset", "Dataset"),
                hist.Bin("mass", "$p_{T}$ [GeV]", 50, 0, 500),
            ),
            "lead_fatjet_tau1": hist.Hist(
                "Events",
                hist.Cat("dataset", "Dataset"),
                hist.Bin("tau", "$\tau_1$", 10, 0, 1),
            ),
            "lead_fatjet_tau2": hist.Hist(
                "Events",
                hist.Cat("dataset", "Dataset"),
                hist.Bin("tau", "$\tau_2$", 10, 0, 1),
            ),
            "lead_fatjet_tau3": hist.Hist(
                "Events",
                hist.Cat("dataset", "Dataset"),
                hist.Bin("tau", "$\tau_3$", 10, 0, 1),
            ),
            "lead_fatjet_tau4": hist.Hist(
                "Events",
                hist.Cat("dataset", "Dataset"),
                hist.Bin("tau", "$\tau_4$", 10, 0, 1),
            ),
            "nfatjet": hist.Hist(
                "Events",
                hist.Cat("dataset", "Dataset"),
                hist.Bin("multiplicity", "$n_{fatjet}$", 6, -0.5, 5.5),
            ),
            'cutflow': processor.defaultdict_accumulator(
                # we don't use a lambda function to avoid pickle issues
                partial(processor.defaultdict_accumulator, int)
            ),
        })

    @property
    def accumulator(self):
        return self._accumulator

    def process(self, events):
        output = self.accumulator.identity()

        dataset = events.metadata['dataset']
               
        output['cutflow'][dataset]['total'] += len(ak.flatten(events.metpuppi_pt))
        output['cutflow'][dataset]['met>200'] += len(events[ak.flatten(events.metpuppi_pt)>200])

        met = events.metpuppi_pt
        fatjet_events = events[ak.num(events.fatjet_pt) > 0]
        fatjet_pt = fatjet_events.fatjet_pt[ak.argsort(fatjet_events.fatjet_pt, ascending=False)]
        fatjet_eta = fatjet_events.fatjet_eta[ak.argsort(fatjet_events.fatjet_pt, ascending=False)]
        fatjet_phi = fatjet_events.fatjet_phi[ak.argsort(fatjet_events.fatjet_pt, ascending=False)]
        fatjet_mass = fatjet_events.fatjet_mass[ak.argsort(fatjet_events.fatjet_pt, ascending=False)]
        fatjet_msoftdrop = fatjet_events.fatjet_msoftdrop[ak.argsort(fatjet_events.fatjet_pt, ascending=False)]
        fatjet_tau1 = fatjet_events.fatjet_tau1[ak.argsort(fatjet_events.fatjet_pt, ascending=False)]
        fatjet_tau2 = fatjet_events.fatjet_tau2[ak.argsort(fatjet_events.fatjet_pt, ascending=False)]
        fatjet_tau3 = fatjet_events.fatjet_tau3[ak.argsort(fatjet_events.fatjet_pt, ascending=False)]
        fatjet_tau4 = fatjet_events.fatjet_tau4[ak.argsort(fatjet_events.fatjet_pt, ascending=False)]
        nfatjet = events.fatjet_size

        output["met"].fill(
            dataset=dataset,
            pt=ak.flatten(met, axis=1),
        )
        output["nfatjet"].fill(
            dataset=dataset,
            multiplicity=nfatjet,
        )
        output["lead_fatjet_pt"].fill(
            dataset=dataset,
            pt=ak.flatten(fatjet_pt[:,0:1], axis=1),
        )
        output["lead_fatjet_eta"].fill(
            dataset=dataset,
            eta=ak.flatten(fatjet_eta[:,0:1], axis=1),
        )
        output["lead_fatjet_phi"].fill(
            dataset=dataset,
            phi=ak.flatten(fatjet_phi[:,0:1], axis=1),
        )
        output["lead_fatjet_mass"].fill(
            dataset=dataset,
            mass=ak.flatten(fatjet_mass[:,0:1], axis=1),
        )
        output["lead_fatjet_sdmass"].fill(
            dataset=dataset,
            mass=ak.flatten(fatjet_msoftdrop[:,0:1], axis=1),
        )
        output["lead_fatjet_tau1"].fill(
            dataset=dataset,
            tau=ak.flatten(fatjet_tau1[:,0:1], axis=1),
        )
        output["lead_fatjet_tau2"].fill(
            dataset=dataset,
            tau=ak.flatten(fatjet_tau2[:,0:1], axis=1),
        )
        output["lead_fatjet_tau3"].fill(
            dataset=dataset,
            tau=ak.flatten(fatjet_tau3[:,0:1], axis=1),
        )
        output["lead_fatjet_tau4"].fill(
            dataset=dataset,
            tau=ak.flatten(fatjet_tau4[:,0:1], axis=1),
        )

        return output

    def postprocess(self, accumulator):
        return accumulator

class meta_processor(processor.ProcessorABC):
    def __init__(self, accumulator={}):
        self._accumulator = processor.dict_accumulator( accumulator )

    @property
    def accumulator(self):
        return self._accumulator

    def process(self, events):
        
        output = self.accumulator.identity()

        dataset = events.metadata['dataset']

        sumw = sum(events['genweight'])
        #sumw2 = sum(events['genEventSumw2'])
        #nevents = sum(events['genEventCount'])

        #output[events.metadata['filename']]['sumWeight'] += sumw  # naming for consistency...
        #output[events.metadata['filename']]['sumWeight2'] += sumw2  # naming for consistency...
        #output[events.metadata['filename']]['nevents'] += nevents
        #output[events.metadata['filename']]['nChunk'] += 1

        output[dataset]['sumWeight'] += sumw
        #output[dataset]['sumWeight2'] += sumw2
        #output[dataset]['nevents'] += nevents
        output[dataset]['nChunk'] += 1
        
        return output

    def postprocess(self, accumulator):
        return accumulator

if __name__ == '__main__':

    from yaml import Loader, Dumper
    import yaml


    import argparse

    argParser = argparse.ArgumentParser(description = "Argument parser")
    argParser.add_argument('--run_delphes', action='store_true', default=None, help="Run on delphes samples")
    argParser.add_argument('--run_flat', action='store_true', default=None, help="Run on flat ntuples")
    argParser.add_argument('--run_flat_remote', action='store_true', default=None, help="Run on flat ntuples")
    argParser.add_argument('--dask', action='store_true', default=None, help="Run on DASK cluster")
    args = argParser.parse_args()


    with open('../data/samples.yaml', 'r') as f:
        samples = yaml.load(f, Loader = Loader)

    meta_accumulator = {}
    for sample in samples:
        if sample not in meta_accumulator:
            meta_accumulator.update({sample: processor.defaultdict_accumulator(int)})
        for f in samples[sample]:
            meta_accumulator.update({f: processor.defaultdict_accumulator(int)})

    import time

    if args.run_delphes:

        tstart = time.time()

        output_delphes = processor.run_uproot_job(
            {'Znunu': samples['ZJetsToNuNu_HT-200To400_14TeV-madgraph_200PU']['delphes']},
            treename='Delphes',
            processor_instance = DelphesProcessor(),
            executor=processor.futures_executor,
            executor_args={"schema": DelphesSchema, "workers": 4},
            chunksize=100000,
            maxchunks=None,
        )
        elapsed = time.time() - tstart

        print ("Running on delphes on the grid: %.2f"%elapsed)

    if args.run_flat_remote:

        if args.dask:
            from tools.helpers import get_scheduler_address
            from dask.distributed import Client, progress

            scheduler_address = get_scheduler_address()
            c = Client(scheduler_address)

            exe_args = {
                'client': c,
                #'function_args': {'flatten': False},
                "schema": BaseSchema,
                #"tailtimeout": 300,
                "retries": 3,
                "skipbadfiles": True
            }
            exe = processor.dask_executor

        else:
            exe = processor.futures_executor
            exe_args = {"schema": BaseSchema, "workers": 20}


        tstart = time.time()

        meta_output_flat_remote = processor.run_uproot_job(
            {
                #'TT_TuneCUETP8M2T4_14TeV-powheg-pythia8_200PU': samples['TT_TuneCUETP8M2T4_14TeV-powheg-pythia8_200PU']['ntuples'],
                'ZJetsToNuNu_HT-200To400_14TeV-madgraph_200PU': samples['ZJetsToNuNu_HT-200To400_14TeV-madgraph_200PU']['ntuples'],
                #'ZJetsToNuNu_HT-400To600_14TeV-madgraph_200PU': samples['ZJetsToNuNu_HT-400To600_14TeV-madgraph_200PU']['ntuples'],
                #'ZJetsToNuNu_HT-600To800_14TeV-madgraph_200PU': samples['ZJetsToNuNu_HT-600To800_14TeV-madgraph_200PU']['ntuples'],
                #'ZJetsToNuNu_HT-800To1200_14TeV-madgraph_200PU': samples['ZJetsToNuNu_HT-800To1200_14TeV-madgraph_200PU']['ntuples'],
                #'ZJetsToNuNu_HT-1200To2500_14TeV-madgraph_200PU': samples['ZJetsToNuNu_HT-1200To2500_14TeV-madgraph_200PU']['ntuples'],
            },
            treename='myana/mytree',
            processor_instance = meta_processor(accumulator=meta_accumulator),
            executor = exe,
            executor_args = exe_args,
            chunksize = 1000000,
            maxchunks = None,
        )

        output_flat_remote = processor.run_uproot_job(
            {
                #'TT_TuneCUETP8M2T4_14TeV-powheg-pythia8_200PU': samples['TT_TuneCUETP8M2T4_14TeV-powheg-pythia8_200PU']['ntuples'],
                'ZJetsToNuNu_HT-200To400_14TeV-madgraph_200PU': samples['ZJetsToNuNu_HT-200To400_14TeV-madgraph_200PU']['ntuples'],
                #'ZJetsToNuNu_HT-400To600_14TeV-madgraph_200PU': samples['ZJetsToNuNu_HT-400To600_14TeV-madgraph_200PU']['ntuples'],
                #'ZJetsToNuNu_HT-600To800_14TeV-madgraph_200PU': samples['ZJetsToNuNu_HT-600To800_14TeV-madgraph_200PU']['ntuples'],
                #'ZJetsToNuNu_HT-800To1200_14TeV-madgraph_200PU': samples['ZJetsToNuNu_HT-800To1200_14TeV-madgraph_200PU']['ntuples'],
                #'ZJetsToNuNu_HT-1200To2500_14TeV-madgraph_200PU': samples['ZJetsToNuNu_HT-1200To2500_14TeV-madgraph_200PU']['ntuples'],
            },
            treename='myana/mytree',
            processor_instance = FlatProcessor(),
            executor = exe,
            executor_args = exe_args,
            chunksize=1000000,
            maxchunks=None,
        )
        elapsed = time.time() - tstart

        print ("Done.\n")
        print ("Running on flat tuples from grid: %.2f"%elapsed)

        meta = {}

        for sample in samples:
            meta[sample] = meta_output[sample]
            good_files = []
            skipped_files = []
            for rootfile in fileset[sample]:
                if meta_output[rootfile]:
                    good_files.append(rootfile)
                else:
                    skipped_files.append(rootfile)
            meta[sample]['good_files'] = good_files
            meta[sample]['n_good'] = len(good_files)
            meta[sample]['bad_files'] = skipped_files
            meta[sample]['n_bad'] = len(skipped_files)
            meta[sample]['xsec'] = samples[sample]['xsec']

        import matplotlib.pyplot as plt
        import mplhep as hep
        plt.style.use(hep.style.CMS)

        N_bins = hist.Bin('multiplicity', r'$N$', 6, -0.5, 5.5)
        mass_bins = hist.Bin('mass', r'$M\ (GeV)$', 30, 0, 300)
        pt_bins = hist.Bin('pt', r'$p_{T}\ (GeV)$', 50, 0, 500)
        fatjet_pt_bins = hist.Bin('pt', r'$p_{T}\ (GeV)$', 50, 200, 700)
        eta_bins = hist.Bin("eta", "$\eta$", 33, -4, 4)
        phi_bins = hist.Bin("phi", "$\phi$", 33, -4, 4)
        tau_bins = hist.Bin("tau", "$\tau$", 10, 0, 1)

        labels ={
            ('ZJetsToNuNu_HT-200To400_14TeV-madgraph_200PU',): r'$ZJets\to\nu\nu\ (HT\ 200\ to\ 400)$',
            ('ZJetsToNuNu_HT-400To600_14TeV-madgraph_200PU',): r'$ZJets\to\nu\nu\ (HT\ 400\ to\ 600)$',
            ('ZJetsToNuNu_HT-600To800_14TeV-madgraph_200PU',): r'$ZJets\to\nu\nu\ (HT\ 600\ to\ 800)$',
            ('ZJetsToNuNu_HT-800To1200_14TeV-madgraph_200PU',): r'$ZJets\to\nu\nu\ (HT\ 800\ to\ 1200)$',
            ('ZJetsToNuNu_HT-1200To2500_14TeV-madgraph_200PU',): r'$ZJets\to\nu\nu\ (HT\ 1200\ to\ 2500)$',
            ('TT_TuneCUETP8M2T4_14TeV-powheg-pythia8_200PU',): r'$t\bar{t}$',
        }

        colors ={
            ('ZJetsToNuNu_HT-200To400_14TeV-madgraph_200PU',): '#FED23F',
            ('ZJetsToNuNu_HT-400To600_14TeV-madgraph_200PU',): '#EB7DB5',
            ('ZJetsToNuNu_HT-600To800_14TeV-madgraph_200PU',): '#442288',
            ('ZJetsToNuNu_HT-800To1200_14TeV-madgraph_200PU',): '#6CA2EA',
            ('ZJetsToNuNu_HT-1200To2500_14TeV-madgraph_200PU',): '#B5D33D',
            ('TT_TuneCUETP8M2T4_14TeV-powheg-pythia8_200PU',): '#355C7D',
        }

        makePlot2(output_flat_remote, meta, 'met', 'pt', pt_bins, r'$MET_{pt}\ (GeV)$', labels, colors, remote=True)
        makePlot2(output_flat_remote, meta, 'lead_fatjet_pt', 'pt', fatjet_pt_bins, r'$p_{T}\ (GeV)$', labels, colors, remote=True)
        makePlot2(output_flat_remote, meta, 'lead_fatjet_eta', 'eta', eta_bins, r'$\eta$', labels, colors, remote=True)
        makePlot2(output_flat_remote, meta, 'lead_fatjet_phi', 'phi', phi_bins, r'$\phi$', labels, colors, remote=True)
        makePlot2(output_flat_remote, meta, 'lead_fatjet_mass', 'mass', mass_bins, r'$mass\ (GeV)$', labels, colors, remote=True)
        makePlot2(output_flat_remote, meta, 'lead_fatjet_sdmass', 'mass', mass_bins, r'$softdrop\ mass\ (GeV)$', labels, colors, remote=True)
        makePlot2(output_flat_remote, meta, 'lead_fatjet_tau1', 'tau', tau_bins, r'$\tau_1$', labels, colors, remote=True)
        makePlot2(output_flat_remote, meta, 'lead_fatjet_tau2', 'tau', tau_bins, r'$\tau_2$', labels, colors, remote=True)
        makePlot2(output_flat_remote, meta, 'lead_fatjet_tau3', 'tau', tau_bins, r'$\tau_3$', labels, colors, remote=True)
        makePlot2(output_flat_remote, meta, 'lead_fatjet_tau4', 'tau', tau_bins, r'$\tau_4$', labels, colors, remote=True)
        makePlot2(output_flat_remote, meta, 'nfatjet', 'multiplicity', N_bins, r'$n_{fatjet}$', labels, colors, remote=True)


    if args.run_flat:

        tstart = time.time()

        output_flat = processor.run_uproot_job(
            {'Znunu': glob.glob('/nfs-7/userdata/dspitzba/ZJetsToNuNu_HT-200To400_14TeV-madgraph_200PU/*.root')},
            treename='myana/mytree',
            processor_instance = FlatProcessor(),
            executor=processor.futures_executor,
            executor_args={"schema": BaseSchema, "workers": 20},
            chunksize=1000000,
            maxchunks=None,
        )
        elapsed = time.time() - tstart

        print ("Running on flat tuples from nfs: %.2f"%elapsed)
        
        import matplotlib.pyplot as plt
        import mplhep as hep
        plt.style.use(hep.style.CMS)
                
        #define bins
        
        N_bins = hist.Bin('multiplicity', r'$N$', 6, -0.5, 5.5)
        mass_bins = hist.Bin('mass', r'$M\ (GeV)$', 20, 0, 200)
        pt_bins = hist.Bin('pt', r'$p_{T}\ (GeV)$', 30, 0, 300)
        fatjet_pt_bins = hist.Bin('pt', r'$p_{T}\ (GeV)$', 30, 200, 500)
        eta_bins = hist.Bin("eta", "$\eta$", 33, -4, 4)
        phi_bins = hist.Bin("phi", "$\phi$", 33, -4, 4)
        tau_bins = hist.Bin("tau", "$\tau$", 10, 0, 1)
                
        labels ={
            ('Znunu',): r'$Z\nu\nu$'
        }
        
        colors ={
            ('Znunu',): '#FFCA3A'
        }
       
        makePlot2(output_flat, 'met', 'pt', pt_bins, r'$MET_{pt}\ (GeV)$', labels, colors)
        makePlot2(output_flat, 'lead_fatjet_pt', 'pt', fatjet_pt_bins, r'$p_{T}\ (GeV)$', labels, colors)
        makePlot2(output_flat, 'lead_fatjet_eta', 'eta', eta_bins, r'$\eta$', labels, colors)
        makePlot2(output_flat, 'lead_fatjet_phi', 'phi', phi_bins, r'$\phi$', labels, colors)
        makePlot2(output_flat, 'lead_fatjet_mass', 'mass', mass_bins, r'$mass\ (GeV)$', labels, colors)
        makePlot2(output_flat, 'lead_fatjet_sdmass', 'mass', mass_bins, r'$softdrop\ mass\ (GeV)$', labels, colors)
        makePlot2(output_flat, 'lead_fatjet_tau1', 'tau', tau_bins, r'$\tau_1$', labels, colors)
        makePlot2(output_flat, 'lead_fatjet_tau2', 'tau', tau_bins, r'$\tau_2$', labels, colors)
        makePlot2(output_flat, 'lead_fatjet_tau3', 'tau', tau_bins, r'$\tau_3$', labels, colors)
        makePlot2(output_flat, 'lead_fatjet_tau4', 'tau', tau_bins, r'$\tau_4$', labels, colors)
        makePlot2(output_flat, 'nfatjet', 'multiplicity', N_bins, r'$n_{fatjet}$', labels, colors)

        #try one makePlot call for now
        
        #my_colors = {
        #    'Znunu': '#FFCA3A'
        #}
        
        #my_labels = {
        #    'Znunu': r'$Z\nu\nu$'
        #}
        
        #makePlot(output_flat, "met", 'pt',
        #    bins=pt_bins, log=False, normalize=True, axis_label=r'$p_{T}^{miss}$', lumi=1,
        #    save='/home/users/ewallace/public_html/HbbMET/delphes_flat_MET_background',
        #)
    #print(output)
