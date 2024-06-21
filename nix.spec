%global nixbld_user nixbld-
%global nixbld_group nixbld

%bcond docs 0

Name:           nix
# 2.20+ currently fails to build: needs newer or patched gc
# https://github.com/NixOS/nix/issues/10147
# https://bugzilla.redhat.com/show_bug.cgi?id=2124760
Version:        2.19.4
Release:        3%{?dist}
Summary:        Nix software deployment system

License:        LGPLv2+
URL:            https://github.com/NixOS/nix
Source0:        https://github.com/NixOS/nix/archive/refs/tags/%{version}.tar.gz#/%{name}-%{version}.tar.gz
# https://nixos.org/manual/nix/unstable/installation/prerequisites-source
Source1:        nix.conf
Source2:        registry.json
Source3:        README.fedora

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
# for newer nix
#BuildRequires:  libgit2-devel
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
BuildRequires:  openssl-devel
BuildRequires:  sqlite-devel
BuildRequires:  xz-devel
BuildRequires:  chrpath
Requires:       %{name}-core = %{version}-%{release}
Requires:       %{name}-daemon = %{version}-%{release}
Obsoletes:      emacs-%{name} < %{version}-%{release}
Obsoletes:      emacs-%{name}-el < %{version}-%{release}

%description
Nix is a purely functional package manager. It allows multiple
versions of a package to be installed side-by-side, ensures that
dependency specifications are complete, supports atomic upgrades and
rollbacks, allows non-root users to install software, and has many
other features. It is the basis of the NixOS Linux distribution, but
it can be used equally well under other Unix systems.


%package        core
Summary:        nix tools

%description    core
This package provides the nix tools.


%package        daemon
Summary:        nix-daemon needed for multi-user
Requires:       %{name}-core%{?_isa} = %{version}-%{release}
Conflicts:      %{name}-singleuser < %{version}-%{release}

%description    daemon
This package provides the nix-daemon needed to support multi-user mode.
Though this package basically presume single-user.


%package        devel
Summary:        Development files for %{name}
Requires:       %{name}%{?_isa} = %{version}-%{release}

%description    devel
The %{name}-devel package contains libraries and header files for
developing applications that use %{name}.


%if %{with docs}
%package        doc
Summary:        Documentation files for %{name}
BuildArch:      noarch

%description    doc
The %{name}-doc package contains documentation files for %{name}.
%endif


%package        singleuser
Summary:        Single user /nix files
Requires:       %{name}-core%{?_isa} = %{version}-%{release}
Conflicts:      %{name}-daemon < %{version}-%{release}

%description    singleuser
This package provides the nix-daemon needed to support multi-user mode
and also the nixbld group and users.


%prep
%autosetup -p1

cp -p %{SOURCE3} .


%build
%undefine _hardened_build
autoreconf --install
# - unit tests disabled because of rapidcheck
# 2.20 uses --disable-unit-tests
# <2.20 uses --disable-tests
# - docs disabled: needs mdbook and avoid https://github.com/NixOS/nix/issues/10148
%configure --localstatedir=/nix/var --docdir=%{_defaultdocdir}/%{name}-doc-%{version} --disable-tests --disable-unit-tests %{!?with_docs:--disable-doc-gen}
%make_build


%install
%make_install

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

# Get rid of Upstart job.
rm -r %{buildroot}%{_sysconfdir}/init

# https://github.com/NixOS/nix/issues/10221
chrpath --delete %{buildroot}%{_bindir}/nix %{buildroot}%{_libdir}/libnixexpr.so %{buildroot}%{_libdir}/libnixmain.so %{buildroot}%{_libdir}/libnixstore.so %{buildroot}%{_libdir}/libnixfetchers.so %{buildroot}%{_libdir}/libnixcmd.so

# nix config
mkdir -p %{buildroot}/etc/nix
cp %{SOURCE1} %{SOURCE2} %{buildroot}/etc/nix/


%pre daemon
getent group %{nixbld_group} >/dev/null || groupadd -r %{nixbld_group}
for i in $(seq 10);
do
  getent passwd %{nixbld_user}$i >/dev/null || \
    useradd -r -g %{nixbld_group} -G %{nixbld_group} -d /var/empty \
      -s %{_sbindir}/nologin \
      -c "Nix build user $i" %{nixbld_user}$i
done


%files
%dir /nix
%dir /nix/var
%dir /nix/var/log
%dir /nix/var/log/nix


%files core
%license COPYING
%doc README.md README.fedora
%{_bindir}/nix*
%exclude %{_bindir}/nix-daemon
%{_libdir}/*.so
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
%attr(1775,root,%{nixbld_group}) /nix/store
%attr(1775,root,%{nixbld_group}) %dir /nix/var/log/nix/drvs
%dir %attr(775,root,%{nixbld_group}) /nix/var/nix
%ghost /nix/var/nix/daemon-socket/socket
%attr(775,root,%{nixbld_group}) /nix/var/nix/temproots
%attr(775,root,%{nixbld_group}) /nix/var/nix/db


%files devel
%{_includedir}/nix
%{_libdir}/pkgconfig/*.pc


%if %{with docs}
%files doc
%docdir %{_defaultdocdir}/%{name}-doc-%{version}
%{_defaultdocdir}/%{name}-doc-%{version}
%endif


%files singleuser
/nix


%changelog
* Fri Jun 21 2024 Jens Petersen <petersen@redhat.com> - 2.19.4-3
- add core and singleuser subpackages
- restore the nixbld group and users in the daemon subpackage

* Mon Jun 17 2024 Jens Petersen <petersen@redhat.com> - 2.19.4-2
- subpackage nix-daemon
- add README.fedora for setup
- add /etc/nix files copied from multi-user copr

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
