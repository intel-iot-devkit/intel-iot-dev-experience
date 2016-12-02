DESCRIPTION = "Configures the global http and https agents to use an upstream HTTP proxy."
LICENSE = "BSD"
SUMMARY = "Global HTTP & HTTPS tunneling"
SECTION = "devel/node"
HOMEPAGE = "github.com/goinstant/global-tunnel"
PR = "r1.0"

LIC_FILES_CHKSUM = "file://${THISDIR}/files/LICENSE;md5=effafd1e58e518742380952debd9b819"

FILESEXTRAPATHS_prepend := "${THISDIR}/files:"
SRC_URI = 	"file://LICENSE \
                 file://global-tunnel-1.2.0.tar.bz2"

S = "${WORKDIR}/node_modules/"

do_install_append () {
    install -d ${D}/usr/lib/node_modules/global-tunnel
    cp -a -R ${S}/global-tunnel ${D}/usr/lib/node_modules
}

FILES_${PN} = "/usr/lib"

RDEPENDS_${PN} = "nodejs"

