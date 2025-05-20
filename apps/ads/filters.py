from django_filters import FilterSet, DateFilter, ModelMultipleChoiceFilter,CharFilter,ModelChoiceFilter, BooleanFilter, ChoiceFilter
from ads.models import Ad, ExchangeProposal
STATUS_CHOICES = [
    ('ожидает', 'ожидает'),
    ('принята', 'принята'),
    ('отклонена', 'отклонена'),
]

CONDITION_CHOICES = [
    ('новое', 'новое'),
    ('б/у', 'б/у')
]
class AdFilter(FilterSet):

    condition = ChoiceFilter(
        choices=CONDITION_CHOICES,
        empty_label="Все состояния",
        label='Состояние вещи'
    )

    class Meta:
        model = Ad
        fields = ['categories', 'title', 'description', 'condition']


class ExchangeFilter(FilterSet):
    # Фильтр по имени отправителя
    ad_sender = CharFilter(
        field_name='ad_sender__user__username',
        lookup_expr='icontains',
        label='Имя отправителя'
    )

    # Фильтр по имени получателя
    ad_receiver = CharFilter(
        field_name='ad_receiver__user__username',
        lookup_expr='icontains',
        label='Имя получателя'
    )

    # Фильтр по статусу
    status = ChoiceFilter(
        choices=STATUS_CHOICES,
        empty_label="Все статусы",
        label='Статус предложения'
    )
    class Meta:
        model = ExchangeProposal
        fields = ['status', 'ad_sender', 'ad_receiver']