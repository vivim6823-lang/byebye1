from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import (
    AreaEntregaViewSet,
    CategoriaViewSet,
    MunicipiosView,
    ProdutoViewSet,
)

router = DefaultRouter()
router.register("categorias", CategoriaViewSet)
router.register("produtos", ProdutoViewSet)
router.register("areas-entrega", AreaEntregaViewSet)

urlpatterns = [
    path("municipios/", MunicipiosView.as_view(), name="municipios"),
    *router.urls,
]
