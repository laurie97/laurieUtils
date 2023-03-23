from django.urls import reverse

from .pages.homepage import TLevelHomePage
from .pages.starts_and_providers_overview import StartsAndProvidersOverview
from .pages.starts_and_providers_growth import StartsAndProvidersGrowthAnalysis
from .pages.outcomes_learner_status import OutcomesLearnerStatus
from .pages.grades_tlevel_comparison import GradesTLevelComparison
from .pages.grades_component_comparison import GradesComponentComparison
from .pages.grades_cohort_comparison import GradesCohortComparison
from .pages.grades_public_external import GradesPublicDataExternal

from .pages.diversity_gender import DiversityGender

from ifa_standards_rms.apps.views.ui3.bokeh.views import BaseBokehPageView


class TLevelDashboardBasePageView(BaseBokehPageView):
    def __init__(self):
        super().__init__()
        self.page_nav_dict = {
            'T Level Dashboard': {'Home Page': ''},
            'Starts and Providers': {
                'Current Overview': 'starts_and_providers/current_overview',
                'Growth Analysis': 'starts_and_providers/growth_analysis',
            },
            'Outcomes': {'Learner Status': 'outcomes/learner_status'},
            'TQ Grades': {
                'Compare T Levels': 'grades/tlevel_comparison',
                'Compare Components': 'grades/component_comparison',
                'Compare Cohorts': 'grades/cohort_comparison',
                'Public Data (External)': 'grades/external_public_data',
            },
            'Diversity and Inclusion': {'Gender Diversity': 'diversity/gender'},
        }
        self.set_guidance_warning('restricted')
        self.dash_name = 'T Level Dashboard'

    def get_full_url(self, url):
        full_url = reverse('views:bokeh:tlevel-dashboard:default')
        return f'{full_url}{url}'


class TLevelHomePageView(TLevelDashboardBasePageView):
    def __init__(self):
        super().__init__()
        self.current_section = 'T Level Dashboard'
        self.current_page = 'Homepage'
        self.page_class = TLevelHomePage
        self.homepage_nav_dict = {
            section: pages
            for section, pages in self.page_nav_dict.items()
            if section != 'T Level Dashboard'
        }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['homepage_nav'] = self.get_page_nav(self.homepage_nav_dict)
        return context


class StartsAndProvidersOverviewView(TLevelDashboardBasePageView):
    def __init__(self):
        super().__init__()
        self.current_section = 'Starts And Providers'
        self.current_page = 'Current Overview'
        self.page_class = StartsAndProvidersOverview


class StartsAndProvidersGrowthAnalysisView(TLevelDashboardBasePageView):
    def __init__(self):
        super().__init__()
        self.current_section = 'Starts and Providers'
        self.current_page = 'Growth Analysis'
        self.page_class = StartsAndProvidersGrowthAnalysis


class OutcomesLearnerStatusView(TLevelDashboardBasePageView):
    def __init__(self):
        super().__init__()
        self.current_section = 'Outcomes'
        self.current_page = 'Learner Status'
        self.page_class = OutcomesLearnerStatus


class GradesTLevelComparisonView(TLevelDashboardBasePageView):
    def __init__(self):
        super().__init__()
        self.current_section = 'TQ Grades'
        self.current_page = 'Compare Grades Between T Levels'
        self.page_class = GradesTLevelComparison


class GradesComponentComparisonView(TLevelDashboardBasePageView):
    def __init__(self):
        super().__init__()
        self.current_section = 'TQ Grades'
        self.current_page = 'Compare Grades Between Components'
        self.page_class = GradesComponentComparison


class GradesCohortComparisonView(TLevelDashboardBasePageView):
    def __init__(self):
        super().__init__()
        self.current_section = 'TQ Grades'
        self.current_page = 'Compare Grades Between Cohorts'
        self.page_class = GradesCohortComparison


class GradesPublicDataExternalView(TLevelDashboardBasePageView):
    def __init__(self):
        super().__init__()
        self.current_section = 'TQ Grades'
        self.current_page = 'Public Data (External)'
        self.page_class = GradesPublicDataExternal
        self.set_guidance_warning('public')


class DiversityGenderStatusView(TLevelDashboardBasePageView):
    def __init__(self):
        super().__init__()
        self.current_section = 'Diversity and Inclusion'
        self.current_page = 'Gender Diversity'
        self.page_class = DiversityGender
