from django.shortcuts import render
from django.http import JsonResponse

import json
from datetime import datetime
from decimal import Decimal

from .models import *


def store(request):
	products = Product.objects.all()
	# if request.user.is_authenticated:
	# 	customer = request.user.customer
	# 	order, created = Order.objects.get_or_create(customer=customer, complete=False)
	# 	items = order.orderitem_set.all()
	# else:
	# 	items = []
	# 	order = {'get_cart_items': 0, 'get_cart_total': 0, 'shipping': False}
	context = {'products': products}
	return render(request, 'store/store.html', context)


def cart(request):

	if request.user.is_authenticated:
		customer = request.user.customer
		order, created = Order.objects.get_or_create(customer=customer, complete=False)
		items = order.orderitem_set.all()
	else:
		items = []
		order = {'get_cart_items': 0, 'get_cart_total': 0, 'shipping': False}
		try:
			cart = json.loads(request.COOKIES.get('cart'))
		except:
			cart = {}
		for key, value in cart.items():
			product = Product.objects.get(id=int(key))
			total = (product.price * value['quantity'])

			order['get_cart_total'] += total
			order['get_cart_items'] += value['quantity']

			item = {
				'product': {
					'id': product.id,
					'name': product.name,
					'price': product.price,
					'imageURL': product.imageURL,
				},
				'quantity': value['quantity'],
				'get_total': total
			}
			items.append(item)

			if product.digital == False:
				order['shipping'] = True

	context = {'items': items, 'order': order}
	return render(request, 'store/cart.html', context)


def checkout(request):
	if request.user.is_authenticated:
		customer = request.user.customer
		order, created = Order.objects.get_or_create(customer=customer, complete=False)
		items = order.orderitem_set.all()
	else:
		items = []
		order = {'get_cart_items': 0, 'get_cart_total': 0, 'shipping': False}
	context = {'items': items, 'order': order}
	return render(request, 'store/checkout.html', context)


def update_item(request):

	data = json.loads(request.body)
	productId = data.get('productId')
	action = data.get('action')

	print('Action:' ,action)
	print('productId', productId)

	customer = request.user.customer
	product = Product.objects.get(id=productId)

	order, created = Order.objects.get_or_create(customer=customer, complete=False)
	orderItem, created = OrderItem.objects.get_or_create(order=order, product=product)

	if action == "add":
		orderItem.quantity = orderItem.quantity + 1
	elif action == "remove":
		orderItem.quantity = orderItem.quantity - 1

	orderItem.save()

	if orderItem.quantity <= 0:
		orderItem.delete()

	return JsonResponse('Item was added', safe=False)


def processOrder(request):

	transaction_id = datetime.now().timestamp()
	data = json.loads(request.body)

	if request.user.is_authenticated:
		customer = request.user.customer
		order, created = Order.objects.get_or_create(customer=customer, complete=False)
		total = Decimal(data['form']['total'])
		order.transaction_id = transaction_id

		if total == Decimal(order.get_cart_total):
			order.complete = True
		order.save()

		if order.shipping == True:
			ShippingAddress.objects.create(
				customer=customer,
				order=order,
				address=data['shipping']['address'],
				city=data['shipping']['city'],
				state=data['shipping']['state'],
				zipcode=data['shipping']['zipcode'],
				)

	else:
		print("User is not logged in...")

	return JsonResponse('Payment completed!', safe=False)