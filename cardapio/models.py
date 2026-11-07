from django.core.validators import MinValueValidator
from django.db import models


class Categoria(models.Model):
    nome = models.CharField(max_length=100, unique=True)
    descricao = models.TextField(blank=True)

    def __str__(self):
        return self.nome


class Produto(models.Model):
    nome = models.CharField(max_length=150)
    preco = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0)],
    )
    disponivel = models.BooleanField(default=True)
    categoria = models.ForeignKey(Categoria, on_delete=models.PROTECT)

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=models.Q(preco__gte=0),
                name='produto_preco_nao_negativo',
            ),
        ]


class AreaEntrega(models.Model):
    municipio = models.CharField(max_length=100)
    codigo_ibge = models.CharField(max_length=7, unique=True)
    taxa_entrega = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0)],
    )

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=models.Q(taxa_entrega__gte=0),
                name="area_entrega_taxa_nao_negativa",
            ),
        ]

    def __str__(self):
        return self.municipio
