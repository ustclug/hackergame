from django.urls import path, include

from group.views import GroupAPI, GroupApplicationAPI, GroupMemberAPI
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register('', GroupAPI, basename='group')
urlpatterns = [
    path('', include(router.urls)),
    path('<int:group_id>/application/', GroupApplicationAPI.as_view()),
    path('<int:group_id>/application/<int:application_id>/', GroupApplicationAPI.as_view()),
    path('<int:group_id>/member/', GroupMemberAPI.as_view()),
    path('<int:group_id>/member/<int:user_id>/', GroupMemberAPI.as_view()),
]
