SUMMARY = "Package Repository Web Interface for gateway"

DESCRIPTION = "Provides website and scripts needed for the Intel Package Repository Web Interface"

LICENSE = "GPLv2"

SECTION = "webconsole"

PR = "r1.0"

SRC_URI = "file://pkg_repo_gui"

S = "${WORKDIR}/pkg_repo_gui"

LIC_FILES_CHKSUM = "file://LICENSE.txt;md5=751419260aa954499f7abaabaa882bbe"

FILESEXTRAPATHS_prepend := ""

inherit systemd

PACKAGES = "${PN}"


do_compile() {
  echo "VERSION=${PV}" > ${WORKDIR}/pkg_repo_gui/www-repo-gui/python/version
  echo "DATE=`date -R`" >> ${WORKDIR}/pkg_repo_gui/www-repo-gui/python/version
}

do_install() {
install -d ${D}${localstatedir}/www
cp -R ${S}/www-repo-gui ${D}${localstatedir}/www
install -d ${D}${systemd_unitdir}/system
install -m 0644 ${WORKDIR}/pkg_repo_gui/iot-dev-hub.service ${D}${systemd_unitdir}/system
install -m 0644 ${WORKDIR}/pkg_repo_gui/iot-dev-hub-update.service ${D}${systemd_unitdir}/system
cp ${WORKDIR}/pkg_repo_gui/LICENSE.txt ${D}${localstatedir}/www/www-repo-gui
}

SYSTEMD_SERVICE_${PN} = "iot-dev-hub.service"

FILES_${PN} += " \
        /lib/systemd/system  \
    ${D}${localstatedir}/www/www-repo-gui \
"
CONFFILES = "/var/www/www-repo-gui/proxy_env /var/www/www-repo-gui/python/developer_hub_config /var/www/www-repo-gui/python/repo_tracking"

RDEPENDS_${PN} = "cherrypy pexpect simplejson routes dh-rfs python-netifaces python-lxml python-netifaces"


