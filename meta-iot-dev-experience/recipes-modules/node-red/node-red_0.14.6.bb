DESCRIPTION = "Node-RED is a tool for wiring together hardware devices, APIs and online services in new and interesting ways."
HOMEPAGE = "http://nodered.org"
LICENSE = "Apache-2.0"
SUMMARY ="Node-RED is a tool for wiring together hardware devices, APIs and online services in new and interesting ways."

LIC_FILES_CHKSUM = "file://LICENSE;md5=2ee41112a44fe7014dce33e26468ba93"

FILESEXTRAPATHS_prepend := "${THISDIR}/files:"

PR = "r0"

SRC_URI = "https://github.com/${PN}/${PN}/releases/download/${PV}/${PN}-${PV}.zip"
SRC_URI[md5sum] = "b89a1309b687af9845d0ae593988e3de"
SRC_URI[sha256sum] = "d4ce01c646550efa96b7c8f9fd117c713d994c9cecd6fc9a53944dd18b384b66"

S = "${WORKDIR}/${PN}-${PV}"

NODE_MODULES_DIR = "${prefix}/lib/node_modules/"
NPM_CACHE_DIR ?= "${WORKDIR}/npm_cache"
NPM_REGISTRY ?= "https://registry.npmjs.org/"
NPM_INSTALL_FLAGS ?= "--production"

do_compile() {
	export NPM_CONFIG_CACHE="${NPM_CACHE_DIR}"
	
	# Clear cache
	npm cache clear

	# Install
	npm --registry=${NPM_REGISTRY} --arch=${TARGET_ARCH} --target_arch=${TARGET_ARCH} ${NPM_INSTALL_FLAGS} install
	npm prune --production
        cd ${WORKDIR}/${PN}-${PV}/node_modules/node-red-node-serialport/node_modules/serialport
        npm --target_arch=${TARGET_ARCH} rebuild --build-from-source
}

do_install() {
	install -d ${D}${NODE_MODULES_DIR}${PN}
    	cp -r ${S}/* ${D}${NODE_MODULES_DIR}${PN}
}

pkg_postinst_${PN}() {
#!/bin/sh
# Post installation script

ln -s ${NODE_MODULES_DIR}${PN}/red.js ${bindir}/${PN}
chmod 755 ${bindir}/${PN}
systemctl restart node-red-experience

}

PACKAGES = "${PN}"

FILES_${PN} = "${NODE_MODULES_DIR}${PN}"


DEPENDS = "nodejs nodejs-native"
RDEPENDS_${PN} = "bash python nodejs"


INHIBIT_PACKAGE_DEBUG_SPLIT = "1"
