import pytest
from django.contrib.auth.models import User
from django.test import RequestFactory, TestCase
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from ads.models import Ad, Category, ExchangeProposal
from ads.views import (
    AdList, AdCreate, AdUpdate, AdDelete,
    OffersList, UserThingList, ExchangeProposalList
)
from ads.forms import AdForm
from django.core.files.images import ImageFile
import tempfile
import shutil
from django.conf import settings
import os


# Фикстуры для тестов
@pytest.fixture
def user(db):
    return User.objects.create_user(username='testuser', password='testpass123')


@pytest.fixture
def auth_client(client, user):
    client.force_login(user)
    return client


@pytest.fixture
def rf():
    return RequestFactory()


@pytest.fixture
def category(db):
    return Category.objects.create(name='Test Category')


@pytest.fixture
def test_image():
    image = SimpleUploadedFile(
        name='test_image.jpg',
        content=b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x00\x00\x00\x21\xf9\x04\x01\x0a\x00\x01\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02\x4c\x01\x00\x3b',
        content_type='image/jpeg'
    )
    return image


@pytest.fixture
def ad(user, category, test_image):
    ad = Ad.objects.create(
        title='Test Ad',
        description='Test Description',
        condition='new',
        user=user,
        image=test_image
    )
    ad.categories.add(category)
    return ad


@pytest.fixture
def exchange_proposal(ad):
    ad_sender = Ad.objects.create(
        title='Sender Ad',
        description='Sender Description',
        condition='used',
        user=User.objects.create_user(username='sender', password='testpass123')
    )
    return ExchangeProposal.objects.create(
        ad_sender=ad_sender,
        ad_receiver=ad,
        comment='Test comment',
        status='ожидает'
    )


# Тесты для Ad Views
@pytest.mark.django_db
def test_ad_list_view(rf, user, ad):
    request = rf.get('/ads/')
    request.user = user
    response = AdList.as_view()(request)
    assert response.status_code == 200
    assert 'ads' in response.context_data
    assert ad in response.context_data['ads']


@pytest.mark.django_db
def test_ad_create_view(auth_client, category, test_image):
    url = reverse('ad_create')

    # GET запрос
    response = auth_client.get(url)
    assert response.status_code == 200

    # POST запрос
    data = {
        'title': 'New Test Ad',
        'description': 'New Test Description',
        'condition': 'excellent',
        'categories': [category.id],
        'image': test_image
    }
    response = auth_client.post(url, data)
    assert response.status_code == 302
    assert Ad.objects.filter(title='New Test Ad').exists()


@pytest.mark.django_db
def test_ad_update_view(auth_client, user, ad, category):
    url = reverse('ad_update', kwargs={'pk': ad.pk})

    # GET запрос
    response = auth_client.get(url)
    assert response.status_code == 200

    # POST запрос
    data = {
        'title': 'Updated Ad',
        'description': 'Updated Description',
        'condition': 'used',
        'categories': [category.id]
    }
    response = auth_client.post(url, data)
    assert response.status_code == 302
    ad.refresh_from_db()
    assert ad.title == 'Updated Ad'


@pytest.mark.django_db
def test_ad_delete_view(auth_client, user, ad):
    url = reverse('ad_delete', kwargs={'pk': ad.pk})

    # GET запрос
    response = auth_client.get(url)
    assert response.status_code == 200

    # POST запрос
    response = auth_client.post(url)
    assert response.status_code == 302
    assert not Ad.objects.filter(pk=ad.pk).exists()


# Тесты для OffersList
@pytest.mark.django_db
def test_offers_list_view(rf, user, ad):
    request = rf.get(f'/ads/{ad.pk}/offers/')
    request.user = user
    response = OffersList.as_view()(request, pk=ad.pk)
    assert response.status_code == 200
    assert 'ads' in response.context_data
    assert 'object' in response.context_data


# Тесты для UserThingList
@pytest.mark.django_db
def test_user_thing_list_view(rf, user, ad):
    request = rf.get('/ads/my_things/')
    request.user = user
    response = UserThingList.as_view()(request)
    assert response.status_code == 200
    assert ad in response.context_data['ads']


# Тесты для ExchangeProposalList
@pytest.mark.django_db
def test_exchange_proposal_list_view(rf, user, exchange_proposal):
    request = rf.get('/exchanges/')
    request.user = user
    response = ExchangeProposalList.as_view()(request)
    assert response.status_code == 200
    assert 'exchanges' in response.context_data
    assert exchange_proposal in response.context_data['exchanges']


# Тесты для функций offer_accept и offer_cancel
@pytest.mark.django_db
def test_offer_accept_view(auth_client, user, exchange_proposal):
    url = reverse('offer_accept', kwargs={'pk': exchange_proposal.pk})
    response = auth_client.post(url)
    assert response.status_code == 302
    exchange_proposal.refresh_from_db()
    assert exchange_proposal.status == 'принята'


@pytest.mark.django_db
def test_offer_cancel_view(auth_client, user, exchange_proposal):
    url = reverse('offer_cancel', kwargs={'pk': exchange_proposal.pk})
    response = auth_client.post(url)
    assert response.status_code == 302
    exchange_proposal.refresh_from_db()
    assert exchange_proposal.status == 'отклонена'


# Тест для функции offer_add
@pytest.mark.django_db
def test_offer_add_view(auth_client, user, ad):
    ad_sender = Ad.objects.create(
        title='Sender Ad',
        description='Sender Description',
        condition='used',
        user=user
    )
    url = reverse('offer_add', kwargs={'pk': ad.pk, 'obj': ad_sender.pk})
    response = auth_client.post(url, {'comment': 'Test comment'})
    assert response.status_code == 302
    assert ExchangeProposal.objects.filter(comment='Test comment').exists()


# Тесты на права доступа
@pytest.mark.django_db
def test_ad_update_permission(auth_client):
    other_user = User.objects.create_user(username='other', password='testpass123')
    ad = Ad.objects.create(
        title='Other Ad',
        description='Other Description',
        condition='new',
        user=other_user
    )
    url = reverse('ad_update', kwargs={'pk': ad.pk})
    response = auth_client.get(url)
    assert response.status_code == 403  # Forbidden


@pytest.mark.django_db
def test_ad_delete_permission(auth_client):
    other_user = User.objects.create_user(username='other', password='testpass123')
    ad = Ad.objects.create(
        title='Other Ad',
        description='Other Description',
        condition='new',
        user=other_user
    )
    url = reverse('ad_delete', kwargs={'pk': ad.pk})
    response = auth_client.post(url)
    assert response.status_code == 403  # Forbidden


# Тесты пагинации
@pytest.mark.django_db
def test_ad_list_pagination(rf, user):
    # Создаем 5 объявлений
    for i in range(5):
        Ad.objects.create(
            title=f'Ad {i}',
            description=f'Description {i}',
            condition='new',
            user=user
        )

    request = rf.get('/ads/?page=2')
    request.user = user
    response = AdList.as_view()(request)
    assert response.status_code == 200
    assert 'page_obj' in response.context_data
    assert response.context_data['page_obj'].number == 2


# Тесты фильтрации
@pytest.mark.django_db
def test_ad_list_filtering(rf, user, category):
    Ad.objects.create(
        title='Filtered Ad',
        description='Filtered Description',
        condition='new',
        user=user
    ).categories.add(category)

    request = rf.get(f'/ads/?categories={category.id}')
    request.user = user
    response = AdList.as_view()(request)
    assert response.status_code == 200
    assert len(response.context_data['ads']) == 1
    assert response.context_data['ads'][0].title == 'Filtered Ad'
