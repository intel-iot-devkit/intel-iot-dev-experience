DESCRIPTION = "Simple XML to JavaScript object converter."
LICENSE = "MIT"
SUMMARY = "Simple XML to JavaScript object converter."
SECTION = "devel/node"
HOMEPAGE = "github.com/Leonidas-from-XIV/node-xml2js"
PR = "r1.0"
FILESEXTRAPATHS_prepend := "${THISDIR}/files:"
SRC_URI = 	"file://LICENSE \
                 file://xml2js-0.4.16.tar.bz2"

LIC_FILES_CHKSUM = "file://${THISDIR}/files/LICENSE;md5=ea41c030b7b22840a196d85eb876f5e8"

S = "${WORKDIR}/node_modules/"

do_install_append () {
    install -d ${D}/usr/lib/node_modules/xml2js
    cp -a -R ${S}/xml2js ${D}/usr/lib/node_modules
}

FILES_${PN} = "/usr/lib"

RDEPENDS_${PN} = "nodejs"
