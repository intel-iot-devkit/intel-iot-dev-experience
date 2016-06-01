DESCRIPTION = "Developer Hub Restore Factory System"
PR = "r1.0"
LICENSE = "GPLv2"
SECTION = "util"

DEPENDS += "wr-iot-agent"

FILESEXTRAPATHS_prepend := "${THISDIR}/files:"
SRC_URI = "file://dh-rfs.c"

LIC_FILES_CHKSUM = "file://${THISDIR}/files/dh-rfs.c;md5=62867122c604605e925dc9ea2e3286a3"

do_compile() {
    ${CC} ${CFLAGS} ${LDFLAGS} ${WORKDIR}/dh-rfs.c -o dh-rfs -lwraclient -lrt -lpthread
}

do_install() {
    install -m 0755 -d ${D}${bindir}
    install -m 0755 ${S}/dh-rfs ${D}${bindir}
}
