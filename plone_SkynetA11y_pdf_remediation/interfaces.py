# -*- coding: utf-8 -*-
"""
Interfaces for SkynetA11y PDF Remediation.

``IPdfRemediationSettings`` is the plone.registry schema that replaces the
Django app's singleton ``PdfRemediationConfig`` model (and, before that, the
Odoo module's ``ir.config_parameter`` rows): one value per field, stored under
the ``plone_SkynetA11y_pdf_remediation.`` registry prefix, editable from the
Configuration Registry (``/portal_registry``). There is deliberately no
separate settings page, only the dashboard.

The defaults are the same ones the Django/Odoo builds shipped with, so nothing
has to be filled in for the dashboard to work.
"""

import re

from zope import schema
from zope.interface import Interface
from zope.publisher.interfaces.browser import IDefaultBrowserLayer

from plone_SkynetA11y_pdf_remediation import _


class IPlonePdfRemediationLayer(IDefaultBrowserLayer):
    """Marker interface that defines a browser layer for this add-on."""


class InvalidUrl(schema.ValidationError):
    __doc__ = _("Enter a valid URL starting with http:// or https://.")


class InvalidEmail(schema.ValidationError):
    __doc__ = _("Enter a valid email address.")


_URL_RE = re.compile(r"^https?://\S+$", re.IGNORECASE)
_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def is_http_url(value):
    """Constraint: blank, or an http(s) URL."""
    if value and not _URL_RE.match(value):
        raise InvalidUrl(value)
    return True


def is_email(value):
    """Constraint: blank, or something shaped like an email address."""
    if value and not _EMAIL_RE.match(value):
        raise InvalidEmail(value)
    return True


class IPdfRemediationSettings(Interface):
    """Settings for the SkynetA11y PDF Remediation dashboard."""

    # -- api_base_url ----------------------------------------------------------
    api_base_url = schema.TextLine(
        title=_("API base URL"),
        description=_("Origin of the SkynetA11y PDF Remediation backend service."),
        default="https://livepdfapi.skynettechnologies.us",
        required=True,
    )

    # -- provision_api_key -----------------------------------------------------
    provision_api_key = schema.TextLine(
        title=_("Provision API key"),
        description=_(
            "X-Api-Key used to provision/sign in the account. Required for "
            "the dashboard to work unless Session URL is set instead. "
            "SECURITY: with no server-side proxy this value is printed into "
            "window.AIOPDF_CONFIG and is visible to anyone who views the "
            "dashboard page's source. Set Session URL to your own "
            "server-side sign-in endpoint if that is not acceptable for "
            "your deployment - see README.md."
        ),
        default="PDF-REMEDATION-PLAN-CHECK",
        required=False,
    )

    # -- account_name / account_email / website --------------------------------
    account_name = schema.TextLine(
        title=_("Account name"),
        description=_(
            "Name the account is registered under. Leave blank to let the "
            "on-screen dialog ask on first use (pre-filled from the signed-in "
            "user's name)."
        ),
        default="",
        required=False,
    )

    account_email = schema.TextLine(
        title=_("Account email"),
        description=_(
            "Address the account is provisioned under. Leave blank to let "
            "the on-screen dialog ask; fill in both this and Website to pin "
            "the account and skip the dialog entirely."
        ),
        default="",
        required=False,
        constraint=is_email,
    )

    website = schema.TextLine(
        title=_("Website"),
        description=_("Site the account is registered against."),
        default="",
        required=False,
    )

    # -- plan_id / country -----------------------------------------------------
    plan_id = schema.TextLine(
        title=_("Plan ID"),
        description=_("Sent on registration."),
        default="free",
        required=False,
    )

    country = schema.TextLine(
        title=_("Country"),
        description=_("Two-letter country code recorded on the account."),
        default="US",
        required=False,
        max_length=2,
    )

    # -- dashboard_url / upgrade_url -------------------------------------------
    dashboard_url = schema.TextLine(
        title=_("Dashboard URL"),
        description=_("Dashboard the coverage modal's upgrade button links to."),
        default="https://ada.skynettechnologies.us",
        required=False,
        constraint=is_http_url,
    )

    upgrade_url = schema.TextLine(
        title=_("Upgrade URL"),
        description=_(
            "Autologin link for the upgrade button. Blank derives it from "
            "the website."
        ),
        default="",
        required=False,
        constraint=is_http_url,
    )

    # -- active_domain ---------------------------------------------------------
    active_domain = schema.TextLine(
        title=_("Active domain"),
        description=_(
            "Domain the Website Scan tab crawls. Blank uses the connected "
            "account's own domain."
        ),
        default="",
        required=False,
    )

    # -- session_url / csrf_token ----------------------------------------------
    session_url = schema.TextLine(
        title=_("Session URL"),
        description=_(
            "Point at your own server-side sign-in endpoint instead of "
            "shipping the provisioning API key to the browser. When set, "
            "sign-in is a single POST to it and Provision API Key above is "
            "never used or shipped to the browser."
        ),
        default="",
        required=False,
        constraint=is_http_url,
    )

    csrf_token = schema.TextLine(
        title=_("CSRF token"),
        description=_(
            "CSRF token for the Session URL POST above, when that endpoint "
            "requires one."
        ),
        default="",
        required=False,
    )

    # -- initial_tab -----------------------------------------------------------
    initial_tab = schema.Choice(
        title=_("Initial tab"),
        description=_("Tab to open on load. Blank honours ?tab= in the URL."),
        vocabulary="plone_SkynetA11y_pdf_remediation.tabs",
        default=None,
        required=False,
    )

    # -- token_key -------------------------------------------------------------
    token_key = schema.TextLine(
        title=_("Token storage key"),
        description=_(
            "localStorage key the session token is cached under in the browser."
        ),
        default="aiopdf_token",
        required=False,
    )
