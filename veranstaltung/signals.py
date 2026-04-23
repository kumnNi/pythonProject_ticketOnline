from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.auth.signals import user_logged_in
from django.contrib.auth.models import User
from .models import UserProfile, Warenkorb
#
# #comment the whole block before creating superuser
# #remove comment after creating super user for this block to work where it transfers
# #the item from an unauthorized user to an authorized user


@receiver(user_logged_in)
def on_user_login(sender, request, user, **kwargs):
    # Update the cart upon user login
    session_id = request.session.session_key
    if session_id:
        user_profile = user.userprofile
        guest_user_profile = UserProfile.objects.filter(user__email='guest@gmail.com').first()

        if guest_user_profile:
            guest_items = Warenkorb.objects.filter(myuser=guest_user_profile)
            for guest_item in guest_items:
                guest_item.myuser = user_profile
                guest_item.save()
            guest_user_profile.delete()

        # Debug print statements
        print("User logged in. Session ID:", session_id)
        print("User Profile:", user_profile)
        print("Guest User Profile:", guest_user_profile)
