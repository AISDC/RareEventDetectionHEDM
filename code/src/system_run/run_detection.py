import sys
sys.path.append('../..')

from src.util.utility import * 
from src.embed.embed import Embed
from src.cluster.cluster import Cluster

import pandas as pd
from tqdm import tqdm
import time

class DetectionRun():

    def __init__(self, args): 
        self._args = args  

    # the following function is used to quantify the distribution and UQ for partial dataset
    # based on the number of degrees
    def ds_anamoly_quantify(self, dsfname, frms, embmdl, clusmdl, min_score, degs=360, degs_mode=1, seed=0):
        if degs_mode == 0 and degs < 360:
            # for the mode 0, we do sampling 20 times
            uqs = []
            for i in range(20):
                # print(f"{i}th sampling start")
                emb, num_patches = embmdl.peak2emb_missingwedge(dsfname, frms=frms, degree=degs, seed=seed+i, degs_mode=degs_mode)
                #print("done with generating embddings")
                uq, dist = clusmdl.kmeans_clustering_and_dist(emb, min_score=min_score)
                uqs.append(uq)
                # print(f"{i}th sampling is done")
            return uqs
        elif degs_mode == 0 and degs >= 360:
            emb, num_patches = embmdl.peak2emb_missingwedge(dsfname, frms=frms, degree=degs, seed=seed)
            #print("done with generating embddings")
            uq, dist = clusmdl.kmeans_clustering_and_dist(emb, min_score=min_score)
            # #print("done with generaring distribution")
            uqs = [uq] * 20
            return uqs
        else:
            emb, num_patches = embmdl.peak2emb_missingwedge(dsfname, frms=frms, degree=degs, seed=seed)
            #print("done with generating embddings")
            uq, dist = clusmdl.kmeans_clustering_and_dist(emb, min_score=min_score)
            # #print("done with generaring distribution")
            return dsfname, np.append(dist, uq), num_patches
    
    def start(self):

        # first find all datasets available:
        list_datasets, list_pressures, list_idx = find_datasets(self._args.ids, self._args.dpre)
    
        # create a new embed class
        embmdl = Embed(self._args.embmdl)

        # use the specfic dataset as the baseline dataset
        emb_bl, _ = embmdl.peak2emb_missingwedge(self._args.bh5)

        print("now need to do kmeans")
        # create a clustering model
        clusmdl = Cluster(numClusters = self._args.ncluster)
        print(emb_bl.shape)
        clusmdl.train(emb_bl)
        print("kmeans is done ...")

        dist_and_uq = [] # used to store distribution and UQ for all datasets
        dataset_tag = [self._args.bh5]
        uq_bl, dist_bl = clusmdl.kmeans_clustering_and_dist(emb_bl, min_score=self._args.uqthr)
        if self._args.degs_mode:
            dist_and_uq.append(np.append(dist_bl, uq_bl))
        else:
            dist_and_uq.append([uq_bl] * 20)

        result = None
        print("start for anomaly detection from 1st dataset (0th one is used for baseline dataset)")
        
        total_patches = 0

        tic = time.perf_counter()

        for i in range(len(list_datasets)):
            test_degrees = 360
            if self._args.bh5 != self._args.ids+list_datasets[i]:
                test_degrees = degs=self._args.degs

            print(f"start for anomaly detection from {i}th dataset (0th one is used for baseline dataset)")
            result = self.ds_anamoly_quantify(self._args.ids+list_datasets[i], self._args.frms, embmdl, clusmdl, 
                                              self._args.uqthr, degs=test_degrees, degs_mode=self._args.degs_mode, seed=self._args.seed)
            #dataset_tag += [_res[0] for _res in result]s
            dataset_tag.append(list_datasets[i])
            if self._args.degs_mode:
                dist_and_uq.append(result[1])
                total_patches += result[2]
            else: 
                dist_and_uq.append(result)

        toc = time.perf_counter()
        print(f"it takes {toc - tic:0.4f} seconds to test {len(list_datasets)} datasets")
        print(f"the average patches for each dataset is {total_patches/(len(list_datasets)-1)}")

        if self._args.degs_mode:
            cols =  [f'c{c}' for c in range(dist_bl.shape[0])] + ['uq', ]
        else:
            cols = [f'test:{c}' for c in range(20)]

        df = pd.DataFrame(dist_and_uq, columns=cols)
        df['dataset'] = dataset_tag
        df.to_csv(self._args.ocsv, index=False)