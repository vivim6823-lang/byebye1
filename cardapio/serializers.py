import requests
from django.core.validators import RegexValidator
from rest_framework import serializers
from rest_framework.exceptions import APIException
from rest_framework.validators import UniqueValidator

from .models import AreaEntrega, Categoria, Produto


class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = "__all__"


class ProdutoSerializer(serializers.ModelSerializer):
    preco = serializers.DecimalField(max_digits=8, decimal_places=2)
    categoria_nome = serializers.CharField(source="categoria.nome", read_only=True)

    class Meta:
        model = Produto
        fields = [
            "id",
            "nome",
            "preco",
            "disponivel",
            "categoria",
            "categoria_nome",
        ]

    def validate_preco(self, value):
        if value < 0:
            raise serializers.ValidationError("O preço não pode ser negativo.")
        return value


class IBGEServiceUnavailable(APIException):
    status_code = 503
    default_detail = "O serviço do IBGE está indisponível. Tente novamente mais tarde."
    default_code = "ibge_unavailable"


class AreaEntregaSerializer(serializers.ModelSerializer):
    codigo_ibge = serializers.CharField(
        max_length=7,
        validators=[
            RegexValidator(
                regex=r"^\d{7}$",
                message="Informe um código IBGE válido com 7 dígitos.",
            ),
            UniqueValidator(queryset=AreaEntrega.objects.all()),
        ],
    )

    class Meta:
        model = AreaEntrega
        fields = ["id", "municipio", "codigo_ibge", "taxa_entrega"]

    def validate_codigo_ibge(self, value):
        url = (
            "https://servicodados.ibge.gov.br/api/v1/localidades/"
            f"municipios/{value}"
        )
        try:
            response = requests.get(url, timeout=(3.05, 10))
        except requests.RequestException as exc:
            raise IBGEServiceUnavailable() from exc

        if response.status_code == 404:
            raise serializers.ValidationError(
                f"O código IBGE {value} não foi encontrado."
            )

        try:
            response.raise_for_status()
            municipio_ibge = response.json()
        except (requests.RequestException, ValueError) as exc:
            raise IBGEServiceUnavailable() from exc

        if municipio_ibge == []:
            raise serializers.ValidationError(
                f"O código IBGE {value} não foi encontrado."
            )

        if (
            not isinstance(municipio_ibge, dict)
            or str(municipio_ibge.get("id")) != value
            or not isinstance(municipio_ibge.get("nome"), str)
        ):
            raise IBGEServiceUnavailable(
                "O IBGE retornou uma resposta inválida. Tente novamente mais tarde."
            )

        return value
