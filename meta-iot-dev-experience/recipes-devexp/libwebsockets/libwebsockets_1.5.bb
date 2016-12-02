SUMMARY = "libwebsockets"
SECTION = "libs"
LICENSE = "MIT"
HOMEPAGE = "https://libwebsockets.org"
DESCRIPTION = "Libwebsockets is a lightweight pure C library built to use minimal CPU and memory resources, and provide fast throughput in both directions."

LIC_FILES_CHKSUM = "file://LICENSE;md5=041a1dec49ec8a22e7f101350fd19550"

FILESEXTRAPATHS_prepend := "${THISDIR}/files:"
SRC_URI = "file://libwebsockets-1.5-chrome47-firefox41.tar.gz"
SRC_URI[md5sum]    = "2b48aa76f35354fc65160ec116bdd36d"
SRC_URI[sha256sum] = "27f3e2dbd04b8375923f6353536c741559a21dd4713f8c302b23441d6fe82403"

S = "${WORKDIR}/libwebsockets-1.5-chrome47-firefox41"

inherit cmake pkgconfig

def map_dest_cpu(target_arch, d):
    import re
    if   re.match('i.86$', target_arch): return ''
    elif re.match('x86_64$', target_arch): return '64'
    return target_arch

EXTRA_OECMAKE = "-DLIB_SUFFIX=${@map_dest_cpu(d.getVar('TARGET_ARCH', True), d)}"

FILES_${PN} += "/usr/share/*"

RDEPENDS_${PN} = "zlib libcrypto openssl"
DEPENDS = "zlib openssl"
