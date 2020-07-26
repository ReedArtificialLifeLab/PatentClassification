import patent_data
import matplotlib.pyplot as plt


if __name__ == "__main__":
    # centroids
    # centroids = patent_data.load_centroids()
    # x = [ len(patent_ids) for patent_ids in centroids.values() ]
    # n, bins, patches = plt.hist(x, 50)
    # plt.grid(True)
    # plt.show()

    # patents
    # patent_data.save_patents()

    
    # centroidsinv
    # patent_data.save_centroidsinv()

    
    # superdocs
    # patent_data.save_superdocs()

    
    # tfidf
    # patent_data.save_tfidf_all()


    # tfidf_best
    # patent_data.save_tfidfbest_all()
    patent_data.save_tfidfbest_all_csv()



