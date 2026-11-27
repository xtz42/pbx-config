#!/usr/bin/env bash
# Сборка SIPp из исходников на AlmaLinux 9 (в EPEL 9 пакета нет).
# Используется только на стенде: ВМ provider (vagrant up provider).
set -euo pipefail

SIPP_TAG="v3.7.9"
SIPP_COMMIT="16aff5f67fd776d0bf79a895930c53b72e98ccfc"
SRC=/usr/local/src/sipp

if (/usr/local/bin/sipp -v 2>&1 || true) | grep -q "${SIPP_TAG}"; then
  echo ">>> SIPp ${SIPP_TAG} уже установлен"; exit 0
fi

dnf -y -q install epel-release dnf-plugins-core
dnf config-manager --set-enabled crb
dnf -y -q install git gcc-c++ cmake make ncurses-devel openssl-devel libpcap-devel gsl-devel pugixml-devel

rm -rf "${SRC}"
git clone -q --depth 1 --branch "${SIPP_TAG}" https://github.com/SIPp/sipp "${SRC}"
actual="$(git -C "${SRC}" rev-parse HEAD)"
if [ "${actual}" != "${SIPP_COMMIT}" ]; then
  echo "Тег ${SIPP_TAG} указывает на ${actual}, ожидался ${SIPP_COMMIT}" >&2; exit 1
fi

cmake -S "${SRC}" -B "${SRC}/build" -DUSE_SSL=1 -DUSE_PCAP=1 -DUSE_GSL=1 -DCMAKE_BUILD_TYPE=Release
make -C "${SRC}/build" -j"$(nproc)"
install -m 0755 "${SRC}/build/sipp" /usr/local/bin/sipp
/usr/local/bin/sipp -v 2>&1 | grep SIPp || true
