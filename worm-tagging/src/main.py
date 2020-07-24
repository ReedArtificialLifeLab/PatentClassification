import patent_data
import tfidf

if __name__ == "__main__":
    # superdocs = patent_data.load_superdocs()
    # print(list(superdocs.items())[0])

    tfidf_dict = tfidf.calculate_tfidf_dict()
    patent_data.save_tfidf_dict(tfidf_dict)
