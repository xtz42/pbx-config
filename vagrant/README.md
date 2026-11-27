# Vagrant-стенд

Хост: Windows 11 / Linux / macOS (x86_64), VirtualBox 7.x, Vagrant ≥ 2.4.
Ansible на хост ставить не нужно: он ставится в каждую ВМ (`bootstrap.sh`,
ansible-core 2.21.6) и раскатывает `site.yml` на саму себя (`ansible_local`).

| ВМ | Память | voice-edge | voice-core | Что |
|----|--------|-----------|-----------|-----|
| `db` | 1 ГБ | — | 192.168.57.30 | PostgreSQL 18: базы `bii`, `kamailio` |
| `sbc` | 1 ГБ | 192.168.56.10 | 192.168.57.10 | Kamailio 6.1.5 + rtpengine mr13.5 |
| `pbx-bii-1` | 1,5 ГБ | — | 192.168.57.21 | Asterisk 22.12.0, тенант bii (ЦОД 1) |
| `provider` | 0,5 ГБ | 192.168.56.5 | — | SIPp («провайдер»), не стартует сам |

Хост в сетях VirtualBox получает 192.168.56.1 и 192.168.57.1;
адрес 192.168.56.1 — разрешённый источник звонков (софтфон на хосте).

## Порядок подготовки

Сначала `db`, затем `sbc` и `pbx-<тенант>-*`: Kamailio и Asterisk подключаются к базе.
Если ВМ уже были подготовлены до появления `db` — подготовьте `db`, затем
повторите подготовку `sbc` и `pbx-bii-1` (`vagrant provision <ВМ>` или `provision.sh`).

## Первый запуск

```powershell
git lfs install
git clone -b <ветка> <репозиторий> pbx-config
cd pbx-config\vagrant
vagrant up
```

Первый `vagrant up` долгий: ВМ собирают RPM rtpengine (~5 мин) и Asterisk
(~10–20 мин на 1 vCPU) из `rpm/*.spec`. Готовые пакеты кладутся в
`vagrant/cache/rpms/` и при `vagrant destroy` / `vagrant up` повторно не собираются.

## Повседневное

```powershell
vagrant provision sbc          # после правок ролей/шаблонов
vagrant ssh pbx-bii-1 -c "sudo asterisk -rvvv"
vagrant ssh sbc -c "sudo tcpdump -i any -nn -A -s0 udp port 5060"
vagrant halt                   # остановить, vagrant destroy -f — удалить ВМ
```

## Провижининг без Vagrant

Если Vagrant на хосте ведёт себя нестабильно, долгий шаг (Ansible) можно
запустить прямо внутри ВМ — результат тот же, что у `vagrant provision`:

```bash
sudo bash /vagrant/vagrant/provision.sh
```

Зайти в ВМ можно обычным ssh (Windows 11: встроенный OpenSSH), ключ создал Vagrant:

```powershell
ssh -i .vagrant\machines\sbc\virtualbox\private_key -p 2222 -o StrictHostKeyChecking=no vagrant@127.0.0.1
```

Порт для каждой ВМ — в `vagrant ssh-config <ВМ>` (у первой ВМ обычно 2222, у второй 2200).

## Если что-то пошло не так

- **Звонок получает `503 Service Unavailable`, в журнале Kamailio «нет доступных
  узлов Asterisk», `kamcmd dispatcher.list` показывает `FLAGS: IP`.** Asterisk
  поднялся позже Kamailio, и узел помечен неактивным; по ADR 0003 он вернётся сам
  после 10 минут успешных проверок (20 × 30 с). Вернуть сразу (на sbc):
  `sudo kamcmd dispatcher.set_state ap 1 sip:192.168.57.21:5060`.

- **`[BUG] Segmentation fault` в `C:/Program Files/Vagrant/embedded/...`** —
  падает встроенный в Vagrant Ruby, ещё до чтения Vagrantfile. Наблюдалось на
  Windows-хосте случайным образом; причина вне репозитория (см. NET-475, этап 2).
  Обходной путь: короткие команды Vagrant (`vagrant up <ВМ> --no-provision`)
  повторять, а провижининг выполнять изнутри ВМ (раздел выше).

- **Не монтируется /vagrant (vboxsf)** — в боксе нет Guest Additions нужной
  версии: `vagrant plugin install vagrant-vbguest`, затем `vagrant reload`.
- **`welcome.wav — указатель Git LFS`** — репозиторий клонирован без LFS:
  `git lfs install && git lfs pull`, затем `vagrant provision pbx-bii-1`.
- **Конфликт адресов 192.168.56/57.x** с другими host-only сетями VirtualBox —
  удалите лишние адаптеры в VirtualBox → «Инструменты» → «Сеть».
