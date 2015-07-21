# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.core.urlresolvers import NoReverseMatch
from django.utils.translation import override

from .test_base import AldrynFaqTest


class TestGetAbsoluteUrls(AldrynFaqTest):

    def test_category_urls(self):

        with override('en'):
            category_1_url = self.category1.get_absolute_url()
            category_2_url = self.category2.get_absolute_url()

        self.assertEquals('/en/faq/1-example/', category_1_url)
        # category2 doesn't exist EN, so this should fallback to DE
        self.assertEquals('/en/faq/2-beispiel2/', category_2_url)

        with override('de'):
            category_1_url = self.category1.get_absolute_url()
            category_2_url = self.category2.get_absolute_url()

        self.assertEquals('/de/faq/1-beispiel/', category_1_url)
        self.assertEquals('/de/faq/2-beispiel2/', category_2_url)

        # Now, test that we can override the context with the language parameter
        with override('en'):
            category_1_url = self.category1.get_absolute_url(language="de")
            category_2_url = self.category2.get_absolute_url(language="de")

        self.assertEquals('/de/faq/1-beispiel/', category_1_url)
        self.assertEquals('/de/faq/2-beispiel2/', category_2_url)

        # For completeness, do the other way too
        with override('de'):
            category_1_url = self.category1.get_absolute_url(language="en")
            category_2_url = self.category2.get_absolute_url(language="en")

        self.assertEquals('/en/faq/1-example/', category_1_url)
        # category2 doesn't exist EN, so this should fallback to DE
        self.assertEquals('/en/faq/2-beispiel2/', category_2_url)

    def test_category_urls_fallbacks(self):
        category_1 = self.category1
        category_2 = self.category2

        # category 2 is not translated in english
        # so given our test fallback config
        # this should fallback to the german category
        self.assertEqual(
            category_2.get_absolute_url("en"),
            "/en/faq/2-beispiel2/"
        )

        # category 1 is not translated in french
        # so given our test fallback config
        # this should fallback to the english category
        self.assertEqual(
            category_1.get_absolute_url("fr"),
            "/fr/faq/1-example/"
        )

        with self.assertRaises(NoReverseMatch):
            # this should raise a NoRerverseMatch error
            # because category 2 is not translated in french
            # so it falls back to english which also does not exist
            category_2.get_absolute_url("fr")

    def test_question_urls(self):
        question_1_pk = self.question1.pk
        question_2_pk = self.question2.pk

        with override('en'):
            question_1 = self.reload(self.question1)
            question_1_url = question_1.get_absolute_url()

            question_2 = self.reload(self.question2)
            question_2_url = question_2.get_absolute_url()

        self.assertEquals('/en/faq/1-example/{pk}/'.format(pk=question_1_pk), question_1_url)
        self.assertEquals('/en/faq/2-beispiel2/{pk}/'.format(pk=question_2_pk), question_2_url)

        with override('de'):
            question_1 = self.reload(self.question1)
            question_1_url = question_1.get_absolute_url()

            question_2 = self.reload(self.question2)
            question_2_url = question_2.get_absolute_url()

        self.assertEquals('/de/faq/1-beispiel/{pk}/'.format(pk=question_1_pk), question_1_url)
        self.assertEquals('/de/faq/2-beispiel2/{pk}/'.format(pk=question_2_pk), question_2_url)

    def test_question_urls_fallbacks(self):
        question_1 = self.question1
        question_1_pk = self.question1.pk

        question_2 = self.question2
        question_2_pk = self.question2.pk

        # question 2 is not translated in english
        # so given our test fallback config
        # this should fallback to the german category
        self.assertEqual(
            question_2.get_absolute_url("en"),
            "/en/faq/2-beispiel2/{pk}/".format(pk=question_2_pk)
        )

        # question 1 is not translated in french
        # so given our test fallback config
        # this should fallback to the english category
        self.assertEqual(
            question_1.get_absolute_url("fr"),
            "/fr/faq/1-example/{pk}/".format(pk=question_1_pk)
        )

        with self.assertRaises(NoReverseMatch):
            # this should raise a NoRerverseMatch error
            # because category 2 is not translated in french
            # so it falls back to english which also does not exist
            question_2.get_absolute_url("fr")
