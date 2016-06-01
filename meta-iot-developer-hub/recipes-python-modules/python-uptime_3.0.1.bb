SUMMARY = "Cross-platform uptime library"
SECTION = "devel/python"
HOMEPAGE = "https://github.com/Cairnarvon/uptime"
LICENSE = "BSD"
DESCRIPTION = "This module provides a cross-platform way to retrieve system uptime and boot time. See documentation for a full list of supported platforms (yours is likely one of them)."
LIC_FILES_CHKSUM = "file://COPYING.txt;md5=369c946d63467ded5d6324dd139afe96"

FILESEXTRAPATHS_prepend := "${THISDIR}/files:"
SRC_URI = "file://uptime-3.0.1.tar.gz"

SRC_URI[md5sum] = "046063e97abbee37bf8de3fd16df674d"
SRC_URI[sha256sum] = "7c300254775b807ce46e3dcbcda30aa3b9a204b9c57a7ac1e79ee6dbe3942973"



S = "${WORKDIR}/uptime-${PV}"

inherit setuptools

