import re
import math
from tqdm import tqdm

import patent_data


def calculate_tfidf_dict():
    print("calculating tfidf_dict...")
    superdocs = patent_data.load_superdocs()

    tf_dict = {} # worm_id => term => term frequency (tf)
    dc_dict = {} # term    => document count
    n_docs  = 0  # number of documents in corpus
    
    for worm_id, superdoc in tqdm(superdocs.items()):
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
    for worm_id in superdocs.keys():
        tfidf_dict[int(worm_id)] = {}
        for term, dc in dc_dict.items():
            if term in tf_dict[worm_id]:
                tf = tf_dict[worm_id][term]
                idf = n_docs / dc
                if 0.5 < idf and idf < 2:
                    tfidf = tf * math.log(idf)
                    tfidf_dict[worm_id][term] = tfidf
            

    return tfidf_dict
