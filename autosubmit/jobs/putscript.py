# This skript is meant to be used to move the REMO-result files
# to the archive while performing a REMO-run.
# It moves files to a tar-file and then moves the tar-file to
# the archive-server.
#
# It is based on putscript.py from the runnigRemo directory of the old SVN
# except that it does not take any arguments, but the information is passed
# directly via autosubmit variable substitution. Some minor changes have been
# implemented
# 
##
# Notes:
# 
# If the directory in the archive already exists,
# it is renamed from e.g. 1989 to 1989_backup
# if also the latter directory exists, the program
# raises an error.
#

#import argparse
import os
import logging
import pickle
import subprocess
import tempfile

from PyRemo.Ftp import check_ftp_path, make_ftp_path, upload_file
from PyRemo.Ftp import rename_ftp_path
from PyRemo.ShellTools import check_make_path
from PyRemo.ShellTools import pack_tar_archive, extract_tar_archive
from PyRemo.ScriptTools import log_check_in
#
# check the parameters
debug = False

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(levelname)-8s %(message)s',
                    datefmt='%d %b %Y %H:%M:%S')

#
#parser = argparse.ArgumentParser(description='Moves REMO output to the archive.',
#        epilog='In case of problems, contact: claas.teichmann@hzg.de')
#parser.add_argument('proj_id', metavar='PROJID', type=str,
#        help='This determines the project directory in the archive.')
#parser.add_argument('expstr', metavar='EXPSTR', type=str,
#        help='The experiment string, e.g. 019400')
#parser.add_argument('year', metavar='YEAR', type=int,
#        help='The year to put to the archive, e.g. 1977.')
#parser.add_argument('--user', metavar='USER', type=str, nargs='?',
#        help='user-number for path definition, e.g., m222026',
#        default='')
#parser.add_argument('--pfiles', action='store_true',
#        help='Also uploading a tar containing p-files.')
#parser.add_argument('--repacking-yearly-efiles', action='store_true',
#        help='Repacking the monthly e-tar files to yearly e-files for each code.')
#parser.add_argument('--overwrite', action='store_true',
#        help='Overwrite existing files in the archive.')
#parser.add_argument('--wrkdir', metavar='WRKDIR', type=str, nargs='?',
#        help='Work directory for output data.')
#args = parser.parse_args()
#print args.proj_id
#print args.expstr
#print args.year
#print args.user

remo_user = '%REMO_USER%'
remo_exp = '%REMO_EXP%'

dic = {}
dic['proj_id'] = '%HPCPROJ%' #args.proj_id
if %REMO_EXP_STR_STYLE% == 1:
    dic['exp_str'] = '{0}'.format(remo_exp)
elif %REMO_EXP_STR_STYLE% == 2:
    dic['exp_str'] = '{0}{1}'.format(remo_user, remo_exp) #args.expstr
else:
    exit (1)
dic['year'] = '%Chunk_START_YEAR%' #args.year
dic['user'] = '%HPCUSER%' #args.user
dic['wrkdir'] = '%WORK_DIR%' #args.wrkdir
dic['scrdir'] = '%SCRATCH_DIR%'
year = dic['year']

do_pfiles = False #args.pfiles
do_repack_yearly_efiles = False #args.repacking_yearly_efiles
overwrite = True #args.overwrite

#
# paths
#
source_dir = "{wrkdir}/res_{exp_str}/{year}".format(**dic)
log_path = '{0}/put_log'.format(source_dir)
check_make_path(log_path)
log_file = os.path.join(log_path, 'put_{exp_str}_{year}.pickle'.format(**dic))
# path in archive accessible via pftp
dest_dir_base = "/hpss/arch/{proj_id}/{user}/exp{exp_str}".format(**dic)
dest_dir      = os.path.join(dest_dir_base, "{year}".format(**dic))
# tmp_base = os.path.join(os.getenv('SCRATCH'), 'put_tmp')
tmp_base = os.path.join("{scrdir}".format(**dic),
                        "put_tmp{exp_str}".format(**dic))
check_make_path(tmp_base)

# check the work already done

if os.path.isfile(log_file):
    f = open(log_file, 'r')
    log_dic = pickle.load(f)
    f.close()
else:
    log_dic = {}

if 'tmp_dir' in log_dic.keys():
    tmp_dir = log_dic['tmp_dir'][0]
else:
    tmp_dir = tempfile.mkdtemp(dir=tmp_base, prefix='{year}_'.format(**dic))
    log_check_in(log_file, log_dic, 'tmp_dir', tmp_dir)

# server
server = 'tape'

log_check_in(log_file, log_dic, year, 'starting')

# defining convenience funktions that could go to PyRemo
# or/and be more generalized. E.g. function call as a parameter.
def pack_tar_archive_log(source_dir, tmp_dir, tar_file_name, file_names,
        log_file, log_dic, year, task, do_remove=True):
    if task in log_dic[year]:
        logging.warning('Already done: SKIPPING {0}'.format(task))
    else:
        logging.info('Processing: {0}'.format(task))
        pack_tar_archive(source_dir, tmp_dir, tar_file_name, file_names,
                         do_remove=do_remove)
        log_check_in(log_file, log_dic, year, task)

def upload_file_log(server, tmp_dir, tar_file_name, dest_dir,
        log_file, log_dic, year, task):
    if task in log_dic[year]:
        logging.warning('Already done: SKIPPING {0}'.format(task))
    else:
        logging.info('Processing: {0}'.format(task))
        upload_file(server, tmp_dir, tar_file_name, dest_dir,
                    remove_source=True)
        log_check_in(log_file, log_dic, year, task)


# packing and uploading mns-files
file_names = []
tar_file_name = 'e{exp_str}mns{year}.tar'.format(**dic)
for dic['mon'] in range(1,13):
    for file_type in 'n':
        dic['type'] = file_type
        file_names.append('e{exp_str}{type}{year}{mon:02d}.tar'.format(**dic))
    for file_type in 'ms':
        dic['type'] = file_type
        file_names.append('e{exp_str}{type}{year}{mon:02d}'.format(**dic))

task = 'pack_tar_archive nms-files'
pack_tar_archive_log(source_dir, tmp_dir, tar_file_name, file_names,
                     log_file, log_dic, year, task, do_remove=False)
#pack_tar_archive(source_dir, tmp_dir, tar_file_name, file_names,
#                 do_remove=False)

path_exists = check_ftp_path(server, dest_dir_base)
if not path_exists:
    make_ftp_path(server, dest_dir_base)

task = 'check_ftp_directory dest_dir'
if task in log_dic[year]:
    logging.warning('Already done: SKIPPING {0}'.format(task))
else:
    logging.info('Processing: {0}'.format(task))
    path_exists = check_ftp_path(server, dest_dir)
    if path_exists:
        if overwrite:
            pass
        else:
            new_dest_dir = dest_dir + '_backup'
            rename_ftp_path(server, dest_dir, new_dest_dir)
            dest_dir = new_dest_dir
    else:
        make_ftp_path(server, dest_dir)

    log_check_in(log_file, log_dic, year, task)

task = 'upload of nms-tar'
upload_file_log(server, tmp_dir, tar_file_name, dest_dir,
                log_file, log_dic, year, task)
#upload_file(server, tmp_dir, tar_file_name, dest_dir,
#            remove_source=True)

# packing and uploading f-files
file_names = []
tar_file_name = 'e{exp_str}f{year}.tar'.format(**dic)
dic['type'] = 'f'
for dic['mon'] in range(1,13):
    file_names.append('e{exp_str}{type}{year}{mon:02d}.tar'.format(**dic))

task = 'pack_tar_archive f-files'
pack_tar_archive_log(source_dir, tmp_dir, tar_file_name, file_names,
                     log_file, log_dic, year, task)
#pack_tar_archive(source_dir, tmp_dir, tar_file_name, file_names)

task = 'upload of f-tar'
upload_file_log(server, tmp_dir, tar_file_name, dest_dir,
                log_file, log_dic, year, task)
#upload_file(server, tmp_dir, tar_file_name, dest_dir,
#            remove_source=True)

# uploading t-files
file_names = []
dic['type'] = 't'
for dic['mon'] in range(1,13):
    akt_file_name = 'e{exp_str}{type}{year}{mon:02d}.tar'.format(**dic)
    task = 'upload of t-tar for month {mon}'.format(**dic)
    upload_file_log(server, source_dir, akt_file_name, dest_dir,
                    log_file, log_dic, year, task)
#    upload_file(server, tmp_dir, tar_file_name, dest_dir,
#                remove_source=True)

# uploading e-files
dic['type'] = 'e'
if do_repack_yearly_efiles:
    if 'e_files_tmp_dir' in log_dic.keys():
        e_files_tmp_dir = log_dic['e_files_tmp_dir'][0]
    else:
        e_files_tmp_dir = tempfile.mkdtemp(dir=tmp_dir, prefix='efiles_')
        log_check_in(log_file, log_dic, 'e_files_tmp_dir', e_files_tmp_dir)
    for dic['mon'] in range(1,13):
        akt_file_name = 'e{exp_str}{type}{year}{mon:02d}.tar'.format(**dic)
        task = 'extract e-file for month {0}'.format(dic['mon'])
        if task in log_dic[year]:
            logging.warning('Already done: SKIPPING {0}'.format(task))
        else:
            logging.info('Processing: {0}'.format(task))
            extract_tar_archive(source_dir, e_files_tmp_dir, akt_file_name,
                                do_remove=True)
            log_check_in(log_file, log_dic, year, task)
    file_list = os.listdir(e_files_tmp_dir)
    code_list = set(map(lambda w: w.split('_')[1], file_list))
    logging.info('Processing codes: {0}'.format(code_list))
    for code in code_list:
        dic['code'] = code
        logging.info('repacking e-files: Processing code {code}'.format(**dic))
        file_names = []
        for dic['mon'] in range(1,13):
            file_names.append('e{exp_str}{type}_{code}_{year}{mon:02d}'.format(**dic))
        tar_file_name = 'e{exp_str}{type}_{code}_{year}{mon:02d}.tar'.format(**dic)
        task = 'pack new tar file for code: {0}'.format(code)
        pack_tar_archive_log(e_files_tmp_dir, tmp_dir, tar_file_name,
                             file_names, log_file, log_dic, year, task)
#        pack_tar_archive(e_files_tmp_dir, tmp_dir, tar_file_name, file_names)
        task = 'upload of e-tar for code: {0}'.format(code)
        upload_file_log(server, tmp_dir, tar_file_name, dest_dir,
                        log_file, log_dic, year, task)
#        upload_file(server, tmp_dir, tar_file_name, dest_dir,
#                    remove_source=True)
    os.rmdir(e_files_tmp_dir)
else:
    file_names = []
    for dic['mon'] in range(1,13):
        akt_file_name = 'e{exp_str}{type}{year}{mon:02d}.tar'.format(**dic)
        task = 'upload e-tar for month: {0}'.format(dic['mon'])
        upload_file_log(server, source_dir, akt_file_name, dest_dir,
                        log_file, log_dic, year, task)
#        upload_file(server, tmp_dir, tar_file_name, dest_dir,
#                    remove_source=True)

# uploading p-tar-file
if do_pfiles:
    dic['type'] = 'p'
    akt_file_name = 'e{exp_str}{type}{year}{mon:02d}.tar'.format(**dic)
    task = 'upload of p-tar'
    upload_file_log(server, source_dir, akt_file_name, dest_dir,
                    log_file, log_dic, year, task)
#    upload_file(server, tmp_dir, tar_file_name, dest_dir, remove_source=True)

os.rmdir(tmp_dir)
