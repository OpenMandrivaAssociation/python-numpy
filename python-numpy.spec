# Simple way to disable tests
%bcond_with tests
%bcond_without python3

%define enable_atlas 0
%{?_with_atlas: %global enable_atlas 1}

%define module	numpy

# disable this for bootstrapping nose and sphinx
%define enable_doc 0

Summary:	A fast multidimensional array facility for Python

Name:		python-%{module}
Epoch:		1
Version:	1.18.1
Release:	1
License:	BSD
Group:		Development/Python
Url: 		http://numpy.scipy.org
Source0:	https://github.com/%{module}/%{module}/releases/download/v%{version}/%{module}-%{version}%{?relc}.tar.gz

%rename	f2py
%if %enable_atlas
BuildRequires:	libatlas-devel
%else
BuildRequires:	blas-devel
%endif
BuildRequires:	lapack-devel
BuildRequires:	gcc-gfortran >= 4.0
%if %enable_doc
BuildRequires:	python3-sphinx >= 1.0
BuildRequires:	python3-matplotlib
%endif
BuildRequires:	pkgconfig(python3)
BuildRequires:	python3-pkg-resources
BuildRequires:	python3-cython
BuildRequires:	python3-nose
BuildRequires:	python3-setuptools

%description
Numpy is a general-purpose array-processing package designed to
efficiently manipulate large multi-dimensional arrays of arbitrary
records without sacrificing too much speed for small multi-dimensional
arrays. Numpy is built on the Numeric code base and adds features
introduced by numarray as well as an extended C-API and the ability to
create arrays of arbitrary type.

Numpy also provides facilities for basic linear algebra routines,
basic Fourier transforms, and random number generation.

%package -n python3-numpy
Summary:        A fast multidimensional array facility for Python3
Provides:	python3-numpy-devel = %{version}-%{release}
Provides:	python-numpy-devel = %{version}-%{release}
Group:          Development/Python
License:        BSD

%description -n python3-numpy
Numpy is a general-purpose array-processing package designed to
efficiently manipulate large multi-dimensional arrays of arbitrary
records without sacrificing too much speed for small multi-dimensional
arrays. Numpy is built on the Numeric code base and adds features
introduced by numarray as well as an extended C-API and the ability to
create arrays of arbitrary type.

Numpy also provides facilities for basic linear algebra routines,
basic Fourier transforms, and random number generation.

%package -n python3-numpy-f2py
Summary:        f2py for numpy
Requires:       python3-numpy = %{epoch}:%{version}-%{release}
Requires:       python3-devel
Provides:       python3-f2py = %{version}-%{release}
Obsoletes:      python3-f2py <= 2.45.241_1927

%description -n python3-numpy-f2py
This package includes a version of f2py that works properly with NumPy.

%prep
%setup -qn numpy-%{version}
%autopatch -p1

# Atlas 3.10 library names
cat >> site.cfg <<EOF
[atlas]
library_dirs = %{_libdir}/atlas
atlas_libs = satlas
EOF

%build
%define __cc gcc
%define __cxx g++

env CC=%{__cc} CXX=%{__cxx } ATLAS=%{_libdir} BLAS=%{_libdir} \
    LAPACK=%{_libdir} CFLAGS="%{optflags}" \
    %{__python3} setup.py build

%install
env ATLAS=%{_libdir} FFTW=%{_libdir} BLAS=%{_libdir} \
    LAPACK=%{_libdir} CFLAGS="%{optflags}" \
    %{__python3} setup.py install --root %{buildroot}


pushd %{buildroot}%{_bindir} &> /dev/null
ln -s f2py3 f2py.numpy
popd &> /dev/null

#symlink for includes, BZ 185079
mkdir -p %{buildroot}%{_includedir}
ln -s %{python3_sitearch}/%{module}/core/include/numpy/ %{buildroot}%{_includedir}/numpy

%check
%if %{with tests}
%ifarch ppc64le
# https://github.com/numpy/numpy/issues/14357
python3 runtests.py -- -k 'not test_einsum_sums_cfloat64'
%else
python3 runtests.py
%endif
%endif

%files -n python3-numpy
%license LICENSE.txt
%doc THANKS.txt site.cfg.example
%{python3_sitearch}/%{module}/__pycache__/*
%dir %{python3_sitearch}/%{module}
%{python3_sitearch}/%{module}/*.py*
%{python3_sitearch}/%{module}/core
%{python3_sitearch}/%{module}/distutils
%{python3_sitearch}/%{module}/doc
%{python3_sitearch}/%{module}/fft
%{python3_sitearch}/%{module}/lib
%{python3_sitearch}/%{module}/linalg
%{python3_sitearch}/%{module}/ma
%{python3_sitearch}/%{module}/random
%{python3_sitearch}/%{module}/testing
%{python3_sitearch}/%{module}/tests
%{python3_sitearch}/%{module}/compat
%{python3_sitearch}/%{module}/matrixlib
%{python3_sitearch}/%{module}/polynomial
%{python3_sitearch}/%{module}-*.egg-info
%exclude %{python3_sitearch}/%{module}/LICENSE.txt
%{_includedir}/numpy

%files -n python3-numpy-f2py
%{_bindir}/f2py
%{_bindir}/f2py3
%{_bindir}/f2py.numpy
%{_bindir}/f2py%{python3_version}
%{python3_sitearch}/%{module}/f2py
