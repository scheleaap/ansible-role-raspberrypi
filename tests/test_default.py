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
    assert_is_symlinked(
            File,
            "/var/spool", "/tmp/var/spool",
            "root", "root"
            )


def test_var_spool_permissions(File):
    f = File("/usr/lib/tmpfiles.d/var.conf")
    assert "/var/spool 1777" in f.content_string


def test_var_lib_mopidy(File):
    assert_is_symlinked(
            File,
            "/var/lib/mopidy", "/tmp/var/lib/mopidy",
            "mopidy", "audio"
            )
    assert_is_tmpfs(File, "/tmp/var/lib/mopidy")


def test_var_cache_mopidy(File):
    assert_is_symlinked(
            File,
            "/var/cache/mopidy", "/tmp/var/cache/mopidy",
            "mopidy", "audio"
            )
    assert_is_tmpfs(File, "/tmp/var/cache/mopidy")


def test_var_lib_snapserver(File):
    assert_is_symlinked(
            File,
            "/var/lib/snapserver", "/tmp/var/lib/snapserver",
            "snapserver", "snapserver"
            )
    assert_is_tmpfs(File, "/tmp/var/lib/snapserver")


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

    assert_is_tmpfs(File, "/tmp/etc")


def test_fstab(File):
    assert_is_tmpfs(File, "/var/log")
    assert_is_tmpfs(File, "/var/log/mopidy")
    assert_is_tmpfs(File, "/var/tmp")
    assert_is_tmpfs(File, "/tmp    ")


def test_sshd_privilege_separation(File):
    f = File("/etc/ssh/sshd_config")
    assert "UsePrivilegeSeparation no" in f.content_string


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


def assert_is_symlinked(
        File, source_path, target_path, target_user, target_group):
    f = File(source_path)
    assert f.is_symlink
    assert f.linked_to == target_path

    f = File(target_path)
    assert f.exists
    assert f.is_directory
    assert f.user == target_user
    assert f.group == target_group


def assert_is_tmpfs(File, path):
    f = File("/etc/fstab")
    assert "tmpfs {} tmpfs nodev,nosuid 0 0".format(path) \
        in f.content_string
