# Simple way to disable tests
%bcond_with tests

%define module numpy

# disable this for bootstrapping nose and sphinx
%define enable_doc 0

# clang-built LTO object files can't be linked into
# gfortran code...
%global _disable_lto 1

# use
%global blaslib flexiblas

%global optflags %{optflags} -fno-semantic-interposition -Wl,-Bsymbolic

Summary:	A fast multidimensional array facility for Python
Name:		python-%{module}
Version:	1.26.4
Release:	2
License:	BSD
Group:		Development/Python
Url: 		https://numpy.scipy.org
Source0:	https://github.com/%{module}/%{module}/releases/download/v%{version}/%{module}-%{version}%{?relc}.tar.gz
Patch0:		numpy-windows-sucks.patch
# Reverse a safety check; without this patch,
# import numpy.core._umath_tests
# fails, breaking invesalius and possibly more.
Patch1:		numpy-1.26.2-dtype-api.patch

BuildRequires:	pkgconfig(%{blaslib})
BuildRequires:	pkgconfig(lapack)
BuildRequires:	gcc-gfortran >= 4.0
%if %enable_doc
BuildRequires:	python%{pyver}dist(sphinx)
BuildRequires:	python%{pyver}dist(matplotlib)
%endif
BuildRequires:	pkgconfig(python3)
BuildRequires:	python-pkg-resources
BuildRequires:	python%{pyver}dist(cython)
BuildRequires:	python%{pyver}dist(nose)
BuildRequires:	python%{pyver}dist(nose)
BuildRequires:	python%{pyver}dist(setuptools)
BuildRequires:	python%{pyver}dist(tomli)
%rename		f2py
Provides:	python%{pyver}-numpy
Provides:	python%{pyver}-numpy-devel = %{version}-%{release}
Provides:	python-numpy-devel = %{version}-%{release}

%description
Numpy is a general-purpose array-processing package designed to
efficiently manipulate large multi-dimensional arrays of arbitrary
records without sacrificing too much speed for small multi-dimensional
arrays. Numpy is built on the Numeric code base and adds features
introduced by numarray as well as an extended C-API and the ability to
create arrays of arbitrary type.

Numpy also provides facilities for basic linear algebra routines,
basic Fourier transforms, and random number generation.

%package -n python-numpy-f2py
Summary:	f2py for numpy
Requires:	python-numpy = %{EVRD}
Requires:	pkgconfig(python3)
Provides:	python-f2py = %{version}-%{release}
Provides:	python3-f2py = %{version}-%{release}
Obsoletes:	python3-f2py <= 2.45.241_1927

%description -n python-numpy-f2py
This package includes a version of f2py that works properly with NumPy.

%prep
%autosetup -p1 -n numpy-%{version}

# Atlas 3.10 library names
cat >> site.cfg <<EOF
[openblas]
libraries = %{blaslib}
library_dirs = %{_libdir}
EOF

%build
%set_build_flags
env CC=%{__cc} CXX=%{__cxx} ATLAS=%{_libdir} FFTW=%{_libdir} BLAS=%{_libdir} \
    LAPACK=%{_libdir} CFLAGS="%{optflags} -fPIC -O3" \
    FFLAGS="%{optflags} -fPIC -O3" \
    python3 setup.py build

%install
env ATLAS=%{_libdir} FFTW=%{_libdir} BLAS=%{_libdir} \
    LAPACK=%{_libdir} CFLAGS="%{optflags} -fPIC -O3" \
    FFLAGS="%{optflags} -fPIC -O3" \
    python setup.py install --root %{buildroot}

pushd %{buildroot}%{_bindir} &> /dev/null
ln -s f2py3 f2py.numpy
popd &> /dev/null

#symlink for includes, BZ 185079
#mkdir -p %{buildroot}%{_includedir}
#ln -s %{python3_sitearch}/%{module}/core/include/numpy/ %{buildroot}%{_includedir}/numpy

%check
%if %{with tests}
%ifarch ppc64le
# https://github.com/numpy/numpy/issues/14357
%python runtests.py -- -k 'not test_einsum_sums_cfloat64'
%else
%python runtests.py
%endif
%endif

%files
%license LICENSE.txt
%doc THANKS.txt site.cfg.example
%dir %{python_sitearch}/%{module}
%{python_sitearch}/%{module}/*.py*
%{python_sitearch}/%{module}/array_api
%{python_sitearch}/%{module}/core
%{python_sitearch}/%{module}/distutils
%{python_sitearch}/%{module}/doc
%{python_sitearch}/%{module}/fft
%{python_sitearch}/%{module}/lib
%{python_sitearch}/%{module}/linalg
%{python_sitearch}/%{module}/ma
%{python_sitearch}/%{module}/random
%{python_sitearch}/%{module}/testing
%{python_sitearch}/%{module}/tests
%{python_sitearch}/%{module}/typing
%{python_sitearch}/%{module}/compat
%{python_sitearch}/%{module}/matrixlib
%{python_sitearch}/%{module}/polynomial
%{python_sitearch}/%{module}/_core
%{python_sitearch}/%{module}/_pyinstaller
%{python_sitearch}/%{module}/_typing
%{python_sitearch}/%{module}/_utils
%{python_sitearch}/%{module}-*.egg-info
%{python_sitearch}/numpy/py.typed
%{python_sitearch}/numpy/__init__.pxd
%exclude %{python_sitearch}/%{module}/LICENSE.txt
#{_includedir}/numpy
%{python3_sitearch}/numpy/__init__.cython-*.pxd

%files -n python-numpy-f2py
%{_bindir}/f2py
%{_bindir}/f2py.numpy
%{python_sitearch}/%{module}/f2py
