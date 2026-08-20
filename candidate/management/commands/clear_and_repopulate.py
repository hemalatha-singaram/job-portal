from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from candidate.models import CandidateProfile, JobApplication
from recruiter.models import Job


class Command(BaseCommand):
    help = 'Clear all data and repopulate with fresh data including Indian locations'

    def handle(self, *args, **options):
        self.stdout.write('Clearing existing data...')
        
        # Delete all data
        JobApplication.objects.all().delete()
        Job.objects.all().delete()
        CandidateProfile.objects.all().delete()
        User.objects.all().delete()
        
        self.stdout.write(self.style.SUCCESS('✅ Data cleared successfully'))
        
        # Now run populate command
        from django.core.management import call_command
        self.stdout.write('Populating with fresh data and Indian locations...')
        call_command('populate_initial_data')
