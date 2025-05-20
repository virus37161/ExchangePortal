from django.db import models
from django.contrib.auth.models import User

STATUS_CHOICES = [
    ('pending', 'ожидает'),
    ('accepted', 'принята'),
    ('rejected', 'отклонена'),
]

CONDITION_CHOICES = [
    ('новое', 'новое'),
    ('б/у', 'б/у')
]

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Ad(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField()
    image = models.ImageField(upload_to='images', blank=True, null=True)
    categories = models.ManyToManyField(Category, related_name='ads')
    condition = models.CharField(max_length=50, choices=CONDITION_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class ExchangeProposal(models.Model):
    ad_sender = models.ForeignKey(Ad, related_name='sent_proposals', on_delete=models.CASCADE)
    ad_receiver = models.ForeignKey(Ad, related_name='received_proposals', on_delete=models.CASCADE)
    comment = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Proposal from {self.ad_sender} to {self.ad_receiver} - Status: {self.status}"

