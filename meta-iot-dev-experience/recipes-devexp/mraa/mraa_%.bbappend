FILESEXTRAPATHS_prepend := "${THISDIR}/${PN}:"

PACKAGECONFIG = "python nodejs java usbplat"
PACKAGECONFIG_quark = "python nodejs java"

PACKAGECONFIG[java] = "-DBUILDSWIGJAVA=ON, -DBUILDSWIGJAVA=OFF, swig-native icedtea7-native,"
PACKAGECONFIG[usbplat] = "-DUSBPLAT=ON, -DUSBPLAT=OFF,,"
PACKAGECONFIG[ftdi4222] = "-DFTDI4222=ON, -DFTDI4222=OFF, libft4222, libft4222"

export JAVA_HOME="${STAGING_DIR}/${BUILD_SYS}/usr/lib/jvm/icedtea7-native"

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
FILES_${PN}_append = "${@' /usr/lib/*' if '${MACHINE}' == 'intel-baytrail-64' else ''}"

INSANE_SKIP_${PN} = "dev-so debug-files"

# only for gateways
PACKAGES = "${PN}"
FILES_${PN}_append = " ${includedir}"
