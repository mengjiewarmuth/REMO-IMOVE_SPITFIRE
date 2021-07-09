# local_setup is copying the current project directory
# to the HPC system (only if COMPILE=True).
set -ex

ssh %HPCUSER%@%HPCHOST% mkdir -p %HPCROOTDIR%

if [[ "%COMPILE%" = "True" ]]
then
    rsync -ave ssh %PROJDIR% %HPCUSER%@%HPCHOST%:%HPCROOTDIR%/
fi

rsync -ave ssh %ROOTDIR%/conf/proj_%EXPID%.conf %HPCUSER%@%HPCHOST%:%HPCROOTDIR%
