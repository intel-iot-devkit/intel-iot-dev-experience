DESCRIPTION = "Simplejson is a simple, fast, complete, correct and extensible JSON <http://json.org> encoder and decoder for Python 2.5+ and Python 3.3+. It is pure Python code with no dependencies, but includes an optional C extension for a serious speed boost."

HOMEPAGE = "https://pypi.python.org/pypi/simplejson/3.7.3"
SECTION = "devel/python"
LICENSE = "MIT"
LIC_FILES_CHKSUM = "file://setup.py;md5=61cd8dab5ff5fc2bf8f03f4264845bc4"

SRCNAME = "simplejson"
PR = "r1.0"
DEPENDS += "python"
DEPENDS_class-native += "python-native"

FILESEXTRAPATHS_prepend := "${THISDIR}/files:"
SRC_URI = "file://simplejson-3.7.3.tar.gz"

S = "${WORKDIR}/${SRCNAME}-${PV}"

inherit distutils 

DISTUTILS_INSTALL_ARGS += "--install-lib=${D}${libdir}/${PYTHON_DIR}/site-packages"

do_install_prepend() {
    install -d ${D}/${libdir}/${PYTHON_DIR}/site-packages
}

RDEPENDS_${PN} = "python-distutils"

RDEPENDS_${PN}_class-native = "\
  python-distutils"

SRC_URI[md5sum] = "117346e5ee4ed4434ffe485f8e58f5ed"
SRC_URI[sha256sum] = "63d7f7b14a20f29f74325a69e6db45925eaf6e3a003eab46c0234fd050a8c93f"

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

echo "./simplejson-3.6.5-py2.7-linux-x86_64.egg" > simplejson.pth
}
