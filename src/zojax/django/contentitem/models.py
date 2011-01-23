from autoslug.fields import AutoSlugField
from django.db import models
from django.contrib.sites.models import Site
from django.utils.translation import ugettext_lazy as _
import datetime
from django.conf import settings
from django.db import models
from django.db.models.fields import FieldDoesNotExist


class CurrentSiteManager(models.Manager):
    "Use this to limit objects to those associated with the current site."
    
    __field_name = 'sites'
    __is_validated = False
    
    def __init__(self, field_name='sites'):
        super(CurrentSiteManager, self).__init__()
        self.__field_name = field_name
        self.__is_validated = False

    def get_query_set(self):
        if not self.__is_validated:
            try:
                self.model._meta.get_field(self.__field_name)
            except FieldDoesNotExist:
                raise ValueError("%s couldn't find a field named %s in %s." % \
                    (self.__class__.__name__, self.__field_name, self.model._meta.object_name))
            self.__is_validated = True
        
        return super(CurrentSiteManager, self).get_query_set().filter(models.Q(**{self.__field_name: Site.objects.get_current().id})
                                                                      #| models.Q(**{self.__field_name + '__isnull': True})
                                                                      )

    def get_query_set_all(self):
        return super(CurrentSiteManager, self).get_query_set()
        

class CurrentSiteModelMixin(models.Model):
    
    sites = models.ManyToManyField(Site, blank=True, related_name="%(app_label)s_%(class)s_related", default=[settings.SITE_ID])
    
    objects = CurrentSiteManager()
    
    class Meta:
        abstract = True
    
    def save(self, *args, **kwargs):
        super(CurrentSiteModelMixin, self).save(*args, **kwargs)

        requires_save = False
        if not len(self.sites.all()):
            self.sites = [Site.objects.get_current()]
            requires_save = True

        if requires_save:
            super(CurrentSiteModelMixin, self).save(*args, **kwargs)


class ContentItemManager(CurrentSiteManager):
    
    def published(self):
        return super(ContentItemManager, self).get_query_set().filter(published=True) 


class ContentItem(CurrentSiteModelMixin):
    
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
        