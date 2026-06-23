from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.crypto import get_random_string
from django.utils import timezone

from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny

from .models import (
    Category, Item, Order, BookingQuote, 
    LiveStream, Testimonial, ContactInquiry, 
    PricingMatrixConfig, HeroSlide
)
from .serializers import OrderSerializer
from utils.brevo import send_email

# =====================================================================
# 1. ISOLATED HERO SLIDES ENDPOINT (Exclusively for background images)
# =====================================================================
@api_view(['GET'])
@permission_classes([AllowAny])
def get_hero_slides_view(request):
    """
    Dedicated background layer aggregator. Keeps carousel streaming 
    isolated from operational catalog lookups.
    """
    slides = HeroSlide.objects.filter(is_active=True).order_by('order', 'id')
    hero_payload = []
    
    for slide in slides:
        if slide.image:
            img_url = slide.image.url if hasattr(slide.image, 'url') else str(slide.image)
            if img_url.startswith("http://"):
                img_url = img_url.replace("http://", "https://")
                
            hero_payload.append({
                "id": slide.id,
                "imageUrl": img_url,  
                "altText": slide.alt_text,
                "title": slide.title
            })
            
    return Response({"heroSlides": hero_payload})


# =====================================================================
# 2. SEPARATE CATERING CATALOG & LOGISTICS ENDPOINT
# =====================================================================
@api_view(['GET'])
@permission_classes([AllowAny])
def get_marketplace_catalogs(request):
    """
    Fetches available large food pots and rental equipment.
    No hero sections are requested here, avoiding empty catalog errors.
    """
    db_items = Item.objects.filter(is_available=True).select_related('category').order_by('name')
    
    food_list = []
    rental_list = []
    
    for item in db_items:
        img_url = item.image.url if item.image else ""
        if img_url.startswith("http://"):
            img_url = img_url.replace("http://", "https://")
            
        item_data = {
            "id": item.id,
            "name": item.name,
            "slug": item.slug,
            "price": float(item.price_per_unit),
            "price_dozen": float(item.price_per_dozen) if item.price_per_dozen else None,
            "desc": item.description,
            "img": img_url
        }
        
        if item.category.is_rental:
            rental_list.append(item_data)
        else:
            food_list.append(item_data)
            
    return Response({
        "foodMenu": food_list,
        "rentalInventory": rental_list
    })


# =====================================================================
# 3. TRANSACTIONAL & OPERATIONAL UTILITIES
# =====================================================================
@api_view(['POST'])
@permission_classes([AllowAny])
def submit_quote_request(request):
    data = request.data
    ref_num = "DINA-Q-" + get_random_string(length=6).upper()
    
    event_date_value = data.get('eventDate') or data.get('event_date') or timezone.now().date()
    event_address_value = data.get('address') or data.get('event_address') or "No Address Provided"
    client_name_value = data.get('name') or data.get('client_name') or "Client Name Not Provided"
    client_email_value = data.get('email') or data.get('client_email') or "no-email-provided@dinacatering.com"
    client_phone_value = data.get('phone') or data.get('client_phone') or "0000000000"
    event_type_value = data.get('eventType') or data.get('event_type') or "General Event"
    
    service_type_value = data.get('serviceType') or data.get('service_type') or 'DELIVERY'
    if service_type_value not in ['DELIVERY', 'HOME_SERVICE', 'FULL_EVENT']:
        service_type_value = 'DELIVERY'

    try:
        guests_count = int(data.get('guestCount', data.get('estimated_guests', 0)))
    except (ValueError, TypeError):
        guests_count = 0

    quote = BookingQuote.objects.create(
        quote_number=ref_num, client_name=client_name_value, client_email=client_email_value,
        client_phone=client_phone_value, event_type=event_type_value, event_date=event_date_value,
        event_address=event_address_value, estimated_guests=guests_count, service_type=service_type_value,
        requested_menu_items=str(data.get('menuItems', data.get('requested_menu_items', ''))),
        requested_rental_items=str(data.get('rentalItems', data.get('requested_rental_items', '')))
    )
    
    subject = f"We have received your Quote Request! Ref: {ref_num}"
    html_message = (
        f"<p>Hello {quote.client_name},</p>"
        f"<p>Thank you for reaching out to Dina Catering and Rentals. Our specialists are reviewing your configuration details for your {quote.event_type}.</p>"
        f"<p>An official breakdown invoice containing exact payment instructions will be sent to you shortly after review.</p>"
    )
    send_email(to_email=quote.client_email, subject=subject, html_content=html_message)
    return Response({"message": "Quote processing started successfully", "ref": ref_num}, status=status.HTTP_201_CREATED)


@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def create_order_endpoint(request):
    data = request.data.copy()
    ref_code = "DINA-OR-" + get_random_string(length=7).upper()
    data['order_number'] = ref_code
    data['delivery_date'] = timezone.now()

    serializer = OrderSerializer(data=data)
    if serializer.is_valid():
        order = serializer.save()
        
        if request.data.get('payment_status') is True:
            order.payment_status = True
            order.status = 'CONFIRMED'
            order.save()
        
        subject = f"Order Received: #{ref_code} - Dina Catering"
        
        if order.payment_method == 'TRANSFER':
            email_body = f"""
            <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 25px; border: 1px solid #e2e8f0; border-radius: 16px; background-color: #ffffff;">
                <h2 style="color: #064e3b; margin-top: 0;">Hello {order.client_name},</h2>
                <p style="color: #334155; font-size: 14px; line-height: 1.6;">We have successfully received your catering order <strong>#{ref_code}</strong>.</p>
                <div style="background-color: #f8fafc; padding: 16px; border-radius: 8px; margin: 15px 0; border: 1px solid #e2e8f0;">
                    <span style="font-size: 12px; color: #64748b; font-weight: bold;">Total Expected Balance:</span>
                    <h3 style="margin: 4px 0 0 0; color: #064e3b; font-size: 22px; font-weight: 900;">₦{float(order.total_amount):,.2f}</h3>
                </div>
                <div style="background-color: #fffbeb; border: 1px solid #fef3c7; padding: 16px; border-radius: 12px; margin: 20px 0;">
                    <h4 style="color: #b45309; margin: 0 0 6px 0; text-transform: uppercase; font-size: 11px;">Manual Bank Settlement Grid</h4>
                    <p style="margin: 0; font-size: 13px; color: #78350f;">
                        <strong>Bank Name:</strong> Access Bank<br/>
                        <strong>Account Name:</strong> Dina Catering and Rental Services<br/>
                        <strong>Account Number:</strong> 1234567890
                    </p>
                </div>
                <p style="font-size: 11px; color: #64748b;"><strong>STATUS: PENDING ADMINISTRATIVE VERIFICATION</strong>. Kindly complete your transfer and upload a screenshot to our WhatsApp channel.</p>
            </div>
            """
        else:
            email_body = f"""
            <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 25px; border: 1px solid #e2e8f0; border-radius: 16px; background-color: #ffffff;">
                <h2 style="color: #064e3b; margin-top: 0;">Hello {order.client_name},</h2>
                <p style="color: #334155; font-size: 14px; line-height: 1.6;">Your online transaction for order <strong>#{ref_code}</strong> has been successfully authorized via Paystack.</p>
                <div style="background-color: #ecfdf5; padding: 16px; border-radius: 8px; margin: 15px 0; border: 1px solid #d1fae5;">
                    <span style="font-size: 12px; color: #065f46; font-weight: bold;">Total Funds Captured:</span>
                    <h3 style="margin: 4px 0 0 0; color: #047857; font-size: 22px; font-weight: 900;">₦{float(order.total_amount):,.2f}</h3>
                </div>
                <p style="font-size: 13px; color: #334155;"><strong>STATUS: PAID & CONFIRMED</strong>. Our kitchen specialists have logged your criteria and queued your order.</p>
            </div>
            """
        send_email(to_email=order.client_email, subject=subject, html_content=email_body)
        return Response({"message": "Order completed successfully", "ref": ref_code}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def live_status_feed(request):
    stream = LiveStream.objects.filter(is_live=True).last()
    if stream:
        return JsonResponse({"is_live": True, "youtube_url": stream.youtube_url, "title": stream.title})
    return JsonResponse({"is_live": False, "youtube_url": ""})


@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def submit_contact_inquiry(request):
    data = request.data
    email_val = data.get('email', '')
    if not email_val:
        return Response({"error": "Email address is required"}, status=status.HTTP_400_BAD_REQUEST)

    name_val = data.get('name', 'Anonymous Writer')
    subject_val = data.get('subject', 'General Inquiry')
    message_val = data.get('message', '')

    ContactInquiry.objects.create(name=name_val, email=email_val, subject=subject_val, message=message_val)

    email_subject = f"Inquiry Received: {subject_val} - Dina Catering"
    html_message = (
        f"<p>Hello {name_val},</p>"
        f"<p>Thank you for contacting Dina Catering. We have successfully received your inquiry regarding <strong>\"{subject_val}\"</strong>.</p>"
    )
    send_email(to_email=email_val, subject=email_subject, html_content=html_message)
    return Response({"message": "Inquiry logged successfully"}, status=status.HTTP_201_CREATED)


def get_live_testimonials(request):
    testimonials = Testimonial.objects.all().order_by('-id')
    data_list = []
    for t in testimonials:
        data_list.append({
            "id": t.id, "name": t.client_name, "text": t.comment, "rating": t.rating,
            "image": t.client_image.url if t.client_image else ""
        })
    return JsonResponse({"testimonials": data_list}, safe=False)


def get_pricing_constants(request):
    config, created = PricingMatrixConfig.objects.get_or_create(pk=1)
    return JsonResponse({
        "standard_rate": float(config.standard_menu_rate),
        "premium_rate": float(config.premium_menu_rate),
        "executive_rate": float(config.executive_menu_rate),
        "canopy_rate": float(config.canopy_base_rate),
    })