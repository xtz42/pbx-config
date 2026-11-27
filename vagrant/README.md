# Vagrant-стенд

Хост: Windows 11 / Linux / macOS (x86_64), VirtualBox 7.x, Vagrant ≥ 2.4.
Ansible на хост ставить не нужно: он ставится в каждую ВМ (`bootstrap.sh`,
ansible-core 2.21.6) и раскатывает `site.yml` на саму себя (`ansible_local`).

| ВМ | Память | voice-edge | voice-core | Что |
|----|--------|-----------|-----------|-----|
| `sbc` | 1 ГБ | 192.168.56.10 | 192.168.57.10 | Kamailio 6.1.5 + rtpengine mr13.5 |
| `pbx-bii-1` | 1,5 ГБ | — | 192.168.57.21 | Asterisk 22.12.0, тенант bii (ЦОД 1) |
| `provider` | 0,5 ГБ | 192.168.56.5 | — | SIPp («провайдер»), не стартует сам |

Хост в сетях VirtualBox получает 192.168.56.1 и 192.168.57.1;
адрес 192.168.56.1 — разрешённый источник звонков (софтфон на хосте).

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
vagrant ssh sbc -c "sudo sngrep"
vagrant halt                   # остановить, vagrant destroy -f — удалить ВМ
```

## Если что-то пошло не так

- **Не монтируется /vagrant (vboxsf)** — в боксе нет Guest Additions нужной
  версии: `vagrant plugin install vagrant-vbguest`, затем `vagrant reload`.
- **`welcome.wav — указатель Git LFS`** — репозиторий клонирован без LFS:
  `git lfs install && git lfs pull`, затем `vagrant provision pbx-bii-1`.
- **Конфликт адресов 192.168.56/57.x** с другими host-only сетями VirtualBox —
  удалите лишние адаптеры в VirtualBox → «Инструменты» → «Сеть».
