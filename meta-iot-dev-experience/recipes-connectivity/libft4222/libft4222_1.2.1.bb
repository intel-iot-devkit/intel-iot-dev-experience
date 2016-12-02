SUMMARY = "FTDI FT4222 Library"
AUTHOR = "Henry Bruce"
SECTION = "libs"
LICENSE_FLAGS = "ftdi"
LICENSE = "CLOSED"

COMPATIBLE_MACHINE = "intel-corei7-64|intel-core2-32|edison|intel-baytrail-64"

# Set subdir variable so that files are unpacked unto ${S}
BUILD_NUMBER = "4"
SRC_URI = "http://www.ftdichip.com/Support/SoftwareExamples/${PN}-${PV}.${BUILD_NUMBER}.tgz;subdir=${PN}-${PV}"
SRC_URI[md5sum] = "bf5042ee5a8241e657650001611899b5"
SRC_URI[sha256sum] = "3a9dfd8eae38530379a95201e55b60c6a20bd2acb93202d374bba2711331447e"

MACHINE_DIR_intel-corei7-64 = "build-x86_64"
MACHINE_DIR_intel-core2-32 = "build-i386"
MACHINE_DIR_edison = "build-i386"
MACHINE_DIR_intel-baytrail-64 = "build-x86_64"

do_install () {
    install -m 0755 -d ${D}${libdir}
    oe_soinstall ${S}/${MACHINE_DIR}/libft4222.so.${PV}.${BUILD_NUMBER} ${D}${libdir}

    install -m 0755 -d ${D}${includedir}
    install -m 0755 ${S}/*.h ${D}${includedir}
}
