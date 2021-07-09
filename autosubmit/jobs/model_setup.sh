# remote_setup is doing the model compilation or copying an old projekt to the
# right location.
# For now only DKRZ is configured.
set -ex
# needed at DKRZ to use modules from a script
source /sw/rhel6-x64/etc/profile.mistral

# load necessary modules for compilation
module load fca/2.5.2393 mxm/3.3.3002 intel/16.0.2 bullxmpi_mlx_mt/bullxmpi_mlx_mt-1.2.8.3

# compile the model and archive project directory or copy archived project
# directory
if [[ "%COMPILE%" = "True" ]]
then
    cd %HPCROOTDIR%/REMO_MPI/build
    make mistral
    cd %HPCROOTDIR%
    tar cf %COMP_NAME%.tar REMO_MPI
    mv %COMP_NAME%.tar %COMP_ARCH%
else
    cd %HPCROOTDIR%
    cp %COMP_ARCH%/%COMP_NAME%.tar .
    tar xf %COMP_NAME%.tar
fi

