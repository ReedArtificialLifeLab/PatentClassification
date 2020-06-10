import sys
import csv
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


# ------------------------------------------------------------------------
# count firms
#


total = -1
for _ in input_reader: total += 1
print("total:", total)


# ------------------------------------------------------------------------
# Cleanup
#


cikgvkey_file.close()
input_file.close()
output_file.close()
