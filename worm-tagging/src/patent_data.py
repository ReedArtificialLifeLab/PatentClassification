import csv
import json
from tqdm import tqdm

data_dir = "../data/"

clusterdocs_path  = data_dir + "cluster_docs.csv"
localthreads_path = data_dir + "local_threads_dth0.06_final_removed.csv"

centroids_path     = data_dir + "centroids.json"
worms_path         = data_dir + "worms.json"

patentsraw_path    = data_dir + "patents_raw.csv"

tfidfdict_path     = data_dir + "tfidf_dict.json"


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
# load data
#


# centroids : centroid_id => list<patent_id>
def load_centroids():
    print("[*] loading centroids...")
    with open(centroids_path, "r+") as centroids_json:
        return json.load(centroids_json)

# centroids_inv : patent_id => centroid_id
def load_centroids_inv():
    centroids = load_centroids()
    print("[*] loading centroids_inv...")
    centroids_inv = {}
    for centroid_id, patent_ids in tqdm(centroids.items()):
        for patent_id in patent_ids:
            centroids_inv[int(patent_id)] = int(centroid_id)
    return centroids_inv

# worms : worm_id => list<centroid_id>
def load_worms():
    print("[*] loading worms...")
    with open(worms_path, "r+") as worms_json:
        return json.load(worms_json)


def load_patentsraw():
    print("[*] loading patents_raw...")
    return csv.reader(open(patentsraw_path, "r+"), delimiter=",")


# superdocs : worm_id => superdoc
def load_superdocs():
    print("[*] loading superdocs...")
    patentsraw = load_patentsraw()
    centroids_inv = load_centroids_inv()

    # print("centroids_inv =", list(centroids_inv.items())[:10])

    superdocs = {} # worm_id => superdoc

    missing_patent_ids = []

    row_count = 10

    for row in tqdm(patentsraw):
        if row_count <= 0: break
        row_count -= 1
        
        patent_id = int(row[0])
        patent_text = row[1]

        if patent_id not in centroids_inv:
            missing_patent_ids.append(patent_id)
            continue

        worm_id = centroids_inv[patent_id]
        if worm_id not in superdocs:
            superdocs[worm_id] = patent_text
        else:
            superdocs[worm_id] = patent_text + " " + superdocs[worm_id]


    print("len(missing_patent_ids) =", len(missing_patent_ids))
    # print("missing_patent_ids", missing_patent_ids)

    return superdocs


# tfidf_dict : worm_id => term => tfidf
def load_tfidf_dict():
    with open(tfidfdict_path, "r+") as tfidfdict_json:
       return json.load(tfidfdict_json)

def save_tfidf_dict(tfidf_dict):
    with open(tfidfdict_path, "w+") as tfidfdict_json:
        json.dump(tfidf_dict, tfidfdict_json)
