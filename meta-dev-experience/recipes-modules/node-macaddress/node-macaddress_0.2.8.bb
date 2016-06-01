DESCRIPTION = "Node-macaddress"
LICENSE = "MIT"
Summary = "node-macaddress"
SECTION = "devel/node"
HOMEPAGE = "github.com/scravy/node-macaddress"
PR = "r1.0"

LIC_FILES_CHKSUM = "file://${THISDIR}/files/README.md;md5=81d78f7e7b411b76ab2769abddc50127"

FILESEXTRAPATHS_prepend := "${THISDIR}/files:"
SRC_URI = 	"file://README.md \
                 file://macaddress-0.2.8.tar.bz2"

S = "${WORKDIR}/node_modules/"

do_install_append () {
    install -d ${D}/usr/lib/node_modules/macaddress
    cp -a -R ${S}/macaddress ${D}/usr/lib/node_modules
}
FILES_${PN} = "/usr/lib/*"

RDEPENDS_${PN} = "nodejs"
