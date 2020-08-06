%global nixbld_user nix-builder-
%global nixbld_group nix-builders

Name:           nix
Version:        2.3.7
Release:        1%{?dist}
Summary:        Nix software deployment system

License:        LGPLv2+
URL:            https://nixos.org/nix
Source0:        https://nixos.org/releases/nix/nix-%{version}/nix-%{version}.tar.xz
# https://github.com/NixOS/nix/issues/3906
Patch0:         nix-2.3.7-GC.patch
BuildRequires:  bzip2-devel
BuildRequires:  boost-devel
BuildRequires:  brotli-devel
BuildRequires:  editline-devel
BuildRequires:  gc-devel
BuildRequires:  gcc-c++
BuildRequires:  libcurl-devel
BuildRequires:  libseccomp-devel
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


%package doc
Summary:        Documentation files for %{name}
BuildArch:      noarch

%description   doc
The %{name}-doc package contains documentation files for %{name}.


%prep
%autosetup -p1


%build
%undefine _hardened_build
%configure --localstatedir=/nix/var --docdir=%{_defaultdocdir}/%{name}-doc-%{version}
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

# Get rid of Upstart job.
rm -r %{buildroot}%{_sysconfdir}/init

chrpath --delete %{buildroot}%{_bindir}/nix %{buildroot}%{_libdir}/libnixexpr.so %{buildroot}%{_libdir}/libnixmain.so %{buildroot}%{_libdir}/libnixstore.so


%pre
getent group %{nixbld_group} >/dev/null || groupadd -r %{nixbld_group}
for i in $(seq 10);
do
  getent passwd %{nixbld_user}$i >/dev/null || \
    useradd -r -g %{nixbld_group} -G %{nixbld_group} -d /var/empty \
      -s %{_sbindir}/nologin \
      -c "Nix build user $i" %{nixbld_user}$i
done


%post
# Enable and start Nix worker
#systemctl enable nix-daemon.socket nix-daemon.service
#systemctl start  nix-daemon.service


%files
%{_bindir}/nix*
%{_libdir}/*.so
%{_prefix}/lib/systemd/system/nix-daemon.socket
%{_prefix}/lib/systemd/system/nix-daemon.service
%{_libexecdir}/nix
%{_datadir}/nix
%{_mandir}/man1/*.1*
%{_mandir}/man5/*.5*
%{_mandir}/man8/*.8*
%config(noreplace) %{_sysconfdir}/profile.d/nix.sh
%config(noreplace) %{_sysconfdir}/profile.d/nix-daemon.sh
%dir /nix
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


%files devel
%{_includedir}/nix
%{_prefix}/lib/pkgconfig/*.pc


%files doc
%docdir %{_defaultdocdir}/%{name}-doc-%{version}
%{_defaultdocdir}/%{name}-doc-%{version}


%changelog
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
