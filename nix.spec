%global nixbld_group nixbld

%bcond docs 0

Name:           nix
Version:        2.28.3
Release:        1%{?dist}
Summary:        A purely functional package manager

License:        LGPL-2.1-or-later
URL:            https://github.com/NixOS/nix
Source0:        https://github.com/NixOS/nix/archive/refs/tags/%{version}.tar.gz#/%{name}-%{version}.tar.gz
Source1:        nix.conf
Source2:        registry.json
Source3:        README.md
Source4:        nix.sysusers
Patch0:         nix-perl-vendorarch.patch

# https://nixos.org/manual/nix/unstable/installation/prerequisites-source
BuildRequires:  bison
BuildRequires:  blake3-devel
BuildRequires:  bzip2-devel
BuildRequires:  boost-devel
BuildRequires:  brotli-devel
BuildRequires:  cmake
BuildRequires:  editline-devel
BuildRequires:  flex
BuildRequires:  gc-devel
BuildRequires:  gcc-c++
BuildRequires:  gmock-devel
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
BuildRequires:  rapidcheck-devel
BuildRequires:  sqlite-devel
BuildRequires:  xz-devel
BuildRequires:  chrpath
BuildRequires:  systemd-rpm-macros
BuildRequires:  toml11-devel
%{?sysusers_requires_compat}
Requires:       %{name}-core = %{version}-%{release}
Obsoletes:      emacs-%{name} < %{version}-%{release}
Obsoletes:      emacs-%{name}-el < %{version}-%{release}
Obsoletes:      %{name}-daemon < %{version}-%{release}
Conflicts:      %{name}-singleuser <= %{version}-%{release}

%description
Nix is a purely functional package manager. It allows multiple
versions of a package to be installed side-by-side, ensures that
dependency specifications are complete, supports atomic upgrades and
rollbacks, allows non-root users to install software, and has many
other features. It is the basis of the NixOS Linux distribution, but
it can be used equally well under other Unix systems.

The package installs nix in the recommended multiuser mode with a daemon process.
If you want single-user mode nix, install nix-singleuser instead.


%package        core
Summary:        nix tools

%description    core
This package provides the nix tools.


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
Summary:        Single user mode nix
Requires:       %{name}-core%{?_isa} = %{version}-%{release}
Conflicts:      %{name} <= %{version}-%{release}

%description    singleuser
This package sets up a single-user mode nix.

If you want multi-user mode install the main nix package instead.


%prep
%autosetup -p1

cp -p %{SOURCE3} README.fedora.md


%build
%meson --sysconf=/etc \
%ifnarch x86_64
  -Dlibutil:cpuid=disabled
%else
%{nil}
%endif
%meson_build


%install
%meson_install

mkdir -p %{buildroot}%{_sysconfdir}/profile.d/
mv %{buildroot}/usr/etc/profile.d/* %{buildroot}%{_sysconfdir}/profile.d/

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

# https://github.com/NixOS/nix/issues/10221
chrpath --delete %{buildroot}%{_bindir}/nix %{buildroot}%{_libdir}/libnixexpr.so %{buildroot}%{_libdir}/libnixmain.so %{buildroot}%{_libdir}/libnixstore.so %{buildroot}%{_libdir}/libnixfetchers.so %{buildroot}%{_libdir}/libnixcmd.so

# nix config
mkdir -p %{buildroot}/etc/nix
cp %{SOURCE1} %{SOURCE2} %{buildroot}/etc/nix/

install -p -D -m 0644 %{SOURCE4} %{buildroot}%{_sysusersdir}/nix.conf


%pre
%sysusers_create_compat %{SOURCE4}


%post singleuser
if [ "$1" = 1 ]; then
mkdir -p /nix/store
mkdir -p /nix/var/log/nix/drvs
mkdir -p /nix/var/nix
mkdir -p /nix/var/nix/temproots
mkdir -p /nix/var/nix/db

echo 'Run "sudo chown -R $USER /nix/*" to complete single-user setup'
fi


%files
%{_bindir}/nix-daemon
%{_sysconfdir}/profile.d/nix-daemon.*sh
%{_prefix}/lib/systemd/system/nix-daemon.*
%{_prefix}/lib/tmpfiles.d/nix-daemon.conf
%attr(1775,root,%{nixbld_group}) /nix/store
%dir /nix/var
%dir /nix/var/log
%dir /nix/var/log/nix
%attr(1775,root,%{nixbld_group}) %dir /nix/var/log/nix/drvs
%dir %attr(775,root,%{nixbld_group}) /nix/var/nix
%ghost /nix/var/nix/daemon-socket/socket
%attr(775,root,%{nixbld_group}) /nix/var/nix/temproots
%attr(775,root,%{nixbld_group}) /nix/var/nix/db
%attr(664,root,%{nixbld_group}) /nix/var/nix/gc.lock
%{_sysusersdir}/nix.conf


%files core
%license COPYING
%doc README.md README.fedora.md
%{_bindir}/nix*
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
%dir /nix
%{_datadir}/bash-completion/completions/nix
%{_datadir}/fish/vendor_completions.d/nix.fish
%{_datadir}/zsh/site-functions/*


%files devel
%{_includedir}/nix
%{_includedir}/nix_api_*.h
%{_libdir}/pkgconfig/*.pc


%if %{with docs}
%files doc
%docdir %{_defaultdocdir}/%{name}-doc-%{version}
%{_defaultdocdir}/%{name}-doc-%{version}
%endif


%files singleuser


%changelog
* Sat May 03 2025 Jens Petersen <petersen@redhat.com> - 2.19.7-1
- update to 2.19.7

* Mon Jun 24 2024 Jens Petersen <petersen@redhat.com> - 2.19.4-5
- remove the sysusers GECOS field from the nixbld group (@FrostyX)

* Sun Jun 23 2024 Jens Petersen <petersen@redhat.com> - 2.19.4-4
- move daemon to base package
- use sysusers.d to define builder group and users
- singleusers now sets up its dirs

* Sat Jun 22 2024 Jens Petersen <petersen@redhat.com> - 2.19.4-3
- add core and singleuser subpackages
- restore the nixbld group and users for multiuser mode

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
