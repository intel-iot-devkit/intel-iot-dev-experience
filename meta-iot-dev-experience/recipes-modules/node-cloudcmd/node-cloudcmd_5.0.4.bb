DESCRIPTION = "Cloud Commander orthodox web file manager with console and editor"
LICENSE = "MIT"
SUMMARY = "Cloud Commander orthodox web file manager with console and editor"
SECTION = "devel/node"
HOMEPAGE = "https://github.com/coderaiser/cloudcmd"
PR = "r1.0"

LIC_FILES_CHKSUM = "file://${THISDIR}/files/LICENSE;md5=ea41c030b7b22840a196d85eb876f5e8"

FILESEXTRAPATHS_prepend := "${THISDIR}/files:"
SRC_URI = 	"file://LICENSE \
                 file://node-cloudcmd.service \
                 file://index.html \
                 file://cloudcmd-5.0.4.tar \
                 file://node-cloudcmd_nginx_https.conf \
                 file://node-cloudcmd_nginx_http.conf" 

S = "${WORKDIR}/node_modules/"

inherit systemd useradd

WR_USER = "gwuser"
WR_GROUP = "admin"
WR_PASSWORD = "\$6\$i379JFoua6/\$nxPIN.z9c.AU1ifz78f8nJYgFuT9vmUZUFxfdrbk3wr6phT0GkRRbVBumbRX/3y0f3d.oqb7zHzSOaq3Rz2TN1"
WR_HOME = "/home/${WR_USER}"
USERADD_PACKAGES = "${PN}"
GROUPADD_PARAM_${PN} = "--system ${WR_GROUP}"
USERADD_PARAM_${PN} = "-m -d ${WR_HOME} -s /bin/bash -g ${WR_GROUP} -p '${WR_PASSWORD}' ${WR_USER}"
HOME_OWNER_AND_GROUP = "-o ${WR_USER} -g ${WR_GROUP}"

CONFFILES = "/etc/nginx/conf.d/node-cloudcmd.conf"

do_install () {
    install -m 0755 ${HOME_OWNER_AND_GROUP} -d ${D}${WR_HOME}
    install -m 0755 ${HOME_OWNER_AND_GROUP} -d ${D}${WR_HOME}/.node-cloudcmd
    install -m 644 ${HOME_OWNER_AND_GROUP} ${WORKDIR}/node-cloudcmd_nginx_http.conf ${D}${WR_HOME}/.node-cloudcmd
    install -m 644 ${HOME_OWNER_AND_GROUP} ${WORKDIR}/node-cloudcmd_nginx_https.conf ${D}${WR_HOME}/.node-cloudcmd
    install -d ${D}${sysconfdir}/nginx
    install -m 0755 -d ${D}/etc/nginx/conf.d
    install -m 644 ${WORKDIR}/node-cloudcmd_nginx_http.conf  ${D}/etc/nginx/conf.d/node-cloudcmd.conf    
    install -d ${D}/usr/lib/node_modules/cloudcmd
    cp -a -R ${S}/cloudcmd ${D}/usr/lib/node_modules
    install -d ${D}/${systemd_unitdir}/system
    install -d ${D}/usr/lib/node_modules/.bin
    install -m 600 ${WORKDIR}/node-cloudcmd.service ${D}/${systemd_unitdir}/system/node-cloudcmd.service
    install -m 644 ${S}/.bin/cloudcmd ${D}/usr/lib/node_modules/.bin
    rm ${D}/usr/lib/node_modules/cloudcmd/html/index.html
    install -m 644 ../index.html ${D}/usr/lib/node_modules/cloudcmd/html
}

SYSTEMD_SERVICE_${PN} = "node-cloudcmd.service"

INSANE_SKIP_${PN} = "staticdev debug-files file-rdeps"
FILES_${PN} = "${WR_HOME} /usr/lib /etc/nginx/conf.d"
RDEPENDS_${PN} = "nodejs"


