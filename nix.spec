%global nixbld_user nix-builder-
%global nixbld_group nix-builders

Name:           nix
Version:        1.11.4
Release:        1%{?dist}
Summary:        Nix software deployment system

License:        LGPLv2+
URL:            http://nixos.org/nix
Source0:        http://nixos.org/releases/nix/nix-%{version}/nix-%{version}.tar.xz

BuildRequires:  bzip2-devel
BuildRequires:  libcurl-devel
BuildRequires:  openssl-devel
BuildRequires:  perl-devel
BuildRequires:  perl(DBD::SQLite)
BuildRequires:  perl(ExtUtils::ParseXS)
BuildRequires:  perl(WWW::Curl)
BuildRequires:  sqlite-devel
BuildRequires:  xz-devel
BuildRequires:  emacs
Requires:       emacs-filesystem >= %{_emacs_version}
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
%setup -q
# Install Perl modules to vendor_perl
# configure.ac need to be changed to make this global; however, this will
# also affect NixOS. Use discretion.
%{__sed} -i 's|perl5/site_perl/$perlversion/$perlarchname|perl5/vendor_perl|' \
  configure


%build
%undefine _hardened_build
%configure --localstatedir=/nix/var --docdir=%{_defaultdocdir}/%{name}-doc-%{version}
make %{?_smp_mflags}
%{_emacs_bytecompile} misc/emacs/nix-mode.el


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

# Copy the byte-compiled mode file by hand
cp -p misc/emacs/nix-mode.elc %{buildroot}%{_emacs_sitelispdir}/

# Get rid of Upstart job.
rm -r %{buildroot}%{_sysconfdir}/init


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
systemctl enable nix-daemon.socket nix-daemon.service
systemctl start  nix-daemon.service


%files
%{_bindir}/nix-*
%{_libdir}/*.so
%{perl_vendorarch}/*
%exclude %dir %{perl_vendorarch}/auto/
%{_prefix}/libexec/*
%{_prefix}/lib/systemd/system/nix-daemon.socket
%{_prefix}/lib/systemd/system/nix-daemon.service
%{_datadir}/emacs/site-lisp/nix-mode.el
%{_datadir}/nix
%{_mandir}/man1/*.1*
%{_mandir}/man5/*.5*
%{_mandir}/man8/*.8*
%config(noreplace) %{_sysconfdir}/profile.d/nix.sh
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
%{_emacs_sitelispdir}/*.el
%{_emacs_sitelispdir}/*.elc


%files devel
%{_includedir}/nix
%{_prefix}/lib/pkgconfig/*.pc


%files doc
%docdir %{_defaultdocdir}/%{name}-doc-%{version}
%{_defaultdocdir}/%{name}-doc-%{version}


%changelog
* Wed Oct  5 2016 Jens Petersen <petersen@redhat.com> - 1.11.4-1
- no longer subpackage the elisp
- BR perl-devel

* Mon Feb 15 2016 Jens Petersen <petersen@redhat.com> - 1.11.2-2
- user/group fixes
- create and own /nix/store and ghost socket

* Sun Feb 14 2016 Jens Petersen <petersen@redhat.com> - 1.11.2-1
- cleanup upstream spec file
