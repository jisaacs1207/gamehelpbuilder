from django.conf import settings

from django_rq import job

from parseradmin.models import HelpUpload


@job
def process_gamehelp_export(id):
    from parseradmin.admin import EntryResource

    er = EntryResource()
    dataset = er.export()

    with open(settings.MEDIA_ROOT + '/help_export.csv', 'w', encoding='UTF8', newline='') as f:
        f.write(dataset.csv)

    # Mark upload as processed
    help_upload_obj = HelpUpload.objects.get(pk=id)
    help_upload_obj.processed = True
    help_upload_obj.save()
