SUMMARY = "Low Level Skeleton Library for Communication on Intel platforms"
SECTION = "libs"
AUTHOR = "Brendan Le Foll, Tom Ingleby"

RDEPENDS_${PN} = "dfu-util"
DEPENDS = "json-c udev"

LICENSE = "MIT"
LIC_FILES_CHKSUM = "file://COPYING;md5=66493d54e65bfc12c7983ff2e884f37f"

S = "${WORKDIR}/git"

inherit distutils-base pkgconfig python-dir cmake systemd

FILES_${PN}-doc += "${datadir}/mraa/examples/"

FILES_${PN}-dbg += "${libdir}/node_modules/mraajs/.debug/ \
                    ${PYTHON_SITEPACKAGES_DIR}/.debug/ \
                    ${prefix}/src/debug/ \
                    ${bindir}/.debug/"

PACKAGECONFIG ??= "python nodejs"
PACKAGECONFIG[python] = "-DBUILDSWIGPYTHON=ON, -DBUILDSWIGPYTHON=OFF, swig-native python"
PACKAGECONFIG[nodejs] = "-DBUILDSWIGNODE=ON, -DBUILDSWIGNODE=OFF, swig-native nodejs"

EXTRA_OECMAKE_append = "-DINSTALLGPIOTOOL=ON -DFIRMATA=ON -DIMRAA=ON -DENABLEEXAMPLES=OFF -DCMAKE_SKIP_RPATH:BOOL=ON"

do_compile_prepend () {
  # when yocto builds in ${D} it does not have access to ../git/.git so git
  # describe --tags fails. In order not to tag our version as dirty we use this
  # trick
  sed -i 's/-dirty//' src/version.c
}

do_install_append () {
  mkdir -p ${D}${systemd_unitdir}/system/
  install -m 0644 ${WORKDIR}/imraa.service ${D}${systemd_unitdir}/system/
  mkdir -p ${D}${datadir}/${PN}/
  install -m 0644 ${WORKDIR}/ConfigurableFirmataCurieImu.ino.bin ${D}${datadir}/${PN}/firmata101.ino.bin
  install -d ${D}${sysconfdir}
  install -m 0644 ${WORKDIR}/imraa.conf ${D}${sysconfdir}/
}

FILES_${PN}_append += " ${systemd_unitdir}/system/imraa.service \
                        ${datadir}/${PN}/firmata101.ino.bin \
                        ${sysconfdir}/imraa.conf \
                      "
SYSTEMD_SERVICE_${PN} = "imraa.service"
