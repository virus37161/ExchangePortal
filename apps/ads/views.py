from django.core.exceptions import PermissionDenied
from django.shortcuts import render
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from ads.models import *
from ads.forms import AdForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.http import HttpResponseRedirect
from ads.filters import AdFilter, ExchangeFilter
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.db.models import Q

class AdList (ListView):
    model = Ad
    template_name = 'ad_list.html'
    context_object_name = 'ads'
    paginate_by = 3
    ordering = ['-created_at']

    def get_queryset(self):
        queryset = super().get_queryset()
        self.filterset = AdFilter(self.request.GET, queryset)
        return self.filterset.qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['filterset'] = self.filterset
        return context

class AdCreate(LoginRequiredMixin, CreateView):
    form_class= AdForm
    model = Ad
    template_name = "ad_create.html"
    success_url = '/ads/'

    def form_valid(self, form):
        ad = form.save(commit=False)
        ad.user_id = self.request.user.id
        self.object = form.save()
        return super().form_valid(form)


class AdUpdate(LoginRequiredMixin, UpdateView):
    model = Ad
    template_name = 'ad_update.html'
    form_class = AdForm
    success_url = reverse_lazy('ad_list')

    def form_valid(self,form):
        if self.object.user_id == self.request.user.id:
            self.object = form.save()
        else:
            return HttpResponseRedirect("Invalid Url")
        return super().form_valid(form)


class AdDelete(LoginRequiredMixin, DeleteView):
    model = Ad
    template_name = 'ad_delete.html'
    success_url = reverse_lazy('ad_list')

    def form_valid(self, form):
        success_url = self.get_success_url()
        if self.object.user_id == self.request.user.id:
            self.object.delete()
        else:
            return HttpResponseRedirect("Invalid Url")
        return HttpResponseRedirect(success_url)


class OffersList(LoginRequiredMixin, ListView):
    model = Ad
    template_name = 'ads_of_user.html'
    context_object_name = 'ads'
    paginate_by = 2

    def dispatch(self, request, *args, **kwargs):
        # Получаем объявление по переданному pk
        ad = Ad.objects.get(id=self.kwargs['pk'])

        # Проверяем, что текущий пользователь не является автором объявления
        if request.user == ad.user:
            raise PermissionDenied("Вы не можете делать предложения по своему собственному объявлению")

        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        queryset = super().get_queryset()
        user_queryset = queryset.filter(user=self.request.user)
        self.filterset = AdFilter(self.request.GET, user_queryset)
        return self.filterset.qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['object'] = Ad.objects.get(id=self.kwargs['pk'])
        return context


@login_required
def offer_add(request, pk, obj):
    comment = request.POST['comment']
    ad_receiver = Ad.objects.get(id=pk)
    ad_sender = Ad.objects.get(id=obj)
    user = request.user
    if user.id != ad_receiver.user.id:
        ExchangeProposal.objects.create(ad_sender=ad_sender, ad_receiver=ad_receiver, comment=comment, status='ожидает')
    return redirect('/ads/')


class UserThingList (LoginRequiredMixin, ListView):
    model = Ad
    template_name = 'user_thing_list.html'
    context_object_name = 'ads'
    paginate_by = 2

    def get_queryset(self):
        queryset = super().get_queryset()
        user_queryset = queryset.filter(user=self.request.user)
        self.filterset = AdFilter(self.request.GET, queryset=user_queryset)
        return self.filterset.qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        return context


class ExchangeProposalList(LoginRequiredMixin, ListView):
    model = ExchangeProposal
    template_name = 'exchanges_list.html'
    context_object_name = 'exchanges'
    paginate_by = 2
    def get_queryset(self):
        queryset = super().get_queryset()
        user_queryset = queryset.filter(
            Q(ad_sender__user=self.request.user) |
            Q(ad_receiver__user=self.request.user)
        )
        self.filterset = ExchangeFilter(self.request.GET, queryset=user_queryset)
        return self.filterset.qs.distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filterset'] = self.filterset
        return context

@login_required
def offer_accept(request, pk):
    exchange = ExchangeProposal.objects.get(id=pk)
    if request.user != exchange.ad_receiver.user:
        return redirect('/ads/')  # Или можно вывести сообщение об ошибке

        # Если проверка пройдена, меняем статус
    exchange.status = 'принята'
    exchange.save()
    return redirect('/ads/')

@login_required
def offer_cancel(request, pk):
    exchange = ExchangeProposal.objects.get(id=pk)
    if request.user != exchange.ad_receiver.user:
        return redirect('/ads/')  # Или можно вывести сообщение об ошибке

        # Если проверка пройдена, меняем статус
    exchange.status = 'отклонена'
    exchange.save()
    return redirect('/ads/')


class DetailView(LoginRequiredMixin, DetailView):
    model = Ad
    template_name = 'detail.html'
    context_object_name = 'ad'