#######
#
# Does the setup for each member of the run
# 
# 1. Creates the Namelist_template for the member of the REMO run
# 2. Creates paths for output data
#
#######

import ConfigParser
import os
import datetime

def createRemoNamelistTemplate(conf_dict, namelist_template_path):
    """Creates a Namelist template for REMO.

    conf_parser: A dictionary of dictionaries (like the _sections attribute
                 of a ConfigParser instance)
    namelist_template_path: Path where the Namelist template should be stored.
    """

    known_sections = ['PARCTL', 'EMGRID', 'RUNCTL', 'DYNCTL', 'HYDCTL',
                      'PHYCTL', 'NMICTL', 'PRICTL', 'DATEN']

    namelist_list = []
    # iterate trough sections
    for section in known_sections:
        namelist_list.append('&{0}'.format(section))

        # put template strings
        if section == 'RUNCTL':
            namelist_list.append(' NHANF   = $NHANF,')
            namelist_list.append(' NHENDE  = $NHENDE,')
            namelist_list.append(' NHFORA  = $NHENDE,')

        # add all options of section
        for key, value in conf_dict[section].items():
            if key is not '__name__':
                namelist_list.append(' {0:<7} = {1},'.format(
                    key.upper(), value))

        namelist_list.append('/')

    with open(namelist_template_path, 'w') as namelist_file:
        namelist_file.write('\n'.join(namelist_list))


#
known_regions = ['eur044', 'eur011']

# get values from project config file (proj_xxxx.conf)
proj_conf_file = os.path.join('%HPCROOTDIR%', 'proj_%EXPID%.conf')

proj_conf = ConfigParser.SafeConfigParser()
proj_conf.readfp(open(proj_conf_file))

proj_conf_dict = proj_conf._sections

# determine region from member name
member = '%MEMBER%'

for region in known_regions:
    if member.find(region) > -1:
        remo_region = region
        break
    else:
        remo_region = 'default'

# get defaults for region
region_conf_file = '%HPCROOTDIR%/REMO_MPI/autosubmit/conf/{0}.conf'.format(remo_region)

region_conf = ConfigParser.SafeConfigParser()
region_conf.readfp(open(region_conf_file))

# set paths, BOUNDARY/REMO experiment, and user numbers for the output
default_data_base_path = '%HPCROOTDIR%/%MEMBER%'
if not os.path.exists(default_data_base_path):
    os.makedirs(default_data_base_path)

if %NUMMEMBERS% > 1:
    member_num = int(re.findall(r'\d+', '%MEMBER%')[-1])
    bound_num = int('%BOUND_EXP%') + member_num - 1
    remo_num = int('%REMO_EXP%') + member_num - 1
    bound_exp = str(bound_num).zfill(3)
    remo_exp = str(remo_num).zfill(3)
else:
    bound_exp = '%BOUND_EXP%'
    remo_exp = '%REMO_EXP%'

bound_user = '%BOUND_USER%'
remo_user = '%REMO_USER%'

if '%DATA_DIRS%' == 'default':
    path_a = 'xa'
    path_e = 'xe'
    path_f = 'xf'
    path_m = 'xm'
    path_n = 'xn'
    path_t = 'xt'
else:
    path_a = '%PATH_A%'
    path_e = '%PATH_E%'
    path_f = '%PATH_F%'
    path_m = '%PATH_M%'
    path_n = '%PATH_N%'
    path_t = '%PATH_T%'

# Necessary complication to provide proper quoted strings in the namelist
region_conf.set('DATEN', 'YADEN', "'{0}'".format(bound_exp))
region_conf.set('DATEN', 'YRDEN', "'{0}'".format(bound_exp))
region_conf.set('DATEN', 'YEDEN', "'{0}'".format(remo_exp))
region_conf.set('DATEN', 'YFDEN', "'{0}'".format(remo_exp))
region_conf.set('DATEN', 'YTDEN', "'{0}'".format(remo_exp))
region_conf.set('DATEN', 'YUSERA', "'{0}'".format(bound_user))
region_conf.set('DATEN', 'YUSERE', "'{0}'".format(remo_user))
region_conf.set('DATEN', 'YADCAT', "'{0}'".format(
    os.path.join(default_data_base_path, path_a)))
region_conf.set('DATEN', 'YRDCAT', "'{0}'".format(
    os.path.join(default_data_base_path, path_a)))
region_conf.set('DATEN', 'YEDCAT', "'{0}'".format(
    os.path.join(default_data_base_path, path_e)))
region_conf.set('DATEN', 'YFDCAT', "'{0}'".format(
    os.path.join(default_data_base_path, path_f)))
region_conf.set('DATEN', 'YMDCAT', "'{0}'".format(
    os.path.join(default_data_base_path, path_m)))
region_conf.set('DATEN', 'YTDCAT', "'{0}'".format(
    os.path.join(default_data_base_path, path_t)))
region_conf.set('DATEN', 'YNDCAT', "'{0}'".format(
    os.path.join(default_data_base_path, path_n)))

region_conf_dict = region_conf._sections

for section in region_conf_dict.keys():
    if proj_conf_dict.has_key(section):
        proj_section_dict = proj_conf_dict[section]
        region_section_dict = region_conf_dict[section]
        for key, value in proj_section_dict.items():
            region_section_dict[key] = value

# Add parameters given by autosubmit
yadat = "'{0}00'".format('%SDATE%')
region_conf_dict['RUNCTL']['YADAT'] = yadat

if '%CALENDAR%'.lower() == 'noleap':
    region_conf_dict['RUNCTL']['LLEAP'] = 'FALSE'

# Configure list of timesteps
dt_str = None
if proj_conf_dict['REMO_RUN'].has_key('dt_list'):
    dt_str = proj_conf_dict['REMO_RUN']['dt_list']

# if list is empty use default from region template
if dt_str is None:
    dt_list = [region_conf_dict['RUNCTL']['dt'],]
else:
    dt_list = dt_str.split(',')

# create namelist templates for member (region)
for i, dt in enumerate(dt_list):
    dt_string = dt.strip()

    # the first value in the list of timesteps defines the default value
    namelist_template_path = '%HPCROOTDIR%/REMO_MPI/autosubmit/INPUT_%MEMBER%_dt{0}'.format(i)

    region_conf_dict['RUNCTL']['dt'] = dt_string
    createRemoNamelistTemplate(region_conf_dict, namelist_template_path)

# create paths for REMO output
for path_keys in ['YADCAT', 'YRDCAT', 'YEDCAT', 'YFDCAT',
                  'YMDCAT', 'YTDCAT', 'YNDCAT']:
    directory = region_conf_dict['DATEN'][path_keys.lower()].strip("'")
    if not os.path.exists(directory):
        os.makedirs(directory)

# boundary data tar path
bound_tar = os.path.join(default_data_base_path, 'bound_tar')
if not os.path.exists(bound_tar):
    os.makedirs(bound_tar)

# prepare warmstart_config if desired
warmstart = %WARMSTART%

if warmstart:
    warm_user = '%WARM_USER%'
    warm_exp = '%WARM_EXP%'
    warm_path = '%WARM_PATH%'
    start_date = datetime.datetime.strptime('%SDATE%', '%Y%m%d')
    afile_path = os.path.join(default_data_base_path, path_a)
    code_list = '54 84 140 141 170 183 194 206 207 208 209 232'
    warm_conf_file = os.path.join(default_data_base_path ,'warmstart.conf')
    
    warm_conf = ConfigParser.SafeConfigParser()
    warm_conf.add_section('a-file')
    warm_conf.set('a-file', 'afile_user', bound_user)
    warm_conf.set('a-file', 'afile_exp', bound_exp)
    warm_conf.set('a-file', 'afile_year', str(start_date.year))
    warm_conf.set('a-file', 'afile_month', str(start_date.month))
    warm_conf.set('a-file', 'afile_day', str(start_date.day))
    warm_conf.set('a-file', 'afile_hour', '0')

    warm_conf.add_section('replace-file')
    warm_conf.set('replace-file', 'rfile_type', 'f')
    warm_conf.set('replace-file', 'rfile_user', warm_user)
    warm_conf.set('replace-file', 'rfile_exp', warm_exp)
    warm_conf.set('replace-file', 'rfile_year', str(start_date.year))
    warm_conf.set('replace-file', 'rfile_month', str(start_date.month))
    warm_conf.set('replace-file', 'rfile_day', str(start_date.day))
    warm_conf.set('replace-file', 'rfile_hour', '0')

    warm_conf.add_section('paths')
    warm_conf.set('paths', 'afile_path', afile_path)
    warm_conf.set('paths', 'rfile_path', warm_path)

    warm_conf.add_section('codes')
    warm_conf.set('codes', 'code_list', code_list)

    warm_conf_file_obj = open(warm_conf_file, 'w')
    warm_conf.write(warm_conf_file_obj)
    warm_conf_file_obj.close()
