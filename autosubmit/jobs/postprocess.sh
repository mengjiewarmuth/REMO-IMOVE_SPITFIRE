set -ex
#
# Moves simulated data from scratch to a different location to keep
# simulation directories clean
#
date
#
# autosubmit variables
UE=%REMO_USER%
EE=%REMO_EXP%
Y=%Chunk_START_YEAR%
M=%Chunk_START_MONTH%
YNEU=%Chunk_END_YEAR%
MNEU=%Chunk_END_MONTH%
DNEU=%Chunk_END_DAY%
HNEU=%Chunk_END_HOUR%

if [ %REMO_EXP_STR_STYLE% = 1 ]
then
    EXP_STR=$EE
elif [ %REMO_EXP_STR_STYLE% = 2 ]
then
    EXP_STR=$UE$EE
else
    exit 1
fi
# Set paths
# Paths and directories have to be the same as in member_setup.sh !!!
SIM_BASE_PATH=%HPCROOTDIR%/%MEMBER%
PFADRES=%WORK_DIR%/res_$EXP_STR
if [ '%DATA_DIRS%' = 'default' ]
then
    DATE=xe
    DATF=xf
    DATM=xm
    DATN=xn
    DATT=xt
else
    DATE=%PATH_E%
    DATF=%PATH_F%
    DATM=%PATH_M%
    DATN=%PATH_N%
    DATT=%PATH_T%
fi

TYPE=e
TYPF=f
TYPG=g
TYPM=m
TYPN=n
TYPT=t
TYPS=s
ART=.tar
#
if [[ "%Chunk_FIRST%" = "TRUE" || $M = '01' ]]
then
    mkdir -p ${PFADRES}/${Y}
fi
#
# COPY/MOVE DATA
#
# *** Restart
cd ${SIM_BASE_PATH}/${DATF}
FFILE=${TYPE}${UE}${EE}${TYPF}${YNEU}${MNEU}${DNEU}${HNEU}
GFILE=${TYPE}${UE}${EE}${TYPG}${YNEU}${MNEU}${DNEU}${HNEU}
TARFILE=${TYPE}${UE}${EE}${TYPF}${Y}${M}${ART}
SAVEFILE=${PFADRES}/${Y}/$TARFILE
if [ ! -s $SAVEFILE ]
then
    tar cf $TARFILE $FFILE $GFILE
    mv $TARFILE $SAVEFILE
fi
#
# *** Monthly files
cd ${SIM_BASE_PATH}/${DATM}
MFILE=${TYPE}${UE}${EE}${TYPM}${Y}${M}
SFILE=${TYPE}${UE}${EE}${TYPS}${Y}${M}
for MYFILE in $MFILE $SFILE
do
    SAVEFILE=${PFADRES}/${Y}/$MYFILE
    if [ ! -s $SAVEFILE ]
    then
	mv $MYFILE $SAVEFILE
    fi
done
#
# *** 3d atmospheric files
cd ${SIM_BASE_PATH}/${DATT}
TFILES=${TYPE}${UE}${EE}${TYPT}${Y}${M}
TARFILE=${TYPE}${UE}${EE}${TYPT}${Y}${M}${ART}
SAVEFILE=${PFADRES}/${Y}/$TARFILE
if [ ! -s $SAVEFILE ]
then
    tar cf $TARFILE ${TFILES}????
    mv $TARFILE $SAVEFILE
    rm ${TFILES}????
fi
#
# *** 2d files, e.g. surface etc. 
cd ${SIM_BASE_PATH}/${DATE}
EFILES=${TYPE}${UE}${EE}${TYPE}
TARFILE=${TYPE}${UE}${EE}${TYPE}${Y}${M}${ART}
SAVEFILE=${PFADRES}/${Y}/$TARFILE
if [ ! -s $SAVEFILE ]
then
    tar cf $TARFILE ${EFILES}_c???_${Y}${M} 
    mv $TARFILE $SAVEFILE
    rm ${EFILES}_c???_${Y}${M}
fi
#
# *** Daily files
cd ${SIM_BASE_PATH}/${DATN}
NFILES=${TYPE}${UE}${EE}${TYPN}
TARFILE=${TYPE}${UE}${EE}${TYPN}${Y}${M}${ART}
SAVEFILE=${PFADRES}/${Y}/$TARFILE
if [ ! -s $SAVEFILE ]
then
    tar cf $TARFILE ${NFILES}_c???_${Y}${M} 
    mv $TARFILE $SAVEFILE
    rm ${NFILES}_c???_${Y}${M}
fi
#
#
date
