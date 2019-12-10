%define module	numpy
# disable this for bootstrapping nose and sphinx
%define enable_tests 0
%define enable_doc 0

%ifnarch %{x86_64} %{riscv}
%ifarch %{ix86}
# Workaround for,
# as of clang 8.0.0-1, python-numpy 1.16.2:
# error: build/temp.linux-i686-3.7/numpy/core/src/umath/cpuid.o: relocation R_386_GOTOFF against preemptible symbol __cpu_model cannot be used when making a shared object
# as well as the issue with other non-x86_64 arches
%global optflags %{optflags} --rtlib=compiler-rt -fuse-ld=bfd
%global ldflags %{optflags} --rtlib=compiler-rt -fuse-ld=bfd
%else
# Workaround for,
# as of clang 8.0.0-1, python-numpy 1.16.2:
# BUILDSTDERR: numpy/core/src/common/templ_common.h.src:29: error: undefined reference to '__mulodi4'
%global optflags %{optflags} --rtlib=compiler-rt
%global ldflags %{optflags} --rtlib=compiler-rt
%endif
%endif

Summary:	A fast multidimensional array facility for Python
Name:		python-%{module}
Version:	1.16.5
Release:	2
License:	BSD
Group:		Development/Python
Url: 		http://numpy.scipy.org
Source0:	https://github.com/numpy/numpy/archive/%{module}-%{version}.tar.gz
Patch0:		numpy-1.10.2-link.patch
Patch1:		numpy-1.14.0-compile.patch
Patch2:		python-numpy-1.16.2-libm-linkage.patch

%rename	f2py

BuildRequires:	blas-devel
BuildRequires:	lapack-devel
BuildRequires:	gcc-gfortran >= 4.0
%if %enable_doc
BuildRequires:	python-sphinx >= 1.0
BuildRequires:	python-matplotlib
%endif
%if %enable_tests
BuildRequires:	python-nose
%endif
BuildRequires: python-cython
BuildRequires: python-setuptools
BuildRequires: python2-setuptools
BuildRequires: pkgconfig(python3)
BuildRequires: pkgconfig(python2)
BuildRequires: python2-distribute
BuildRequires: python-pkg-resources
BuildRequires: python2-pkg-resources
%ifarch %{x86_64}
BuildRequires: pkgconfig(atlas)
%endif

%description
Numpy is a general-purpose array-processing package designed to
efficiently manipulate large multi-dimensional arrays of arbitrary
records without sacrificing too much speed for small multi-dimensional
arrays. Numpy is built on the Numeric code base and adds features
introduced by numarray as well as an extended C-API and the ability to
create arrays of arbitrary type.

Numpy also provides facilities for basic linear algebra routines,
basic Fourier transforms, and random number generation.

%package devel
Summary:	Numpy headers and development tools
Group:		Development/Python
Requires:	%{name} = %{EVRD}

%description devel
This package contains tools and header files need to develop modules 
in C and Fortran that can interact with Numpy

%package -n python2-numpy
Summary:        A fast multidimensional array facility for Python2
Group:          Development/Python
License:        BSD

%description -n python2-numpy
Numpy is a general-purpose array-processing package designed to
efficiently manipulate large multi-dimensional arrays of arbitrary
records without sacrificing too much speed for small multi-dimensional
arrays. Numpy is built on the Numeric code base and adds features
introduced by numarray as well as an extended C-API and the ability to
create arrays of arbitrary type.

Numpy also provides facilities for basic linear algebra routines,
basic Fourier transforms, and random number generation.

%package -n python2-numpy-devel
Summary:        Numpy headers and development tools
Group:          Development/Python
Requires:       python2-numpy = %{EVRD}

%description -n python2-numpy-devel
This package contains tools and header files need to develop modules.
in C and Fortran that can interact with Numpy.

%prep
%setup -qc
cd %{module}-%{version}
%apply_patches
cd ..
mv %{module}-%{version} python2
cp -a python2 python3
cd python2
# workaround for rhbz#849713
# http://mail.scipy.org/pipermail/numpy-discussion/2012-July/063530.html
rm numpy/distutils/command/__init__.py && touch numpy/distutils/command/__init__.py
cd -

cd python3
rm numpy/distutils/command/__init__.py && touch numpy/distutils/command/__init__.py
cd -

%build
export MATHLIB="m,dl"
cd python3
%ifnarch %{x86_64}
ATLAS=None BLAS=None \
%endif
CFLAGS="%{optflags} -O3 -fno-lto" PYTHONDONTWRITEBYTECODE= %{__python3} setup.py config_fc --fcompiler=gnu95 build
cd -

cd python2
%ifnarch %{x86_64}
ATLAS=None BLAS=None \
%endif
CFLAGS="%{optflags} -O3 -fno-lto" PYTHONDONTWRITEBYTECODE= %{__python2} setup.py config_fc --fcompiler=gnu95 build

%if %enable_doc
cd doc
export PYTHONPATH=`dir -d ../build/lib.linux*`
%make html
cd -
%endif

cd -


%install
# first install python2 so the binaries are overwritten by the python2 ones
cd python2
%ifnarch %{x86_64}
ATLAS=None BLAS=None \
%endif
CFLAGS="%{optflags} -fPIC -O3 -fno-lto" PYTHONDONTWRITEBYTECODE= %{__python2} setup.py install --root=%{buildroot}

rm -rf %{buildroot}%{py2_platsitedir}/%{module}/__pycache__

# Drop shebang from non-executable scripts to make rpmlint happy
find %{buildroot}%{py2_platsitedir} -name "*py" -perm 644 -exec sed -i '/#!\/usr\/bin\/env python/d' {} \;

cd -

cd python3
%ifnarch %{x86_64}
ATLAS=None BLAS=None \
%endif
CFLAGS="%{optflags} -fPIC -O3 -fno-lto" PYTHONDONTWRITEBYTECODE= %{__python3} setup.py install --root=%{buildroot}

rm -rf %{buildroot}%{py3_platsitedir}/%{module}/tools/
rm -rf %{buildroot}%{py3_platsitedir}/%{module}/__pycache__

# Remove doc files that should be in %doc:
rm -f %{buildroot}%{py3_platsitedir}/%{module}/COMPATIBILITY
rm -f %{buildroot}%{py3_platsitedir}/%{module}/*.txt
rm -f %{buildroot}%{py3_platsitedir}/%{module}/site.cfg.example

# Drop shebang from non-executable scripts to make rpmlint happy
find %{buildroot}%{py3_platsitedir} -name "*py" -perm 644 -exec sed -i '/#!\/usr\/bin\/env python/d' {} \;
cd -

# We push that in with %%doc
rm -f %{buildroot}%{_prefix}/*/python*/site-packages/%{module}/LICENSE.txt

%check
%if %enable_tests
# Don't run tests from within main directory to avoid importing the uninstalled numpy stuff:
cd doc &> /dev/null
PYTHONPATH="%{buildroot}%{py2_platsitedir}" %{__python2} -c "import pkg_resources, numpy; numpy.test()"
cd - &> /dev/null

cd doc &> /dev/null
PYTHONPATH="%{buildroot}%{py3_platsitedir}" %{__python3} -c "import pkg_resources, numpy ; numpy.test()"
cd - &> /dev/null
%endif

%files 
%doc python3/LICENSE.txt python3/THANKS.txt python3/site.cfg.example 
%if %enable_doc
%doc python3/doc/build/html
%endif
%dir %{py_platsitedir}/%{module}
%{py_platsitedir}/%{module}/__pycache__
%{py_platsitedir}/%{module}/*.py*
%{py_platsitedir}/%{module}/core/ 
%{py_platsitedir}/%{module}/compat/
%{py_platsitedir}/%{module}/doc/
%exclude %{py_platsitedir}/%{module}/core/include/
%exclude %{py_platsitedir}/%{module}/core/lib/*.a
%{py_platsitedir}/%{module}/fft/
%{py_platsitedir}/%{module}/lib/
%{py_platsitedir}/%{module}/linalg/
%{py_platsitedir}/%{module}/ma/
%{py_platsitedir}/%{module}/matrixlib/
%{py_platsitedir}/%{module}/polynomial/
%{py_platsitedir}/%{module}/random/
%exclude %{py_platsitedir}/%{module}/random/randomkit.h
%{py_platsitedir}/%{module}/testing/
%{py_platsitedir}/%{module}/tests/ 
%{py_platsitedir}/%{module}-*.egg-info
%{_bindir}/f2py
%{_bindir}/f2py3
%{_bindir}/f2py3.*

%files devel
%{py_platsitedir}/%{module}/core/include/
%{py_platsitedir}/%{module}/core/lib/*.a
%{py_platsitedir}/%{module}/distutils/
%{py_platsitedir}/%{module}/random/randomkit.h
%{py_platsitedir}/%{module}/f2py/

%files -n python2-numpy
%doc python2/LICENSE.txt python2/THANKS.txt python2/site.cfg.example
%dir %{py2_platsitedir}/%{module}
%{_bindir}/f2py2
%{_bindir}/f2py2.7
%{py2_platsitedir}/%{module}/*.py*
%{py2_platsitedir}/%{module}/doc
%{py2_platsitedir}/%{module}/core
%exclude %{py2_platsitedir}/%{module}/core/include/
%exclude %{py2_platsitedir}/%{module}/core/lib/*.a
%{py2_platsitedir}/%{module}/fft
%{py2_platsitedir}/%{module}/lib
%{py2_platsitedir}/%{module}/linalg
%{py2_platsitedir}/%{module}/ma
%{py2_platsitedir}/%{module}/random
%exclude %{py2_platsitedir}/%{module}/random/randomkit.h
%{py2_platsitedir}/%{module}/testing
%{py2_platsitedir}/%{module}/tests
%{py2_platsitedir}/%{module}/compat
%{py2_platsitedir}/%{module}/matrixlib
%{py2_platsitedir}/%{module}/polynomial
%{py2_platsitedir}/%{module}-*.egg-info

%files -n python2-numpy-devel
%{py2_platsitedir}/%{module}/core/include/
%{py2_platsitedir}/%{module}/f2py
%{py2_platsitedir}/%{module}/core/lib/*.a
%{py2_platsitedir}/%{module}/distutils/
%{py2_platsitedir}/%{module}/random/randomkit.h
