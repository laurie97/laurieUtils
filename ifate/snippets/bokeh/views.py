from bokeh.resources import CDN
from django.urls import reverse
from django.views.generic.base import TemplateView
from marko.ext.gfm import gfm
import logging
from csp.decorators import csp_replace, csp_update

logger = logging.getLogger(__name__)


def _make_dash_url_title(section, page):
    url = reverse('views:technical-demo-2', kwargs={'section': section, 'page': page})
    return (url, page)


class BaseBokehPageView(TemplateView):
    template_name = 'ui3/bokeh/charts.html'

    def __init__(self):
        super().__init__()
        self.page_nav_dict = {}
        self.set_guidance_warning('internal')
        self.dash_name = None
        self.current_section = None
        self.current_page = None

    @csp_update(SCRIPT_SRC="'unsafe-eval'")
    @csp_replace(STYLE_SRC="'self' 'unsafe-inline'", IMG_SRC="'self' data:")
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_full_url(self, url):
        full_url = url
        return full_url

    def get_page_nav(self, page_nav_dict=None):
        """
        Convert a page nav dictionary to a page nav list that can be looped over in html code
        Page nav dict has form {section: {page: url}}
        """

        if not page_nav_dict:
            page_nav_dict = self.page_nav_dict

        page_nav = [
            [section, [(self.get_full_url(url), page) for page, url in pages.items()]]
            for section, pages in page_nav_dict.items()
        ]

        return page_nav

    def set_guidance_warning(self, guidance_level):
        if guidance_level not in ['internal', 'restricted', 'public']:
            raise ValueError(
                "guidance_level has to be 'internal', 'restricted' or 'public'"
            )

        self.guidance_warning = guidance_level

    def log_dash_use(self):
        """ function to log use of dashboards to azure, focus on using values
        from the context that is pulled together to get the page
        """
        req_attr = ['dash_name', 'current_section', 'current_page']
        for attr in req_attr:
            if getattr(self, attr) is None:
                raise TypeError(f'{attr} value not set, please assign value')

        dash_details = {
            'custom_dimensions': {
                'product_type': 'Dashboard',
                'product_name': self.dash_name,
                'dash_page': self.current_page,
                'url': self.request.path,
                'user': self.request.user.get_full_name(),
                'superuser': self.request.user.is_superuser,
                'dash_section': self.current_section,
            }
        }

        logger.info(
            f'Dashboard Run: {self.dash_name} - {self.current_page}', extra=dash_details
        )

    def get_context_data(self, **kwargs):
        # log dash usage
        self.log_dash_use()

        page_class = self.page_class

        script, div, page_title, description = page_class().generate_bokeh_page()

        if script is None:
            script = ''

        if div is None:
            div = ''

        content = gfm.convert(description)

        page_nav = self.get_page_nav()
        context = {
            'script': script,
            'chart': div,
            'content': content,
            'nav': page_nav,
            'section': self.current_section,
            'page': self.current_page,
            'guidance_warning': self.guidance_warning,
            'page_title': page_title,
        }

        return context
