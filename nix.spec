# needs mdbook
%bcond docs 0
# test failures complain NIX_STORE undefined
# and missing rapidcheck
%bcond tests 0

Name:           nix
Version:        2.31.1
Release:        6%{?dist}
Summary:        A purely functional package manager

License:        LGPL-2.1-or-later
URL:            https://github.com/NixOS/nix
Source0:        https://github.com/NixOS/nix/archive/%{version}/%{name}-%{version}.tar.gz
Source1:        nix.conf
Source2:        registry.json
Source3:        README.md
# soversion patches:
# https://github.com/NixOS/nix/pull/13995
Patch0:         https://patch-diff.githubusercontent.com/raw/NixOS/nix/pull/13995.patch
# https://github.com/NixOS/nix/pull/14001
Patch1:         https://patch-diff.githubusercontent.com/raw/NixOS/nix/pull/14001.patch
# https://github.com/NixOS/nix/pull/14005
Patch2:         https://patch-diff.githubusercontent.com/raw/NixOS/nix/pull/14005.patch

# https://nixos.org/manual/nix/unstable/installation/prerequisites-source
# missing aws-cpp-sdk-s3 aws-c-auth aws-c-s3
#BuildRequires:  aws-c-common
BuildRequires:  bison
BuildRequires:  blake3-devel
BuildRequires:  bzip2-devel
BuildRequires:  boost-devel
BuildRequires:  boost-url
BuildRequires:  brotli-devel
%ifarch x86_64 aarch64 ppc64le
BuildRequires:  busybox
%endif
# needed for toml11
BuildRequires:  cmake
%if %{with docs}
BuildRequires:  doxygen
%endif
BuildRequires:  flex
BuildRequires:  gc-devel
BuildRequires:  gcc-c++
%if %{with tests}
BuildRequires:  gmock-devel
%endif
BuildRequires:  libgit2-devel
BuildRequires:  jq
BuildRequires:  json-devel
BuildRequires:  libarchive-devel
%if %{defined fedora}
%ifarch x86_64
BuildRequires:  libcpuid-devel
%endif
%endif
BuildRequires:  libcurl-devel
BuildRequires:  libseccomp-devel
BuildRequires:  libsodium-devel
BuildRequires:  lowdown
BuildRequires:  lowdown-devel
BuildRequires:  meson
BuildRequires:  openssl-devel
%if %{with tests}
#BuildRequires:  rapidcheck-devel
%endif
BuildRequires:  readline-devel
BuildRequires:  sqlite-devel
BuildRequires:  systemd-rpm-macros
BuildRequires:  toml11-devel
BuildRequires:  xz-devel
Requires:       nix-libs%{?_isa} = %{version}-%{release}
Recommends:     nix-daemon = %{version}-%{release}
%ifarch x86_64 aarch64 ppc64le
Recommends:     busybox
%endif

%description
Nix is a purely functional package manager. It allows multiple
versions of a package to be installed side-by-side, ensures that
dependency specifications are complete, supports atomic upgrades and
rollbacks, allows non-root users to install software, and has many
other features. It is the basis of the NixOS Linux distribution, but
it can be used equally well under other Unix systems.

See the README.fedora.md file for setup instructions.


%package daemon
Summary:        The nix daemon
BuildArch:      noarch
Requires:       %{name} = %{version}-%{release}

%description daemon
This package provides nix-daemon and associated files.


%package devel
Summary:        Development files for %{name}
Requires:       %{name}-libs%{?_isa} = %{version}-%{release}

%description devel
The %{name}-devel package contains libraries and header files for
developing applications that use %{name}.


%if %{with docs}
%package doc
Summary:        Documentation files for %{name}
BuildArch:      noarch

%description doc
The %{name}-doc package contains documentation files for %{name}.
%endif


%package libs
Summary:        Runtime libraries for %{name}

%description libs
The package provides the the runtime libraries for %{name}.


%if %{with tests}
%package test
Summary:        Nix test programs
Requires:       %{name}%{?_isa} = %{version}-%{release}

%description test
This package provides the nix-test programs.
%endif


%prep
%autosetup -p1

install -p -m 0644 %{SOURCE3} README.fedora.md


%build
MESON_OPTS=(
    --sysconf=%{_sysconfdir}
    --localstatedir=/nix/var
    --libexecdir=%{_libexecdir}
    -Dbindings=false
    -Ddoc-gen=%[%{with docs}?"true":"false"]
    -Dlibcmd:readline-flavor=readline
    -Dlibstore:sandbox-shell=%{_bindir}/busybox
    -Dnix:profile-dir=%{_sysconfdir}/profile.d
    -Dunit-tests=%[%{with tests}?"true":"false"]
%ifarch x86_64
# missing from epel10: https://bugzilla.redhat.com/show_bug.cgi?id=2368495
%if %{undefined fedora}
    -Dlibutil:cpuid=disabled
%endif
%else
    -Dlibutil:cpuid=disabled
%endif
    )

%meson "${MESON_OPTS[@]}"
%meson_build


%install
%meson_install

# nix config
mkdir -p %{buildroot}/etc/nix
cp %{SOURCE1} %{SOURCE2} %{buildroot}/etc/nix/


%check
LD_LIBRARY_PATH=%{buildroot}%{_libdir} %{buildroot}%{_bindir}/nix --help
%if %{with tests}
#export TEST_ROOT=/var/home/petersen/tmp/nix-test
%meson_test
%endif


%post daemon
%systemd_post nix-daemon.service


%preun daemon
%systemd_preun nix-daemon.service


%postun daemon
%systemd_postun_with_restart nix-daemon.service


%files
%doc README.md README.fedora.md
%{_bindir}/nix*
%if %{with tests}
%exclude %{_bindir}/nix*-test
%endif
%exclude %{_bindir}/nix-daemon
%{_libexecdir}/nix
%config(noreplace) %{_sysconfdir}/nix/nix.conf
%config(noreplace) %{_sysconfdir}/nix/registry.json
%config(noreplace) %{_sysconfdir}/profile.d/nix.sh
%config(noreplace) %{_sysconfdir}/profile.d/nix.fish
%{_datadir}/bash-completion/completions/nix
%{_datadir}/fish/vendor_completions.d/nix.fish
%{_datadir}/zsh/site-functions/*


%files daemon
%{_bindir}/nix-daemon
%{_sysconfdir}/profile.d/nix-daemon.*sh
%{_prefix}/lib/systemd/system/nix-daemon.*
%{_prefix}/lib/tmpfiles.d/nix-daemon.conf


%files devel
%{_includedir}/nix
%{_includedir}/nix_api_*.h
%{_includedir}/nix_api_*.hh
%{_libdir}/libnixcmd.so
%{_libdir}/libnixexpr.so
%{_libdir}/libnixexprc.so
%{_libdir}/libnixfetchers.so
%{_libdir}/libnixfetchersc.so
%{_libdir}/libnixflake.so
%{_libdir}/libnixflakec.so
%{_libdir}/libnixmain.so
%{_libdir}/libnixmainc.so
%{_libdir}/libnixstore.so
%{_libdir}/libnixstorec.so
%{_libdir}/libnixutil.so
%{_libdir}/libnixutilc.so
%{_libdir}/pkgconfig/*.pc


%if %{with docs}
%files doc
%{_defaultdocdir}/%{name}
%endif


%files libs
%license COPYING
%{_libdir}/libnixcmd.so.%{version}
%{_libdir}/libnixexpr.so.%{version}
%{_libdir}/libnixexprc.so.%{version}
%{_libdir}/libnixfetchers.so.%{version}
%{_libdir}/libnixfetchersc.so.%{version}
%{_libdir}/libnixflake.so.%{version}
%{_libdir}/libnixflakec.so.%{version}
%{_libdir}/libnixmain.so.%{version}
%{_libdir}/libnixmainc.so.%{version}
%{_libdir}/libnixstore.so.%{version}
%{_libdir}/libnixstorec.so.%{version}
%{_libdir}/libnixutil.so.%{version}
%{_libdir}/libnixutilc.so.%{version}

%if %{with tests}
%files test
%{_bindir}/nix*-test
%endif


%changelog
* Wed Sep 17 2025 Jens Petersen <petersen@redhat.com> - 2.31.1-6
- list .so files explicitly without globbing (#2388768)

* Mon Sep 15 2025 Jens Petersen <petersen@redhat.com> - 2.31.1-5
- set the soversion to the nix version (#13995, #14001, #14005)

* Sun Sep 14 2025 Jens Petersen <petersen@redhat.com> - 2.31.1-4
- add simple check with LD_LIBRARY_PATH

* Fri Sep 12 2025 Jens Petersen <petersen@redhat.com> - 2.31.1-3
- revert to shared libs, add libs subpackage and restore devel
- apply upstream submitted PR to enable soname versioning (#13966)

* Thu Sep 11 2025 Jens Petersen <petersen@redhat.com> - 2.31.1-2
- noarch nix-daemon subpackage cannot use _isa requires

* Wed Sep 10 2025 Jens Petersen <petersen@redhat.com> - 2.31.1-1
- https://github.com/NixOS/nix/blob/2.31.1/doc/manual/source/release-notes/rl-2.31.md
- rename nix-core to base package
- use readline (#2388768)
- improve MESON_OPTS setup (zbyszek, #2388768)
- use static libs and drop devel package
- disable perl binding

* Sat Aug 16 2025 Jens Petersen <petersen@redhat.com> - 2.30.2-2
- fix nix-devel requires
- add systemd scriptlets for nix-daemon

* Fri Aug 15 2025 Jens Petersen <petersen@redhat.com> - 2.30.2-1
- initial packaging of nix programs without /nix
