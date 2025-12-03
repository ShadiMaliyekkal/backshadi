from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import (
    PostViewSet,
    CommentViewSet,
    LikeViewSet,
    register_view,
    current_user,
)

router = DefaultRouter()
router.register(r'posts', PostViewSet, basename='post')
router.register(r'comments', CommentViewSet, basename='comment')
router.register(r'likes', LikeViewSet, basename='like')

urlpatterns = router.urls

# Add auth helpers
urlpatterns += [
    path('auth/register/', register_view, name='register'),
    path('auth/user/', current_user, name='current_user'),
]
