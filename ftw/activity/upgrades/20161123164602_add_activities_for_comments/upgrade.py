from Acquisition import aq_inner
from Acquisition import aq_parent
from DateTime import DateTime
from ftw.activity.catalog import comment_added
from ftw.upgrade import UpgradeStep


class AddActivitiesForComments(UpgradeStep):
    """Add activities for comments.
    """

    def __call__(self):
        self.install_upgrade_profile()

        for comment in self.objects({'portal_type': 'Discussion Item'},
                                    type(self).__doc__):
            discussion = aq_parent(aq_inner(comment))
            context = aq_parent(aq_inner(discussion))
            comment_added(context,
                          comment,
                          actor_userid=comment.Creator(),
                          date=DateTime(comment.creation_date))
