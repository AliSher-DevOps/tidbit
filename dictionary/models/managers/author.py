from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone

from ...utils.settings import GENERIC_PRIVATEUSER_ID


# todo: Log these!

class AccountTerminationQueueManager(models.Manager):
    def get_terminated(self):
        return self.exclude(state="FZ").filter(termination_date__lt=timezone.now())

    @staticmethod
    def terminate_no_trace(user):
        user.delete()

    def terminate_legacy(self, user):
        anonymous_author_placeholder = get_user_model().objects.get(pk=GENERIC_PRIVATEUSER_ID)

        if not user.is_novice:
            # Migrate entries before deleting the user completely
            user.entry_set.all().update(author=anonymous_author_placeholder)

        self.terminate_no_trace(user)

    def commit_terminations(self):
        for termination in self.get_terminated():
            if termination.state == "NT":
                self.terminate_no_trace(termination.author)
            elif termination.state == "LE":
                self.terminate_legacy(termination.author)