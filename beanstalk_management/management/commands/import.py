from django.core.management.base import BaseCommand
import beanstalk
from beanstalk_management.models import *

class Command(BaseCommand):
    args = "None"
    help = 'Import data from beanstalkapp.com'

    def handle(self, *args, **options):
        print 'Starting import.'
        results={}
        
        results['repositories'] = Repository.beanstalk_import()
        results['users'] = User.beanstalk_import()

        for model,set in results.iteritems():
            print model
            print '------------------'
            for type, value in set.iteritems():
                print '%s: %s' %(type, value)
            print
            
        print 'Done importing.'