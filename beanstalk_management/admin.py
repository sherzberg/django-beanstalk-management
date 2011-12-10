from django.contrib import admin
from django.contrib.auth.models import Permission

from models import User, Repository

class UserAdmin(admin.ModelAdmin):
    list_display = ('user', 'admin', 'owner', 'created_at', )
    list_filter = ('created_at', 'admin',)
    
class RepositoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'name', 'vcs', 'storage_used_bytes', 'created_at', 'last_commit_at', )
    list_filter = ('vcs', 'created_at', 'last_commit_at',)
    prepopulated_fields = {'name': ('title',)}

    fieldsets = (
        (None, {
            'fields': (
                       ('title', 'name', ),
                       ('vcs',),
                       'color_label',
                       )
        }),
    )
    
admin.site.register(User, UserAdmin)
admin.site.register(Repository, RepositoryAdmin)
admin.site.register(Permission)