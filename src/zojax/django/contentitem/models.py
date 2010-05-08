from autoslug.fields import AutoSlugField
from django.db import models
from django.utils.translation import ugettext_lazy as _
import datetime


class ContentItemManager(models.Manager):
    
    def published(self):
        return super(ContentItemManager, self).get_query_set().filter(published=True) 


class ContentItem(models.Model):
    
    title = models.CharField(max_length=300)
    slug = AutoSlugField(populate_from='title', verbose_name=_(u"Slug"), always_update=True)

    published = models.BooleanField(default=False)
    published_on = models.DateTimeField(null=True, blank=True)

    created_on = models.DateTimeField(default=datetime.datetime.now)

    objects = ContentItemManager()

    def __unicode__(self):
        return self.title

    def save(self, *args, **kwargs):
        if self.published and not self.published_on:
            self.published_on = datetime.datetime.now()
        if not self.published:
            self.published_on = None

        super(ContentItem, self).save(*args, **kwargs)

    class Meta:
        abstract = True
        