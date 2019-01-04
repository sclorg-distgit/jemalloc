%{?scl:%scl_package jemalloc}

Name:           %{?scl:%scl_prefix}jemalloc
Version:        5.0.1

Release:        3.bs1%{?dist}
Summary:        General-purpose scalable concurrent malloc implementation

Group:          System Environment/Libraries
License:        BSD
URL:            http://www.canonware.com/jemalloc/
Source0:        https://github.com/jemalloc/jemalloc/releases/download/%{version}/jemalloc-%{version}.tar.bz2
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

# Disable explicit altivec
Patch4:         jemalloc-5.0.1.no_explicit_altivec.patch

# No Transparent Hugepages on systems not supporting them
Patch5:         jemalloc-4.4.0.disable_thp.patch

# Upstream issue #979
Patch6:         jemalloc_fix_test_suite_segv_aarch64.patch

BuildRequires:  /usr/bin/xsltproc
%ifnarch s390 %{mips}
BuildRequires:  valgrind-devel
%endif
%{?scl:Requires:%scl_runtime}

%description
General-purpose scalable concurrent malloc(3) implementation.
This distribution is the stand-alone "portable" implementation of %{name}.

%package devel
Summary:        Development files for %{name}
Requires:       %{name} = %{version}-%{release}
Group:          Development/Libraries

%description devel
The %{name}-devel package contains libraries and header files for
developing applications that use %{name}.

%prep
%setup -q -n jemalloc-%{version}

%patch4

# Disable thp on systems not supporting this, trusting that Fedora will enable
# this on the build servers when ready for installed systems.
%ifarch %ix86 %arm aarch64 s390x
%define disable_thp --disable-thp
%patch5
%endif
%patch6 -p1

sed -i '/^LIBPREFIX/s/@libprefix@/@libprefix@%{scl}/' Makefile.in

%build
%ifarch %ix86
%if 0%{?fedora} >= 21
CFLAGS="%{optflags} -msse2"
%endif
%endif

%if 0%{?rhel} && 0%{?rhel} < 7
export LDFLAGS="%{?__global_ldflags} -lrt"
%endif

echo "For debugging package builders"
echo "What is the pagesize?"
getconf PAGESIZE

echo "What mm features are available?"
ls /sys/kernel/mm
ls /sys/kernel/mm/transparent_hugepage || true
cat /sys/kernel/mm/transparent_hugepage/enabled || true

echo "What kernel version and config is this?"
uname -a

%configure %{?disable_thp}
make %{?_smp_mflags}


%check
make check


%install
rm -rf %{buildroot}
make install DESTDIR=%{buildroot}
# Install this with doc macro instead
rm %{buildroot}%{_datadir}/doc/jemalloc/jemalloc.html

# None of these in fedora
find %{buildroot}%{_libdir}/ -name '*.a' -exec rm -vf {} ';'

mv %{buildroot}%{_libdir}/pkgconfig/jemalloc.pc %{buildroot}%{_libdir}/pkgconfig/%{scl_prefix}jemalloc.pc

%clean
rm -rf %{buildroot}


%files
%defattr(-,root,root,-)
%{_libdir}/lib*jemalloc.so.*
%{_bindir}/jemalloc.sh
%{_bindir}/jemalloc-config
%{_libdir}/pkgconfig/%{scl_prefix}jemalloc.pc
%doc COPYING README VERSION
%doc doc/jemalloc.html

%files devel
%defattr(-,root,root,-)
%{_includedir}/jemalloc
%{_bindir}/jeprof
%{_libdir}/lib*jemalloc.so
%{_mandir}/man3/jemalloc.3*

%post -p /sbin/ldconfig

%postun -p /sbin/ldconfig

%changelog
* Thu Jul 19 2018 Luboš Uhliarik <luhliari@redhat.com> - 5.0.1-3
- rebuild against new rh-varnish6

* Mon Jan 22 2018 Luboš Uhliarik <luhliari@redhat.com> - 5.0.1-2
- Resolves: #1536477 - provide without rh-varnish5 prefix

* Thu Jan 04 2018 Luboš Uhliarik <luhliari@redhat.com> - 5.0.1-1
- update to jemalloc 5.x, merge with Fedora

* Tue Aug 22 2017 Joe Orton <jorton@redhat.com> - 3.6.0-13
- update to be SCL agnostic

* Mon Aug 17 2015 Jan Kaluza <jkaluza@redhat.com> - 3.6.0-12
- add rh-varnish4 infix to jemalloc library (#1254034)

* Wed Jul 08 2015 Jan Kaluza <jkaluza@redhat.com> - 3.6.0-10
- rebuild against new scl-utils

* Thu Jul 02 2015 Jan Kaluza <jkaluza@redhat.com> - 3.6.0-9
- packaged as Software collection

* Mon Aug 18 2014 Ingvar Hagelund <ingvar@redpill-linpro.com> - 3.6.0-8
- valgrind-devel is not available on s390, closes #1131014

* Sat Aug 16 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 3.6.0-7
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_22_Mass_Rebuild

* Fri Aug 15 2014 Ingvar Hagelund <ingvar@redpill-linpro.com> - 3.6.0-6
- bz #1106933 fix only for fedora 21 and above

* Fri Aug 15 2014 Ingvar Hagelund <ingvar@redpill-linpro.com> - 3.6.0-5
- Added valgrind-devel to BuildRequires, fixing bz #974270

* Fri Aug 15 2014 Ingvar Hagelund <ingvar@redpill-linpro.com> - 3.6.0-4
- Added an i686 build fixing bz #1106933

* Sun Jun 08 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 3.6.0-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_Mass_Rebuild

* Tue Apr 01 2014 Ingvar Hagelund <ingvar@redpill-linpro.com> - 3.6.0-2
- Patch that removes explicit altivec on el5/ppc

* Mon Mar 31 2014 Ingvar Hagelund <ingvar@redpill-linpro.com> - 3.6.0-1
- New upstream release. This release fixes a critical regression 

* Fri Mar 28 2014 Ingvar Hagelund <ingvar@redpill-linpro.com> - 3.5.1-1
- New upstream release
- Updated nopprof patch to match new release
- Fixed a few bogus changelog entries

* Sat Aug 03 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 3.4.0-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_20_Mass_Rebuild

* Fri Jun 07 2013 Ingvar Hagelund <ingvar@redpill-linpro.com> - 3.4.0-1
- New upstream release

* Mon Mar 11 2013 Ingvar Hagelund <ingvar@redpill-linpro.com> - 3.3.1-1
- New upstream release
- Dropped s390 patch, it's in upstream now.

* Fri Jan 25 2013 Ingvar Hagelund <ingvar@redpill-linpro.com> - 3.3.0-1
- New upstream release
 
* Mon Nov 19 2012 Ingvar Hagelund <ingvar@redpill-linpro.com> - 3.2.0-1
- New upstream release
 
* Tue Oct 23 2012 Ingvar Hagelund <ingvar@redpill-linpro.com> - 3.1.0-1
- New upstream release
- Removed ptmalloc_lock_all patch, it is merged upstream

* Thu Jul 19 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 3.0.0-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Thu May 24 2012 Ingvar Hagelund <ingvar@redpill-linpro.com> - 3.0.0-2
- Added a patch from upstream, fixing a crash in ptmalloc_lock_all,
  closing #824646

* Mon May 14 2012 Ingvar Hagelund <ingvar@redpill-linpro.com> - 3.0.0-1
- New upstream release
- Updated no_pprof patch to match new release
- Updated s390 patch to match new relase
- Added make check
- Added new script jemalloc.sh
- Added a patch for atomic operations on epel5/ppc

* Sat Apr 21 2012 Peter Robinson <pbrobinson@fedoraproject.org> - 2.2.5-5
- Improve ARM patch

* Fri Apr 20 2012 Dennis Gilmore <dennis@ausil.us> - 2.2.5-4
- no attomics on armv5tel

* Wed Feb 08 2012 Dan Horák <dan[at]danny.cz> - 2.2.5-3
- substitute version information in the header (#788517)

* Fri Jan 13 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.2.5-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_17_Mass_Rebuild

* Sun Nov 06 2011 Ingvar Hagelund <ingvar@redpill-linpro.com> - 2.2.5-1
- New upstream release, closes #75618

* Sun Nov 06 2011 Ingvar Hagelund <ingvar@redpill-linpro.com> - 2.2.4-1
- New upstream release

* Thu Oct 13 2011 Ingvar Hagelund <ingvar@redpill-linpro.com> - 2.2.3-1
- New upstream release, closes #735057

* Mon Aug 01 2011 Ingvar Hagelund <ingvar@redpill-linpro.com> - 2.2.2-1
- New upstream release, closes #727103
- Updated no_pprof patch for 2.2.2

* Thu Mar 31 2011 Ingvar Hagelund <ingvar@redpill-linpro.com> - 2.2.1-1
- New upstream release

* Sun Mar 27 2011 Ingvar Hagelund <ingvar@redpill-linpro.com> - 2.2.0-1
- New upstream release
- Updated no_pprof patch for 2.2.0

* Tue Mar 15 2011 Ingvar Hagelund <ingvar@redpill-linpro.com> - 2.1.3-2
- New upstream release

* Wed Feb 09 2011 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.1.1-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_15_Mass_Rebuild

* Tue Feb 01 2011 Ingvar Hagelund <ingvar@redpill-linpro.com> - 2.1.1-1
- New upstream release

* Wed Jan 05 2011 Ingvar Hagelund <ingvar@redpill-linpro.com> - 2.1.0-1
- New upstream release
- Updated patch to remove pprof
- Added html doc and xsltproc as a requirement to build it

* Sat Dec 11 2010 Dan Horák <dan[at]danny.cz> - 2.0.1-3
- fix build on s390

* Thu Nov 18 2010 Ingvar Hagelund <ingvar@redpill-linpro.com> - 2.0.1-2
- Added a patch that removes pprof, as it already exists in the
  google-perftools package
- Cosmetic fixes as requested in the package review (rhbz#653682)

* Mon Nov 15 2010 Ingvar Hagelund <ingvar@redpill-linpro.com> - 2.0.1-1
- First cut of an rpm distribution of jemalloc
