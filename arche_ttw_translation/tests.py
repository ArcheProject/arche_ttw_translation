from unittest import TestCase

from pyramid import testing
from zope.interface.verify import verifyClass
from zope.interface.verify import verifyObject
from BTrees.OOBTree import OOBTree
from arche.testing import barebone_fixture

from arche_ttw_translation.interfaces import ITranslations


class TranslationsTests(TestCase):
    
    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()

    @property
    def _cut(self):
        from arche_ttw_translation.models import Translations
        return Translations

    def test_verify_class(self):
        self.failUnless(verifyClass(ITranslations, self._cut))

    def test_verify_object(self):
        self.failUnless(verifyObject(ITranslations, self._cut(testing.DummyModel())))

    def test_setitem(self):
        obj = self._cut(testing.DummyModel())
        obj['lang'] = {'one': 'two'}
        self.assertIsInstance(obj['lang'], OOBTree)

    def test_setitem_bad_value(self):
        obj = self._cut(testing.DummyModel())
        try:
            obj['lang'] = 1
            self.fail()
        except ValueError:
            pass

    def test_translate(self):
        request = testing.DummyRequest()
        obj = self._cut(testing.DummyModel())
        obj['sv'] = {'hello': 'Hej'}
        self.assertEqual(obj('hello', request, lang = 'sv'), 'Hej')


class IntegrationTests(TestCase):

    def setUp(self):
        self.config = testing.setUp(request = testing.DummyRequest())
        self.config.include('arche_ttw_translation')

    def tearDown(self):
        testing.tearDown()

    def test_adapter_registration(self):
        root = barebone_fixture(self.config)
        self.failUnless(ITranslations(root, None))

    def test_register_and_call_behaviour_are_the_same(self):
        from arche_ttw_translation.models import Translatable
        t = Translatable()
        t('one', 'One')
        t('Two')
        self.config.register_ttwt(t)
        root = barebone_fixture(self.config)
        tr = ITranslations(root)
        self.assertEqual(tr('one', 'One'), 'One')
        self.assertEqual(tr('Two'), 'Two')
