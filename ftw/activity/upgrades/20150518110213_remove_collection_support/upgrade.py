from ftw.upgrade import UpgradeStep


class RemoveCollectionSupport(UpgradeStep):
    """Remove collection support.
    """

    def __call__(self):
        self.install_upgrade_profile()
