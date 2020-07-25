import csv
import json
from tqdm import tqdm

import re
import math


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
superdocs_path    = data_dir + "superdocs.json"
tfidf_path        = data_dir + "tfidf.json"


#
# clusterdocs -> centroids
#


def convert_clusterdocs_to_centroids():
    with open(clusterdocs_path, "r+") as clusterdocs_csv:
        clusterdocs_reader = csv.reader(clusterdocs_csv, delimiter=",")

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


        with open(centroids_path, "w+") as centroids_json:
            json.dump(centroids, centroids_json)

            
#
# localthreads -> worms
#


def convert_localthreads_worms():
    with open(localthreads_path, "r+") as localthreads_csv:
        localthreads_reader = csv.reader(localthreads_csv, delimiter=",")

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

        with open(worms_path, "w+") as worms_json:
            json.dump(worms, worms_json)


#
# centroids
#


# centroids : centroid_id => list<patent_id>
def load_centroids():
    print("[*] loading centroids...")
    with open(centroids_path, "r+") as centroids_json:
        return json.load(centroids_json)

            
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
    with open(centroidsinv_path, "r+") as centroidsinv_json:
        return json.load(centroidsinv_json)


def save_centroidsinv(centroidsinv=None):
    if centroidsinv is None:
        centroidsinv = calculate_centroidsinv()
    with open(centroidsinv_path, "w+") as centroidsinv_json:
        json.dump(centroidsinv, centroidsinv_json)


#
# worms
#


# worms : worm_id => list<centroid_id>
def load_worms():
    print("[*] loading worms...")
    with open(worms_path, "r+") as worms_json:
        return json.load(worms_json)
        
    
#
# superdocs
#
#   a superdoc is the concatenation of all the patent_text of
#   the patents in the superdoc's worm
#


# superdocs : worm_id => superdoc
def calculate_superdocs():
    print("[*] loading superdocs...")
    patentsraw = load_patentsraw()
    centroidsinv = load_centroidsinv()

    # print("centroidsinv =", list(centroidsinv.items())[:10])

    superdocs = {} # worm_id => superdoc

    missing_patent_ids = []

    take = 10 # TEST

    for row in tqdm(patentsraw):
        if take is not None:
            if take <= 0:
                break
            else:
                take -= 1
        
        patent_id = int(row[0])
        patent_text = row[1]

        if str(patent_id) not in centroidsinv:
            missing_patent_ids.append(patent_id)
            continue

        worm_ids = centroidsinv[str(patent_id)]
        for worm_id in worm_ids:
            if worm_id in superdocs:
                superdocs[worm_id] += " " + patent_text
            else:
                superdocs[worm_id] = patent_text

    print("len(missing_patent_ids) =", len(missing_patent_ids))
    # print("missing_patent_ids", missing_patent_ids) # DEBUG

    return superdocs


# patentsraw : csv<patent_id, patent_text>
def load_patentsraw():
    print("[*] loading patents_raw...")
    return csv.reader(open(patentsraw_path, "r+"), delimiter=",")


# superdocs : worm_id => superdoc
def load_superdocs():
    print("[*] loading superdocs...")
    with open(superdocs_path, "r+") as superdocs_json:
        return json.load(superdocs_json)

def save_superdocs(superdocs=None):
    if superdocs is None:
        superdocs = calculate_superdocs()
    with open(superdocs_path, "w+") as superdocs_json:
        json.dump(superdocs, superdocs_json)

        
#
# tfidf
#


def calculate_tfidf():
    print("calculating tfidf_dict...")
    superdocs = load_superdocs()

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

    tfidf_dict = {} # worm_id => term => tfidf

    # calculate idf and tfidf for each term in corpus relative to each doc in corpus
    for worm_id in map(int, superdocs.keys()):
        tfidf_dict[int(worm_id)] = {}
        for term, dc in dc_dict.items():
            if term in tf_dict[worm_id]:
                tf = tf_dict[worm_id][term]
                idf = n_docs / dc
                if 0.5 < idf and idf < 2:
                    tfidf = tf * math.log(idf)
                    tfidf_dict[worm_id][term] = tfidf
            

    return tfidf_dict


# tfidf : worm_id => term => tfidf
def load_tfidf():
    with open(tfidf_path, "r+") as tfidf_json:
       return json.load(tfidf_json)

def save_tfidf(tfidf=None):
    if tfidf is None:
        tfidf = calculate_tfidf()
    with open(tfidf_path, "w+") as tfidf_json:
        json.dump(tfidf, tfidf_json)

