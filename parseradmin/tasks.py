from django.conf import settings

from django_rq import job

from parseradmin.models import Entry, HelpUpload

@job
def process_gamehelp_export(upload_id=None):
    from parseradmin.admin import EntryResource
    from parseradmin.formats import GameHelpFileFormat

    data = EntryResource().export(Entry.objects.all())
    export_data = GameHelpFileFormat.export_set(data)

    with open(settings.MEDIA_ROOT + '/help_export.txt', 'w', encoding='UTF8', newline='') as f:
        f.write(export_data)

    if upload_id:
        # Mark upload as processed
        help_upload_obj = HelpUpload.objects.get(pk=id)
        help_upload_obj.processed = True
        help_upload_obj.save()
