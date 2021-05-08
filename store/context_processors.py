from .models import Customer, Order


def cart_items(request):
	customer = request.user.customer
	order, _ = Order.objects.get_or_create(customer=customer, complete=False)
	return {'cart_items': order.get_cart_items}