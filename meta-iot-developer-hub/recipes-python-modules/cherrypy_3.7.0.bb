DESCRIPTION = "CherryPy is a pythonic, object-oriented HTTP framework"
HOMEPAGE = "https://pypi.python.org/pypi/CherryPy/3.8.0"
SECTION = "devel/python"
LICENSE = "BSD-3-Clause"
LIC_FILES_CHKSUM = "file://setup.py;md5=1d13a08525536268c1359eb1fc2f8f29"

SRCNAME = "CherryPy"
PR = "r1.0"
DEPENDS += "python"
DEPENDS_class-native += "python-native"

FILESEXTRAPATHS_prepend := "${THISDIR}/files:"
SRC_URI = "file://CherryPy-3.7.0.tar.gz"

S = "${WORKDIR}/${SRCNAME}-${PV}"

inherit distutils

DISTUTILS_INSTALL_ARGS += "--install-lib=${D}${libdir}/${PYTHON_DIR}/site-packages"

do_install_prepend() {
    install -d ${D}/${libdir}/${PYTHON_DIR}/site-packages
    install -d ${D}/usr/share/cherrypy
}

RDEPENDS_${PN} = "python-distutils"

RDEPENDS_${PN}_class-native = "\
  python-distutils \
  python-compression \
"

FILES_${PN} = "${libdir} ${bindir} /usr/share/"

SRC_URI[md5sum] = "fbf36f0b393aee2ebcbc71e3ec6f6832"
SRC_URI[sha256sum] = "2d19b9a99dc70c01d7ac58b5c2a0c6f6c0e12620e6f5dc1f556f6c1cdfd90ef8"

BBCLASSEXTEND = "native"

pkg_postinst_${PN} () {
#!/bin/sh 
if [ x"$D" != "x" ]; then
	exit 1
fi
#actions to cary out on device

if [ -d /usr/lib64 ]; then
   cd /usr/lib64/python2.7/site-packages
else
   cd /usr/lib/python2.7/site-packages
fi

echo "./CherryPy-3.7.0-py2.7.egg" > cherrypy.pth
}
