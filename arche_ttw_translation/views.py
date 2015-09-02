from copy import copy

from arche.interfaces import IRoot
from arche.views.base import BaseForm
from arche.views.base import BaseView
from pyramid.httpexceptions import HTTPForbidden
from pyramid.httpexceptions import HTTPFound
import colander
from pyramid.decorator import reify

from arche_ttw_translation import PERM_EDIT_TRANSLATION
from arche_ttw_translation.interfaces import ITranslations
from arche_ttw_translation.models import get_registered_ttwt


class TranslationsView(BaseView):

    @reify
    def current_keys(self):
        return frozenset(get_registered_ttwt(self.request).keys())

    def __call__(self):
        ttwt = ITranslations(self.context)
        if 'add' in self.request.POST:
            lang = self.request.POST.get('lang')
            if len(lang) > 5:
                raise HTTPForbidden("Too long")
            ttwt[lang] = {}
            return HTTPFound(location = self.request.url)
        return {'ttwt': ttwt}


@colander.deferred
def edit_translations_title(node, kw):
    view = kw['view']
    return "Edit translations: %s" % view.lang


class EditTranslations(BaseForm):

    @property
    def lang(self):
        return self.request.GET.get('lang', None)

    @property
    def ttwt(self):
        return ITranslations(self.context)

    def get_schema(self):
        class EditTranslationsSchema(colander.Schema):
            translations = colander.Schema(title = edit_translations_title)
        schema = EditTranslationsSchema()        
        for (k, v) in get_registered_ttwt(self.request).items():
            schema['translations'].add(colander.SchemaNode(colander.String(),
                                                           name = k,
                                                           title = v and v or k,
                                                           description = "ID: %s" % k,
                                                           missing = ""))
        return schema

    def appstruct(self):
        return {'translations': dict(self.ttwt.get(self.lang, {}))}

    def save_success(self, appstruct):
        for (k, v) in copy(appstruct['translations']).items():
            if not v:
                del appstruct['translations'][k]
        self.ttwt[self.lang] = appstruct['translations']
        self.flash_messages.add('Success')
        return HTTPFound(location = self.request.resource_url(self.context, 'ttw_translation'))

    def cancel_success(self, *args):
        return HTTPFound(location = self.request.resource_url(self.context, 'ttw_translation'))


def includeme(config):
    config.add_view(TranslationsView,
                    context = IRoot,
                    name="ttw_translation",
                    renderer = "arche_ttw_translation:templates/translations.pt",
                    permission = PERM_EDIT_TRANSLATION)
    config.add_view(EditTranslations,
                    context = IRoot,
                    name="edit_ttw_translation",
                    renderer = "arche:templates/form.pt",
                    permission = PERM_EDIT_TRANSLATION)
