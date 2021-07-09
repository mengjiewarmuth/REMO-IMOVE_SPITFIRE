#!/usr/bin/env python
# -*- coding: utf-8 -*-
# replaces parameters in an a-file with data from an t-file
# the precision and endian will be the same as in a-file
# this is in some way a python-version of the ext_mod script
# by Alberto, Ralf and Christof
# use the corresponding config-file to run this script
# usage:
# replace_codes.py <config-file>
# because of the need of numpy it does not work on blizzard so far
# (on lizard and all other mpi computers it works!)
#

import datetime
import ConfigParser
import logging
import shutil
import os
import sys

from optparse import OptionParser
from PyRemo.OoPlot.DataFile import IegFile

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(levelname)-8s %(message)s',
                    datefmt='%d %b %Y %H:%M:%S')

logging.info('Using Python version ' + sys.version)

parser = OptionParser("usage: %prog [options] <config_file.txt>")
(options, args) = parser.parse_args()

if len(args) != 1:
    parser.error('Wrong number of parameters!')
else:
    config_file = args[0]

# loading defaults
config = ConfigParser.SafeConfigParser()
config.readfp(open(config_file))

#
# Data specific configuration
#
afile_date = datetime.datetime(int(config.get('a-file', 'afile_year')),
                               int(config.get('a-file', 'afile_month')),
                               int(config.get('a-file', 'afile_day')),
                               int(config.get('a-file', 'afile_hour')))
rfile_date = datetime.datetime(int(config.get('replace-file', 'rfile_year')),
                               int(config.get('replace-file', 'rfile_month')),
                               int(config.get('replace-file', 'rfile_day')),
                               int(config.get('replace-file', 'rfile_hour')))

#
# Data paths
#
afile_path = config.get('paths', 'afile_path')
rfile_path = config.get('paths', 'rfile_path')

#
# Codes
#
codes_str = config.get('codes', 'code_list').split()
codes = []
for code in codes_str:
    codes.append(int(code))
logging.info("codes {0} will be replaced".format(codes))

#
# Read a-file and do a backup
#
afile_name = 'a{0}{1}a{2}'.format(config.get('a-file', 'afile_user'),
                                  config.get('a-file', 'afile_exp'),
                                  afile_date.strftime('%Y%m%d%H'))
afile_full_name = os.path.join(afile_path, afile_name)
afile_backup = '{0}.ori'.format(afile_full_name)
logging.info("backup of {0}".format(afile_full_name))

if os.path.isfile(afile_backup):
    logging.warning("backup file {0} already exists!".format(afile_backup))
else:
    shutil.move(afile_full_name, afile_backup)

afile_in = IegFile(afile_backup)
afile_endian = afile_in.is_big_endian()
afile_precision = afile_in.is_double_precision() 
afile_header, afile_arr, afile_cdic = afile_in.read_all_sel_data()
afile_in.close()

#
# Read replace-file
#

rfile_name = 'e{0}{1}{2}{3}'.format(config.get('replace-file', 'rfile_user'),
                                    config.get('replace-file', 'rfile_exp'),
                                    config.get('replace-file', 'rfile_type'),
                                    rfile_date.strftime('%Y%m%d%H'))
rfile_full_name = os.path.join(rfile_path, rfile_name)

rfile_in = IegFile(rfile_full_name)
rfile_header, rfile_arr, rfile_cdic = rfile_in.read_all_sel_data()
rfile_in.close()

#
# Write new a-file and take codes from codelist from replace-file
# the rest of the original a-file stays the same.
# The time information is taken from a-file.
#

with IegFile(afile_full_name, mode='w', big_endian=afile_endian,
             double_precision=afile_precision) as afile_out:
    for index, header in enumerate(rfile_header):
        if header.pdb[6] in codes:
            new_header = header
            new_header.pdb[10] = afile_date.year
            new_header.pdb[11] = afile_date.month
            new_header.pdb[12] = afile_date.day
            new_header.pdb[13] = afile_date.hour
            afile_out.write_data_set(new_header, rfile_arr[index])
            logging.info("using code {0} from replace-file".format(
                    rfile_header[index].pdb[6]))
    for index, header in enumerate(afile_header):
        if not header.pdb[6] in codes:
            afile_out.write_data_set(header, afile_arr[index])
            logging.info("using code {0} from a-file".format(
                    afile_header[index].pdb[6]))
