import json

from .models import *


def cookieCart(request):
	items = []
	order = {'get_cart_items': 0, 'get_cart_total': 0, 'shipping': False}
	try:
		cart = json.loads(request.COOKIES.get('cart'))
	except:
		cart = {}
	for key, value in cart.items():
		try:
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
		except:
			pass

	return {"order": order, "items": items}


def cartData(request):
	if request.user.is_authenticated:
		customer = request.user.customer
		order, created = Order.objects.get_or_create(customer=customer, complete=False)
		items = order.orderitem_set.all()
	else:
		cookieData = cookieCart(request)
		items = cookieData.get("items")
		order = cookieData.get("order")
	return {'items': items, 'order': order}


def guestOrder(request, data):
	print("User is not logged in...")

	print("COOKIES:", request.COOKIES.get('cart'))
	name = data['form']['name']
	email = data['form']['email']

	cookieData = cookieCart(request)
	items = cookieData.get("items")	

	customer, created = Customer.objects.get_or_create(email=email)
	customer.name = name
	customer.save()

	order = Order.objects.create(customer=customer, complete=False)

	for item in items:
		product = Product.objects.get(id=item['product']['id'])
		orderItem = OrderItem.objects.create(product=product,
			order=order, quantity=item['quantity'])

	return customer, order