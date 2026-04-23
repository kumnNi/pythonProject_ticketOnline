import uuid
from datetime import date, datetime
from decimal import Decimal

from django.contrib import messages
from django.contrib.auth import user_logged_in, login
#from django.contrib.auth.forms import UserCreationForm
from veranstaltung.forms import UserCreationForm, CustomUserCreateForm,CustomUserCreateFormSet

from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Sum
from django.dispatch import receiver
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.utils import timezone
from django.views import generic, View
from django.views.decorators.http import require_http_methods
from django.views.generic import TemplateView, UpdateView, DeleteView, CreateView
from django.contrib.auth.decorators import login_required
from veranstaltung.forms import UpdateEventForm, UpdateEventLocationForm, UpdateCategoryForm
from veranstaltung.models import Event, EventLocation, Category, User, UserProfile, Warenkorb, Ticket


# Create your views here.

class HomePageView(TemplateView):
    template_name = "homepage.html"
    paginate_by = 6

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if self.request.user.is_authenticated:
            if self.request.user.is_superuser:
                self.setup_admin_context(context)
            elif self.request.user.is_staff:
                self.setup_user_context(context)
            else:
                self.setup_guest_context(context)
        else:
            self.setup_guest_context(context)
        return context

    def setup_admin_context(self, context):
        context["event_page"] = self.get_paginated_data(Event.objects.all(), 'event_page')
        context["eventLocation_page"] = self.get_paginated_data(EventLocation.objects.all(), 'eventLocation_page')
        context["category_page"] = self.get_paginated_data(Category.objects.all(), 'category_page')

    def setup_user_context(self, context):
        user_profile = get_object_or_404(UserProfile, user=self.request.user)
        my_events = Event.objects.filter(userID=user_profile)
        my_locations = EventLocation.objects.filter(userID=user_profile)
        context["event_page"] = self.get_paginated_data(my_events, 'event_page')
        context["eventLocation_page"] = self.get_paginated_data(my_locations, 'eventLocation_page')
        context["category_page"] = self.get_paginated_data(Category.objects.all(), 'category_page')

    def setup_guest_context(self, context):
        context["event_page"] = self.get_paginated_data(Event.objects.all(), 'event_page')
        context["eventLocation_page"] = self.get_paginated_data(EventLocation.objects.all(), 'eventLocation_page')
        context["category_page"] = self.get_paginated_data(Category.objects.all(), 'category_page')

    def get_paginated_data(self, queryset, parameter_name):
        paginator = Paginator(queryset, self.paginate_by)
        page_number = self.request.GET.get(parameter_name)
        return paginator.get_page(page_number)


# Event-Classes
class EventListView(generic.ListView):
    model = Event
    context_object_name = 'event_list'
    template_name = 'events/eventList.html'
    paginate_by = 6

    def get_context_data(self, **kwargs):
        context = super(EventListView, self).get_context_data(**kwargs)
        event_list_sorted = Event.objects.order_by('datum').all()
        event_paginator = Paginator(event_list_sorted, self.paginate_by)
        event_page_number = self.request.GET.get('event_page')
        event_page = event_paginator.get_page(event_page_number)
        current_url = self.request.build_absolute_uri()
        context["event_List_sorted"] = event_list_sorted
        context['title'] = 'Events'
        context['current_url'] = current_url[-8:-1]
        context['event_page'] = event_page
        return context


# EventDetailView shows details for the Event
class EventDetailView(generic.DetailView):
    model = Event
    context_object_name = 'event'
    template_name = 'events/event_details.html'


# EventUpdateView updates the eventdetails via form
class EventUpdateView (UpdateView):
    model = Event
    form_class = UpdateEventForm
    template_name = 'events/event_update.html'
    success_url = '/events'

    def form_valid(self, form):
        submitted_data = form.cleaned_data

    # Additional processing can be done here if needed
    # For example, logging or sending a notification
        return super().form_valid(form)


# EventDeleteView delete Event
class EventDeleteView (DeleteView):
    model = Event
    context_object_name = 'event'
    success_url = reverse_lazy("homepage")
    template_name = 'events/event_delete.html'


# EventCreateView creates a new Event
class EventCreateView (CreateView):
    model = Event
    form_class = UpdateEventForm
    template_name = 'events/event_create.html'
    success_url = '/'
    # today = date.today()
    # today_aware = timezone.make_aware(datetime.combine(today, datetime.min.time()))
    # initial = {'start_date': today_aware}

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Create any data and add it to the context
        context['title'] = 'Event erstellen'
        return context

    def form_valid(self, form):
        # Set the userid to the currently logged-in user
        # form.instance.userid = self.request.user

        # Continue with the standard form_valid behavior
        return super().form_valid(form)


#check location available for Event
def is_location_available(location_id, event_date):
    try:
        location = EventLocation.objects.get(id=location_id)
        events_at_location = Event.objects.filter(locationID=location, datum=event_date)
        return not events_at_location.exists()
    except EventLocation.DoesNotExist:
        return False
        events_at_location = event.objects.filter(locationid=location, datum=event_date)
        return not events_at_location.exists()
    except EventLocation.DoesNotExist:
        return False


#create Event
@login_required
def create_event_view(request):
    if request.method == 'POST':
        event_form = UpdateEventForm(request.POST)
        user_profile = get_object_or_404(UserProfile, user=request.user.id)
        print(user_profile)
        print(request.POST)
        print(event_form)
        #https://stackoverflow.com/questions/3305413/how-to-preserve-timezone-when-parsing-date-time-strings-with-strptime
        #https://stackoverflow.com/questions/22108634/django-how-to-make-a-datetime-object-aware-of-the-timezone-in-which-it-was-crea
        event_date_str = datetime.strptime(request.POST['datum'], '%Y-%m-%d')
        event_date_aware = timezone.make_aware(event_date_str, timezone.get_current_timezone())
        location_id = request.POST.get('locationID')
        if event_form.is_valid():
            if len(request.POST['name']) < 3:
                messages.warning(request, 'Name des Events ist zu kurz.')
                return render(request, 'events/event_create.html', {'form': event_form, 'title': 'create Event'})
            elif event_date_aware < timezone.now():
                messages.warning(request, 'Das Veranstaltungsdatum muss in der Zukunft liegen.')
                return render(request, 'events/event_create.html', {'form': event_form, 'title': 'create Event'})

            elif is_location_available(location_id, event_date_str):
                #vent_form.userID = user_profile
                #event_form = UpdateEventForm(user_id=request.user.id)
                event_form.userID_id = request.user.id
                event_form.save()
                messages.success(request, 'Veranstaltung erfolgreich erstellt.')
                return redirect('homepage')

            else:
                return render(request, 'events/unavailable_location.html')
        else:
            pass
            print(request.user.id)
            print('no Information')
            print(event_form.errors)
            messages.warning(request, 'no Information.')
        return redirect('event-create')

    else: # request.method == 'GET'
        event_form = UpdateEventForm()
        context = {'form': event_form }
        context['title'] = "Create an Event"
        return render(request, 'events/event_create.html', context)


# EventLocation
class EventLocationListView(generic.ListView):
    model = EventLocation
    context_object_name = 'eventLocation_list'
    template_name = 'eventlocations/eventLocationList.html'
    paginate_by = 20

    def get_context_data(self, **kwargs):
        context = super(EventLocationListView, self).get_context_data(**kwargs)
        eventLocation_list = EventLocation.objects.all()
        eventLocation_paginator = Paginator(eventLocation_list, self.paginate_by)
        eventLocation_page_number = self.request.GET.get('eventLocation_page')
        eventLocation_page = eventLocation_paginator.get_page(eventLocation_page_number)
        current_url = self.request.build_absolute_uri()

        context['title'] = 'Venues'
        context["eventLocation_page"] = eventLocation_page
        context["current_url"] = current_url[-16:-1] # takes last fourteen characters of the current url
        return context


class EventLocationDetailView(generic.DetailView):
    model = EventLocation
    context_object_name = 'eventLocation'
    template_name = 'eventlocations/eventLocation_details.html'

    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super(EventLocationDetailView, self).get_context_data(**kwargs)

        location_pk = self.kwargs['pk']
        event_list_sorted = Event.objects.filter(locationID=location_pk).order_by('-datum').all()
        location_name = EventLocation.objects.filter(id=location_pk).values('location').get()
        place = EventLocation.objects.filter(id=location_pk).values('standort').get()
        capacity = EventLocation.objects.filter(id=location_pk).values('seatingCapacity').get()
        detail = EventLocation.objects.filter(id=location_pk).values('detail').get()

        paginator = Paginator(event_list_sorted, self.paginate_by)
        page = self.request.GET.get('page')

        try:
            events = paginator.page(page)
        except PageNotAnInteger:
            events = paginator.page(1)
        except EmptyPage:
            events = paginator.page(paginator.num_pages)

        context['event_list'] = events
        context['location'] = location_name
        context['place'] = place
        context['capacity'] = capacity
        context['detail'] = detail
        return context


# EventLocationUpdateView updates the eventdetails via form
class EventLocationUpdateView (UpdateView):
    model = EventLocation
    form_class = UpdateEventLocationForm
    template_name = 'eventlocations/eventLocation_update.html'
    success_url = '/eventLocations'

    def form_valid(self, form):
        submitted_data = form.cleaned_data
        return super().form_valid(form)


# EventLocationDeleteView delete Event
class EventLocationDeleteView (DeleteView):
    model = EventLocation
    context_object_name = 'eventLocation'
    success_url = reverse_lazy("homepage")
    template_name = 'eventlocations/eventLocation_delete.html'


# EventCreateView creates a new Event
class EventLocationCreateView (CreateView):
    model = EventLocation
    template_name = 'eventlocations/eventLocation_create.html'
    success_url = '/'
    fields = ['location', 'standort', 'seatingCapacity', 'detail']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Create Venue'
        return context

    def form_valid(self, form):
        # Set the userid to the currently logged-in user
        #user_profile = get_object_or_404(UserProfile, user=self.request.user)
        #form.instance.userID_id = user_profile
        form.instance.userID_id = self.request.user.id
        # Continue with the standard form_valid behavior
        return super().form_valid(form)

@require_http_methods(["GET"])
def event_in_location_view(request, location_id):
    context = {}
    location = get_object_or_404(EventLocation, id=location_id)
    context['title'] = 'Liste aller Location in : '+str(location)
    context["eventInLocation"] = Event.objects.filter(locationID=location)
    return render(request, "events/event_in_location.html", context)


@require_http_methods(["GET"])
def category_list_view(request):
    context = {}
    category_list = Category.objects.all().order_by('title')
    paginator = Paginator(category_list, 10)
    page_number = request.GET.get('category_page')
    try:
        category_page = paginator.page(page_number)
    except PageNotAnInteger:
        category_page = paginator.page(1)
    except EmptyPage:
        category_page = paginator.page(paginator.num_pages)
    context['title'] = 'Categories'
    context["category_page"] = category_page
    context['showNavbar'] = True
    return render(request, "categories/categoryList.html", context)


class CategoryDetailView(generic.DetailView):
    model = Category
    context_object_name = 'category'
    template_name = 'categories/category_details.html'


def create_category_view(request):
    if request.method == 'POST':
        category_form = UpdateCategoryForm(request.POST)
        if category_form.is_valid():
            if len(request.POST['title']) < 2:
                messages.success(request, 'Name des Category ist zu kurz.')
                return render(request, 'categories/category_create.html', {'form': category_form, 'title': 'create Category'})
            elif len(request.POST['description']) < 3:
                messages.success(request, 'Name des Events ist zu kurz.')
                return render(request, 'categories/category_create.html',
                              {'form': category_form, 'title': 'create Category'})
            else:
                category_form.save()
        else:
            print('invalid category')
            pass
        return redirect('category-list')
    else:  # request.method == 'GET'
        category_form = UpdateCategoryForm()

    context = {'form': category_form, 'title': "Create Category"}
    return render(request, 'categories/category_create.html', context)


def update_category_view (request, id):
    categoryUpdate = get_object_or_404(Category, id=id)
    if request.method == 'POST':
        category_form = UpdateCategoryForm(request.POST, instance=categoryUpdate)
        if category_form.is_valid():
            category_form.save()
            return redirect('category-list')
    else:
        category_form = UpdateCategoryForm(instance=categoryUpdate)

    context = {'form': category_form, 'title': "Update Category" }
    return render(request, 'categories/category_update.html', context)


def delete_category_view(request, id):
    category_Delete = get_object_or_404(Category, id=id)
    context = {'category': category_Delete}
    if request.method == "POST":
        # delete object
        category_Delete.delete()
        return redirect('category-list')
    return render(request, "categories/category_delete.html", context)


@require_http_methods(["GET"])
def event_in_category_view(request, category_id):
    context = {}
    category = get_object_or_404(Category, id=category_id)
    context['title'] = 'Liste aller Category : '+str(category)
    context["eventInCategory"] = Event.objects.filter(categoryID=category)
    return render(request, "categories/event_in_category.html", context)

#new Warenkorb

def cart_summary(request):
    user_profile = None
    session_id = request.session.session_key

    if request.user.is_authenticated:
        user_profile = UserProfile.objects.get(user=request.user)
    if user_profile:
        event_item = Warenkorb.objects.filter(myuser=user_profile)

    else:
        event_item = Warenkorb.objects.filter(sessionID=session_id)

    total_price = sum(item.total_price() for item in event_item)

    if request.method == "POST":
        item_id = request.POST.get("item_id")
        quantity = int(request.POST.get("quantity"))
        item = get_object_or_404(Warenkorb, id=item_id)

    return render(request, 'cart/cart_summary.html', {"page": {
        "title": "Event",
        "headline": "Deez Venues"
    }, "event_items": event_item,
        "total_price": total_price})

def cart_create(request, event_id):
    session_id = request.session.session_key
    if not session_id:
        request.session.save()  # Ensure a session ID is created
        session_id = request.session.session_key
    # Check if the user is authenticated
    if request.user.is_authenticated:
        user_profile = UserProfile.objects.get(user=request.user)

        guest_user_profile = UserProfile.objects.filter(user__email__in='guest@gmail.com').first()
        print("Before deletion - Guest User Profile:", guest_user_profile)
        if guest_user_profile:
            guest_items = Warenkorb.objects.filter(myuser=guest_user_profile)
            if guest_items.exists():
                print("Items associated with Guest User Profile:")
                for guest_item in guest_items:
                    print(f"- {guest_item}")
                    # Update ownership to the authenticated user
                    guest_item.myuser = user_profile
                    guest_item.save()
                    # Print User instance associated with the guest_user_profile
                print("User instance associated with Guest User Profile:", guest_user_profile.user)
                # Delete the guest profile
                guest_user_profile.delete()# Print User instance after deletion
                print("User instance after deletion:", guest_user_profile.user)

                print("After deletion - Guest User Profile:", guest_user_profile)

                # Query Warenkorb for items asciated with the authenticated user
                user_items = Warenkorb.objects.filter(myuser=user_profile)

                # Print information about the items associated with the authenticated user
                if user_items.exists():
                    print("Items associated with the authenticated user:")
                    for user_item in user_items:
                        print(f"- {user_item}")
                else:
                    print("No items found for the authenticated user.")
    else:
        # print("Guest User Profile not found.")
        # Create a dummy or guest user for reference in the Warenkorb object
        guest_user, created = User.objects.get_or_create(email='guest@gmail.com')
        user_profile, _ = UserProfile.objects.get_or_create(user=guest_user, defaults={'nickname': 'Guest'})

    event_instance = get_object_or_404(Event, pk=event_id)

    event_item, created = Warenkorb.objects.get_or_create(
        myuser=user_profile,
        eventID=event_instance,
        sessionID=session_id,
        defaults={'quantity': 1}
    )

    if not created:
        event_item.quantity += 1
        event_item.save()

    # Update the session variable with the total quantity of items in the cart
    total_quantity = Warenkorb.objects.filter(sessionID=session_id).aggregate(Sum('quantity'))['quantity__sum'] or 0
    request.session['cart'] = total_quantity
    request.session.save()
    #messages.success(request, "Item added to your cart")
    print("After updating session - Cart Quantity:", request.session['cart'])
    return redirect("cart-summary")


def cart_delete(request, warenkorb_id):
    user_profile = None
    session_id = request.session.session_key

    cart_item = get_object_or_404(Warenkorb, id=warenkorb_id)
    if request.user.is_authenticated:
        user_profile = UserProfile.objects.get(user=request.user)
        if cart_item.myuser == user_profile:
            cart_item.delete()
            messages.success(request, "Item removed from your cart.")

    elif cart_item.sessionID == session_id:
        cart_item.delete()

    # Update the session variable with the total quantity of items in the cart
    total_quantity = Warenkorb.objects.filter(sessionID=session_id).aggregate(Sum('quantity'))['quantity__sum'] or 0
    request.session['cart'] = total_quantity
    request.session.save()
        # messages.success(request, "Item removed from your cart.")

    return redirect("cart-summary")


@login_required()
def ticket_pay_create_view(request):
    tickets = []

    if request.method == 'POST':
        event_ids = request.POST.getlist('eventID')
        location_ids = request.POST.getlist('eventLocationID')
        prices = request.POST.getlist('price')
        quantities = request.POST.getlist('quantity')

        # Iterate through the submitted form data
        for event_id, event_location_id, price, quantity in zip(event_ids, location_ids, prices, quantities):
            event_id = int(event_id)
            event_location_id = int(event_location_id)
            price = float(price)
            quantity = int(quantity)

            # Retrieve objects from the database
            event_location = get_object_or_404(EventLocation, id=event_location_id)
            event = get_object_or_404(Event, id=event_id)
            user_profile = UserProfile.objects.get(user=request.user)

            # Check quantity before payment
            if quantity <= event_location.seatingCapacity:
                total_price = quantity * price

                ticket = Ticket.objects.create(
                    userID=user_profile,
                    eventID=event,
                    eventLocationID=event_location,
                    price=total_price,
                    quantity=quantity
                )
                ticket.save()
                Warenkorb.objects.filter(myuser=user_profile).delete()
                tickets.append(ticket)

                # Update seating capacity and other logic
                if quantity == event_location.seatingCapacity:
                    Event.objects.filter(id=event_id).update(ticketAvailability=False)
                else:
                    event_location.seatingCapacity -= quantity
                    event_location.save()
            else:
                messages.warning(request, 'quantity of seatingCapacity  is bigger than we have')
                return redirect('cart-summary')
        if ticket:
            return render(request, 'cart/ticket_pay.html', {'tickets': tickets})
    return render(request, 'cart/cart_summary.html')


@login_required()
def ticket_view(request, userid):
    user_profile = get_object_or_404(UserProfile, user=userid)

    context = {}
    ticket_list = Ticket.objects.filter(userID=user_profile)
    paginator = Paginator(ticket_list, 5)
    page_number = request.GET.get('ticket_page')
    try:
        ticket_page = paginator.page(page_number)
    except PageNotAnInteger:
        ticket_page = paginator.page(1)
    except EmptyPage:
        ticket_page = paginator.page(paginator.num_pages)
    context['title'] = 'Purchase History'
    context["ticket_page"] = ticket_page
    context['showNavbar'] = True
    return render(request, "ticket/ticketList.html", context)


@require_http_methods(["GET"])
def ticket_detail_view(request, id):
    ticket_list = get_object_or_404(Ticket, id=id)

    return render(request, "ticket/ticket_details.html", {'ticket': ticket_list})


def register_view(request):
    if request.method == 'POST':

        user_form = CustomUserCreateForm(request.POST)
        profile_formset = CustomUserCreateFormSet(request.POST)

        if user_form.is_valid() and profile_formset.is_valid():
            user = user_form.save()
            profile_formset = CustomUserCreateFormSet(request.POST, instance=user)
            profile_formset.save()

            #is_staff = request.POST.get('is_staff', False)
            is_staff_checked = 'is_staff' in request.POST.getlist('is_staff')
            print(is_staff_checked)
            if is_staff_checked:
                user.is_staff = True
                user.save()

            login(request, user)
            #return render(request, 'homepage.html', {'user_form': user_form, 'profile_formset': profile_formset})
            return redirect('homepage')
    else:
        user_form = CustomUserCreateForm()
        profile_formset = CustomUserCreateFormSet()

    return render(request, 'registration/register.html', {'user_form': user_form, 'profile_formset':profile_formset})

















