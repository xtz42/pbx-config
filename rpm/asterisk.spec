# RPM Asterisk 22 LTS для pbx-config (ADR 0001).
#
# Сборка (на AlmaLinux 9 с включёнными CRB и EPEL):
#   rpmdev-setuptree
#   spectool -g -R rpm/asterisk.spec          # исходники в ~/rpmbuild/SOURCES
#   cp rpm/asterisk.service ~/rpmbuild/SOURCES/
#   dnf builddep -y rpm/asterisk.spec
#   rpmbuild -bb rpm/asterisk.spec
# На Vagrant-стенде это делает роль asterisk (roles/asterisk/tasks/build.yml)
# и кэширует пакет в vagrant/cache/rpms/.
#
# Сборка не ходит в сеть: pjproject передаётся как Source1 через
# --with-externals-cache, звуки и MOH не скачиваются (их ставит роль sounds).

%global pjproject_version 2.17
%global _hardened_build 1
# Без LTO: компоновка с LTO требует много памяти, а на стенде RPM
# собирается на ВМ с 1,5 ГБ (roles/asterisk). Asterisk от LTO почти не выигрывает.
%global _lto_cflags %{nil}

Name:           asterisk
Version:        22.12.0
Release:        1.pbx%{?dist}
Summary:        Asterisk PBX (сборка pbx-config)
License:        GPL-2.0-only
URL:            https://www.asterisk.org
Source0:        https://downloads.asterisk.org/pub/telephony/asterisk/releases/asterisk-%{version}.tar.gz
Source1:        https://raw.githubusercontent.com/asterisk/third-party/master/pjproject/%{pjproject_version}/pjproject-%{pjproject_version}.tar.bz2
Source2:        asterisk.service

BuildRequires:  gcc
BuildRequires:  gcc-c++
BuildRequires:  make
BuildRequires:  patch
BuildRequires:  bzip2
BuildRequires:  binutils-devel
BuildRequires:  jansson-devel
BuildRequires:  libcurl-devel
BuildRequires:  libedit-devel
BuildRequires:  libsrtp-devel
BuildRequires:  libtool-ltdl-devel
BuildRequires:  libuuid-devel
BuildRequires:  libxml2-devel
BuildRequires:  ncurses-devel
BuildRequires:  openssl-devel
BuildRequires:  speexdsp-devel
BuildRequires:  sqlite-devel
BuildRequires:  systemd-devel
BuildRequires:  systemd-rpm-macros
BuildRequires:  unixODBC-devel

Requires(pre):  shadow-utils
%{?systemd_requires}

# Внутренние библиотеки Asterisk не должны «предоставляться» системе.
%global __provides_exclude_from ^%{_libdir}/asterisk/modules/.*$

%description
Asterisk 22 LTS, собранный для АТС колл-центра (pbx-config, NET-475):
PJSIP со встроенным pjproject, ODBC realtime, очереди, запись разговоров,
WebRTC (SRTP). Конфигурация в /etc/asterisk управляется Ansible.

%prep
%autosetup -n asterisk-%{version}

%build
%configure \
    --with-pjproject-bundled \
    --with-externals-cache=%{_sourcedir} \
    --with-jansson \
    --with-srtp \
    --with-unixodbc \
    --with-libcurl \
    --with-ssl \
    --without-spandsp \
    --without-x11

make menuselect.makeopts
menuselect/menuselect \
    --disable BUILD_NATIVE \
    --disable-category MENUSELECT_CORE_SOUNDS \
    --disable-category MENUSELECT_MOH \
    --disable-category MENUSELECT_EXTRA_SOUNDS \
    --disable chan_iax2 \
    --disable chan_unistim \
    --disable res_phoneprov \
    --disable res_pjsip_phoneprov_provider \
    --disable res_fax_spandsp \
    menuselect.makeopts

%make_build NOISY_BUILD=yes

%install
make install DESTDIR=%{buildroot} NOISY_BUILD=yes
install -D -m 0644 %{SOURCE2} %{buildroot}%{_unitdir}/asterisk.service
install -d -m 0750 %{buildroot}%{_sysconfdir}/asterisk
install -d -m 0750 %{buildroot}%{_localstatedir}/log/asterisk/cdr-csv
install -d -m 0750 %{buildroot}%{_localstatedir}/spool/asterisk/monitor
install -d -m 0750 %{buildroot}%{_localstatedir}/spool/asterisk/voicemail
install -d -m 0755 %{buildroot}%{_localstatedir}/lib/asterisk/sounds
install -d -m 0755 %{buildroot}%{_localstatedir}/lib/asterisk/moh
# Каталог миграций Alembic из исходников — нужен роли postgresql (этап 3).
install -d %{buildroot}%{_datadir}/asterisk
cp -a contrib/ast-db-manage %{buildroot}%{_datadir}/asterisk/ast-db-manage
find %{buildroot}%{_datadir}/asterisk/ast-db-manage -name '*.pyc' -delete
# Политика RPM EL9 запрещает неоднозначный «#!/usr/bin/env python».
sed -i '1s|^#!/usr/bin/env python$|#!/usr/bin/python3|' %{buildroot}%{_localstatedir}/lib/asterisk/scripts/*.py
# Демонстрационные и ненужные файлы.
rm -rf %{buildroot}%{_localstatedir}/lib/asterisk/phoneprov
rm -f  %{buildroot}%{_sbindir}/safe_asterisk %{buildroot}%{_mandir}/man8/safe_asterisk.8*

%pre
getent group asterisk >/dev/null || groupadd -r asterisk
getent passwd asterisk >/dev/null || \
    useradd -r -g asterisk -d %{_localstatedir}/lib/asterisk -s /sbin/nologin \
            -c "Asterisk PBX" asterisk
exit 0

%post
/sbin/ldconfig
%systemd_post asterisk.service

%preun
%systemd_preun asterisk.service

%postun
/sbin/ldconfig
%systemd_postun_with_restart asterisk.service

%files
%license COPYING LICENSE
%doc README.md CHANGES.md
%{_sbindir}/asterisk
%{_sbindir}/astcanary
%{_sbindir}/astdb2sqlite3
%{_sbindir}/astdb2bdb
%{_sbindir}/astgenkey
%{_sbindir}/astversion
%{_sbindir}/autosupport
%{_sbindir}/rasterisk
%{_libdir}/libasterisk*.so*
%{_libdir}/asterisk/
%{_unitdir}/asterisk.service
%{_mandir}/man8/*
%{_datadir}/asterisk/
%attr(0750,asterisk,asterisk) %dir %{_sysconfdir}/asterisk
%attr(-,asterisk,asterisk) %{_localstatedir}/lib/asterisk/
%attr(-,asterisk,asterisk) %{_localstatedir}/log/asterisk/
%attr(-,asterisk,asterisk) %{_localstatedir}/spool/asterisk/

%changelog
* Fri Nov 27 2026 pbx-config <noreply@example.test> - 22.12.0-1.pbx
- Первая сборка для pbx-config (NET-475).
