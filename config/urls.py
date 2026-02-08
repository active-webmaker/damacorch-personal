from django.contrib import admin
from django.urls import path

from app_settings.views import AppSettingsPublicView
from core.views import HealthView

from accounts.views import LoginView, LogoutView, MeView, SignupView
from analysis.views import AnalysisResultDetailView, AnalysisResultCreateView, UserAnalysisResultsView, MypageView
from psy.views import PsyQuestionsView, PsySubmitView
from quests.views import HomeView, QuestBulkStatusView, QuestHistoryByDateView, QuestHistorySummaryView, QuestsView, QuestStatusView
from selfcheck.views import SelfCheckInitView, SelfCheckSubmitView
from sns_integration.views import MeSnsAccountsView, SnsChannelsView, SnsImportView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("health", HealthView.as_view()),
    path("api/app-settings/public", AppSettingsPublicView.as_view()),
    path("api/auth/signup", SignupView.as_view()),
    path("api/auth/login", LoginView.as_view()),
    path("api/auth/logout", LogoutView.as_view()),
    path("api/auth/me", MeView.as_view()),
    path("api/home", HomeView.as_view()),
    path("api/quests", QuestsView.as_view()),
    path("api/quests/bulk-status", QuestBulkStatusView.as_view()),
    path("api/quests/<int:userQuestId>", QuestStatusView.as_view()),
    path("api/quest-history", QuestHistoryByDateView.as_view()),
    path("api/quest-history/summary", QuestHistorySummaryView.as_view()),
    path("api/psy-test/questions", PsyQuestionsView.as_view()),
    path("api/psy-test/submit", PsySubmitView.as_view()),
    path("api/self-check", SelfCheckInitView.as_view()),
    path("api/self-check/submit", SelfCheckSubmitView.as_view()),
    path("api/analysis-results/<int:id>", AnalysisResultDetailView.as_view()),
    path("api/analysis-results", AnalysisResultCreateView.as_view()),
    path("api/users/<int:userId>/analysis-results", UserAnalysisResultsView.as_view()),
    path("api/mypage", MypageView.as_view()),
    path("api/sns/channels", SnsChannelsView.as_view()),
    path("api/me/sns-accounts", MeSnsAccountsView.as_view()),
    path("api/sns/import", SnsImportView.as_view()),
]
