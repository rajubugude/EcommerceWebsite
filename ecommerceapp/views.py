from django.shortcuts import render,HttpResponse,redirect
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.conf import settings
from .models import *
from math import ceil
import razorpay
import datetime
from django.template.loader import render_to_string
from razorpay.errors import SignatureVerificationError
from django.core.mail import EmailMessage
import json


def index(request): #filter based on category wise
    allProds = []
    catprods = Product.objects.values('category','id')
    cats = {item['category'] for item in catprods}
    for cat in cats:
        prod= Product.objects.filter(category=cat)
        n=len(prod) 
        nSlides = n // 4 + ceil((n / 4) - (n // 4))
        allProds.append([prod, range(1, nSlides), nSlides])

    params= {'allProds':allProds}
    return render(request,'index.html',params)



def contact(request):
    if request.method=="POST":
        name=request.POST.get("name")
        email=request.POST.get("email")
        desc=request.POST.get("desc")
        pnumber=request.POST.get("pnumber")
        my_object=Contact(name=name,email=email,desc=desc,phonenumber=pnumber)
        my_object.save()
        messages.info(request,"we will get back to you soon..")
        return render(request,"contact.html")


    return render(request,"contact.html")


def about(request):
    return render(request,"about.html")


def checkout(request):
    if not request.user.is_authenticated:
        messages.warning(request, "Please login and try again")
        return redirect('/auth/login')

    if request.method == "POST":
        items_json = request.POST.get('itemsJson', '')
        name = request.POST.get('name', '')
        amount = request.POST.get('amt')
        email = request.POST.get('email', '')
        address1 = request.POST.get('address1', '')
        city = request.POST.get('city', '')
        state = request.POST.get('state', '')
        zip_code = request.POST.get('zip_code', '')
        phone = request.POST.get('phone', '')

        order = Orders(
            items_json=items_json,
            name=name,
            amount=amount,
            email=email,
            address1=address1,
            city=city,
            state=state,
            zip_code=zip_code,
            phone=phone
        )

        print(amount)

        # Payment integration code with Razorpay
        client = razorpay.Client(auth=(settings.RAZORPAY_API_KEY, settings.RAZORPAY_API_SECRET))
        order_data = {
            'amount': int(float(amount) * 100),  # Amount in paise (multiply by 100)
            'currency': 'INR',
            'payment_capture': '1',
        }
        razorpay_order = client.order.create(order_data)

        order.set_razorpay_order_id(razorpay_order['id'])  # Store the Razorpay order ID in the oid field of the Order model

        update = OrderUpdate(order_id=order, update_desc="The order has been placed")
        update.save()

        context = {
            'order': order,
            'razorpay_order': razorpay_order,
            'amount': int(float(amount) * 100),  # Convert amount to paise (multiply by 100)
        }
        return render(request, 'checkout.html', context)

    return render(request, 'checkout.html')



def handle_payment(request):
    if request.method == 'GET':
        payment_id = request.GET.get('payment_id')
        order_id = request.GET.get('razorpay_order_id')
        signature = request.GET.get('signature')
        try:
            order = Orders.objects.get(oid=order_id)
        except Orders.DoesNotExist:
            # Order does not exist in the database
            # Redirect to a failure page
            return redirect('payment_failure')

        # Verify the payment using Razorpay API
        client = razorpay.Client(auth=(settings.RAZORPAY_API_KEY, settings.RAZORPAY_API_SECRET))
        params = {
            'razorpay_order_id': order.oid,
            'razorpay_payment_id': payment_id,
            'razorpay_signature': signature
        }
        try:
            client.utility.verify_payment_signature(params)
            # Payment verification successful
            order.amountpaid = str(order.amount)
            order.paymentstatus = 'Paid'  # Update the payment status of the order
            order.save()


            #invoice sending to mail 
            items_data = json.loads(order.items_json)
            # print(items_data)
            items = []
            for item_key, item_values in items_data.items():
                item = {
                    'name': item_values[1].strip(),
                    'quantity': item_values[0],
                    'price': item_values[2],
                    'total': item_values[0] * item_values[2],
                }
                items.append(item)

            current_timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            subject = 'Invoice for Order #{}'.format(order.order_id)
            email_template = 'invoice_email.html'
            email_context = {'order': order,'timestamp': current_timestamp,'items':items}
            email_content = render_to_string(email_template, email_context)

            email = EmailMessage(
                subject=subject,
                body=email_content,
                from_email='raju.7102000@gmail.com',  # Replace with your email address
                to=[order.email]
            )
            email.content_subtype = 'html'
            email.send()
            context = {
                'payment_id': payment_id,
                'order': order
            }
            return render(request, 'payment_success.html', context)
        except SignatureVerificationError:
            # Payment verification failed
            # Handle the failure scenario (e.g., update order status, notify user, etc.)
            order.paymentstatus = 'Failed'  # Update the payment status of the order
            order.save()

            update = OrderUpdate(order_id=order, update_desc="Payment failed")
            update.save()

            # Redirect to a failure page
            return redirect('payment_failure')

    # Redirect to a failure page if the request method is not GET
    return redirect('payment_failure')




def payment_failure(request):
    return render(request, 'payment_failure.html')




def profile(request):
    currentuser = request.user.username
    orders = Orders.objects.filter(email=currentuser)
    print(currentuser)
    items_list = []
    for order in orders:
        items_data = json.loads(order.items_json)
        
        items = []
        for item_key, item_values in items_data.items():
            item = {
                'name': item_values[1].strip(),
                'quantity': item_values[0],
                'price': item_values[2],
                'total': item_values[0] * item_values[2],
            }
            items.append(item)
        
        status = OrderUpdate.objects.filter(order_id=order.order_id)
        
        items_list.append({
            "order": order, #here "order" is order_object
            "items": items,
            "status": status,
        })
    context = {
        "items_list": items_list,
        "currentuser": currentuser,
    }
    
    return render(request, "profile.html", context)