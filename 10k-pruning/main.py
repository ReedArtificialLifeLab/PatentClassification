import sys
import csv
import tqdm
import bigger_csv_entries
bigger_csv_entries.init()

# ------------------------------------------------------------------------
# parameters
# - input csv file
# - output csv file (to write)
#

if len(sys.argv) < 2:
    print('please provide a input CSV file')
    quit()

# if len(sys.argv) < 3:
#     print('please provide an output CSV file')
#     quit()

VERBOSITY = 1
MAX_ROW = None # 2000
TOTAL = 179717  # number of papers in input csv
CATCH = False

# ------------------------------------------------------------------------
# files
#

cikgvkey_filename = 'csv/cik_to_gvkey.csv'
input_filename = sys.argv[1]
if len(sys.argv) < 3:
    output_filename = input_filename[:-4] + ' [filtered].csv'
else:
    output_filename = sys.argv[2]

# open files

cikgvkey_file = open(cikgvkey_filename, 'r')
input_file = open(input_filename, 'r')
output_file = open(output_filename, 'w+')


# ------------------------------------------------------------------------
# setup csv readers and writers
#

cikgvkey_reader = csv.reader(cikgvkey_file)
input_reader = csv.reader(input_file, delimiter=',')
output_writer = csv.writer(output_file, delimiter=',')

# create cikgvkey dict


# in the corpus, ciks are padded by 0s to 10 digits
def format_cik(cik):
    while len(cik) < 10:
        cik = '0' + cik
    return cik


cikgvkey_dict = dict()
for row in cikgvkey_reader:
    cikgvkey_dict[format_cik(row[0])] = row[1]

# ------------------------------------------------------------------------
# filter firms
#


# ids format: [sic]_[cik]_[date]_[name]
def parse_ids(ids):
    # if ids.startswith("CLASSIFICATION:_"):
    #     ids = ids[len("CLASSIFICATION:_"):]
    ids = ids.split('_')
    return ids[0], ids[1], ids[2], ids[3]


# check if row should be included
def check_row(irow):
    i, row = irow

    # copy header row
    if i == 0: return True

    # read row data
    ids = row[0]

    # problem row...
    if ids.startswith("CLASSIFICATION"):
        print('ids.startswith("CLASSIFICATION")')
        print(row)
        quit()
        return False

    # text = row[1]
    sic, cik, date, name = parse_ids(ids)
    sic = int(sic)
    cik = format_cik(cik)

    # whether or not to include row
    result = True

    # remove firms without Compustat data
    if cik not in cikgvkey_dict.keys():
        result = False
    # remove financial firms (SIC codes in the range 6000–6999)
    elif 6000 <= sic < 7000:
        result = False
    # TODO: remove firms with nonpositive sales
    # TODO: remove firms with assets of less than $1 million
    # TODO: remove firms without 1 year of lagged Compustat data

    if VERBOSITY >= 2:
        if result:
            print("✓", ids)
        else:
            print(" ", ids)
    return result


# ignore first header row
total = -1
included = -1


# check all rows, writing included rows to output
for (i, row) in tqdm.tqdm(enumerate(input_reader), total=TOTAL):
    total += 1

    def do():
        global total, included
        if check_row((i, row)):
            output_writer.writerow(row)
            included += 1
        if MAX_ROW is not None and total >= MAX_ROW:
            return True

    if CATCH:
        try:
            stop = do()
        except:
            print("error on row:", row)
            print("row:", row)
            quit()
    else:
        stop = do()

    if stop: break


if VERBOSITY >= 1:
    print()
    print("         total:", total)
    print("      included:", included)
    print("included/total:", included/total)
    print()


"""
# create a bash script that finds CIKs in the cik_to_gvkey CSV
with open("tmp.sh", "w+") as file:
    ciks = list(cikgvkey_dict.keys())
    # patterns = ' '.join([ '-e "0000{0}_"'.format(cik) for cik in ciks[2000:2050] ])
    patterns = ' '.join([ '-e "0000{0}_"'.format(cik) for cik in ciks[0:50] ])
    # file.write('echo | grep -c {0} {1}'.format(patterns, input_filename))
    file.write('grep {0} {1} > out.txt'.format(patterns, input_filename))

    # for i in range(1000, 1020):
    #     cik = ciks[i]
    #     file.write('grep -c "{0}_" {1} > out.txt\n'.format(cik, input_filename))
"""


# ------------------------------------------------------------------------
# Cleanup
#


cikgvkey_file.close()
input_file.close()
output_file.close()
