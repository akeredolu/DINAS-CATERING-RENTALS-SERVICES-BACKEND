from django.urls import path
from .views import (
    submit_quote_request, get_pricing_constants, create_order_endpoint,
    get_marketplace_catalogs, get_hero_slides_view, live_status_feed,
    submit_contact_inquiry, get_live_testimonials
)

urlpatterns = [
    # Quotes & Configurations
    path('quotes/submit/', submit_quote_request, name='submit-quote'),
    path('pricing-config/', get_pricing_constants, name='pricing-config'),
    path('orders/create/', create_order_endpoint, name='create-order'),
    
    # Catering Pots & Rental Supplies Inventory
    path('marketplace-catalog/', get_marketplace_catalogs, name='marketplace-catalog-api'),
    
    # Isolated Hero Section Background Carousel Link
    path('hero-slides/', get_hero_slides_view, name='hero-slides-api'),
    
    # Real-Time Operational Data
    path('live-status/', live_status_feed, name='live_status'),
    path('contact/', submit_contact_inquiry, name='submit-contact'),
    path('testimonials/', get_live_testimonials, name='live-testimonials'),
]