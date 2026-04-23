
from django.urls import path, include
from . import views

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('', views.HomePageView.as_view(), name='homepage'),
    path('meine-veranstaltungen/', views.HomePageView.as_view(), name='my-events'),
    path('events/', views.EventListView.as_view(), name='eventListSorted'),
    path('events/<int:pk>', views.EventDetailView.as_view(), name='event-details'),
    path('events/create/', views.create_event_view, name='event-create'),
    path('events/delete/<int:pk>', views.EventDeleteView.as_view(), name='event-delete'),
    path('events/update/<int:pk>', views.EventUpdateView.as_view(), name='event-update'),

    path('eventLocations/', views.EventLocationListView.as_view(), name='eventLocations'),
    path('eventLocations/<int:pk>', views.EventLocationDetailView.as_view(), name='eventLocation-details'),
    path('eventLocations/create/', views.EventLocationCreateView.as_view(), name='eventLocation-create'),
    path('eventLocations/delete/<int:pk>', views.EventLocationDeleteView.as_view(), name='eventLocation-delete'),
    path('eventLocations/update/<int:pk>', views.EventLocationUpdateView.as_view(), name='eventLocation-update'),

    path('categories/', views.category_list_view, name='category-list'),
    path('categories/<int:pk>/', views.CategoryDetailView.as_view(), name='category-details'),
    path('categories/create/', views.create_category_view, name='category-create'),
    path('categories/delete/<int:id>/', views.delete_category_view, name='category-delete'),
    path('categories/update/<int:id>/', views.update_category_view, name='category-update'),

    path('event-in-location/<int:location_id>/', views.event_in_location_view, name='event-in-location'),
    path('event-in-category/<int:category_id>/', views.event_in_category_view, name='event-in-category'),

    path('cart/', views.cart_summary, name='cart-summary'),
    path('cart/create/<int:event_id>/', views.cart_create, name='cart-create'),
    path('cart/delete/<int:warenkorb_id>/', views.cart_delete, name='cart-delete'),

    path('cart/ticket/', views.ticket_pay_create_view, name='ticket-pay'),
    path('ticket/<int:userid>/', views.ticket_view, name='ticket-view'),
    path('ticket/detail/<int:id>/', views.ticket_detail_view, name='ticket-details'),

]
