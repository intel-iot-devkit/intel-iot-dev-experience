DESCRIPTION = "Mosquitto is an open source implementation of a server for \
			   version 3.1 of the MQTT protocol."

LICENSE = "BSD-4-Clause"
DEPENDS = "openssl util-linux"


PR = "r0"

inherit autotools-brokensep systemd useradd 

SYSTEMD_SERVICE_${PN} = "mosquitto.service"
 
CFLAGS += "-L${STAGING_LIBDIR}"

EXTRA_OEMAKE += 'STRIP="echo" prefix="/usr"'

SRC_URI = "file://${BPN}-${PV}.tar.gz \
           file://mosquitto.service \
           file://mosquitto.conf"

FILES_${PN} += "${libdir}/python2.*/*"

do_compile_prepend() {
   cd ${S}; sed -i "s/WITH_WEBSOCKETS:=no/WITH_WEBSOCKETS:=yes/g" config.mk
   cd ${S}; sed -i "s/WITH_EC:=yes/WITH_EC:=no/g" config.mk
}

do_install_append() {
    install -d -m 0755 ${D}${sysconfdir}/init.d
    install -d -m 0755 ${D}${sysconfdir}/mosquitto/

    install -m 0755 ${WORKDIR}/mosquitto.conf ${D}${sysconfdir}/mosquitto/

	mv ${D}/usr/lib ${D}/usr/${baselib} || true
	install -d ${D}${systemd_unitdir}/system
	install -m 0644 ${WORKDIR}/mosquitto.service ${D}${systemd_unitdir}/system
}


# useradd and user group for mosquitto
USERADD_PACKAGES = "${PN}"
M_USER = "mosquitto"
M_GROUP = "mosquitto"
GROUPADD_PARAM_${PN} = "--system ${M_GROUP}"
USERADD_PARAM_${PN} = "--system -s /bin/bash -g ${M_GROUP} ${M_USER}"
M_OWNER_AND_GROUP = "-o ${M_USER} -g ${M_GROUP}"


SRC_URI[md5sum] = "46008028563eb750c6aa93281ab2e181"
SRC_URI[sha256sum] = "75a8b051c7859a2426ffc15bf45b44f79c8288395a325d791ba54e5df9af58a8"

DEPENDS = "c-ares libwebsockets util-linux"
RDEPENDS_${PN} = "c-ares libwebsockets"
LIC_FILES_CHKSUM = "file://LICENSE.txt;md5=62ddc846179e908dc0c8efec4a42ef20"
