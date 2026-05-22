%global package_speccommit 022819bd2e2490d0e1e4250c65bb3059cca21365
%global usver 6.2.1
%global xsver 5
%global xsrel %{xsver}%{?xscount}%{?xshash}
#
# Important for %%{ix86}:
# This rpm has to be build on a CPU with sse2 support like Pentium 4 !
#

Summary: GNU arbitrary precision library
Name: gmp
Version: 6.2.1
Release: %{?xsrel}~XCPNG2698.3%{?dist}

%if 0%{?xenserver} < 9
Epoch: 1
%else
# XenServer 9 reset all Epoch
Epoch: 0
%endif

URL: https://gmplib.org/
Source0: gmp-6.2.1.tar.xz
Source2: gmp.h
Source3: gmp-mparam.h
Patch0: gmp-6.0.0-debuginfo.patch
Patch1: gmp-intel-cet.patch
License: LGPLv3+ or GPLv2+
BuildRequires: autoconf automake libtool
BuildRequires: gcc
BuildRequires: gcc-c++
BuildRequires: git
#autoreconf on arm needs:
BuildRequires: make

%description
The gmp package contains GNU MP, a library for arbitrary precision
arithmetic, signed integers operations, rational numbers and floating
point numbers. GNU MP is designed for speed, for both small and very
large operands. GNU MP is fast because it uses fullwords as the basic
arithmetic type, it uses fast algorithms, it carefully optimizes
assembly code for many CPUs' most common inner loops, and it generally
emphasizes speed over simplicity/elegance in its operations.

Install the gmp package if you need a fast arbitrary precision
library.

%package c++
Summary: C++ bindings for the GNU MP arbitrary precision library
Requires: %{name}%{?_isa} = %{epoch}:%{version}-%{release}

%description c++
Bindings for using the GNU MP arbitrary precision library in C++ applications.

%package devel
Summary: Development tools for the GNU MP arbitrary precision library
Requires: %{name}%{?_isa} = %{epoch}:%{version}-%{release}
Requires: %{name}-c++%{?_isa} = %{epoch}:%{version}-%{release}

%description devel
The libraries, header files and documentation for using the GNU MP
arbitrary precision library in applications.

If you want to develop applications which will use the GNU MP library,
you'll need to install the gmp-devel package.  You'll also need to
install the gmp package.

%package static
Summary: Development tools for the GNU MP arbitrary precision library
Requires: %{name}-devel = %{epoch}:%{version}-%{release}

%description static
The static libraries for using the GNU MP arbitrary precision library
in applications.

%prep
%autosetup -S git

%build
autoreconf -ifv
if as --help | grep -q execstack; then
  # the object files do not require an executable stack
  export CCAS="gcc -c -Wa,--noexecstack"
fi

%configure --enable-cxx --enable-fat

sed -e 's|^hardcode_libdir_flag_spec=.*|hardcode_libdir_flag_spec=""|g' \
    -e 's|^runpath_var=LD_RUN_PATH|runpath_var=DIE_RPATH_DIE|g' \
    -e 's|-lstdc++ -lm|-lstdc++|' \
    -i libtool
export LD_LIBRARY_PATH=`pwd`/.libs
%make_build

%if %{with fips}
%define __spec_install_post \
    %{?__debug_package:%{__debug_install_post}} \
    %{__arch_install_post} \
    %{__os_install_post} \
    fipshmac -d $RPM_BUILD_ROOT%{_libdir} $RPM_BUILD_ROOT%{_libdir}/libgmp.so.10.* \
    file=`basename $RPM_BUILD_ROOT%{_libdir}/libgmp.so.10.*.hmac` && \
        mv $RPM_BUILD_ROOT%{_libdir}/$file $RPM_BUILD_ROOT%{_libdir}/.$file && \
        ln -s .$file $RPM_BUILD_ROOT%{_libdir}/.libgmp.so.10.hmac
%{nil}
%endif

%install
export LD_LIBRARY_PATH=`pwd`/.libs
%make_install
install -m 644 gmp-mparam.h ${RPM_BUILD_ROOT}%{_includedir}
rm -f $RPM_BUILD_ROOT%{_libdir}/lib{gmp,mp,gmpxx}.la
rm -f $RPM_BUILD_ROOT%{_infodir}/dir
/sbin/ldconfig -n $RPM_BUILD_ROOT%{_libdir}
ln -sf libgmpxx.so.4 $RPM_BUILD_ROOT%{_libdir}/libgmpxx.so

# Rename gmp.h to gmp-<arch>.h and gmp-mparam.h to gmp-mparam-<arch>.h to
# avoid file conflicts on multilib systems and install wrapper include files
# gmp.h and gmp-mparam-<arch>.h
basearch=%{_arch}
# always use arm for arm*
%ifarch %{arm}
basearch=arm
%endif

mv %{buildroot}/%{_includedir}/gmp.h %{buildroot}/%{_includedir}/gmp-${basearch}.h
install -m644 %{SOURCE2} %{buildroot}/%{_includedir}/gmp.h
mv %{buildroot}/%{_includedir}/gmp-mparam.h %{buildroot}/%{_includedir}/gmp-mparam-${basearch}.h
install -m644 %{SOURCE3} %{buildroot}/%{_includedir}/gmp-mparam.h


%check
%ifnarch ppc
export LD_LIBRARY_PATH=`pwd`/.libs
%make_build check
%endif

%ldconfig_scriptlets

%ldconfig_scriptlets c++

%files
%license COPYING COPYING.LESSERv3 COPYINGv2 COPYINGv3
%doc NEWS README
%{_libdir}/libgmp.so.*
%if %{with fips}
%{_libdir}/.libgmp.so.*.hmac
%endif

%files c++
%{_libdir}/libgmpxx.so.*

%files devel
%{_libdir}/libgmp.so
%{_libdir}/libgmpxx.so
%{_libdir}/pkgconfig/gmp.pc
%{_libdir}/pkgconfig/gmpxx.pc
%{_includedir}/*.h
%{_infodir}/gmp.info*

%files static
%{_libdir}/libgmp.a
%{_libdir}/libgmpxx.a

%changelog
* Tue Nov 25 2025 Lin Liu <lin.liu01@citrix.com> - 6.2.1-5
- CP-310102: Add Epoch as part of package Requries version

* Tue Nov 11 2025 Lin Liu <lin.liu01@citrix.com> - 6.2.1-4
- CP-310102: Rebuild in XS8 to support gnutls update

* Mon Jan 13 2025 Chunjie Zhu <chunjie.zhu@cloud.com> - 6.2.1-3
- CP-53083: Remove dependency on perl-Carp

* Thu Sep 12 2024 AshwinH <ashwin.h@cloud.com> - 6.2.1-2
- CP-50735: Remove legacy Buildrequires fipscheck

* Tue Jun 27 2023 Lin Liu <lin.liu@citrix.com> - 6.2.1-1
- First imported release

