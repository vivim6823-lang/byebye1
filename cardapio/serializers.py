from rest_framework import serializers

from .models import Categoria, Produto


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
