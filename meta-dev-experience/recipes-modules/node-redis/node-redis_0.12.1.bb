DESCRIPTION = "This is a complete Redis client for node.js. It supports all Redis commands, including many recently added commands like EVAL from experimental Redis server branches."
LICENSE = "MIT"
SUMMARY = "A complete Redis client for node.js."
SECTION = "devel/node"
HOMEPAGE = "https://github.com/NodeRedis/node_redis"
PR = "r1.0"
LIC_FILES_CHKSUM = "file://${THISDIR}/files/README.md;md5=c7cad7ebfc5d59b6aceda78984a6c33b"

FILESEXTRAPATHS_prepend := "${THISDIR}/files:"
SRC_URI = 	"file://README.md \
                 file://redis-0.12.1.tar.bz2"

S = "${WORKDIR}/node_modules/"

do_install_append () {
    install -d ${D}/usr/lib/node_modules/redis
    cp -a -R ${S}/redis ${D}/usr/lib/node_modules
}

FILES_${PN} = "/usr/lib/*"

RDEPENDS_${PN} = "nodejs"
