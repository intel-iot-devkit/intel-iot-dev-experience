DESCRIPTION = "Intel Iot Developer Hub - Azure Service Bus Sample Solution"
PR = "r0"
LICENSE = "MIT"


FILESEXTRAPATHS_prepend := "${THISDIR}/files:"
SRC_URI = "file://azuresb_crypto.js \
           file://azuresb-rx.js \
           file://azuresb-tx.js \
           file://azure-sb-txrx-nr-sample.json \
           file://azure-sb-txrx-NR-Tutorial.json \
           file://cputemp.sh \
           file://memused.js \
           file://package.json \
           file://sbcfg_origin.json \
           file://sbconfig.json \
           file://LICENSE.TXT"

LIC_FILES_CHKSUM = "file://LICENSE.TXT;md5=4c9da977cfb1c90bb9f4fc575074ffab"

S = "${WORKDIR}"
inherit useradd

WR_USER = "gwuser"
WR_GROUP = "admin"
WR_PASSWORD = "\$6\$i379JFoua6/\$nxPIN.z9c.AU1ifz78f8nJYgFuT9vmUZUFxfdrbk3wr6phT0GkRRbVBumbRX/3y0f3d.oqb7zHzSOaq3Rz2TN1"
WR_HOME = "/home/${WR_USER}"
USERADD_PACKAGES = "${PN}"
GROUPADD_PARAM_${PN} = "--system ${WR_GROUP}"
USERADD_PARAM_${PN} = "-m -d ${WR_HOME} -s /bin/bash -g ${WR_GROUP} -p '${WR_PASSWORD}' ${WR_USER}"
HOME_OWNER_AND_GROUP = "-o ${WR_USER} -g ${WR_GROUP}"

do_install() {
    install -m 0755 ${HOME_OWNER_AND_GROUP} -d ${D}${WR_HOME}
    install -m 0755 ${HOME_OWNER_AND_GROUP} -d ${D}${WR_HOME}/.node-red/lib/flows
    install -m 0755 ${HOME_OWNER_AND_GROUP} -d ${D}${WR_HOME}/azure-sb-solution
    install -m 0755 ${HOME_OWNER_AND_GROUP} ${S}/package.json ${D}${WR_HOME}/azure-sb-solution
    install -m 0755 ${HOME_OWNER_AND_GROUP} ${S}/azuresb_crypto.js ${D}${WR_HOME}/azure-sb-solution
    install -m 0755 ${HOME_OWNER_AND_GROUP} ${S}/azuresb-rx.js ${D}${WR_HOME}/azure-sb-solution
    install -m 0755 ${HOME_OWNER_AND_GROUP} ${S}/azuresb-tx.js ${D}${WR_HOME}/azure-sb-solution
    install -m 0755 ${HOME_OWNER_AND_GROUP} ${S}/cputemp.sh ${D}${WR_HOME}/azure-sb-solution
    install -m 0755 ${HOME_OWNER_AND_GROUP} ${S}/memused.js ${D}${WR_HOME}/azure-sb-solution
    install -m 0755 ${HOME_OWNER_AND_GROUP} ${S}/package.json ${D}${WR_HOME}/azure-sb-solution
    install -m 0644 ${HOME_OWNER_AND_GROUP} ${S}/sbcfg_origin.json ${D}${WR_HOME}/azure-sb-solution
    install -m 0644 ${HOME_OWNER_AND_GROUP} ${S}/sbconfig.json ${D}${WR_HOME}/azure-sb-solution
    install -m 0644 ${HOME_OWNER_AND_GROUP} ${S}/azure-sb-txrx-nr-sample.json ${D}${WR_HOME}/.node-red/lib/flows
    install -m 0644 ${HOME_OWNER_AND_GROUP} ${S}/azure-sb-txrx-NR-Tutorial.json ${D}${WR_HOME}/.node-red/lib/flows
}

RDEPENDS_${PN} = "libwebsockets mosquitto node-xml2js node-shelljs node-global-tunnel node-macaddress node-url-parse"

FILES_${PN} = "${WR_HOME}"

FILES_${PN}-dbg += "${WR_HOME}/azure-sb-solution/.debug"
