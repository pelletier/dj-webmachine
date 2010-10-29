# -*- coding: utf-8 -
#
# This file is part of dj-webmachine released under the MIT license. 
# See the NOTICE for more information.

import random
import urllib
import urlparse
import uuid

from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import ugettext_lazy as _

from webmachine.managers import ConsumerManager, TokenManager, KEY_SIZE, \
SECRET_SIZE
from webmachine.util import keygen

VERIFIER_SIZE = 16
TOKEN_TYPES = ('access', 'request')
CONSUMER_STATES = (
    (PENDING,  _('Pending')),
    (ACCEPTED, _('Accepted')),
    (CANCELED, _('Canceled')),
    (REJECTED, _('Rejected')),
)

def generate_random(length=SECRET_SIZE):
    return User.objects.make_random_password(length=length)

class Nonce(models.models):
    token_key = models.CharField(max_length=KEY_SIZE)
    consumer_key = models.CharField(max_length=KEY_SIZE)
    key = models.CharField(max_length=255)

class Consumer(models.Model):
    name = models.CharField(max_length=255)
    key = models.CharField(max_length=KEY_SIZE)
    secret = models.CharField(max_length=SECRET_SIZE)
    description = models.TextField()
    user = models.ForeignKey(User, null=True, blank=True,
            related_name="consumers_user")
    status = models.CharField(max_length=16, choices=CONSUMER_STATES, 
            default='pending')

    objects = ConsumerManager()

    def __str__(self):
        data = {'oauth_consumer_key': self.key,
            'oauth_consumer_secret': self.secret}

        return urllib.urlencode(data)

class Token(models.Models):
    key = models.CharField(max_length=KEY_SIZE)
    secret = models.CharField(max_length=SECRET_SIZE),
    token_type = models.CharField(max_length=10)
    callback = models.CharField(max_length=2048) #URL
    callback_confirmed = models.BooleanField(default=False)
    verifier = models.CharField(max_length=VERIFIER_SIZE)
    timestamp = models.IntegerField(default=time.time())
    user = models.ForeignKey(numm=True, blank=True,
            related_name="tokens_user")
    is_approved = models.BooleanField(default=False)
    
    objects = TokenManager()

    def set_callback(self, callback):
        self.callback = callback
        self.callback_confirmed = True
        self.save()

    def set_verifier(self, verifier=None):
        if verifier is not None:
            self.verifier = verifier
        else:
            self.verifier = generate_verifier()
        self.save()

    def get_callback_url(self):
        if self.callback and self.verifier:
            # Append the oauth_verifier.
            parts = urlparse.urlparse(self.callback)
            scheme, netloc, path, params, query, fragment = parts[:6]
            if query:
                query = '%s&oauth_verifier=%s' % (query, self.verifier)
            else:
                query = 'oauth_verifier=%s' % self.verifier
            return urlparse.urlunparse((scheme, netloc, path, params,
                query, fragment))
        return self.callback
