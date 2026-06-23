from django.contrib import admin, messages
from django.template.loader import render_to_string
from django.utils.html import format_html
from django.urls import path, reverse
from django.shortcuts import get_object_or_404, redirect, render
from django.http import HttpResponseRedirect

from .models import HeroSlide

# Secure Brevo API utility script wrapper
from utils.brevo import send_email  

# Imported your new ContactInquiry model right alongside existing ones
from .models import Category, Item, Order, OrderItem, BookingQuote, LiveStream, Testimonial, ContactInquiry

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'client_name', 'payment_method', 'payment_status', 'status', 'total_amount', 'acknowledge_payment_button')
    list_filter = ('payment_method', 'payment_status', 'status')
    inlines = [OrderItemInline]
    actions = ['mark_as_verified_and_thank']

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('<int:order_id>/thank-you/', self.admin_site.admin_view(self.send_thank_you_mail), name='order-thank-you'),
        ]
        return custom_urls + urls

    def acknowledge_payment_button(self, obj):
        return format_html(
            '<a class="button" href="{}">⚡ Send Thank You Email</a>',
            f"./{obj.id}/thank-you/"
        )
    acknowledge_payment_button.short_description = "Quick Actions"

    def send_thank_you_mail(self, request, order_id):
        order = get_object_or_404(Order, id=order_id)
        order.payment_status = True
        order.status = 'CONFIRMED'
        order.save()

        # Build formal message header criteria
        subject = f"Payment Received & Confirmed - Order #{order.order_number}"
        
        # 🟢 Upgraded, Professional Corporate Email Branding Template (No external HTML file required!)
        html_message = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <style>
                    body {{
                        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
                        -webkit-font-smoothing: antialiased;
                        margin: 0;
                        padding: 0;
                        background-color: #f8fafc;
                        color: #334155;
                    }}
                </style>
            </head>
            <body style="background-color: #f8fafc; margin: 0; padding: 20px 0;">
                <table border="0" cellpadding="0" cellspacing="0" width="100%" style="max-width: 600px; margin: 0 auto; background-color: #ffffff; border-radius: 16px; overflow: hidden; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05); border: 1px solid #e2e8f0;">
                    
                    <!-- 🟢 BRAND HEADER PANEL -->
                    <tr>
                        <td align="center" style="background-color: #064e3b; padding: 32px 24px; text-align: center;">
                            <h1 style="color: #ffffff; font-size: 24px; font-weight: 900; margin: 0; letter-spacing: 0.05em; text-transform: uppercase;">
                                DINA CATERING
                            </h1>
                            <p style="color: #f59e0b; font-size: 11px; font-weight: 700; margin: 4px 0 0 0; letter-spacing: 0.15em; text-transform: uppercase;">
                                & RENTAL SERVICES
                            </p>
                        </td>
                    </tr>
                    
                    <!-- 📝 MAIN BODY CONTAINER -->
                    <tr>
                        <td style="padding: 40px 32px;">
                            <h2 style="font-size: 16px; font-weight: 700; color: #1e293b; margin-top: 0; margin-bottom: 12px;">
                                Hello {order.client_name},
                            </h2>
                            <p style="font-size: 14px; line-height: 1.7; color: #334155; margin-bottom: 20px;">
                                We have successfully verified your payment transaction and locked your booking securely into our schedule! Thank you for clearing your balance.
                            </p>
                            
                            <div style="background-color: #f8fafc; padding: 16px; border-radius: 8px; margin: 20px 0; border: 1px solid #e2e8f0; font-size: 13px; line-height: 1.6; color: #475569;">
                                <strong>Order Number:</strong> #{order.order_number}<br/>
                                <strong>Total Captured Amount:</strong> ₦{float(order.total_amount):,.2f}<br/>
                                <strong>Transaction Status:</strong> PAID & VERIFIED
                            </div>

                            <p style="font-size: 14px; line-height: 1.7; color: #334155; margin-bottom: 32px;">
                                Our central kitchen artisans have been assigned to your menu items list, and our material logistics supervisor has checked your event canopy supplies lines for timely dispatch tracking execution.
                            </p>
                            
                            <hr style="border: 0; border-top: 1px solid #f1f5f9; margin-bottom: 24px;" />
                            
                            <!-- SIGNATURE MATRIX -->
                            <p style="font-size: 13px; line-height: 1.5; color: #64748b; margin: 0;">
                                Best regards,<br>
                                <strong style="color: #064e3b; font-weight: 700;">Dina Catering Management Desk</strong><br>
                                <span style="font-size: 12px;">Operational Headquarters, Abuja, Nigeria</span>
                            </p>
                        </td>
                    </tr>
                    
                    <!-- 🏢 BRAND FOOTER TERMINAL -->
                    <tr>
                        <td style="background-color: #f8fafc; padding: 24px 32px; text-align: center; border-top: 1px solid #e2e8f0;">
                            <p style="font-size: 11px; line-height: 1.6; color: #94a3b8; margin: 0;">
                                This message was transmitted securely via our administrative engine client portal request line.<br>
                                © 2026 Dina Catering and Rental Services. All Rights Reserved.
                            </p>
                        </td>
                    </tr>
                </table>
            </body>
            </html>
            """
        
        # Route directly through Brevo API utility script wrapper
        success = send_email(to_email=order.client_email, subject=subject, html_content=html_message)
        
        if success:
            self.message_user(request, f"Payment verified and thank-you email sent successfully to {order.client_email}!")
        else:
            self.message_user(request, f"Order confirmed, but the Brevo API failed to send the email notification.", level=messages.ERROR)
            
        return redirect('admin:services_order_changelist')

@admin.register(BookingQuote)
class BookingQuoteAdmin(admin.ModelAdmin):
    list_display = ('id', 'client_name', 'event_type', 'event_date', 'status', 'generated_total', 'send_invoice_button')
    list_filter = ('status', 'event_type')
    
    # Keep standard field layout access inside detail view forms
    readonly_fields = ('quote_number', 'created_at')

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            # Pattern matches your relative link in the button cleanly
            path('<int:quote_id>/send-invoice/', self.admin_site.admin_view(self.process_and_send_invoice), name='send-invoice'),
        ]
        return custom_urls + urls

    def send_invoice_button(self, obj):
        # Generates a relative link appending directly to the current model administration router path
        return format_html(
            '<a class="button" style="background-color: #064e3b; color: white; padding: 5px 10px; border-radius: 4px; font-weight: bold; text-decoration: none;" href="./{}/send-invoice/">📄 Send Official Invoice</a>',
            obj.id
        )
    send_invoice_button.short_description = "Invoice System"

    def process_and_send_invoice(self, request, quote_id):
        quote = get_object_or_404(BookingQuote, id=quote_id)
        quote.status = 'INVOICED'
        quote.save()

        subject = f"Official Invoice & Event Package Details - Dina Catering"
        
        # 🟢 Branded HTML Invoice Template
        html_message = f"""
            <!DOCTYPE html>
            <html>
            <head><meta charset="utf-8"></head>
            <body style="font-family: Arial, sans-serif; background-color: #f8fafc; margin: 0; padding: 20px 0; color: #334155;">
                <table border="0" cellpadding="0" cellspacing="0" width="100%" style="max-width: 600px; margin: 0 auto; background-color: #ffffff; border-radius: 16px; overflow: hidden; border: 1px solid #e2e8f0; box-shadow: 0 4px 6px rgba(0,0,0,0.02);">
                    <tr>
                        <td align="center" style="background-color: #064e3b; padding: 32px 24px; text-align: center;">
                            <h1 style="color: #ffffff; font-size: 24px; font-weight: 900; margin: 0; letter-spacing: 0.05em; text-transform: uppercase;">DINA CATERING</h1>
                            <p style="color: #f59e0b; font-size: 11px; font-weight: 700; margin: 4px 0 0 0; letter-spacing: 0.15em;">& RENTAL SERVICES</p>
                        </td>
                    </tr>
                    <tr>
                        <td style="padding: 40px 32px;">
                            <h2 style="font-size: 16px; font-weight: 700; color: #1e293b; margin-top: 0; margin-bottom: 15px;">Hello {quote.client_name},</h2>
                            <p style="font-size: 14px; line-height: 1.6;">Our management team has reviewed your booking criteria request for your upcoming <strong>{quote.event_type}</strong> execution on {quote.event_date}. Below is your officially compiled bill balance breakdown:</p>
                            
                            <div style="background-color: #f8fafc; padding: 20px; border-radius: 12px; margin: 24px 0; border: 1px solid #e2e8f0;">
                                <span style="font-size: 11px; text-transform: uppercase; color: #64748b; font-weight: bold;">Total Calculated Balance Due:</span>
                                <h2 style="margin: 4px 0 0 0; color: #064e3b; font-size: 28px; font-weight: 900;">₦{float(quote.generated_total):,.2f}</h2>
                            </div>

                            <p style="font-size: 14px; line-height: 1.6;">To secure lock your event date parameters into our operational calendar grid schedule, please execute a direct bank settlement transfer using the headquarters account coordinates credentials detailed below:</p>
                            
                            <div style="background-color: #fffbeb; border: 1px solid #fef3c7; padding: 18px; border-radius: 12px; margin: 20px 0; font-size: 13px; line-height: 1.6; color: #78350f;">
                                <strong>Bank Name:</strong> Access Bank<br/>
                                <strong>Account Name:</strong> Dina Catering and Rental Services<br/>
                                <strong>Account Number:</strong> 1234567890
                            </div>

                            <p style="font-size: 13px; line-height: 1.6; color: #475569;">After transferring funds, kindly log a screenshot slip receipt directly over to our WhatsApp supervisor to clear your contract parameters immediately.</p>
                            <hr style="border: 0; border-top: 1px solid #f1f5f9; margin: 24px 0;" />
                            <p style="font-size: 13px; color: #64748b; margin: 0;">Best regards,<br/><strong>Dina Catering Management Desk</strong><br/>Abuja, Nigeria</p>
                        </td>
                    </tr>
                </table>
            </body>
            </html>
            """
        
        success = send_email(to_email=quote.client_email, subject=subject, html_content=html_message)
        
        if success:
            self.message_user(request, f"Invoice smoothly generated and emailed to {quote.client_email}!")
        else:
            self.message_user(request, f"Invoice status updated to INVOICED, but the Brevo transactional mail delivery failed.", level=messages.ERROR)
            
        # 🟢 Dynamic URL lookup: Automatically works regardless of your Django app name
        changelist_url = reverse(f'admin:{self.model._meta.app_label}_{self.model._meta.model_name}_changelist')
        return HttpResponseRedirect(changelist_url)
    

# 🚀 NEW: Comprehensive Contact Inquiry Model Administration Table Interface 
@admin.register(ContactInquiry)
class ContactInquiryAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'subject', 'created_at', 'reply_action_button')
    readonly_fields = ('name', 'email', 'subject', 'message', 'created_at')
    search_fields = ('name', 'email', 'subject')
    list_filter = ('created_at',)

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('<int:inquiry_id>/reply/', self.admin_site.admin_view(self.reply_to_client_view), name='contact-reply'),
        ]
        return custom_urls + urls

    def reply_action_button(self, obj):
        return format_html(
            '<a class="button" style="background-color: #1e3a8a; color: white; padding: 5px 10px; border-radius: 4px;" href="{}">✉️ Compose Reply</a>',
            f"./{obj.id}/reply/"
        )
    reply_action_button.short_description = "Management Desk"

    def reply_to_client_view(self, request, inquiry_id):
        inquiry = get_object_or_404(ContactInquiry, id=inquiry_id)

        # Handle message delivery if administrative form is submitted
        if request.method == 'POST':
            reply_text = request.POST.get('reply_message')
            email_subject = request.POST.get('reply_subject', f"Re: {inquiry.subject}")

            if not reply_text:
                self.message_user(request, "❌ Reply message text content cannot be blank.", level=messages.ERROR)
                return HttpResponseRedirect(request.path)

            # Build a formal message structure
                        # 💎 Upgraded, Professional Corporate Email Branding Template
            html_message = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <style>
                    body {{
                        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
                        -webkit-font-smoothing: antialiased;
                        margin: 0;
                        padding: 0;
                        -ms-text-size-adjust: 100%;
                        -webkit-text-size-adjust: 100%;
                        background-color: #f8fafc;
                        color: #334155;
                    }}
                    table {{ border-collapse: collapse !important; mso-table-lspace: 0pt; mso-table-rspace: 0pt; }}
                    img {{ -ms-interpolation-mode: bicubic; border: 0; height: auto; line-height: 100%; outline: none; text-decoration: none; }}
                </style>
            </head>
            <body style="background-color: #f8fafc; margin: 0; padding: 20px 0;">
                <table border="0" cellpadding="0" cellspacing="0" width="100%" style="max-width: 600px; margin: 0 auto; background-color: #ffffff; border-radius: 16px; overflow: hidden; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03); border: 1px solid #e2e8f0;">
                    
                    <!-- 🟢 BRAND HEADER PANEL -->
                    <tr>
                        <td align="center" style="background-color: #064e3b; padding: 32px 24px; text-align: center;">
                            <h1 style="color: #ffffff; font-size: 24px; font-weight: 900; margin: 0; letter-spacing: 0.05em; text-transform: uppercase;">
                                DINA CATERING
                            </h1>
                            <p style="color: #f59e0b; font-size: 11px; font-weight: 700; margin: 4px 0 0 0; letter-spacing: 0.15em; text-transform: uppercase;">
                                & RENTAL SERVICES
                            </p>
                        </td>
                    </tr>
                    
                    <!-- 📝 MAIN BODY CONTAINER -->
                    <tr>
                        <td style="padding: 40px 32px;">
                            <h2 style="font-size: 16px; font-weight: 700; color: #1e293b; margin-top: 0; margin-bottom: 20px;">
                                Hello {inquiry.name},
                            </h2>
                            
                            <div style="font-size: 14px; line-height: 1.7; color: #334155; margin-bottom: 32px; white-space: pre-wrap;">
                                {reply_text}
                            </div>
                            
                            <!-- HORIZONTAL SEPARATOR LINE -->
                            <hr style="border: 0; border-top: 1px solid #f1f5f9; margin-bottom: 24px;" />
                            
                            <!-- SIGNATURE MATRIX -->
                            <table border="0" cellpadding="0" cellspacing="0" width="100%">
                                <tr>
                                    <td>
                                        <p style="font-size: 13px; line-height: 1.5; color: #64748b; margin: 0;">
                                            Best regards,<br>
                                            <strong style="color: #064e3b; font-weight: 700;">Dina Catering Management Desk</strong><br>
                                            <span style="font-size: 12px;">Operational Headquarters, Abuja, Nigeria</span>
                                        </p>
                                    </td>
                                </tr>
                            </table>
                        </td>
                    </tr>
                    
                    <!-- 🏢 BRAND FOOTER TERMINAL -->
                    <tr>
                        <td style="background-color: #f8fafc; padding: 24px 32px; text-align: center; border-top: 1px solid #e2e8f0;">
                            <p style="font-size: 11px; line-height: 1.6; color: #94a3b8; margin: 0;">
                                This message was transmitted securely via our administrative engine client portal request line.<br>
                                © 2026 Dina Catering and Rental Services. All Rights Reserved.
                            </p>
                            <p style="margin: 12px 0 0 0; font-size: 11px;">
                                <a href="mailto:info@dinacatering.com" style="color: #064e3b; text-decoration: none; font-weight: 600; margin: 0 8px;">Contact Support</a> | 
                                <a href="https://dinacatering.com" style="color: #064e3b; text-decoration: none; font-weight: 600; margin: 0 8px;">Visit Website</a>
                            </p>
                        </td>
                    </tr>
                    
                </table>
            </body>
            </html>
            """


            # Route through your working Brevo API utility script
            api_success = send_email(to_email=inquiry.email, subject=email_subject, html_content=html_message)

            if api_success:
                self.message_user(request, f"🚀 Administrative reply successfully emailed to {inquiry.email}!")
                return redirect('admin:services_contactinquiry_changelist')
            else:
                self.message_user(request, "❌ Brevo API execution failed. Check system console logs.", level=messages.ERROR)

        # Context layout parameters to display on your custom compose page
        context = {
            'opts': self.model._meta,
            'original': inquiry,
            'title': f"Reply to {inquiry.name}",
            'has_permission': True,
        }
        return render(request, 'admin/reply_contact_form.html', context)


from .models import PricingMatrixConfig

@admin.register(PricingMatrixConfig)
class PricingMatrixConfigAdmin(admin.ModelAdmin):
    list_display = ('id', 'standard_menu_rate', 'premium_menu_rate', 'executive_menu_rate', 'canopy_base_rate')
    
    def has_add_permission(self, request):
        # Disables adding new entries if one already exists
        return not PricingMatrixConfig.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


from django.contrib import admin
from django.utils.html import format_html  # 🟢 FIXED: Required import for dashboard image previews
from .models import HeroSlide

@admin.register(HeroSlide)
class HeroSlideAdmin(admin.ModelAdmin):
    list_display = ('display_thumbnail', 'title', 'order', 'is_active')
    list_editable = ('order', 'is_active')  
    list_filter = ('is_active',)
    search_fields = ('title', 'alt_text')
    
    def display_thumbnail(self, obj):
        if obj.image:
            url = obj.image.url if hasattr(obj.image, 'url') else str(obj.image)
            if url.startswith("http://"):
                url = url.replace("http://", "https://")
            return format_html(
                '<img src="{}" style="width: 80px; height: 45px; object-fit: cover; border-radius: 4px; border: 1px solid #ddd;" />',
                url
            )
        return "No Cloudinary Asset Found"
    
    display_thumbnail.short_description = "Live Cloudinary Preview"
    
    fieldsets = (
        ("Core Asset Data", {
            'fields': ('title', 'image', 'alt_text') 
        }),
        ("Display Configuration Logic", {
            'fields': ('order', 'is_active'),
        }),
    )



admin.site.register(Category)
admin.site.register(Item)
admin.site.register(LiveStream)
admin.site.register(Testimonial)
