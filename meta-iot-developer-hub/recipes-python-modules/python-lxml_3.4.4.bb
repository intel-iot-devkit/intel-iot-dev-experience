DESCRIPTION = "Powerful and Pythonic XML processing library combining \
libxml2/libxslt with the ElementTree API."
HOMEPAGE = "http://codespeak.net/lxml"
LICENSE = "BSD"
LIC_FILES_CHKSUM = "file://LICENSES.txt;md5=f9f1dc24f720c143c2240df41fe5073b"
SRCNAME = "lxml"
PV="3.4.4"
PR = "r2"

DEPENDS = "libxml2 libxslt"
RDEPENDS_${PN} += "libxml2 libxslt python-compression"

FILESEXTRAPATHS_prepend := "${THISDIR}/files:"
SRC_URI = "file://lxml-3.4.4.tar.gz"
SRC_URI[lxml.md5sum] = "a9a65972afc173ec7a39c585f4eea69c"
SRC_URI[lxml.sha256sum] = "b3d362bac471172747cda3513238f115cbd6c5f8b8e6319bf6a97a7892724099"

S = "${WORKDIR}/${SRCNAME}-${PV}"

inherit setuptools

DISTUTILS_BUILD_ARGS += " \
                     --with-xslt-config='${STAGING_BINDIR_NATIVE}/pkg-config libxslt' \
                     --with-xml2-config='${STAGING_BINDIR_CROSS}/xml2-config' \
"

DISTUTILS_INSTALL_ARGS += " \
                     --with-xslt-config='${STAGING_BINDIR_NATIVE}/pkg-config libxslt' \
                     --with-xml2-config='${STAGING_BINDIR_CROSS}/xml2-config' \
"

BBCLASSEXTEND = "native nativesdk"
RDEPENDS_${PN}_virtclass-native = "libxml2-native libxslt-native"

RPROVIDES_${PN} = "python-lxml"

