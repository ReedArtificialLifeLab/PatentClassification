import csv


def read_csv(csv_filename):
    with open(csv_filename) as csv_file:
        return csv.reader(csv_file, delimiter=',')
        
