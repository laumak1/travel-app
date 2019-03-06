import json

from django.conf import settings

from apps.home.models import SiteConfiguration
from apps.translations.models import Language, Translation


def get_translations(language):
    return {trans.message.message_id: trans.text for trans in Translation.objects.filter(language=language)}


def generate_messages():
    return {language.pk: get_translations(language) for language in Language.objects.all()}


def get_enabled_languages(config):
    return list(
        {
            'code': lang.pk,
            'flag': lang.flag.url if lang.flag else '',
            'name': lang.name
        } for lang in config.enabled_languages.all()
    )


def get_page_translations(page, add_content=False):
    if page is None:
        return {}
    translations = {}
    icon = page.icon.url if page.icon else None
    for translation in page.page_translations.all():
        translations[translation.language.pk] = {
            'slug': translation.slug,
            'title': translation.title,
            'icon': icon,
            'content': translation.text if add_content else None
        }
    return translations


def generate_const():
    return {}


def generate_manifest():
    site_config = SiteConfiguration.get_solo()
    site_default_lang = site_config.default_language
    config = {
        'enabled_languages': get_enabled_languages(site_config),
        'default_language': site_default_lang.code if site_default_lang else settings.DEFAULT_LANGUAGE,
    }

    js_vars = """
    window._app_messages = {};
    window._app_constants = {};
    window._app_conf = {}
    """.format(
        json.dumps(generate_messages()),
        json.dumps(generate_const()),
        json.dumps(config),
    )
    return js_vars
