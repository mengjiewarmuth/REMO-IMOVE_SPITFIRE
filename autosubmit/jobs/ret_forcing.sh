# Returns the boundary files for the current year
#
set -ex
# needed at DKRZ to use modules from a script
source /sw/rhel6-x64/etc/profile.mistral
# load pftp module
module load pftp
#
module load python/2.7-ve0
#
function ftp_input {
cat > ftp.inp << EOF
cd $1/year$2
bin
get $3
quit
EOF
}

function download {
    #
    # *** style for achiving yearly|monthly
    YY=$1
    if [ "%BOUND_ARCH_STYLE%" = "monthly" ]
    then
	for MM in 01 02 03 04 05 06 07 08 09 10 11 12
	do
	    DNBOUND=a${BUSER}${BEXP}a${YY}${MM}.tar

	    ftp_input $CDIR $YY $DNBOUND

            pftp < ftp.inp
#
	done
#
    elif [ "%BOUND_ARCH_STYLE%" = "yearly" ]
    then
	DNBOUND=a${BUSER}${BEXP}a${YY}.tar

	ftp_input $CDIR $YY $DNBOUND
	
        pftp < ftp.inp
	tar xf a${BUSER}${BEXP}a${YY}.tar
	wait
	rm a${BUSER}${BEXP}a${YY}.tar
    else
	exit 2
    fi
}

YEAR=%Chunk_START_YEAR%
MONTH=%Chunk_START_MONTH%
BUSER=%BOUND_USER%         # for boundary data
BEXP=%BOUND_EXP%
CURRENT_FILE=a${BUSER}${BEXP}a${YEAR}${MONTH}.tar
#
###############################################################################
#
# Archive directory of boundary data
if [ %BOUND_EXP_STR_STYLE% = 1 ]
then
    CDIR=%BOUND_ARCH_PATH%/exp$BEXP
elif [ %BOUND_EXP_STR_STYLE% = 2 ]
then
    CDIR=%BOUND_ARCH_PATH%/exp${BUSER}${BEXP}
else
    exit 1
fi

PFADFRC=%HPCROOTDIR%/%MEMBER%/bound_tar  # local directory for boundary files

# Path for unpacked boundary files
if [ "%DATA_DIRS%" = "default" ]
then
    PFADXA=%HPCROOTDIR%/%MEMBER%/xa
else
    PFADXA=%PATH_A%
fi

cd $PFADFRC

# Download missing data
if [ ! -s $CURRENT_FILE ]
then
    download $YEAR
fi

# Download next year data
if [[ $MONTH = 12 && "%Chunk_LAST%" = "FALSE" ]]
then
    NEXT_YEAR=$(( $YEAR + 1 ))
    download $NEXT_YEAR
    
    # Delete boundary data of previous year
    if [[ "%Chunk_FIRST%" = "FALSE" && "%KEEP_BOUND%" = "False" ]]
    then
	PREV_YEAR=$(( $YEAR - 1 ))
	set +e
	rm a${BUSER}${BEXP}a${PREV_YEAR}??.tar
	set -ex
    fi
fi

# Empty boundary data directory
cd $PFADXA
set +e
rm a${BUSER}${BEXP}a*
set -ex

# Copy and unpack current file to boundary file path
cp $PFADFRC/$CURRENT_FILE .
tar xf $CURRENT_FILE
wait
rm $CURRENT_FILE

# In case of warmstart replace soilparameters
if [[ "%Chunk_FIRST%" = "TRUE" && "%WARMSTART%" = "True" ]]
then
    WARM_CONF=%HPCROOTDIR%/%MEMBER%/warmstart.conf
    REPLACE_SCRIPT=%HPCROOTDIR%/REMO_MPI/autosubmit/jobs/replace_codes.py
    python $REPLACE_SCRIPT $WARM_CONF
fi
