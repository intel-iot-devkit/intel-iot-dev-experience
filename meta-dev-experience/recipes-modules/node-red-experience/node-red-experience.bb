PR = "r1.0"

def version_check(target_arch, d):
    import re
    if   re.match('i.86$', target_arch): return 'node-red-experience_0.12.2.inc'
    elif re.match('x86_64$', target_arch): return 'node-red-experience_0.13.4.inc'
    return target_arch

require ${@version_check(d.getVar('TARGET_ARCH', True), d)}
