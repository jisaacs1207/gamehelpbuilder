from django.contrib import admin
from .models import Entry
from django_better_admin_arrayfield.admin.mixins import DynamicArrayMixin
from import_export import fields, resources
from import_export.admin import ImportExportMixin
from import_export.tmp_storages import CacheStorage
from simple_history.admin import SimpleHistoryAdmin
from django.utils.html import format_html
from django.urls import reverse
from .formats import GameHelpFile

from parseradmin.models import HelpUpload
from parseradmin.tasks import process_gamehelp_export

class EntryResource(resources.ModelResource):    
    id = fields.Field(attribute='id', column_name='id')

    class Meta:
        model = Entry
        fields = ('id', 'restriction', 'restriction_type','keyword_main', 'keywords', 'syntax', 'see_also', 'description', 'raw')
        import_id_fields = ('keyword_main',)

    def get_queryset(self):
        return self._meta.model.objects.order_by('keyword_main') 
    
    def before_import(self, dataset, using_transactions, dry_run, **kwargs):
        Entry.objects.all().delete()

class EntryAdmin(ImportExportMixin, DynamicArrayMixin, SimpleHistoryAdmin):
    tmp_storage_class = CacheStorage
    resource_class = EntryResource
    list_display = ['keyword_main', 'keywords']
    search_fields = ['keyword_main', 'keywords']
    readonly_fields = ['raw', 'lookup_link']

    def get_form(self, request, *args, **kwargs):
        self.request = request
        return super().get_form(request, *args, **kwargs)
    
    @admin.display(description='Lookup Link')
    def lookup_link(self, obj):
        lookupUri = ''
        if obj.keyword_main:
            lookupUri = self.request.build_absolute_uri(reverse('lookup', args=[obj.keyword_main]))
            lookupUri = format_html('<a href="{0}" target="_blank">{0}</a>', lookupUri)
        return lookupUri
    
    def get_import_formats(self):
        self.formats = [GameHelpFile]  # + self.formats
        return [f for f in self.formats if f().can_import()]
    
    def get_export_formats(self):
        self.formats = [GameHelpFile] # + self.formats
        return [f for f in self.formats if f().can_import()]

    def get_export_filename(self, request, queryset, file_format):
        filename = "%s.%s" % ("help",
                             file_format.get_extension())
        return filename

    def add_success_message(self, result, request):
        super().add_success_message(result, request)
        hu = HelpUpload.objects.create(
            upload_file=request.POST.get('original_file_name'),
            user_id=request.user.id
        )
        # Process export
        process_gamehelp_export.delay(hu.id)


class HelpUploadAdmin(admin.ModelAdmin):
    list_display = ('pk', 'created', 'upload_file', 'user', )

    class Meta:
        model = HelpUpload


admin.site.register(Entry, EntryAdmin)
admin.site.register(HelpUpload, HelpUploadAdmin)
