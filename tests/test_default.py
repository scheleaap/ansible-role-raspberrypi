import testinfra.utils.ansible_runner

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    '.molecule/ansible_inventory').get_hosts('all')


def test_apt_packages_are_installed_and_deinstalled(Package):
    packages = [
        ("triggerhappy", False),
        ("cron", False),
        ("logrotate", False),
        ("dphys-swapfile", False),
        ("xserver-common", False),
        ("lightdm", False),
        ("fake-hwclock", False),
        ("busybox-syslogd", True),
        ("rsyslog", False),
        ]

    for package_name, package_state_or_version in packages:
        package = Package(package_name)
        if package_state_or_version in (True, False):
            assert is_installed(package) is package_state_or_version
        else:
            assert is_installed(package)
            assert package.version == package_state_or_version


def test_var_spool(File):
    f = File("/var/spool")
    assert f.is_symlink
    assert f.linked_to == "/tmp/var/spool"

    f = File("/tmp/var/spool")
    assert f.exists
    assert f.is_directory
    assert f.user == "root"
    assert f.group == "root"


def test_fstab(File):
    f = File("/etc/fstab")
    assert "tmpfs /var/log tmpfs nodev,nosuid 0 0" in f.content_string
    assert "tmpfs /var/tmp tmpfs nodev,nosuid 0 0" in f.content_string
    assert "tmpfs /tmp     tmpfs nodev,nosuid 0 0" in f.content_string


def test_sshd_privilege_separation(File):
    f = File("/etc/ssh/sshd_config")
    assert "UsePrivilegeSeparation no" in f.content_string


def test_resolv_conf(File):
    # Disabled because changing /etc/resolv.conf does not work in Docker
    # f = File("/etc/resolv.conf")
    # assert f.is_symlink
    # assert f.linked_to == "/tmp/etc/resolv.conf"

    f = File("/tmp/etc/resolv.conf")
    assert f.exists
    assert f.is_file
    assert f.user == "root"
    assert f.group == "root"


def test_var_spool_permissions(File):
    f = File("/usr/lib/tmpfiles.d/var.conf")
    assert "/var/spool 1777" in f.content_string


def test_boot_options(File):
    f = File("/boot/cmdline.txt")
    assert " fastboot" in f.content_string
    assert " noswap" in f.content_string
    assert " ro" in f.content_string


def is_installed(package):
    """Returns whether a given package is installed.

    This function is needed because Package.is_installed throws an
    AssertionError if it is not installed.

    @param package: A Package object.
    @return A boolean indicating whether the package is installed.
    """
    try:
        return package.is_installed
    except AssertionError:
        return False
