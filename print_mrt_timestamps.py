#!/usr/bin/env python
'''
print_timestamps.py - a script to print timestamp from the MRT format

Written by Andras Majdan <majdan.andras@gmail.com>
License: BSD

Example:
wget ftp://routeviews.org/route-views.sydney/bgpdata/2016.05/UPDATES/updates.20160501.*
ls updates* | sort > filelist.txt
./print_mrt_timestamps.py -f filelist.txt -t ts.txt -a abs.txt -d diff.txt
'''

import sys, getopt
from datetime import *
from mrtparse import *

def help_and_exit(exitcode=0):
	print('print_mrt_timestamps.py -f <fileslist_input> -t <timestamp_output> -a <abstime_output> -d <difftime_output>')
	sys.exit(exitcode)

def set_param(paramset, mask):
	if paramset & mask:
		print('Error: parameter repeat')
		help_and_exit(1)
	else:
		paramset |= mask
	return paramset 

def process_timestamps(mrtfile, timestamph, abstimeh, difftimeh, first_timestamp=1, firstdate=None, prevdate=None):
	d = Reader(mrtfile)
	
	for m in d:
		m = m.mrt
		
		if m.err == MRT_ERR_C['MRT Header Error']:
			# do not print timestamp
			continue
			
		if first_timestamp == 1:
			first_timestamp = 0
			prevdate = datetime.fromtimestamp(m.ts)
			firstdate = prevdate
			abstimeh.write('bgpabstime\n')
			difftimeh.write('bgpdifftime\n')
			
		mrt_date = datetime.fromtimestamp(m.ts)
		absdatetime = (mrt_date - firstdate).total_seconds()
		diffdatetime = (mrt_date - prevdate).total_seconds()
		prevdate = mrt_date
		
		sdate = str(mrt_date.year) + "{0:0>2}".format(mrt_date.month) + "{0:0>2}".format(mrt_date.day)
		stime = "{0:0>2}".format(mrt_date.hour) + ':' + "{0:0>2}".format(mrt_date.minute) + ':' + "{0:0>2}".format(mrt_date.second)
		timestamph.write(sdate + ' ' + stime + '\n')
		abstimeh.write(str(int(absdatetime))+'\n')
		difftimeh.write(str(int(diffdatetime))+'\n')
		
	try: 
		d.close()
	except:
		pass

	return first_timestamp, firstdate, prevdate

def main(argv):
	filelistfile = ''
	timestampfile = ''
	abstimefile = ''
	difftimefile = ''
	paramset = 0
	
	try:
		opts, args = getopt.getopt(argv,'hf:t:a:d:',['filelist=','timestamp=','abstime=','difftime='])
	except getopt.GetoptError:
		help_and_exit(2) 
	for opt, arg in opts:
		if opt in ('-h', '--help'):
			help_and_exit()
		elif opt in ('-f', '--filelist'):
			filelistfile = arg
			paramset = set_param(paramset, 1)
		elif opt in ('-t', '--timestamp'):
			timestampfile = arg
			paramset = set_param(paramset, 2)
		elif opt in ('-a', '--abstime'):
			abstimefile = arg
			paramset = set_param(paramset, 4)
		elif opt in ('-d', '--difftime'):
			difftimefile = arg
			paramset = set_param(paramset, 8)
				   
	if paramset != (1+2+4+8):
		print('Error: not all parameters set')
		help_and_exit(2)
				   
	print('Filelist file: ' + filelistfile)
	print('Timestamp output file: ' + timestampfile)
	print('Absolute time output file: ' + abstimefile)
	print('Time difference output file: ' + difftimefile)
	print('')
	sys.stdout.write('Processing ')
	sys.stdout.flush()
	
	timestamph = open(timestampfile, 'w')
	abstimeh = open(abstimefile, 'w')
	difftimeh = open(difftimefile, 'w')
	
	first_timestamp=1;
	firstdate=None
	prevdate=None
	
	with open(filelistfile) as flh:
		for line in flh:
			sys.stdout.write('.')
			sys.stdout.flush()
			first_timestamp, firstdate, prevdate = \
				process_timestamps(line.strip(), timestamph, abstimeh, difftimeh, \
				first_timestamp, firstdate, prevdate)
			
	timestamph.close()
	abstimeh.close()
	difftimeh.close()
	print('')
	
if __name__ == "__main__":
	main(sys.argv[1:])
