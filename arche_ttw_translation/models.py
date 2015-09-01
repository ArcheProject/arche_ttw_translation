from __future__ import unicode_literals
from UserDict import IterableUserDict

from arche.interfaces import IRoot
from BTrees.OOBTree import OOBTree
from zope.component import adapter
from zope.interface import implementer

from arche_ttw_translation.interfaces import ITranslations


_marker = object()

@adapter(IRoot)
@implementer(ITranslations)
class Translations(IterableUserDict):

    def __init__(self, context):
        self.context = context

    def __call__(self, txt, request, lang = None, default = _marker):
        lang = lang and lang or request.localizer.locale_name
        default = default == _marker and txt or default
        return self.get(lang, {}).get(txt, default)

    @property
    def data(self):
        try:
            return self.context.__ttw_translations__
        except AttributeError:
            self.context.__ttw_translations__ = OOBTree()
            return self.context.__ttw_translations__

    def __setitem__(self, lang, translations):
        if not isinstance(translations, dict):
            raise ValueError("Must be a dict")
        self.data[lang] = OOBTree(translations)


def register_ttwt(config, translations):
    assert isinstance(translations, dict)
    if not hasattr(config.registry, '_ttwt'):
        config.registry._ttwt = []
    config.registry._ttwt.append(translations)

def get_registered_ttwt(request):
    results = {}
    for translations in getattr(request.registry, '_ttwt', ()):
        results.update(translations)
    return results

def includeme(config):
    config.registry.registerAdapter(Translations)
    config.add_directive('register_ttwt', register_ttwt)
