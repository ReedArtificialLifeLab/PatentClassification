import csv
import json
from tqdm import tqdm

import re
import math
import numpy as np
np.random.seed(1234567890)


#
# file structure i.e. directories and paths
# 


data_dir = "../data/"

clusterdocs_path  = data_dir + "cluster_docs.csv"
localthreads_path = data_dir + "local_threads_dth0.06_final_removed.csv"

centroids_path    = data_dir + "centroids.json"
centroidsinv_path = data_dir + "centroids_inv.json"
worms_path        = data_dir + "worms.json"

patentsraw_path   = data_dir + "patents_raw.csv"
patents_path      = data_dir + "patents.json"
superdocs_path    = data_dir + "superdocs.json"

tfidf_dir         = data_dir + "tfidf/"
tfidf_path        = lambda worm_id: tfidf_dir + str(worm_id) + ".json"

tfidfbest_dir     = data_dir + "tfidf_best/"
tfidfbest_path    = lambda worm_id: tfidfbest_dir + str(worm_id) + ".json"


superdocs_sample_path = data_dir + "superdocs_sample.json"


#
# clusterdocs -> centroids
#


def convert_clusterdocs_to_centroids():
    with open(clusterdocs_path, "r+") as clusterdocs_file:
        clusterdocs_reader = csv.reader(clusterdocs_file, delimiter=",")

        # get centroid_ids
        for centroid_ids in clusterdocs_reader:
            centroid_ids = list(map(int, centroid_ids))
            break

        # initialize centroids : centroid_id => list patent_id
        centroids = { int(centroid_id): [] for centroid_id in centroid_ids }

        for patent_ids in tqdm(clusterdocs_reader):
            for centroid_index, patent_id in enumerate(patent_ids):
                if not patent_id: continue
                centroids[centroid_ids[centroid_index]].append(int(patent_id))


        with open(centroids_path, "w+") as centroids_file:
            json.dump(centroids, centroids_file)

            
#
# localthreads -> worms
#


def convert_localthreads_worms():
    with open(localthreads_path, "r+") as localthreads_file:
        localthreads_reader = csv.reader(localthreads_file, delimiter=",")

        worms = {}

        # first entry of row is worm_id
        # after first, entries are centroid_ids
        for row in tqdm(localthreads_reader):
            worm_id = int(row[0])
            centroid_ids = \
              [ int(float(centroid_id))
                for centroid_id in row[1:]
                if centroid_id ]
            worms[worm_id] = centroid_ids

        with open(worms_path, "w+") as worms_file:
            json.dump(worms, worms_file)


#
# centroids
#


# centroids : centroid_id => list<patent_id>
def load_centroids():
    print("[*] loading centroids...")
    with open(centroids_path, "r+") as centroids_file:
        return json.load(centroids_file)

            
#
# centroidsinv
#
#   a convenient mapping of patent_ids to a list of the centroids
#   that they are clustered with at one point during their history
#
            

# centroidsinv : patent_id => list<centroid_id>
def calculate_centroidsinv():
    centroids = load_centroids()
    print("[*] loading centroidsinv...")
    centroidsinv = {}
    for centroid_id, patent_ids in tqdm(centroids.items()):
        for patent_id in patent_ids:
            if int(patent_id) in centroidsinv:
                centroidsinv[int(patent_id)].append(int(centroid_id))
            else:
                centroidsinv[int(patent_id)] = [int(centroid_id)]
    return centroidsinv
            

# centroidsinv : patent_id => list<centroid_id>
def load_centroidsinv():
    with open(centroidsinv_path, "r+") as centroidsinv_file:
        return json.load(centroidsinv_file)


def save_centroidsinv(centroidsinv=None):
    if centroidsinv is None:
        centroidsinv = calculate_centroidsinv()
    with open(centroidsinv_path, "w+") as centroidsinv_file:
        json.dump(centroidsinv, centroidsinv_file)


#
# worms
#


# worms : worm_id => list<centroid_id>
def load_worms():
    print("[*] loading worms...")
    with open(worms_path, "r+") as worms_file:
        return json.load(worms_file)
        

#
# patents
#

# patentsraw : csv<patent_id, patent_text>
def load_patentsraw():
    print("[*] loading patents_raw...")
    return csv.reader(open(patentsraw_path, "r+"), delimiter=",")


# patents : patent_id => patent_text
def calculate_patents():
    print("[*] calculating patents...")
    patentsraw = load_patentsraw()
    patents = {}
    for row in tqdm(patentsraw):
        patents[int(row[0])] = row[1]
    return patents

def load_patents():
    print("[*] loading patents...")
    with open(patents_path, "r+") as patents_file:
        return json.load(patents_file)

def save_patents(patents=None):
    if patents is None:
        patents = calculate_patents()
    print("[*] saving patents...")
    with open(patents_path, "w+") as patents_file:
        json.dump(patents, patents_file)
        
    
#
# superdocs
#
#   a superdoc is the concatenation of all the patent_text of
#   the patents in the superdoc's worm
#

superdoc_config = {
    "size": 50
}

# superdocs : worm_id => superdoc
def calculate_superdocs():
    patents   = load_patents()
    centroids = load_centroids()
    print("[*] calculating superdocs...")

    superdocs = {} # worm_id => superdoc_text

    # centroids that were are small
    # (i.e. smaller than superdoc_config.size
    centroid_ids_omitted = []

    # patent_ids that were in centroids dict but not patents dict
    patent_ids_missing = []

    # for each worm, take a random sample of patent_ids
    for centroid_id, patent_ids in tqdm(centroids.items()):
        centroid_id = int(centroid_id)
        # centroid is too small
        if len(patent_ids) < superdoc_config["size"]:
            centroid_ids_omitted.append(centroid_id)
            continue

        superdoc_patent_ids = np.random.choice(patent_ids, size=superdoc_config["size"])

        superdoc_text = ""
        for patent_id in superdoc_patent_ids:
            patent_id = str(patent_id)
            if patent_id not in patents:
                patent_ids_missing.append(patent_id)
                continue
            superdoc_text += " " + patents[patent_id]

        superdocs[centroid_id] = superdoc_text

    print("[*] len(centroid_ids_omitted) =", len(centroid_ids_omitted))
    print("[*] len(patent_ids_missing)   =", len(patent_ids_missing))

    return superdocs


# superdocs : worm_id => superdoc
def load_superdocs():
    print("[*] loading superdocs...")
    with open(superdocs_path, "r+") as superdocs_file:
        return json.load(superdocs_file)

def save_superdocs(superdocs=None):
    if superdocs is None:
        superdocs = calculate_superdocs()
    with open(superdocs_path, "w+") as superdocs_file:
        json.dump(superdocs, superdocs_file)


# only works with the first 10 centroids
def calculate_superdocs_sample():
    patents   = load_patents()
    centroids = load_centroids()
    print("[*] calculating superdocs...")

    superdocs = {} # worm_id => superdoc_text

    # centroids that were are small
    # (i.e. smaller than superdoc_config.size
    centroid_ids_omitted = []

    # patent_ids that were in centroids dict but not patents dict
    patent_ids_missing = []

    # for each worm, take a random sample of patent_ids
    for centroid_id, patent_ids in tqdm(list(centroids.items())[:10]):
        centroid_id = int(centroid_id)
        # centroid is too small
        if len(patent_ids) < superdoc_config["size"]:
            centroid_ids_omitted.append(centroid_id)
            continue

        superdoc_patent_ids = np.random.choice(patent_ids, size=superdoc_config["size"])

        superdoc_text = ""
        for patent_id in superdoc_patent_ids:
            patent_id = str(patent_id)
            if patent_id not in patents:
                patent_ids_missing.append(patent_id)
                continue
            superdoc_text += " " + patents[patent_id]

        superdocs[centroid_id] = superdoc_text

    print("[*] len(centroid_ids_omitted) =", len(centroid_ids_omitted))
    print("[*] len(patent_ids_missing)   =", len(patent_ids_missing))

    return superdocs
        
        
def save_superdocs_sample():
    superdocs_sample = calculate_superdocs_sample()
    print("[*] saving superdocs sample...")
    with open(superdocs_sample_path, "w+") as superdocs_sample_file:
        json.dump(superdocs_sample, superdocs_sample_file)

def load_superdocs_sample():
    print("[*] loading superdocs sample...")
    with open(superdocs_sample_path, "r+") as superdocs_sample_file:
        return json.load(superdocs_sample_file)

    
#
# tfidf
#


def calculate_tfidf_all():
    superdocs = load_superdocs()
    # superdocs = load_superdocs_sample() # TEST

    print("[*] calculating tfidf for all worms...")

    tf_dict = {} # worm_id => term => term frequency (tf)
    dc_dict = {} # term    => document count
    n_docs  = 0  # number of documents in corpus
    
    for worm_id, superdoc in tqdm(superdocs.items()):
        worm_id = int(worm_id)
        tf_dict[worm_id] = {}
        
        n_docs += 1
        terms   = set() # set of terms in this document
        tc_dict = {}    # term => term count in this document
        
        for term in re.split(r"[\.\s|\?\s|\!\s|\n]", superdoc):
            term = term.lower()
            if not term: continue

            if term in dc_dict: dc_dict[term] += 1
            else:               dc_dict[term] = 1

            if term in tc_dict: tc_dict[term] += 1
            else:               tc_dict[term] = 1

            terms.add(term)

        # calculate tf for terms in this document
        term_count = len(terms)
        for term in terms:
            tf_dict[worm_id][term] = tc_dict[term] / term_count

    tfidf_all_dict = {} # worm_id => term => tfidf

    # calculate idf and tfidf for each term in corpus relative to each doc in corpus
    for worm_id in superdocs.keys():
        worm_id = int(worm_id)
        tfidf_all_dict[worm_id] = {}
        for term, dc in dc_dict.items():
            if term in tf_dict[worm_id]:
                tf = tf_dict[worm_id][term]
                idf = n_docs / dc
                if 0.5 < idf and idf < 2:
                    tfidf = tf * math.log(idf)
                    tfidf_all_dict[worm_id][term] = tfidf
            
    return tfidf_all_dict


# tfidf : worm_id => term => tfidf
def load_tfidf(worm_id):
    print("[*] loading tfidf for worm_id="+str(worm_id)+"...")
    with open(tfidf_path(worm_id), "r+") as tfidf_file:
       return json.load(tfidf_file)

def save_tfidf(worm_id, tfidf):
    with open(tfidf_path(worm_id), "w+") as tfidf_file:
        json.dump(tfidf, tfidf_file)
   
def save_tfidf_all(tfidf_all=None):
    print("[*] saving tfidf for all worms...")
    if tfidf_all is None:
        tfidf_all = calculate_tfidf_all()
    for worm_id, tfidf in tfidf_all.items():
        save_tfidf(worm_id, tdidf)

            
#
# tfidf best
#


def save_tfidfbest_all():
    worms = load_worms()
    # worms = load_superdocs_sample() # TEST

    print("[*] calculating tfidf_best for all worms...")

    for worm_id in worms.keys():
        worm_id = int(worm_id)
        tfidf = load_tfidf(worm_id)
        tfidfbest = list(sorted(tfidf.items(), key=lambda x: x[1], reverse=True))[:50]
        with open(tfidfbest_path(worm_id), "w+") as tfidfbest_file:
            json.dump(tfidfbest, tfidfbest_file)
        
