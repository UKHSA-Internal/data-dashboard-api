from django.db.models import Manager

from cms.forms.models import FormPage

DEFAULT_FORM_PAGE_MANAGER = FormPage.objects


class CMSInterface:
    """This is the explicit interface from which the feedback API interacts with the CMS.
    Note that this is enforced via the architectural constraints of this codebase.

    It is intended that the feedback API calls for the data that it needs via model managers
    from the CMS through this abstraction only.

    Parameters:
    -----------
    form_page_manager : `FormPageManager`
        The model manager for the `FormPage` model belonging to the CMS
        Defaults to the concrete `FormPageManager` via `FormPage.objects`

    """

    def __init__(
        self,
        *,
        form_page_manager: Manager = DEFAULT_FORM_PAGE_MANAGER,
    ):
        self.form_page_manager = form_page_manager

    def get_form_page_manager(self):
        return self.form_page_manager
