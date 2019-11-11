from ftw.upgrade import UpgradeStep


class UpgradeToFtwTheming(UpgradeStep):
    """Upgrade to ftw.theming.
    """

    def __call__(self):
        self.install_upgrade_profile()
