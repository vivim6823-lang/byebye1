from decimal import Decimal
import json
from unittest.mock import Mock, patch

from django.contrib import admin
from django.contrib.auth import get_user_model
from django.test import SimpleTestCase, TestCase
from requests import Timeout
from rest_framework.authtoken.models import Token
from rest_framework.renderers import JSONRenderer
from rest_framework.test import APIClient, APITestCase

from .admin import AreaEntregaAdmin, CategoriaAdmin, ProdutoAdmin, ProdutoInline
from .models import AreaEntrega, Categoria, Produto
from .serializers import CategoriaSerializer, ProdutoSerializer


class AdminConfigurationTests(TestCase):
    def test_area_entrega_is_registered_in_admin(self):
        self.assertIsInstance(admin.site._registry[AreaEntrega], AreaEntregaAdmin)

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


class CardapioPageTests(TestCase):
    def test_homepage_renders_products_from_database(self):
        categoria = Categoria.objects.create(
            nome="Lanches",
            descricao="Feitos na hora",
        )
        Produto.objects.create(
            nome="X-Burger",
            preco=Decimal("18.90"),
            categoria=categoria,
        )

        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "X-Burger")
        self.assertContains(response, "R$ 18,90")
        self.assertContains(response, "Feitos na hora")
        self.assertContains(response, "images.unsplash.com")
        self.assertContains(response, "cardapio/css/cardapio.css")

    def test_each_menu_item_has_a_matching_photo_and_alt_text(self):
        beverages = Categoria.objects.create(nome="Bebidas")
        snacks = Categoria.objects.create(nome="Lanches")
        desserts = Categoria.objects.create(nome="Sobremesas")
        photo_by_product = {
            "Refrigerante lata": (
                "photo-1554866585-cd94860890b7",
                "Lata de refrigerante",
                beverages,
            ),
            "Suco natural": (
                "photo-1600271886742-f049cd451bba",
                "Copo de suco de laranja",
                beverages,
            ),
            "Água mineral": (
                "photo-1638688569176-5b6db19f9d2a",
                "Garrafa de água",
                beverages,
            ),
            "X-Burger": (
                "photo-1568901346375-23c9450c58cd",
                "Hambúrguer com queijo",
                snacks,
            ),
            "X-Salada": (
                "photo-1586816001966-79b736744398",
                "Hambúrguer com alface e tomate",
                snacks,
            ),
            "X-Bacon": (
                "photo-1700835880369-a8e1eb918474",
                "Hambúrguer com bacon, alface, tomate e queijo",
                snacks,
            ),
            "Batata frita": (
                "photo-1630384060421-cb20d0e0649d",
                "Cesta de batatas fritas",
                snacks,
            ),
            "Brownie": (
                "photo-1606313564200-e75d5e30476c",
                "Brownies de chocolate",
                desserts,
            ),
            "Pudim": (
                "photo-1792860462957-11334eabf81c",
                "Pudim com calda de caramelo",
                desserts,
            ),
            "Sorvete": (
                "photo-1497034825429-c343d7c6a68f",
                "Sorvete em casquinha",
                desserts,
            ),
        }
        for name, (_, _, categoria) in photo_by_product.items():
            Produto.objects.create(
                nome=name,
                preco=Decimal("5.00"),
                categoria=categoria,
            )

        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)
        for image_id, alt_text, _ in photo_by_product.values():
            self.assertContains(response, image_id)
            self.assertContains(response, f'alt="{alt_text}"')


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
        self.assertIn("/api/municipios/", schema_response.data["paths"])
        self.assertIn("/api/areas-entrega/", schema_response.data["paths"])
        self.assertEqual(swagger_response.status_code, 200)


class MunicipiosApiTests(APITestCase):
    @patch("cardapio.views.requests.get")
    def test_returns_municipios_from_ibge(self, mock_get):
        response_ibge = Mock()
        response_ibge.json.return_value = [
            {"id": 2604106, "nome": "Caruaru"},
            {"id": 2611606, "nome": "Recife"},
        ]
        mock_get.return_value = response_ibge

        response = self.client.get("/api/municipios/?uf=pe")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.data,
            {
                "uf": "PE",
                "total": 2,
                "municipios": [
                    {"codigo_ibge": 2604106, "nome": "Caruaru"},
                    {"codigo_ibge": 2611606, "nome": "Recife"},
                ],
            },
        )
        mock_get.assert_called_once_with(
            "https://servicodados.ibge.gov.br/api/v1/localidades/"
            "estados/PE/municipios",
            timeout=(3.05, 10),
        )
        response_ibge.raise_for_status.assert_called_once()

    @patch("cardapio.views.requests.get")
    def test_requires_valid_uf(self, mock_get):
        for url in ("/api/municipios/", "/api/municipios/?uf=", "/api/municipios/?uf=XX"):
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, 400)

        mock_get.assert_not_called()

    @patch("cardapio.views.requests.get")
    def test_returns_503_on_ibge_timeout(self, mock_get):
        mock_get.side_effect = Timeout

        response = self.client.get("/api/municipios/?uf=PE")

        self.assertEqual(response.status_code, 503)

    @patch("cardapio.views.requests.get")
    def test_returns_503_on_invalid_ibge_response(self, mock_get):
        response_ibge = Mock()
        response_ibge.json.return_value = {"erro": "indisponível"}
        mock_get.return_value = response_ibge

        response = self.client.get("/api/municipios/?uf=PE")

        self.assertEqual(response.status_code, 503)


class AreaEntregaApiTests(APITestCase):
    def setUp(self):
        user = get_user_model().objects.create_user(
            username="area-admin",
            password="test-password",
        )
        self.client.force_authenticate(user=user)

    @patch("cardapio.serializers.requests.get")
    def test_creates_area_for_existing_ibge_code(self, mock_get):
        ibge_response = Mock()
        ibge_response.status_code = 200
        ibge_response.json.return_value = {"id": 2611606, "nome": "Recife"}
        mock_get.return_value = ibge_response

        response = self.client.post(
            "/api/areas-entrega/",
            {
                "municipio": "Recife",
                "codigo_ibge": "2611606",
                "taxa_entrega": "7.50",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 201, response.data)
        self.assertEqual(response.data["codigo_ibge"], "2611606")
        self.assertTrue(
            AreaEntrega.objects.filter(
                municipio="Recife",
                codigo_ibge="2611606",
                taxa_entrega=Decimal("7.50"),
            ).exists()
        )
        mock_get.assert_called_once_with(
            "https://servicodados.ibge.gov.br/api/v1/localidades/"
            "municipios/2611606",
            timeout=(3.05, 10),
        )

    @patch("cardapio.serializers.requests.get")
    def test_rejects_nonexistent_ibge_code(self, mock_get):
        ibge_response = Mock()
        ibge_response.status_code = 200
        ibge_response.json.return_value = []
        mock_get.return_value = ibge_response

        response = self.client.post(
            "/api/areas-entrega/",
            {
                "municipio": "Município inexistente",
                "codigo_ibge": "9999999",
                "taxa_entrega": "7.50",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn(
            "O código IBGE 9999999 não foi encontrado.",
            str(response.data["codigo_ibge"]),
        )
        self.assertFalse(AreaEntrega.objects.exists())

    @patch("cardapio.serializers.requests.get")
    def test_returns_503_when_ibge_request_times_out(self, mock_get):
        mock_get.side_effect = Timeout

        response = self.client.post(
            "/api/areas-entrega/",
            {
                "municipio": "Recife",
                "codigo_ibge": "2611606",
                "taxa_entrega": "7.50",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 503)
        self.assertFalse(AreaEntrega.objects.exists())

    @patch("cardapio.serializers.requests.get")
    def test_rejects_code_with_invalid_format_without_calling_ibge(self, mock_get):
        response = self.client.post(
            "/api/areas-entrega/",
            {
                "municipio": "Recife",
                "codigo_ibge": "ABC",
                "taxa_entrega": "7.50",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("7 dígitos", str(response.data["codigo_ibge"]))
        mock_get.assert_not_called()

    @patch("cardapio.serializers.requests.get")
    def test_rejects_duplicate_ibge_code_without_calling_ibge(self, mock_get):
        AreaEntrega.objects.create(
            municipio="Recife",
            codigo_ibge="2611606",
            taxa_entrega=Decimal("7.50"),
        )

        response = self.client.post(
            "/api/areas-entrega/",
            {
                "municipio": "Recife novamente",
                "codigo_ibge": "2611606",
                "taxa_entrega": "8.00",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertTrue(response.data["codigo_ibge"])
        self.assertEqual(AreaEntrega.objects.count(), 1)
        mock_get.assert_not_called()
