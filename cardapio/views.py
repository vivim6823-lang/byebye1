from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from .models import Categoria, Produto
from .serializers import CategoriaSerializer, ProdutoSerializer


class CategoriaViewSet(ModelViewSet):
    queryset = Categoria.objects.all().order_by("pk")
    serializer_class = CategoriaSerializer
    search_fields = ("nome",)

    @action(detail=True, methods=["get"])
    def produtos(self, request, pk=None):
        categoria = self.get_object()
        produtos = (
            Produto.objects.filter(categoria=categoria)
            .select_related("categoria")
            .order_by("pk")
        )
        page = self.paginate_queryset(produtos)
        if page is not None:
            serializer = ProdutoSerializer(
                page,
                many=True,
                context=self.get_serializer_context(),
            )
            return self.get_paginated_response(serializer.data)
        return Response(serializer.data)


class ProdutoViewSet(ModelViewSet):
    queryset = Produto.objects.all().order_by("pk")
    serializer_class = ProdutoSerializer
    search_fields = ("nome",)

    def get_queryset(self):
        queryset = super().get_queryset().select_related("categoria")
        disponivel = self.request.query_params.get("disponivel")

        if disponivel is None:
            return queryset

        disponivel = disponivel.lower()
        if disponivel not in {"true", "false"}:
            raise ValidationError(
                {"disponivel": "Informe 'true' ou 'false' para filtrar produtos."}
            )

        return queryset.filter(disponivel=disponivel == "true")
