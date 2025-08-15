%bcond docs 0
# test failures complain NIX_STORE undefined
# missing rapidcheck
%bcond tests 0

Name:           nix
Version:        2.30.2
Release:        1%{?dist}
Summary:        A purely functional package manager

License:        LGPL-2.1-or-later
URL:            https://github.com/NixOS/nix
Source0:        https://github.com/NixOS/nix/archive/v%{version}/%{name}-%{version}.tar.gz
Source1:        nix.conf
Source2:        registry.json
Source3:        README.md
Patch0:         nix-perl-vendorarch.patch

# https://nixos.org/manual/nix/unstable/installation/prerequisites-source
# missing aws-cpp-sdk-s3 aws-c-auth aws-c-s3
#BuildRequires:  aws-c-common
BuildRequires:  bison
BuildRequires:  blake3-devel
BuildRequires:  bzip2-devel
BuildRequires:  boost-devel
BuildRequires:  brotli-devel
BuildRequires:  busybox
BuildRequires:  cmake
BuildRequires:  editline-devel
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
BuildRequires:  perl-devel
BuildRequires:  perl-macros
BuildRequires:  perl-DBD-SQLite
BuildRequires:  perl-ExtUtils-ParseXS
%if %{with tests}
#BuildRequires:  rapidcheck-devel
%endif
BuildRequires:  sqlite-devel
BuildRequires:  xz-devel
BuildRequires:  chrpath
BuildRequires:  toml11-devel

%description
Nix is a purely functional package manager. It allows multiple
versions of a package to be installed side-by-side, ensures that
dependency specifications are complete, supports atomic upgrades and
rollbacks, allows non-root users to install software, and has many
other features. It is the basis of the NixOS Linux distribution, but
it can be used equally well under other Unix systems.

See the README.fedora.md file for setup instructions.


%package core
Summary:        Nix tools
Recommends:     busybox

%description core
The package provide the Nix package manager programs.

See the README.fedora.md file for setup instructions.


%package daemon
Summary:        The nix daemon
Requires:       nix-core = %{version}-%{release}

%description daemon
This package provides nix-daemon and associated files.


%package devel
Summary:        Development files for %{name}
Requires:       %{name}%{?_isa} = %{version}-%{release}

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


%if %{with tests}
%package test
Summary:        Nix test programs
Requires:       %{name}-core%{?_isa} = %{version}-%{release}

%description test
This package provides the nix-test programs.
%endif


%prep
%autosetup -p1

cp -p %{SOURCE3} README.fedora.md


%build
MESON_OPTS=(
    --sysconf=%{_sysconfdir}
    --localstatedir=/nix/var
    -Dlibstore:sandbox-shell=%{_bindir}/busybox
    -Dnix:profile-dir=%{_sysconfdir}/profile.d
    )
%if %{without tests}
MESON_OPTS+=(-Dunit-tests=false)
%endif
%ifarch x86_64
# missing from epel10: https://bugzilla.redhat.com/show_bug.cgi?id=2368495
%if %{undefined fedora}
MESON_OPTS+=(-Dlibutil:cpuid=disabled)
%endif
%else
MESON_OPTS+=(-Dlibutil:cpuid=disabled)
%endif

%meson "${MESON_OPTS[@]}"
%meson_build


%install
%meson_install

# https://github.com/NixOS/nix/issues/10221
chrpath --delete %{buildroot}%{_bindir}/nix %{buildroot}%{_libdir}/libnixexpr.so %{buildroot}%{_libdir}/libnixmain.so %{buildroot}%{_libdir}/libnixstore.so %{buildroot}%{_libdir}/libnixfetchers.so %{buildroot}%{_libdir}/libnixcmd.so

# nix config
mkdir -p %{buildroot}/etc/nix
cp %{SOURCE1} %{SOURCE2} %{buildroot}/etc/nix/


%if %{with tests}
%check
#export TEST_ROOT=/var/home/petersen/tmp/nix-test
%meson_test
%endif


%files core
%license COPYING
%doc README.md README.fedora.md
%{_bindir}/nix*
%if %{with tests}
%exclude %{_bindir}/nix*-test
%endif
%exclude %{_bindir}/nix-daemon
%{_libdir}/*.so
%{perl_vendorarch}/Nix
%{perl_vendorarch}/auto/Nix
%{_libexecdir}/nix
%if %{with docs}
%{_datadir}/nix
%{_mandir}/man1/*.1*
%{_mandir}/man5/*.5*
%{_mandir}/man8/*.8*
%endif
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
%{_libdir}/pkgconfig/*.pc


%if %{with docs}
%files doc
%docdir %{_defaultdocdir}/%{name}-doc-%{version}
%{_defaultdocdir}/%{name}-doc-%{version}
%endif


%if %{with tests}
%files test
%{_bindir}/nix*-test
%endif


%changelog
* Fri Aug 15 2025 Jens Petersen <petersen@redhat.com> - 2.30.2-1
- initial packaging of nix programs without /nix
