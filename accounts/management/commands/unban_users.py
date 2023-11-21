from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from accounts.models import ReportUser, CustomUser  # Replace 'your_app' with your actual app name

class Command(BaseCommand):
    help = 'Unban users whose ban period has expired.'

    def handle(self, *args, **options):
        now = timezone.now()
        one_week_ago = now - timedelta(weeks=1)  # Calculate the datetime for one week ago

        # Filtering users whose unban_time is less than or equal to one_week_ago
        for report in ReportUser.objects.filter(unban_time__lte=one_week_ago):
            user = report.user
            user.is_active = True
            user.save()

            report.unban_time = None  # Reset the unban_time
            report.report_count = 0  # Reset the unban_time
            report.save()

            self.stdout.write(self.style.SUCCESS(f'Successfully unbanned user {user.id}'))

