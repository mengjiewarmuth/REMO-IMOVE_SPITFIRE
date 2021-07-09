set -ex

# Set modelrun command depending on machine
#
if [ '%CURRENT_ARCH%' == 'LOCAL' ]
then
    function modelrun {
    time mpirun -np $NCPU ${PFL}/rremo < INPUT
    }
elif [ '%CURRENT_ARCH%' == 'dkrz' ]
then
    ulimit -s unlimited
    function modelrun {
    time srun ${PFL}/rremo < INPUT
    }
else
    echo "%CURRENT_ARCH% invalid MACHINE!"
    exit
fi

# model binary
MODELDIR=%HPCROOTDIR%/REMO_MPI # Model location
PFL=${MODELDIR}/libs

#
# Set beginning and end of simulation (works only on full day basis)
#
KSA=$(( %PREV% * 24 ))
KSE=$(( %Chunk_End_IN_DAYS% * 24 ))
#
NCPU=%NUMTASK%

#
# Number of failed simulations
#
DT=%FAIL_COUNT%
date
#
set -ex
#
# Namelist substitution
#
python -c "from string import Template
txt = Template(file('${MODELDIR}/autosubmit/INPUT_%MEMBER%_dt${DT}').read()).safe_substitute(NHANF=${KSA},NHENDE='${KSE}',NHFORA='${KSE}')
file('%HPCROOTDIR%/%MEMBER%/INPUT','w').write(txt)"
#
# model run
#
cd %HPCROOTDIR%/%MEMBER%
modelrun
#
