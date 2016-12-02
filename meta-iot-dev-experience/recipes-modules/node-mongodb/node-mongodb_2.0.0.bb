DESCRIPTION = "The MongoDB driver is the high level part of the 2.0 or higher MongoDB driver and is meant for end users.."
LICENSE = "Apache-2.0"
SUMMARY = "Mongodb plugin for NodeJS"
SECTION = "devel/node"
HOMEPAGE = "https://github.com/mongodb/node-mongodb-native"
PR = "r1.0"

LIC_FILES_CHKSUM = "file://${THISDIR}/files/LICENSE;md5=6c4db32a2fa8717faffa1d4f10136f47"

FILESEXTRAPATHS_prepend := "${THISDIR}/files:"
SRC_URI = 	"file://LICENSE \
                 file://mongodb-2.0.39.tar.bz2"

S = "${WORKDIR}/node_modules/"

do_install () {
    install -d ${D}/usr/lib/node_modules/mongodb
    cp -a -R ${S}/mongodb ${D}/usr/lib/node_modules
}

FILES_${PN} = "/usr/lib"

RDEPENDS_${PN} = "nodejs"
