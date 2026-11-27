# Настройка ОС (AlmaLinux 9)

Чеклист для test/prod. На Vagrant-стенде то же делает роль `base`
(`base_manage_os: true`); в test/prod роль `base` не запускается.

- [ ] AlmaLinux 9 (minimal), последние обновления: `dnf -y upgrade`
- [ ] Имя хоста по инвентарю (`sbc-1`, `pbx-<тенант>-1` …)
- [ ] Часовой пояс: `timedatectl set-timezone Asia/Almaty`
- [ ] NTP: `chronyd` включён, источники времени — внутренние NTP (плейсхолдер)
- [ ] Репозитории: `dnf -y install epel-release`, `dnf config-manager --set-enabled crb`
- [ ] SELinux — enforcing (не отключать)
- [ ] firewalld включён; зоны `voice-edge`, `voice-core` с подсетями-источниками;
      порты — по `docs/network.md`
- [ ] Пакеты из `docs/packages.md` (раздел «Базовые»)
- [ ] Учётная запись для Ansible с sudo, ключ SSH (плейсхолдер)
- [ ] Диск: отдельный раздел/том под `/var/spool/asterisk` на узлах Asterisk (записи разговоров)

Дополняется по мере этапов (PostgreSQL — этап 3, SMB для записей — этап 4).
