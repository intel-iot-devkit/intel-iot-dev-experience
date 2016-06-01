DESCRIPTION = "Small footprint URL parser that works seamlessly across Node.js and browser environments."
LICENSE = "MIT"
Summary = "Small footprint URL parser that works seamlessly across Node.js and browser environments."
SECTION = "devel/node"
HOMEPAGE = "https://github.com/unshiftio/url-parse"
PR = "r1.0"
LIC_FILES_CHKSUM = "file://${THISDIR}/files/LICENSE;md5=4310a14e1d911cc6e4b5a34dbcbeaddd"

FILESEXTRAPATHS_prepend := "${THISDIR}/files:"
SRC_URI = 	"file://LICENSE \
                 file://node-url-parse-1.0.5.tar.bz2"

S = "${WORKDIR}/node_modules/"

do_install_append () {
    install -d ${D}/usr/lib/node_modules/url-parse
    cp -a -R ${S}/url-parse ${D}/usr/lib/node_modules
}

FILES_${PN} = "/usr/lib/*"

RDEPENDS_${PN} = "nodejs"
