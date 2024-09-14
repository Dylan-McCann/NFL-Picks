from django.contrib import admin
from . models import Game,Choice,Week,Record

# Register your models here.

admin.site.register(Game)
admin.site.register(Choice)
admin.site.register(Week)
admin.site.register(Record)