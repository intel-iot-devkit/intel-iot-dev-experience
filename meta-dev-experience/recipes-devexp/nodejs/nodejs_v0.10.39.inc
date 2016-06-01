PV = "v0.10.39"

FILESEXTRAPATHS_prepend := "${THISDIR}/files:"
SRC_URI = "file://node-v0.10.39.tar.gz"

LIC_FILES_CHKSUM = "file://LICENSE;md5=e804bf1e856481415099460bc54d9316"

SRC_URI[md5sum] = "9f12c4f796f9ff040618a7f6122ebd73 "
SRC_URI[sha256sum] = "68f8d8f9515c4e77e2a06034b742e19e9848c1fee5bcadedc1d68f3e4302df37" 

S = "${WORKDIR}/node-v0.10.39"

CCACHE = ""
def map_dest_cpu(target_arch, d):
    import re
    if   re.match('i.86$', target_arch): return 'ia32'
    elif re.match('x86_64$', target_arch): return 'x64'
    return target_arch

do_configure () {
  export LD="${CXX}"
  alias g++="${CXX}"
  GYP_DEFINES="${GYP_DEFINES}" export GYP_DEFINES
  ./configure --prefix=${prefix} --without-snapshot --shared-openssl --dest-cpu=${@map_dest_cpu(d.getVar('TARGET_ARCH', True), d)}
  unalias g++
}

do_compile () {
  export LD="${CXX}"
  alias g++="${CXX}"
  make BUILDTYPE=Release
  unalias g++
}

do_install () {
  oe_runmake DESTDIR=${D} install
}

#do_install_append_class-native() {
#  # make sure we use node from PATH instead of absolute path to sysroot
#  sed "1s^.*^#\!/usr/bin/env node^g" -i ${D}/usr/lib/node_modules/npm/bin/npm-cli.js
#}

do_install_append_class-target() {
  # make sure we use node from PATH instead of absolute path to sysroot
  sed "1s^.*^#\!${bindir}/env node^g" -i ${D}/usr/lib/node_modules/npm/bin/npm-cli.js
}



PACKAGES =+ "${PN}-npm"
FILES_${PN}-npm = "${libdir}/node_modules ${bindir}/npm /usr/lib/*"
RDEPENDS_${PN}-npm = "bash python-compiler python-shell python-datetime python-subprocess python-multiprocessing python-crypt python-textutils python-netclient python-misc"

PACKAGES =+ "${PN}-dtrace"
FILES_${PN}-dtrace = "${libdir}/dtrace"

PACKAGES =+ "${PN}-systemtap"
FILES_${PN}-systemtap = "${datadir}/systemtap"

BBCLASSEXTEND = "native"
