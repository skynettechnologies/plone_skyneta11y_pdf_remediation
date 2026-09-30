# -*- coding: utf-8 -*-
from zope.interface import provider
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary

from plone_SkynetA11y_pdf_remediation import _


@provider(IVocabularyFactory)
def tabs_vocabulary(context):
    """Tabs the dashboard can open on. (Blank = follow ?tab= in the URL.)"""
    return SimpleVocabulary(
        [
            SimpleTerm("upload", "upload", _("Upload")),
            SimpleTerm("scan", "scan", _("Website Scan")),
            SimpleTerm("remediated", "remediated", _("Remediated")),
        ]
    )
