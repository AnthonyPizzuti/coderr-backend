"""Admin registration for offer models."""

from django.contrib import admin

from offers_app.models import Offer, OfferDetail

admin.site.register(Offer)
admin.site.register(OfferDetail)
