from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse, NoReverseMatch
from django.db import models
from django.utils.translation import get_language, ugettext_lazy as _

from cms.models.fields import PlaceholderField
from cms.models.pluginmodel import CMSPlugin
from cms.utils.i18n import get_current_language, force_language

from hvad.manager import TranslationManager
from hvad.models import TranslatableModel, TranslatedFields
from hvad.utils import get_translation

from adminsortable.fields import SortableForeignKey
from adminsortable.models import Sortable

from djangocms_text_ckeditor.fields import HTMLField

from sortedm2m.fields import SortedManyToManyField


def get_slug_in_language(record, language):
    if not record:
        return None
    if language == record.language_code:
        return record.lazy_translation_getter('slug')
    else:  # hit db
        try:
            translation = get_translation(record, language_code=language)
        except models.ObjectDoesNotExist:
            return None
        else:
            return translation.slug


class RelatedManager(TranslationManager):
    def filter_by_language(self, language):
        return self.language(language)

    def filter_by_current_language(self):
        return self.filter_by_language(get_language())


class CategoryManager(TranslationManager):
    def get_categories(self, language):
        categories = self.language(language).prefetch_related('questions')

        for category in categories:
            category.count = (category.questions
            .filter_by_language(language).count())
        return sorted(categories, key=lambda x: -x.count)


class Category(TranslatableModel):
    translations = TranslatedFields(
        name=models.CharField(max_length=255),
        slug=models.SlugField(_('Slug'), max_length=255, blank=True,
                              help_text=_('Auto-generated. Clean it to have it re-created. '
                                          'WARNING! Used in the URL. If changed, the URL will change. ')),
    )

    objects = CategoryManager()

    class Meta:
        verbose_name = _('category')
        verbose_name_plural = _('categories')

    def __unicode__(self):
        return self.lazy_translation_getter('name', str(self.pk))

    def model_type_id(self):
        return ContentType.objects.get_for_model(self.__class__).id

    def get_absolute_url(self, language=None):
        language = language or get_current_language()
        slug = get_slug_in_language(self, language)
        with force_language(language):
            if not slug:  # category not translated in given language
                return '/%s/' % language
            kwargs = {'category_slug': slug}
            return reverse('aldryn_faq:faq-category', kwargs=kwargs)



class Question(TranslatableModel, Sortable):
    translations = TranslatedFields(
        title=models.CharField(_('Title'), max_length=255),
        answer_text=HTMLField(_('answer'))
    )
    category = SortableForeignKey(Category, related_name='questions')

    answer = PlaceholderField('faq_question_answer', related_name='faq_questions')
    is_top = models.BooleanField(default=False)

    objects = RelatedManager()

    class Meta(Sortable.Meta):
        verbose_name = _('question')
        verbose_name_plural = _('questions')

    def __unicode__(self):
        return self.lazy_translation_getter('title', str(self.pk))

    def model_type_id(self):
        return ContentType.objects.get_for_model(self.__class__).id

    def get_absolute_url(self, language=None):
        language = language or get_current_language()
        category = self.category
        try:
            translation = get_translation(self, language_code=language)
        except models.ObjectDoesNotExist:
            translation = None
        cat_slug = get_slug_in_language(category, language)
        if translation and cat_slug:
            with force_language(language):
                return reverse('aldryn_faq:faq-answer', args=(cat_slug, self.pk))
        else:
            return category.get_absolute_url(language)


class QuestionsPlugin(models.Model):
    questions = models.IntegerField(default=5, help_text=_('The number of questions to be displayed.'))

    def get_queryset(self):
        return Question.objects.filter_by_language(self.language)

    def get_questions(self):
        questions = self.get_queryset()
        return questions[:self.questions]

    class Meta:
        abstract = True


class QuestionListPlugin(CMSPlugin):
    questions = SortedManyToManyField(Question, limit_choices_to={'language': get_language})

    def __unicode__(self):
        return str(self.questions.count())

    def copy_relations(self, oldinstance):
        self.questions = oldinstance.questions.all()

    def get_questions(self):
        return self.questions.all()


class CategoryListPlugin(CMSPlugin):

    def copy_relations(self, oldinstance):
        for category in oldinstance.selected_categories.all():
            category.pk = None
            category.cms_plugin = self
            category.save()

    def get_categories(self):
        """
        By default, if no categories were chosen return all categories.
        Otherwise, return the chosen categories.
        """
        categories = Category.objects.get_categories(language=self.language)

        if self.selected_categories.exists():
            category_ids = self.selected_categories.values_list('category__pk', flat=True)
            # categories is a list, and a sorted one so no need for another db call.
            selected_categories = []
            for id in category_ids:
                category = next((x for x in categories if x.pk == id), None)
                if category:
                    selected_categories.append(category)
            return selected_categories
        return categories


class LatestQuestionsPlugin(CMSPlugin, QuestionsPlugin):
    def get_queryset(self):
        qs = super(LatestQuestionsPlugin, self).get_queryset()
        return qs.order_by('-id')


class SelectedCategory(models.Model):
    category = models.ForeignKey(to=Category, verbose_name=_('category'))
    position = models.PositiveIntegerField(verbose_name=_('position'), blank=True, null=True)
    cms_plugin = models.ForeignKey(to=CategoryListPlugin, related_name='selected_categories')

    class Meta:
        ordering = ['position']

    def __unicode__(self):
        return self.category.name


class TopQuestionsPlugin(CMSPlugin, QuestionsPlugin):
    def get_queryset(self):
        qs = super(TopQuestionsPlugin, self).get_queryset()
        return qs.filter(is_top=True)
