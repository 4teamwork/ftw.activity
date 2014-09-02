from ftw.activity.browser.activity import ActivityView


class ActivityTab(ActivityView):

    def __call__(self):
        return self.raw()
