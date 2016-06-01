DESCRIPTION = "Node.js is a platform built on Chrome's JavaScript runtime for easily building fast, scalable network applications."
HOMEPAGE = "http://nodejs.org"
LICENSE = "MIT"
SECTION = "devel"
SUMMARY = "Node.js is a platform built on Chrome's JavaScript runtime for easily building fast, scalable network applications."

DEPENDS = "openssl"
DEPENDS_class-native += " openssl-native"

RCONFLICTS_${PN} = "node"

PR = "r1.0"

def version_check(target_arch, d):
    import re
    if   re.match('i.86$', target_arch): return 'nodejs_v0.10.39.inc'
    elif re.match('x86_64$', target_arch): return 'nodejs_v4.4.0.inc'
    return target_arch

require ${@version_check(d.getVar('TARGET_ARCH', True), d)}
