DESCRIPTION = "Node-RED is a tool for wiring together hardware devices, APIs and online services in new and interesting ways."
HOMEPAGE = "http://nodered.org"
LICENSE = "Apache-2.0"
SUMMARY ="Node-RED is a tool for wiring together hardware devices, APIs and online services in new and interesting ways."

PV = "0.13.4"

LIC_FILES_CHKSUM = "file://${THISDIR}/files/LICENSE;md5=2ee41112a44fe7014dce33e26468ba93"

def map_dest_cpu(target_arch, d):
    import re
    if   re.match('i.86$', target_arch): return 'node-red-0.13.4-i586.tar.bz2'
    elif re.match('x86_64$', target_arch): return 'node-red-0.13.4.tar.bz2'
    return target_arch

FILESEXTRAPATHS_prepend := "${THISDIR}/files:"
SRC_URI = 	"file://LICENSE \
                 file://${@map_dest_cpu(d.getVar('TARGET_ARCH', True), d)}"

S = "${WORKDIR}/node_modules/"

do_install() {
    install -d ${D}/usr/lib/node_modules/node-red
    cp -a -R ${S}/node-red ${D}/usr/lib/node_modules
    install -d ${D}/usr/lib/node_modules/.bin
    install -m 644 ${S}/.bin/node-red ${D}/usr/lib/node_modules/.bin
    install -m 644 ${S}/.bin/node-red-pi ${D}/usr/lib/node_modules/.bin
}

INSANE_SKIP_${PN} = "staticdev already-stripped debug-files"
FILES_${PN} = "/usr/lib/*"

RDEPENDS_${PN} += "python bash nodejs node-redis node-mongodb"
