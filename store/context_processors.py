from .models import Customer, Order, Product
import json


def cart_items(request):
	if request.user.is_authenticated:
		customer = request.user.customer
		order, _ = Order.objects.get_or_create(customer=customer, complete=False)
		return {'cart_items': order.get_cart_items}
	else:
		cart = None
		items = 0
		try:
			cart = json.loads(request.COOKIES.get('cart'))
		except:
			cart = {}
		print(cart)
		for key, value in cart.items():
			items += value['quantity']
		return {'cart_items': items}