# RPM rtpengine для SBC pbx-config (ADR 0001).
#
# Основан на официальном el/rtpengine.spec из репозитория sipwise/rtpengine
# (тег mr13.5.1.33, ветка долгой поддержки mr13.5). Отличия от официального:
#   - без транскодирования (make with_transcoding=no): не нужен ffmpeg,
#     которого нет в AlmaLinux 9/EPEL; WebRTC-браузеры и провайдер
#     работают с G.711 (PCMA/PCMU), Asterisk предлагает те же кодеки;
#   - без модуля ядра (подпакеты kernel/dkms) — на стенде и для начала
#     в проде пересылка медиа в userspace (table = -1);
#   - без recording-daemon и perftest (требуют транскодирования);
#   - утилиты rtpengine-ctl/rtpengine-ng-client — в основном пакете;
#   - патч rtpengine-optional-ffmpeg.patch: проверка ffmpeg необязательна.
#
# Сборка (AlmaLinux 9, включены CRB и EPEL):
#   spectool -g -R rpm/rtpengine.spec && cp rpm/rtpengine-*.patch ~/rpmbuild/SOURCES/
#   dnf builddep -y rpm/rtpengine.spec
#   rpmbuild -bb rpm/rtpengine.spec
# На Vagrant-стенде это делает роль rtpengine и кэширует RPM в vagrant/cache/rpms/.

%global upstream_tag mr%{version}

Name:           ngcp-rtpengine
Version:        13.5.1.33
Release:        1.pbx%{?dist}
Summary:        Sipwise rtpengine — медиа-прокси для Kamailio (userspace, без транскодирования)
License:        GPL-3.0-only
URL:            https://github.com/sipwise/rtpengine
Source0:        https://github.com/sipwise/rtpengine/archive/refs/tags/%{upstream_tag}.tar.gz#/rtpengine-%{upstream_tag}.tar.gz
# Скрипт сборки mr13.5 безусловно требует pkg-config ffmpeg (libav*),
# хотя без транскодирования они не используются.
Patch0:         rtpengine-optional-ffmpeg.patch

BuildRequires:  gcc
BuildRequires:  make
BuildRequires:  pkgconfig
BuildRequires:  redhat-rpm-config
BuildRequires:  gperf
BuildRequires:  pandoc
BuildRequires:  perl-IPC-Cmd
BuildRequires:  perl-podlators
BuildRequires:  libatomic
BuildRequires:  glib2-devel
BuildRequires:  json-glib-devel
BuildRequires:  libcurl-devel
BuildRequires:  libevent-devel
BuildRequires:  libpcap-devel
BuildRequires:  openssl-devel
BuildRequires:  pcre2-devel
BuildRequires:  zlib-devel
BuildRequires:  hiredis-devel
BuildRequires:  mosquitto-devel
BuildRequires:  libjwt-devel
BuildRequires:  liburing-devel
BuildRequires:  systemd-devel
BuildRequires:  ncurses-devel
BuildRequires:  mariadb-connector-c-devel
BuildRequires:  pkgconfig(opus)
BuildRequires:  pkgconfig(spandsp)
BuildRequires:  pkgconfig(libwebsockets)
BuildRequires:  pkgconfig(libmnl)
BuildRequires:  pkgconfig(libnftnl)
BuildRequires:  pkgconfig(libiptc)

Requires(pre):  shadow-utils
Requires:       perl-Config-Tiny
Requires:       nc
Provides:       rtpengine = %{version}-%{release}

%description
Sipwise rtpengine — прокси RTP и других медиапотоков для Kamailio:
мост WebRTC (ICE, DTLS-SRTP) ↔ RTP, разделение внешнего и внутреннего
интерфейсов. Сборка pbx-config: только userspace, без транскодирования.

%prep
%autosetup -p1 -n rtpengine-%{upstream_tag}

%build
%{set_build_flags}
RTPENGINE_VERSION="\"%{version}-%{release}\"" %make_build with_transcoding=no all

%install
%{set_build_flags}
RTPENGINE_VERSION="\"%{version}-%{release}\"" make DESTDIR=%{buildroot} with_transcoding=no install
install -D -p -m 0644 el/rtpengine.service   %{buildroot}%{_unitdir}/rtpengine.service
install -D -p -m 0644 el/rtpengine.sysconfig %{buildroot}%{_sysconfdir}/sysconfig/rtpengine
install -D -p -m 0644 etc/rtpengine.conf     %{buildroot}%{_sysconfdir}/rtpengine/rtpengine.conf
install -d %{buildroot}%{_sharedstatedir}/%{name}
install -d %{buildroot}%{_var}/spool/rtpengine

%pre
getent group %{name} >/dev/null || groupadd -r %{name}
getent passwd %{name} >/dev/null || useradd -r -g %{name} \
    -s /sbin/nologin -c "%{name} daemon" -d %{_sharedstatedir}/%{name} %{name}
exit 0

%post
%systemd_post rtpengine.service

%preun
%systemd_preun rtpengine.service

%postun
%systemd_postun_with_restart rtpengine.service

%files
%license LICENSE
%doc README.md debian/changelog
%{_bindir}/rtpengine
%{_bindir}/rtpengine-ctl
%{_bindir}/rtpengine-ng-client
%{_libexecdir}/rtpengine/
%{_unitdir}/rtpengine.service
%config(noreplace) %{_sysconfdir}/sysconfig/rtpengine
%config(noreplace) %{_sysconfdir}/rtpengine/rtpengine.conf
%dir %attr(0750,%{name},%{name}) %{_sharedstatedir}/%{name}
%dir %attr(0750,%{name},%{name}) %{_var}/spool/rtpengine
%{_mandir}/man8/rtpengine.8*
%{_mandir}/man1/rtpengine-ctl.1*
%{_mandir}/man1/rtpengine-ng-client.1*

%changelog
* Fri Nov 27 2026 pbx-config <noreply@example.test> - 13.5.1.33-1.pbx
- Сборка для pbx-config (NET-475) на основе официального el/rtpengine.spec.
