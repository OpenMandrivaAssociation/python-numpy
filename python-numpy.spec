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

# Python module doesn't need to use -lpython
%global _disable_ld_no_undefined 1

Summary:	A fast multidimensional array facility for Python
Name:		python-%{module}
Version:	2.5.3
Release:	1
License:	BSD
Group:		Development/Python
Url: 		https://numpy.org
Source0:	https://github.com/%{module}/%{module}/releases/download/v%{version}/%{module}-%{version}%{?relc}.tar.gz

BuildRequires:	pkgconfig(%{blaslib})
BuildRequires:	pkgconfig(lapack)
BuildRequires:	gcc-gfortran >= 4.0
%if %enable_doc
BuildRequires:	python%{pyver}dist(nose)
BuildRequires:	python%{pyver}dist(sphinx)
BuildRequires:	python%{pyver}dist(matplotlib)
%endif
BuildRequires:	pkgconfig(python3)
BuildRequires:	python-pkg-resources
BuildRequires:	python%{pyver}dist(cython)
BuildRequires:	python%{pyver}dist(setuptools)
BuildRequires:	python%{pyver}dist(tomli)
BuildRequires:	python%{pyver}dist(meson-python)
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
export CC=%{__cc} CXX=%{__cxx} ATLAS=%{_libdir} FFTW=%{_libdir} BLAS=%{_libdir} \
    LAPACK=%{_libdir} CFLAGS="%{optflags} -fPIC -O3" \
    FFLAGS="%{optflags} -fPIC -O3"
%py_build

# Array/ufunc/linalg/fft paths are exactly where PGO helps. meson-python
# leaves the compiled extensions in the build tree after %%py_build.
%pgo
root=
for cand in \
	$(find . -path '*/numpy/_core/_multiarray_umath*.so' -printf '%h\n' 2>/dev/null) \
	$(find . -path '*/numpy/_core/_multiarray_umath*.so' 2>/dev/null | sed 's|/[^/]*$||'); do
	# cand is .../numpy/_core ; package root is .../numpy
	r=$(dirname "$cand")
	[ -f "$r/__init__.py" ] && root="$r" && break
done
if [ -z "$root" ]; then
	echo "PGO: compiled numpy extensions not found after %%py_build" >&2
	find . -name '_multiarray_umath*' 2>/dev/null | head
	exit 1
fi
export PYTHONPATH="$(dirname "$root")${PYTHONPATH:+:$PYTHONPATH}"
%python - <<'PY'
import numpy as np
rng = np.random.default_rng(0)
a = rng.standard_normal((256, 256))
b = a @ a.T
np.linalg.eigvalsh(b[:64, :64])
np.linalg.svd(a[:128, :64], full_matrices=False)
np.fft.fft2(a)
np.sort(a, axis=0)
np.dot(a, a)
np.einsum("ij,jk->ik", a, a)
c = a.astype(np.float32)
np.mean(c, axis=0)
np.sum(c)
np.sin(c)
np.exp(c * 0.01)
x = rng.integers(0, 100, size=10000)
np.bincount(x)
np.unique(x)
PY

%install
export ATLAS=%{_libdir} FFTW=%{_libdir} BLAS=%{_libdir} \
    LAPACK=%{_libdir} CFLAGS="%{optflags} -fPIC -O3" \
    FFLAGS="%{optflags} -fPIC -O3"
%py_install

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
%doc THANKS.txt
%dir %{python_sitearch}/%{module}
%{_bindir}/numpy-config
%{python_sitearch}/%{module}/*.py*
%{python_sitearch}/%{module}/char
%{python_sitearch}/%{module}/core
%{python_sitearch}/%{module}/ctypeslib
%{python_sitearch}/%{module}/doc
%{python_sitearch}/%{module}/fft
%{python_sitearch}/%{module}/lib
%{python_sitearch}/%{module}/linalg
%{python_sitearch}/%{module}/ma
%{python_sitearch}/%{module}/random
%{python_sitearch}/%{module}/testing
%{python_sitearch}/%{module}/tests
%{python_sitearch}/%{module}/typing
%{python_sitearch}/%{module}/matrixlib
%{python_sitearch}/%{module}/polynomial
%{python_sitearch}/%{module}/rec
%{python_sitearch}/%{module}/strings
%{python_sitearch}/%{module}/_core
%{python_sitearch}/%{module}/_pyinstaller
%{python_sitearch}/%{module}/_typing
%{python_sitearch}/%{module}/_utils
%{python_sitearch}/%{module}-*.dist-info
%{python_sitearch}/numpy/py.typed
%{python_sitearch}/numpy/__init__.pxd
%{python_sitearch}/numpy/__pycache__
#{_includedir}/numpy
%{python3_sitearch}/numpy/__init__.cython-*.pxd

%files -n python-numpy-f2py
%{_bindir}/f2py
%{_bindir}/f2py.numpy
%{python_sitearch}/%{module}/f2py
