FILESEXTRAPATHS_prepend := "${THISDIR}/${PN}:"

DEPENDS_append = " libmodbus"
RDEPENDS_${PN}_append = " libmodbus"

export JAVA_HOME="${STAGING_DIR}/${BUILD_SYS}/usr/lib/jvm/icedtea7-native"

PACKAGECONFIG ??= "python nodejs java"

PACKAGECONFIG[java] = "-DBUILDSWIGJAVA=ON, -DBUILDSWIGJAVA=OFF, swig-native icedtea7-native,"

cmake_do_generate_toolchain_file_append() {
  echo "
set (JAVA_AWT_INCLUDE_PATH ${JAVA_HOME}/include CACHE PATH \"AWT include path\" FORCE)
set (JAVA_AWT_LIBRARY ${JAVA_HOME}/jre/lib/amd64/libjawt.so CACHE FILEPATH \"AWT Library\" FORCE)
set (JAVA_INCLUDE_PATH ${JAVA_HOME}/include CACHE PATH \"java include path\" FORCE)
set (JAVA_INCLUDE_PATH2 ${JAVA_HOME}/include/linux CACHE PATH \"java include path\" FORCE)
set (JAVA_JVM_LIBRARY ${JAVA_HOME}/jre/lib/amd64/libjvm.so CACHE FILEPATH \"path to JVM\" FORCE)
" >> ${WORKDIR}/toolchain.cmake
}

# include .jar files in /usr/lib/java for 64 bit builds
FILES_${PN}_append = "${@' /usr/lib/java/*.jar' if '${MACHINE}' == 'intel-baytrail-64' else ''}"

# include nodejs files in /usr/lib/node_modules for 64 bit builds
FILES_${PN}_append = "${@' /usr/lib/node_modules/*' if '${MACHINE}' == 'intel-baytrail-64' else ''}"

INSANE_SKIP_${PN} = "dev-so"

# only for gateways
INHIBIT_PACKAGE_DEBUG_SPLIT = "1"
PACKAGES = "${PN}"
FILES_${PN}_append = " ${includedir}"
