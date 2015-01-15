import xlrd
import csv
import sys

""" use: $python xls2csv 'filename'

"""

fn=sys.argv[1]
 

def csv_from_excel(filename):

	wb = xlrd.open_workbook(filename)
	sh = wb.sheet_by_name('Sheet1')
	your_csv_file = open(filename+'.csv', 'wb')
	#wr = csv.writer(your_csv_file, quoting=csv.QUOTE_ALL)
	wr = csv.writer(your_csv_file)

	for rownum in xrange(sh.nrows):
	    wr.writerow(sh.row_values(rownum))

	your_csv_file.close()

def main():
	fn=sys.argv[1]
	csv_from_excel(fn)


if __name__ == '__main__':
	main()