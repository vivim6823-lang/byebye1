from django.contrib import admin

from .models import AreaEntrega, Categoria, Produto


class ProdutoInline(admin.TabularInline):
    model = Produto
    extra = 1


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ("nome", "descricao")
    inlines = (ProdutoInline,)


@admin.register(Produto)
class ProdutoAdmin(admin.ModelAdmin):
    list_display = ("nome", "preco", "categoria", "disponivel")
    list_filter = ("categoria", "disponivel")
    search_fields = ("nome",)
    list_editable = ("disponivel",)
    actions = ("marcar_indisponiveis",)

    @admin.action(description="Marcar produtos selecionados como indisponíveis")
    def marcar_indisponiveis(self, request, queryset):
        queryset.update(disponivel=False)


@admin.register(AreaEntrega)
class AreaEntregaAdmin(admin.ModelAdmin):
    list_display = ("municipio", "codigo_ibge", "taxa_entrega")
    search_fields = ("municipio", "codigo_ibge")


admin.site.site_header = "Administração da Lanchonete"
