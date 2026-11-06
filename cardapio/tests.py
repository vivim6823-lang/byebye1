from decimal import Decimal
import json

from django.contrib import admin
from django.test import SimpleTestCase, TestCase
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient, APITestCase
from rest_framework.renderers import JSONRenderer
from django.contrib.auth import get_user_model

from .admin import CategoriaAdmin, ProdutoAdmin, ProdutoInline
from .models import Categoria, Produto
from .serializers import CategoriaSerializer, ProdutoSerializer


class AdminConfigurationTests(TestCase):
    def test_categoria_admin_has_product_inline(self):
        categoria_admin = admin.site._registry[Categoria]

        self.assertIsInstance(categoria_admin, CategoriaAdmin)
        self.assertIn(ProdutoInline, categoria_admin.inlines)
        self.assertIs(ProdutoInline.model, Produto)

    def test_product_admin_action_marks_selected_products_unavailable(self):
        categoria = Categoria.objects.create(nome="Lanches")
        produto_disponivel = Produto.objects.create(
            nome="Hambúrguer",
            preco=Decimal("18.50"),
            disponivel=True,
            categoria=categoria,
        )
        produto_nao_selecionado = Produto.objects.create(
            nome="Batata",
            preco=Decimal("9.00"),
            disponivel=True,
            categoria=categoria,
        )
        produto_admin = admin.site._registry[Produto]

        produto_admin.marcar_indisponiveis(
            request=None,
            queryset=Produto.objects.filter(pk=produto_disponivel.pk),
        )

        produto_disponivel.refresh_from_db()
        produto_nao_selecionado.refresh_from_db()
        self.assertFalse(produto_disponivel.disponivel)
        self.assertTrue(produto_nao_selecionado.disponivel)

    def test_admin_has_custom_header(self):
        self.assertEqual(admin.site.site_header, "Administração da Lanchonete")


class CategoriaSerializerTests(SimpleTestCase):
    def test_serializes_all_category_fields(self):
        categoria = Categoria(nome="Bebidas", descricao="Bebidas geladas")

        self.assertEqual(
            CategoriaSerializer(categoria).data,
            {"id": None, "nome": "Bebidas", "descricao": "Bebidas geladas"},
        )


class ProdutoSerializerTests(SimpleTestCase):
    def test_rejects_negative_price_with_clear_message(self):
        serializer = ProdutoSerializer(data={"preco": "-0.01"}, partial=True)

        self.assertFalse(serializer.is_valid())
        self.assertEqual(
            str(serializer.errors["preco"][0]),
            "O preço não pode ser negativo.",
        )

    def test_accepts_zero_price(self):
        serializer = ProdutoSerializer(data={"preco": "0.00"}, partial=True)

        self.assertTrue(serializer.is_valid(), serializer.errors)
        self.assertEqual(serializer.validated_data["preco"], Decimal("0.00"))

    def test_includes_category_name_in_json(self):
        categoria = Categoria(nome="Bebidas")
        produto = Produto(
            nome="Suco",
            preco=Decimal("4.50"),
            categoria=categoria,
        )

        content = JSONRenderer().render(ProdutoSerializer(produto).data)

        self.assertEqual(json.loads(content), {
            "id": None,
            "nome": "Suco",
            "preco": "4.50",
            "disponivel": True,
            "categoria": None,
            "categoria_nome": "Bebidas",
        })


class ProdutoViewSetTests(APITestCase):
    def setUp(self):
        self.categoria = Categoria.objects.create(nome="Lanches")
        self.outra_categoria = Categoria.objects.create(nome="Bebidas")
        Produto.objects.create(
            nome="Hambúrguer",
            preco=Decimal("18.50"),
            disponivel=True,
            categoria=self.categoria,
        )
        Produto.objects.create(
            nome="Batata",
            preco=Decimal("9.00"),
            disponivel=False,
            categoria=self.categoria,
        )
        Produto.objects.create(
            nome="Suco",
            preco=Decimal("5.00"),
            disponivel=True,
            categoria=self.outra_categoria,
        )

    def test_filters_products_by_availability(self):
        available = self.client.get("/api/produtos/?disponivel=true")
        unavailable = self.client.get("/api/produtos/?disponivel=false")

        self.assertEqual(available.status_code, 200)
        self.assertEqual(
            {product["nome"] for product in available.data["results"]},
            {"Hambúrguer", "Suco"},
        )
        self.assertTrue(
            all(product["disponivel"] for product in available.data["results"])
        )

        self.assertEqual(unavailable.status_code, 200)
        self.assertEqual(
            [product["nome"] for product in unavailable.data["results"]],
            ["Batata"],
        )
        self.assertTrue(
            all(
                not product["disponivel"]
                for product in unavailable.data["results"]
            )
        )

    def test_rejects_invalid_availability_filter(self):
        response = self.client.get("/api/produtos/?disponivel=talvez")

        self.assertEqual(response.status_code, 400)
        self.assertIn("Informe 'true' ou 'false'", str(response.data))

    def test_lists_products_for_category_with_category_name(self):
        response = self.client.get(
            f"/api/categorias/{self.categoria.pk}/produtos/"
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            {product["nome"] for product in response.data["results"]},
            {"Hambúrguer", "Batata"},
        )
        self.assertTrue(
            all(
                product["categoria_nome"] == "Lanches"
                for product in response.data["results"]
            )
        )

    def test_searches_products_by_name(self):
        response = self.client.get("/api/produtos/?search=batata")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            [product["nome"] for product in response.data["results"]],
            ["Batata"],
        )

    def test_product_list_is_paginated(self):
        for number in range(9):
            Produto.objects.create(
                nome=f"Produto {number}",
                preco=Decimal("1.00"),
                categoria=self.categoria,
            )

        response = self.client.get("/api/produtos/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 12)
        self.assertEqual(len(response.data["results"]), 10)
        self.assertIsNotNone(response.data["next"])

    def test_write_requires_authentication_and_token_allows_create(self):
        payload = {"nome": "Sobremesas"}
        anonymous_response = self.client.post(
            "/api/categorias/",
            payload,
            format="json",
        )
        self.assertEqual(anonymous_response.status_code, 401)

        user = get_user_model().objects.create_user(
            username="api-user",
            password="test-password",
        )
        token = Token.objects.create(user=user)
        authenticated_client = APIClient()
        authenticated_client.credentials(
            HTTP_AUTHORIZATION=f"Token {token.key}"
        )
        authenticated_response = authenticated_client.post(
            "/api/categorias/",
            payload,
            format="json",
        )

        self.assertEqual(authenticated_response.status_code, 201)
        self.assertEqual(authenticated_response.data["nome"], "Sobremesas")

    def test_token_endpoint_returns_user_token(self):
        get_user_model().objects.create_user(
            username="token-user",
            password="test-password",
        )

        response = self.client.post(
            "/api/token/",
            {"username": "token-user", "password": "test-password"},
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("token", response.data)


class ApiDocumentationTests(APITestCase):
    def test_schema_and_swagger_pages_are_available(self):
        schema_response = self.client.get("/api/schema/")
        swagger_response = self.client.get("/api/docs/")

        self.assertEqual(schema_response.status_code, 200)
        self.assertIn("openapi", schema_response.data)
        self.assertEqual(swagger_response.status_code, 200)
