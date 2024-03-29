%bcond docs 0

Name:           nix
Version:        2.19.4
Release:        1%{?dist}
Summary:        Nix software deployment system

License:        LGPLv2+
URL:            https://github.com/NixOS/nix
Source0:        https://github.com/NixOS/nix/archive/refs/tags/%{version}.tar.gz#/%{name}-%{version}.tar.gz
# https://nixos.org/manual/nix/unstable/installation/prerequisites-source
BuildRequires:  autoconf-archive
BuildRequires:  automake
BuildRequires:  bison
BuildRequires:  bzip2-devel
BuildRequires:  boost-devel
BuildRequires:  brotli-devel
BuildRequires:  editline-devel
BuildRequires:  flex
BuildRequires:  gc-devel
BuildRequires:  gcc-c++
BuildRequires:  jq
BuildRequires:  json-devel
BuildRequires:  libarchive-devel
BuildRequires:  libcpuid-devel
BuildRequires:  libcurl-devel
BuildRequires:  libseccomp-devel
BuildRequires:  libsodium-devel
BuildRequires:  lowdown
BuildRequires:  lowdown-devel
BuildRequires:  openssl-devel
BuildRequires:  sqlite-devel
BuildRequires:  xz-devel
BuildRequires:  chrpath
Obsoletes:      emacs-%{name} < %{version}-%{release}
Obsoletes:      emacs-%{name}-el < %{version}-%{release}

%description
Nix is a purely functional package manager. It allows multiple
versions of a package to be installed side-by-side, ensures that
dependency specifications are complete, supports atomic upgrades and
rollbacks, allows non-root users to install software, and has many
other features. It is the basis of the NixOS Linux distribution, but
it can be used equally well under other Unix systems.


%package        devel
Summary:        Development files for %{name}
Requires:       %{name}%{?_isa} = %{version}-%{release}

%description   devel
The %{name}-devel package contains libraries and header files for
developing applications that use %{name}.


%if %{with docs}
%package doc
Summary:        Documentation files for %{name}
BuildArch:      noarch

%description   doc
The %{name}-doc package contains documentation files for %{name}.
%endif


%prep
%autosetup -p1


%build
%undefine _hardened_build
autoreconf
# - unit tests disabled because of rapidcheck
# 2.20 uses --disable-unit-tests
# <2.20 uses --disable-tests
# - docs disabled: needs mdbook and avoid https://github.com/NixOS/nix/issues/10148
%configure --localstatedir=/nix/var --docdir=%{_defaultdocdir}/%{name}-doc-%{version} --disable-tests --disable-unit-tests %{!?with_docs:--disable-doc-gen}
make %{?_smp_mflags}


%install
make DESTDIR=%{buildroot} install

find %{buildroot} -name '*.la' -exec rm -f {} ';'

mkdir -p %{buildroot}/nix/store
mkdir -p %{buildroot}/nix/var/log/nix/drvs
# make per-user directories
for d in profiles gcroots;
do
  mkdir -p %{buildroot}/nix/var/nix/$d/per-user
  chmod 1777 %{buildroot}/nix/var/nix/$d/per-user
done
for i in db temproots ; do
  mkdir %{buildroot}/nix/var/nix/$i
done
touch %{buildroot}/nix/var/nix/gc.lock

# fix permission of nix profile
# (until this is fixed in the relevant Makefile)
chmod -x %{buildroot}%{_sysconfdir}/profile.d/nix.sh

rm %{buildroot}%{_sysconfdir}/profile.d/nix-daemon.sh

# Get rid of Upstart job.
rm -r %{buildroot}%{_sysconfdir}/init

# https://github.com/NixOS/nix/issues/10221
chrpath --delete %{buildroot}%{_bindir}/nix %{buildroot}%{_libdir}/libnixexpr.so %{buildroot}%{_libdir}/libnixmain.so %{buildroot}%{_libdir}/libnixstore.so %{buildroot}%{_libdir}/libnixfetchers.so %{buildroot}%{_libdir}/libnixcmd.so


%files
%{_bindir}/nix*
%{_libdir}/*.so
%{_prefix}/lib/systemd/system/nix-daemon.socket
%{_prefix}/lib/systemd/system/nix-daemon.service
%{_prefix}/lib/tmpfiles.d/nix-daemon.conf
%{_libexecdir}/nix
%if %{with docs}
%{_datadir}/nix
%{_mandir}/man1/*.1*
%{_mandir}/man5/*.5*
%{_mandir}/man8/*.8*
%endif
%config(noreplace) %{_sysconfdir}/profile.d/nix.sh
%config(noreplace) %{_sysconfdir}/profile.d/nix.fish
%config(noreplace) %{_sysconfdir}/profile.d/nix-daemon.fish
/nix
%{_datadir}/bash-completion/completions/nix
%{_datadir}/fish/vendor_completions.d/nix.fish
%{_datadir}/zsh/site-functions/*


%files devel
%{_includedir}/nix
%{_libdir}/pkgconfig/*.pc


%if %{with docs}
%files doc
%docdir %{_defaultdocdir}/%{name}-doc-%{version}
%{_defaultdocdir}/%{name}-doc-%{version}
%endif


%changelog
* Sun Mar 10 2024 Jens Petersen <petersen@redhat.com> - 2.19.4-1
- update to 2.19.4
- https://nixos.org/manual/nix/stable/release-notes/rl-2.19

* Fri Aug  4 2023 Jens Petersen <petersen@redhat.com> - 2.17.0-1
- update to 2.17.0

* Tue Jan  4 2022 Jens Petersen <petersen@redhat.com> - 2.3.16-1
- update to 2.3.16

* Thu Aug 13 2020 Jens Petersen <petersen@redhat.com> - 2.3.7-3
- drop nixbld group and users: only use single-user mode

* Fri Aug  7 2020 Jens Petersen <petersen@redhat.com> - 2.3.7-2
- upstream renamed nix-builder group to nixbld

* Thu Aug  6 2020 Jens Petersen <petersen@redhat.com> - 2.3.7-1
- update to 2.3.7
- drop erroring systemd units for now

* Tue Sep  4 2018 Jens Petersen <petersen@redhat.com> - 2.1-1
- update to 2.1
- https://nixos.org/nix/manual/#ssec-relnotes-2.1

* Wed Oct  5 2016 Jens Petersen <petersen@redhat.com> - 1.11.4-1
- no longer subpackage the elisp
- BR perl-devel

* Mon Feb 15 2016 Jens Petersen <petersen@redhat.com> - 1.11.2-2
- user/group fixes
- create and own /nix/store and ghost socket

* Sun Feb 14 2016 Jens Petersen <petersen@redhat.com> - 1.11.2-1
- cleanup upstream spec file
