DESCRIPTION = "Provides communication to the Intel XDK"
LICENSE = "Proprietary"

LIC_FILES_CHKSUM = "file://LICENSE;md5=a73c59556102dc129206ba79d12f4499"

DEPENDS = "nodejs-native mdns"
RDEPENDS_${PN} = "libarchive-bin nodejs bash mdns-dev"

PR = "r0"

# needed to unset no_proxy for internal development
export no_proxy = ""

SRC_URI = "http://download.xdk.intel.com/iot/xdk-daemon-0.1.4.tar.bz2"

SRC_URI[md5sum] = "56e88df9a57aaf1b27c065f08bc242d0"
SRC_URI[sha256sum] = "84e10d67ea1f65af27c6446e63dcab19f5da378ed98d366e05533da6482ece8f"

# we don't care about debug for the few binary node modules
INHIBIT_PACKAGE_DEBUG_SPLIT = "1"

do_compile () {
    # changing the home directory to the working directory, the .npmrc will be created in this directory
    export HOME=${WORKDIR}

    # does not build dev packages
    npm config set dev false

    # access npm registry using http
    npm set strict-ssl false
    npm config set registry http://registry.npmjs.org/

    # configure http proxy if neccessary
    if [ -n "${http_proxy}" ]; then
        npm config set proxy ${http_proxy}
    fi
    if [ -n "${HTTP_PROXY}" ]; then
        npm config set proxy ${HTTP_PROXY}
    fi

    # configure cache to be in working directory
    npm set cache ${WORKDIR}/npm_cache

    # clear local cache prior to each compile
    npm cache clear

    # NPM is picky about arch names
    if [ "${TARGET_ARCH}" == "i586" ]; then
        npm config set target_arch ia32
        export TARGET_ARCH=ia32
    fi
    # npm is dumb, it needs to get given --arch but not in npm config
    npm install
    cd current/ && npm install --arch=${TARGET_ARCH}
    cd node-inspector-server && npm install --build-from-source --arch=${TARGET_ARCH}

    sed -i '/TM/d' ${S}/xdk-daemon
}

do_install () {
    install -d ${D}/opt/xdk-daemon/
    cp -a ${S}/* ${D}/opt/xdk-daemon/

    install -d ${D}${systemd_unitdir}/system/
    install -m 0644 ${S}/xdk-daemon-mdns.service ${D}${systemd_unitdir}/system/xdk-daemon.service
}

inherit systemd

SYSTEMD_SERVICE_${PN} = "xdk-daemon.service"

FILES_${PN} = "/opt/xdk-daemon/ \
               ${systemd_unitdir}/system/xdk-daemon.service \
               ${bindir}/"

PACKAGES = "${PN}"

