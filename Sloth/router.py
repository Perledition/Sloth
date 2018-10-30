from todo.API.views import TodoViewSet
from rest_framework import routers

router = routers.DefaultRouter()
router.register('todo', TodoViewSet)
