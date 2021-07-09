# Welcome to the regional climate model REMO.

## Compling Remo

To compile REMO, just go to the `build` directory and type 
```
make
```
You will get a list of machines for which Makefile templates are available, e.g.,
```
echo "usage: <make clean> <make clean_all> <make mistral> <make blizzard> <make tornado> \
             <make ubuntu_laptop> <make meteo> <make bull> <make juropa> <make mac>"
```
The only purpose of the makefile here is to create a machine specific makefile from 
some files in the subdirectory `makefiles`. There are some predefined makefile configurations 
for different machines but, in general, they only differ in which fortran compiler or mpi 
implementation is used. Just choose your machine and type, e.g., if you are on the
DKRZ Mistral:
```
make mistral
```
This should compile Remo, if you have the appropriate modules loaded, e.g., the intel
compiler and the bullxmpi compiler.
The make command will create a number of Makefiles in the `makefiles` subdirectory and
choose the appropriate one. The makefiles here are created from template files in the
`template` subdirectory. If you want to change you configuration, you should not change
the template, but the actual Makefile itself, e.g., the one for the Mistral would be
Makefile_mistral in the `makefile` subdirectory.

### Compiling Remo with NETCDF support.

To use the NETCDF support, you have to change the Makefile in the `makefiles` subdirectory
in the `build` directory, e.g., the `Makefile_mistral`. Open the Makefile and uncomment
the lines that define the `NCMODE` and `NCFLAGS` variable (for compiling) and the `NCLIBS` variable (for linking).
For the Mistral, these lines should be something like this:
```
NCMODE    =  NETCDF_IO
NCFLAGS   = -D${NCMODE} -I/sw/rhel6-x64/netcdf/netcdf_fortran-4.4.2-intel14/include
NCLIBS    = -L/sw/rhel6-x64/netcdf/netcdf_fortran-4.4.2-intel14/lib -lnetcdff \
            -Wl,-rpath,/sw/rhel6-x64/netcdf/netcdf_fortran-4.4.2-intel14/lib \
            -L/sw/rhel6-x64/netcdf/netcdf_c-4.3.2-gcc48/lib \
            -Wl,-rpath,/sw/rhel6-x64/netcdf/netcdf_c-4.3.2-gcc48/lib \
            -L/sw/rhel6-x64/hdf5/hdf5-1.8.14-threadsafe-gcc48/lib \
            -Wl,-rpath,/sw/rhel6-x64/hdf5/hdf5-1.8.14-threadsafe-gcc48/lib \
            -L/sw/rhel6-x64/sys/libaec-0.3.2-gcc48/lib \
            -Wl,-rpath,/sw/rhel6-x64/sys/libaec-0.3.2-gcc48/lib \
            -lnetcdf -lhdf5_hl -lhdf5 -lsz -lcurl -lz
```
The `NCMODE` variable will define a flag for a macro called that is interpreted by the preprocessor.
The `NCMODE` has three options:
```
NCMODE    =  NETCDF_IO    for Netcd Input and Output
NCMODE    =  NETCDF_IN    for Netcdf Input and IEG Output
NCMODE    =  NETCDF_OUT   for IEG Input and Netcdf Output
```
Note, that in the case you choose IEG input and Netcdf Output, the restart file will be written
still in IEG format so that the model can be restarted with IEG input.

Make sure, that you have activated the preprocessor, e.g, the `-fpp` flag for the Intel compiler or
the `-xf77-cpp-input` for the GNU compiler (it's actually c preprocessor syntax). 
But this should be already prepared in the appropriate Makefile templates.
Furthermore, you have to uncomment the lines, that include the new dependencies of the
REMO netcdf module source code (in the `CODE` directory). 
These are further down in the Makefile, e.g.:
```
include ../CODE/makefile.netcdf
```
We have separated the netcdf dependencies and used preprocessor macros because this is the
most flexible way to handle the different implementations of the IO module. This is also useful
because REMO can still be compiled without relying on the external fortran netcdf library.

Now, you can compile REMO the usual way by typing, e.g.:
```
make mistral
```
Remeber, you have to be in the `build` directory for this to work.
If you did already compile REMO before without NETCDF support, you have to recompile.
To make sure, first clean up and compile then, e.g.:
```
make clean_all
make mistral
```
That sould compile REMO with NETCDF support.

#### Notes
For NETCDF support, you need the Fortran NETCDF libray installed on you system. You can see
in the Makefile template for the Mistral, that all pathes and libraries are already filled in.
If you are on your Ubuntu Laptop, the appropriate Makefile template should usually work, 
if you have installed NETCDF in, e.g., `/usr/lib`. You can do this by typing, e.g.
```
sudo apt-get install libnetcdf-dev
```
If, for whatever reason, your NETCDF library in installed somewhere else, or if you are
on a different supercomputer for which no template exists, you can find out the compilation
and linking flags with the `nf-config` tool. To get the compilation flags, type
```
nf-config --fflags
nf-config --flibs
```