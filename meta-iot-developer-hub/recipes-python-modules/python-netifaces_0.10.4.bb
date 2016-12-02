SUMMARY = "Portable network interface information."
SECTION = "devel/python"
HOMEPAGE = "https://bitbucket.org/al45tair/netifaces"
LICENSE = "MIT"
DESCRIPTION = "Portable network interface information."
LIC_FILES_CHKSUM = "file://README.rst;md5=eb2589e54e6b0f477fb19bec275454de"

FILESEXTRAPATHS_prepend := "${THISDIR}/files:"
SRC_URI = "file://netifaces-0.10.4.tar.gz"

SRC_URI[md5sum] = "36da76e2cfadd24cc7510c2c0012eb1e"
SRC_URI[sha256sum] = "9656a169cb83da34d732b0eb72b39373d48774aee009a3d1272b7ea2ce109cde"




S = "${WORKDIR}/netifaces-${PV}"

inherit setuptools

