# -*- coding: utf-8 -*-
"""
Settings -> ``window.AIOPDF_CONFIG``.

The Odoo build did this in a qweb ``t-set aiopdf_config`` block and the Django
build in ``views.dashboard()``. Here it is a small, framework-free module so
the mapping can be unit-tested without a running Plone site.

Nothing in here talks to the remediation service: every request the dashboard
makes goes straight from the browser to ``api_base_url``, exactly as in the
Odoo and Django builds.
"""

import json

from zope.schema import getFieldNamesInOrder

from plone_SkynetA11y_pdf_remediation.interfaces import IPdfRemediationSettings

SETTINGS_PREFIX = "plone_SkynetA11y_pdf_remediation"


def read_settings(registry):
    """Return every setting as ``{field_name: value}``.

    Missing records (add-on not installed / not upgraded yet) and empty values
    fall back to the schema default, the way ``PdfRemediationConfig.get_solo()``
    fell back to the model defaults. Blank/None values come back as ``''``.
    """
    values = {}
    for name in getFieldNamesInOrder(IPdfRemediationSettings):
        default = IPdfRemediationSettings[name].default
        value = registry.get("{}.{}".format(SETTINGS_PREFIX, name), default)
        values[name] = "" if value is None else value
    return values


def build_config(settings, fullname="", username="", email="", host=""):
    """Build the dict that is printed into ``window.AIOPDF_CONFIG``.

    Same keys and same fallbacks as ``views.dashboard()`` in the Django app:
    the account name/email fall back to the signed-in user's own details, and
    ``accountKey`` fingerprints the cached session token to this deployment
    (Odoo used the database name, Django ``request.get_host()``; here it is
    the site's host[:port]).
    """
    return {
        "apiBaseUrl": settings["api_base_url"],
        "provisionApiKey": settings["provision_api_key"],
        "accountName": settings["account_name"] or fullname or username,
        "accountEmail": settings["account_email"] or email or username,
        "website": settings["website"],
        "activeDomain": settings["active_domain"],
        "planId": settings["plan_id"],
        "country": settings["country"],
        "dashboardUrl": settings["dashboard_url"],
        "upgradeUrl": settings["upgrade_url"],
        "sessionUrl": settings["session_url"],
        "csrfToken": settings["csrf_token"],
        "initialTab": settings["initial_tab"],
        "tokenKey": settings["token_key"],
        "accountKey": host,
    }


def json_for_script(data):
    """JSON that is safe to print inside an inline ``<script>`` element.

    ``json.dumps`` alone is not enough: a value containing ``</script>`` (an
    account name, say) would end the script block early. Escaping ``<``, ``>``
    and ``&`` as unicode escapes keeps it valid JS *and* valid JSON.
    """
    return (
        json.dumps(data)
        .replace("<", "\\u003c")
        .replace(">", "\\u003e")
        .replace("&", "\\u0026")
        .replace("\u2028", "\\u2028")
        .replace("\u2029", "\\u2029")
    )
