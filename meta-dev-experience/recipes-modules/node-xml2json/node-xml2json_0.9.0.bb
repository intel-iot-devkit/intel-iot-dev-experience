DESCRIPTION = "Converts xml to json and vice-versa, using node-expat."
LICENSE = "MIT"
SUMMARY = "Converts xml to json and vice-versa, using node-expat."
SECTION = "devel/node"
HOMEPAGE = "github.com/buglabs/node-xml2json"
PR = "r1.0"
def map_dest_cpu(target_arch, d):
    import re
    if   re.match('i.86$', target_arch): return 'xml2json-0.9.0-i586.tar.bz2'
    elif re.match('x86_64$', target_arch): return 'xml2json-0.9.0.tar.bz2'
    return target_arch

FILESEXTRAPATHS_prepend := "${THISDIR}/files:"
SRC_URI = 	"file://LICENSE \
                 file://${@map_dest_cpu(d.getVar('TARGET_ARCH', True), d)}"

LIC_FILES_CHKSUM = "file://${THISDIR}/files/LICENSE;md5=ea41c030b7b22840a196d85eb876f5e8"

S = "${WORKDIR}/node_modules/"

do_install_append () {
    install -d ${D}/usr/lib/node_modules/xml2json
    install -d ${D}/usr/lib/node_modules/.bin
    cp -a -R ${S}/xml2json ${D}/usr/lib/node_modules
    install -m 644 ${S}/.bin/xml2json ${D}/usr/lib/node_modules/.bin
}
INSANE_SKIP_${PN} = "staticdev already-stripped"
FILES_${PN} = "/usr/lib"
FILES_${PN}-dbg = "/usr/lib/node_modules/xml2json/node_modules/node-expat/build/Release/.debug \
                /usr/lib/node_modules/xml2json/node_modules/node-expat/build/Release/obj.target/.debug"

RDEPENDS_${PN} = "nodejs"
