DESCRIPTION = "Portable Unix shell commands for Node.js"
LICENSE = "BSD-3-Clause"
SUMMARY = "Portable Unix shell commands for Node.js"
SECTION = "devel/node"
HOMEPAGE = "https://github.com/arturadib/shelljs"
PR = "r1.0"

FILESEXTRAPATHS_prepend := "${THISDIR}/files:"
SRC_URI = 	"file://LICENSE \
                 file://shelljs-0.5.3.tar.bz2"

LIC_FILES_CHKSUM = "file://${THISDIR}/files/LICENSE;md5=984c31fdd47cf012f52739542dd857c4"

S = "${WORKDIR}/node_modules/"

do_install_append () {
    install -d ${D}/usr/lib/node_modules/shelljs
    install -d ${D}/usr/lib/node_modules/.bin
    cp -a -R ${S}/shelljs ${D}/usr/lib/node_modules
    install -m 644 ${S}/.bin/shjs ${D}/usr/lib/node_modules/.bin
}


FILES_${PN} = "/usr/lib"

RDEPENDS_${PN} = "nodejs"
