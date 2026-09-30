# -*- coding: utf-8 -*-
"""
The dashboard views.

``DashboardView`` is the Plone equivalent of ``views.dashboard()`` in the Django
app (and of the qweb page ``website/dashboard_page.xml`` in the Odoo module):
it resolves the settings, falls back to the signed-in user's own name/email,
prints the result into ``window.AIOPDF_CONFIG`` and renders the same markup
with the same static JS (config.js -> icons.js -> account.js -> api.js ->
app.js; the load order matters).

Nothing here talks to the remediation service itself - every request the
dashboard makes goes straight from the browser to ``api_base_url``.

Access control is enforced on the view itself (permission ``cmf.ManagePortal``,
i.e. Manager / Site Administrator - the counterpart of Django's "staff" and
Odoo's ``base.group_system``), so there is no way to reach the dashboard, or the
API key embedded in it, without being signed in as one.
"""

from importlib.metadata import PackageNotFoundError
from importlib.metadata import version as _dist_version
from plone import api
from plone.registry.interfaces import IRegistry
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from urllib.parse import urlparse
from zope.component import getUtility

from plone_SkynetA11y_pdf_remediation.config import build_config
from plone_SkynetA11y_pdf_remediation.config import json_for_script
from plone_SkynetA11y_pdf_remediation.config import read_settings

STATIC_NAME = "++plone++plone_SkynetA11y_pdf_remediation"

try:
    # Appended to every asset URL so a new release is never served from a
    # browser's or proxy's cached copy of the previous one.
    ASSET_VERSION = _dist_version("plone-SkynetA11y-pdf-remediation")
except PackageNotFoundError:  # running from a source checkout
    ASSET_VERSION = "dev"


class DashboardView(BrowserView):
    """Standalone dashboard page: ``<site>/@@pdf-remediation-dashboard``."""

    index = ViewPageTemplateFile("templates/dashboard.pt")

    def __call__(self):
        response = self.request.response
        # This page is a complete HTML document of its own (it is also framed
        # by the Site Setup entry below), so keep the site theme (Diazo) from
        # wrapping it in the site chrome, and allow same-origin framing
        # whatever the site-wide X-Frame-Options default is - the counterpart
        # of Django's @xframe_options_sameorigin.
        response.setHeader("X-Theme-Disabled", "True")
        response.setHeader("X-Frame-Options", "SAMEORIGIN")
        # The page carries the configured API key and the signed-in user's
        # details: never let a browser cache or shared proxy keep a copy.
        response.setHeader("Cache-Control", "no-store")
        return self.index()

    @property
    def static_url(self):
        return "{}/{}".format(self.context.absolute_url(), STATIC_NAME)

    @property
    def asset_version(self):
        return ASSET_VERSION

    @property
    def back_url(self):
        """Where the "Back to Plone" button goes: the site root."""
        return self.context.absolute_url()

    @property
    def config_json(self):
        registry = getUtility(IRegistry)
        settings = read_settings(registry)

        user = api.user.get_current()
        fullname = (user.getProperty("fullname", "") or "").strip()
        email = user.getProperty("email", "") or ""
        username = user.getUserName() or ""

        host = urlparse(self.context.absolute_url()).netloc

        return json_for_script(
            build_config(
                settings,
                fullname=fullname,
                username=username,
                email=email,
                host=host,
            )
        )


class DashboardAdminView(BrowserView):
    """The dashboard inside Plone's own chrome (Site Setup entry).

    Same idea as the Django app's admin-sidebar entry: the actual dashboard is
    embedded via a same-origin ``<iframe>`` pointing at the standalone route,
    so its CSS/JS never has to coexist with the site theme on one DOM, and the
    Plone session cookie carries over - no second sign-in.
    """

    index = ViewPageTemplateFile("templates/dashboard_admin.pt")

    def __call__(self):
        return self.index()

    @property
    def dashboard_url(self):
        return "{}/@@pdf-remediation-dashboard".format(self.context.absolute_url())
