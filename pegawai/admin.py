from django.contrib import admin
from pegawai.models import *

# Register your models here.
# class Akun(admin.ModelAdmin):
#     list_display = ['nama', 'pegawai']
#     list_filter = ()
#     search_fields = ['nama', 'pegawai']
#     list_per_page = 25
admin.site.register(AkunModel)
admin.site.register(GolonganModel)
admin.site.register(OpdModel)
