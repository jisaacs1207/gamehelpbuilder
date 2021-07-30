from django.shortcuts import render
from .models import Entry
from django.db.models import Q
from django.http import JsonResponse, HttpResponse
from django.core.serializers import serialize
import json
from django.template import loader


def search(request, query):
    query = query.upper()
    entries = Entry.objects.filter(Q(keyword_main__contains=query) | Q(keywords__contains=[query]))
    serialized_entries = [dict({'id': s['pk']}, **s['fields']) for s in
                          serialize('python', entries, use_natural_foreign_keys=True)]
    array_keys = ['keywords', 'syntax', 'see_also']
    for item in serialized_entries:
        del item['raw']
        for ak in array_keys:
            item[ak] = json.loads(item[ak])
    return JsonResponse(serialized_entries, safe=False)


def lookup(request, query):
    query = query.upper()
    entry = Entry.objects.get(Q(keyword_main=query) | Q(keywords__contains=[query]))
    template = loader.get_template('lookup.html')
    context = {
        'entry': entry,
    }
    return HttpResponse(template.render(context, request))
