# a wrapper shell script to call the python based putscript is needed,
# because of "module load" commands.

# needed at DKRZ to use modules from a script
source /sw/rhel6-x64/etc/profile.mistral

# pftp
module load pftp

# python
module load python

# Define some variables
UE=%REMO_USER%
EE=%REMO_EXP%

if [ %REMO_EXP_STR_STYLE% = 1 ]
then
    EXP_STR=$EE
elif [ %REMO_EXP_STR_STYLE% = 2 ]
then
    EXP_STR=$UE$EE
else
    exit 1
fi

python %HPCROOTDIR%/REMO_MPI/autosubmit/utils/putscript.py %HPCPROJ% $EXP_STR %Chunk_START_YEAR% --user %HPCUSER% --wrkdir %WORK_DIR% --overwrite
