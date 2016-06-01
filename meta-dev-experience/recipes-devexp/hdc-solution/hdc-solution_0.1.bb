DESCRIPTION = "Intel Iot Developer Hub - HDC Sample Solution"
PR = "r0"
LICENSE = "MIT"

DEPENDS += "wr-iot-agent"

FILESEXTRAPATHS_prepend := "${THISDIR}/files:"
SRC_URI = "file://hdc-send-data.c \
           file://package.json \
           file://hdc_config.json \
           file://hdc_reader.js \
           file://hdc_restapi.js \
           file://hdc_snum.js \
           file://HDC-Data-Send-CPU_TEMP-flow.json \
           file://HDC-Reader-CPU_TEMP-flow.json \
           file://HelixDeviceCloudTutorial.json \
           file://hdc_server_add.py \
           file://LICENSE"

LIC_FILES_CHKSUM = "file://LICENSE;md5=7dd262ad6474570455f77caf74b56ca1"

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

do_compile() {
    ${CC} ${CFLAGS} ${LDFLAGS} ${WORKDIR}/hdc-send-data.c -o hdc-send-data -lwraclient -lrt -lpthread
}

do_install() {
    install -m 0755 ${HOME_OWNER_AND_GROUP} -d ${D}${WR_HOME}
    install -m 0755 ${HOME_OWNER_AND_GROUP} -d ${D}${WR_HOME}/.node-red/lib/flows
    install -m 0755 ${HOME_OWNER_AND_GROUP} -d ${D}${WR_HOME}/hdc-solution
    install -m 0755 ${HOME_OWNER_AND_GROUP} ${S}/package.json ${D}${WR_HOME}/hdc-solution
    install -m 0755 ${HOME_OWNER_AND_GROUP} ${S}/hdc_restapi.js ${D}${WR_HOME}/hdc-solution
    install -m 0755 ${HOME_OWNER_AND_GROUP} ${S}/hdc_config.json ${D}${WR_HOME}/hdc-solution
    install -m 0755 ${HOME_OWNER_AND_GROUP} ${S}/hdc-send-data ${D}${WR_HOME}/hdc-solution
    install -m 0755 ${HOME_OWNER_AND_GROUP} ${S}/hdc_reader.js ${D}${WR_HOME}/hdc-solution
    install -m 0755 ${HOME_OWNER_AND_GROUP} ${S}/hdc_restapi.js ${D}${WR_HOME}/hdc-solution
    install -m 0755 ${HOME_OWNER_AND_GROUP} ${S}/hdc_snum.js ${D}${WR_HOME}/hdc-solution
    install -m 0644 ${HOME_OWNER_AND_GROUP} ${S}/HDC-Data-Send-CPU_TEMP-flow.json ${D}${WR_HOME}/hdc-solution
    install -m 0644 ${HOME_OWNER_AND_GROUP} ${S}/HDC-Reader-CPU_TEMP-flow.json ${D}${WR_HOME}/hdc-solution
    install -m 0644 ${HOME_OWNER_AND_GROUP} ${S}/hdc_server_add.py ${D}${WR_HOME}/hdc-solution
    install -m 0644 ${HOME_OWNER_AND_GROUP} ${S}/HelixDeviceCloudTutorial.json ${D}${WR_HOME}/.node-red/lib/flows
}

RDEPENDS_${PN} = "nodejs libwebsockets mosquitto node-xml2js node-shelljs node-global-tunnel node-macaddress node-url-parse"

FILES_${PN} = "${WR_HOME}"

FILES_${PN}-dbg += "${WR_HOME}/hdc-solution/.debug"
