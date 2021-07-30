from django.db import models
from django.utils.translation import gettext_lazy as _
# from django.contrib.postgres.fields import ArrayField
from django_better_admin_arrayfield.models.fields import ArrayField
from django.db.models import Q
from simple_history.models import HistoricalRecords
import textwrap
import re

class Entry(models.Model):
    
    class Restrictions(models.TextChoices):
        EVERYONE = '-1', _('Everyone')
        CLASS = '-2', _('Class')
        RACE = '-3', _('Race')
        CABAL = '-4', _('Cabal')
        PSALM = '-5', _('Psalm')
        LEVEL51 = '51', _('Level51')
        LEVEL52 = '52', _('Level52')
        LEVEL53 = '53', _('Level53')
        LEVEL54 = '54', _('Level54')
        LEVEL55 = '55', _('Level55')
        LEVEL56 = '56', _('Level56')
        LEVEL57 = '57', _('Level57')
        LEVEL58 = '58', _('Level58')
        LEVEL59 = '59', _('Level59')
        LEVEL60 = '60', _('Level60')
   
    restriction = models.CharField(
        max_length=2,
        choices=Restrictions.choices,
        default=Restrictions.EVERYONE,
    )
    restriction_type = models.CharField(max_length=255, blank=True, null=True)
    keyword_main = models.CharField(max_length=255, unique=True)
    keywords = ArrayField(models.CharField(max_length=200, unique=True), blank=True, null=True, default=list)
    syntax = ArrayField(models.CharField(max_length=255), blank=True, null=True, default=list)
    see_also = ArrayField(models.CharField(max_length=200), blank=True, null=True, default=list)
    description = models.TextField(blank=True, null=True)
    raw = models.TextField(blank=True, null=True)
    history = HistoricalRecords()

    class Meta:
        verbose_name_plural = _("Entries")
        ordering = ('keyword_main',)
        permissions = [
            ('can_import_entries', "Can Import Entries"),
            ('can_export_entries', "Can Export Entries")
        ]

    def __str__(self):
        restrictionLabel = ''
        for value, label in self.Restrictions.choices:
            if value == self.restriction:
                restrictionLabel = label
                break

        #return restrictionLabel + (' | ' + self.restriction_type if self.restriction_type else '') + (' | ' + self.keyword_main if self.keyword_main else '')
        return self.keyword_main

    def save(self, *args, **kwargs):
        if self.keywords:
            self.keywords = list(dict.fromkeys(self.keywords))
            self.keywords = [k.replace('~', '') for k in self.keywords if type(self).objects.filter(~Q(keyword_main = self.keyword_main) & (Q(keywords__contains=[k]) | Q(keyword_main = k)) ).count() == 0]
        if self.description:
            width = 77
            adjusted_description = self.description.replace('\r\n','\n')
            adjusted_description = re.split('\n{2,}', adjusted_description)            
            adjusted_description = ['\n'.join(textwrap.wrap(p.replace('\n',' '), width, break_long_words=False)) for p in adjusted_description]
            self.description = '\n\n'.join(adjusted_description).replace('~', '')
        if self.restriction_type:
            self.restriction_type = self.restriction_type.replace('~', '')
        if self.keyword_main:
            self.keyword_main = self.keyword_main.replace('~', '')
        if self.syntax:
            self.syntax = [s.replace('~', '') for s in self.syntax]
        if self.see_also:
            self.see_also = [s.replace('~', '') for s in self.see_also]

        super(type(self), self).save(*args, **kwargs)


class HelpUpload(models.Model):
    upload_file = models.CharField(max_length=255)
    user = models.ForeignKey('auth.User', related_name='uploaded_by', on_delete=models.CASCADE)
    processed = models.BooleanField(default=False)

    # Auto-updated created and updated times.
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = _("Help Imports")
        ordering = ('-created',)

