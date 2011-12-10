from django.db import models
from datetime import datetime
import beanstalk
from django.contrib.auth import models as authmodels

class BeanstalkResource():
    def beanstalk_import(self):
        raise NotImplementedError()
    
    @staticmethod
    def fix_date(repo_date):
        try:
            split = repo_date.split(' ')
        except:
            return None
        sdate = "%s %s" %(split[0].replace('/','-'), split[1])
        format = '%Y-%m-%d %H:%M:%S'
        date = datetime.strptime(sdate,format)
        return date
    
class Repository(models.Model, BeanstalkResource):
    TYPE_CHOICES = (
                    ('subversion','Subversion'),
                    ('git','Git'),
                    )
    COLOR_CHOICES = (('label-{0}'.format(color), color) for color in 'red orange yellow green blue pink grey'.split(' '))
    
    name = models.SlugField(help_text='This will be used for the checkout url: git://hostname:NAME.git')
    vcs = models.CharField(blank=False, max_length=50, choices=TYPE_CHOICES, default='svn')
    title = models.CharField(max_length=50)
    color_label = models.CharField(blank=False, max_length=50, choices=COLOR_CHOICES, default='label-white')
    
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    last_commit_at = models.DateTimeField(null=True, blank=True)
    storage_used_bytes = models.IntegerField()

    class Meta:
        verbose_name_plural = 'repositories'
    
    def save(self, *args, **kwargs):
        if not self.id:
            result = beanstalk.api.repository.create(self.name, self.title, self.color_label, self.vcs)
            print result
            repo = Repository._load_from_json(self, result['%s_repository'%self.vcs])
            repo.save()
        else:
            super(Repository, self).save(*args, **kwargs)
    
    @staticmethod
    def _load_from_json(model, json):
        model.id = json['id']
        model.name = json['name']
        model.title = json['title']
        model.vcs = json['vcs']
        model.color_label = json['color_label']
        model.storage_used_bytes = json['storage_used_bytes']
        model.created_at = Repository.fix_date(json['created_at'])
        model.updated_at = Repository.fix_date(json['updated_at'])
        if Repository.fix_date(json['last_commit_at']):
            model.last_commit_at = Repository.fix_date(json['last_commit_at'])
        return model
    
    @staticmethod
    def beanstalk_import(id=None):
        results = {'add':0, 'edit':0}
        if id:
            repos = [beanstalk.api.repository.find(id)]
        else:
            repos = beanstalk.api.repository.find()
            
        for raw in repos:
            r = raw['repository']
            try:
                repo = Repository.objects.get(id=r['id'])
                results['edit'] += 1
            except Repository.DoesNotExist:
                repo = Repository()
                results['add'] += 1
            repo = Repository._load_from_json(repo, r)
            repo.save()
        
        return results
        
        
        
class User(models.Model):
    user = models.OneToOneField(authmodels.User)
    owner = models.BooleanField()
    admin = models.BooleanField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    
#    def save(self, *args, **kwargs):
#        if not self.id:
#            result = beanstalk.api.user.create(self.user.username, self.user.first_name, self.user.last_name, 'beanstalk')
#            print result
#            repo = Repository._load_from_json(self, result['%s_repository'%self.vcs])
#            repo.save()
#        else:
#            super(Repository, self).save(*args, **kwargs)
            
    @staticmethod
    def _load_from_json(model, json):
        model.id = json['id']
        model.owner = True if json['owner'] else False  
        model.admin = True if json['admin'] else False
        model.created_at = Repository.fix_date(json['created_at'])
        model.updated_at = Repository.fix_date(json['updated_at'])
        return model
    
    @staticmethod
    def beanstalk_import(id=None):
        results = {'add':0, 'edit':0, 'invited': 0}
        if id:
            repos = [beanstalk.api.user.find(id)]
        else:
            repos = beanstalk.api.user.find()
            
        for raw in repos:
            r = raw['user']
            if r['login']:
                try:
                    user = authmodels.User.objects.get(username=r['login'])
                    results['edit'] += 1
                except authmodels.User.DoesNotExist:
                    user = authmodels.User()
                    user.username = r['login']
                    user.first_name = r['first_name']
                    user.last_name = r['last_name']
                    user.email = r['email']
                    user.save()
                    
                    results['add'] += 1
                b_user = User()
                b_user = User._load_from_json(b_user, r)
                b_user.user = user
                b_user.save()
            else:
                results['invited'] += 1
            
        return results
   
        
        