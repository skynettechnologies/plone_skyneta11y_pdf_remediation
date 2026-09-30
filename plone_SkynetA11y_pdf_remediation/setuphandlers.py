# -*- coding: utf-8 -*-
from plone.base.interfaces import INonInstallable
from zope.interface import implementer


@implementer(INonInstallable)
class HiddenProfiles(object):
    def getNonInstallableProfiles(self):
        """Hide the uninstall profile from the add-ons control panel."""
        return ["plone_SkynetA11y_pdf_remediation:uninstall"]

    def getNonInstallableProducts(self):
        return []
