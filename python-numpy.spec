# Simple way to disable tests
%bcond_with tests

%define enable_atlas 0
%{?_with_atlas: %global enable_atlas 1}

%define module numpy

# disable this for bootstrapping nose and sphinx
%define enable_doc 0

# clang-built LTO object files can't be linked into
# gfortran code...
%global _disable_lto 1

%global optflags %{optflags} -fno-semantic-interposition -Wl,-Bsymbolic

Summary:	A fast multidimensional array facility for Python
Name:		python-%{module}
Version:	1.22.0
Release:	2
License:	BSD
Group:		Development/Python
Url: 		http://numpy.scipy.org
Source0:	https://github.com/%{module}/%{module}/releases/download/v%{version}/%{module}-%{version}%{?relc}.tar.gz
%if %enable_atlas
BuildRequires:	libatlas-devel
%else
BuildRequires:	blas-devel
%endif
BuildRequires:	lapack-devel
BuildRequires:	gcc-gfortran >= 4.0
%if %enable_doc
BuildRequires:	python-sphinx >= 1.0
BuildRequires:	python-matplotlib
%endif
BuildRequires:	pkgconfig(python)
BuildRequires:	python-pkg-resources
BuildRequires:	python-cython
BuildRequires:	python-nose
BuildRequires:	python-setuptools
%rename		f2py
Provides:	python3-numpy
Provides:	python3-numpy-devel = %{version}-%{release}
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
[atlas]
library_dirs = %{_libdir}/atlas
atlas_libs = satlas
EOF

%build
env CC=%{__cc} CXX=%{__cxx } ATLAS=%{_libdir} FFTW=%{_libdir} BLAS=%{_libdir} \
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
python3 runtests.py -- -k 'not test_einsum_sums_cfloat64'
%else
python3 runtests.py
%endif
%endif

%files
%license LICENSE.txt
%doc THANKS.txt site.cfg.example
#{python_sitearch}/%{module}/__pycache__/*
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
%{python_sitearch}/%{module}-*.egg-info
%{python_sitearch}/numpy/py.typed
%{python_sitearch}/numpy/__init__.pxd
%exclude %{python_sitearch}/%{module}/LICENSE.txt
#{_includedir}/numpy
%{python3_sitearch}/numpy/__init__.cython-*.pxd

%files -n python-numpy-f2py
%{_bindir}/f2py
%{_bindir}/f2py3
%{_bindir}/f2py.numpy
%{_bindir}/f2py%{python_version}
%{python_sitearch}/%{module}/f2py
