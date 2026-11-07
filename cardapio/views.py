import requests
from django.shortcuts import render
from django.utils.text import slugify
from drf_spectacular.utils import (
    OpenApiParameter,
    OpenApiTypes,
    extend_schema,
    inline_serializer,
)
from rest_framework import serializers
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from .models import AreaEntrega, Categoria, Produto
from .serializers import AreaEntregaSerializer, CategoriaSerializer, ProdutoSerializer


FOTOS_POR_PRODUTO = {
    "refrigerante-lata": (
        "photo-1554866585-cd94860890b7",
        "Lata de refrigerante",
    ),
    "suco-natural": (
        "photo-1600271886742-f049cd451bba",
        "Copo de suco de laranja",
    ),
    "agua-mineral": (
        "photo-1638688569176-5b6db19f9d2a",
        "Garrafa de água",
    ),
    "x-burger": (
        "photo-1568901346375-23c9450c58cd",
        "Hambúrguer com queijo",
    ),
    "x-salada": (
        "photo-1586816001966-79b736744398",
        "Hambúrguer com alface e tomate",
    ),
    "x-bacon": (
        "photo-1700835880369-a8e1eb918474",
        "Hambúrguer com bacon, alface, tomate e queijo",
    ),
    "batata-frita": (
        "photo-1630384060421-cb20d0e0649d",
        "Cesta de batatas fritas",
    ),
    "brownie": (
        "photo-1606313564200-e75d5e30476c",
        "Brownies de chocolate",
    ),
    "pudim": (
        "photo-1792860462957-11334eabf81c",
        "Pudim com calda de caramelo",
    ),
    "sorvete": (
        "photo-1497034825429-c343d7c6a68f",
        "Sorvete em casquinha",
    ),
}
FOTOS_POR_CATEGORIA = {
    "bebidas": ("photo-1600271886742-f049cd451bba", "Bebida gelada"),
    "lanches": ("photo-1568901346375-23c9450c58cd", "Hambúrguer"),
    "sobremesas": ("photo-1497034825429-c343d7c6a68f", "Sobremesa"),
}
FOTO_PADRAO = ("photo-1568901346375-23c9450c58cd", "Prato da lanchonete")


def pagina_cardapio(request):
    categorias = Categoria.objects.prefetch_related("produto_set").order_by("nome")
    secoes = []

    for categoria in categorias:
        produtos = []
        fotos_categoria = FOTOS_POR_CATEGORIA.get(
            slugify(categoria.nome),
            FOTO_PADRAO,
        )
        for produto in categoria.produto_set.all():
            foto_id, foto_alt = FOTOS_POR_PRODUTO.get(
                slugify(produto.nome),
                fotos_categoria,
            )
            produtos.append({
                "produto": produto,
                "foto_alt": foto_alt,
                "foto_url": (
                    "https://images.unsplash.com/"
                    f"{foto_id}?auto=format&fit=crop&w=900&q=85"
                ),
            })
        secoes.append(
            {
                "categoria": categoria,
                "slug": f"{slugify(categoria.nome)}-{categoria.pk}",
                "produtos": produtos,
            }
        )

    return render(
        request,
        "cardapio/cardapio.html",
        {
            "secoes": secoes,
            "total_produtos": sum(len(secao["produtos"]) for secao in secoes),
        },
    )


VALID_UFS = {
    "AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO",
    "MA", "MT", "MS", "MG", "PA", "PB", "PR", "PE", "PI",
    "RJ", "RN", "RS", "RO", "RR", "SC", "SP", "SE", "TO",
}

MUNICIPIOS_RESPONSE = inline_serializer(
    name="MunicipiosResponse",
    fields={
        "uf": serializers.CharField(),
        "total": serializers.IntegerField(),
        "municipios": serializers.ListField(
            child=inline_serializer(
                name="Municipio",
                fields={
                    "codigo_ibge": serializers.IntegerField(),
                    "nome": serializers.CharField(),
                },
            )
        ),
    },
)
ERROR_RESPONSE = inline_serializer(
    name="MunicipiosError",
    fields={"detail": serializers.CharField()},
)


class MunicipiosView(APIView):
    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="uf",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                required=True,
                description="Sigla da unidade federativa, por exemplo PE.",
            )
        ],
        responses={
            200: MUNICIPIOS_RESPONSE,
            400: ERROR_RESPONSE,
            503: ERROR_RESPONSE,
        },
    )
    def get(self, request):
        uf = request.query_params.get("uf", "").strip().upper()
        if uf not in VALID_UFS:
            return Response(
                {"detail": "Informe uma UF válida no parâmetro 'uf'."},
                status=400,
            )

        url = (
            "https://servicodados.ibge.gov.br/api/v1/localidades/"
            f"estados/{uf}/municipios"
        )
        try:
            response = requests.get(url, timeout=(3.05, 10))
            response.raise_for_status()
            municipios_ibge = response.json()
        except (requests.RequestException, ValueError):
            return Response(
                {"detail": "Não foi possível consultar os municípios no IBGE."},
                status=503,
            )

        if not isinstance(municipios_ibge, list) or any(
            not isinstance(municipio, dict)
            or not isinstance(municipio.get("id"), int)
            or not isinstance(municipio.get("nome"), str)
            for municipio in municipios_ibge
        ):
            return Response(
                {"detail": "O IBGE retornou uma resposta inválida."},
                status=503,
            )

        municipios = [
            {"codigo_ibge": municipio["id"], "nome": municipio["nome"]}
            for municipio in municipios_ibge
        ]
        return Response(
            {
                "uf": uf,
                "total": len(municipios),
                "municipios": municipios,
            }
        )


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


class AreaEntregaViewSet(ModelViewSet):
    queryset = AreaEntrega.objects.all().order_by("pk")
    serializer_class = AreaEntregaSerializer
    search_fields = ("municipio", "codigo_ibge")
