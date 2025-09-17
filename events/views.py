from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.timezone import localtime

from .forms import EventForm
from .models import Event
from attendance.models import Registration
from attendance.utils import generate_qr_png, build_invitation
import os
from django.conf import settings

def public_list(request):
    active = Event.objects.filter(is_active=True).order_by('start_at')
    old = Event.objects.filter(is_active=False).order_by('-start_at')[:50]
    return render(request, 'events/public_list.html', {'active_events':active, 'old_events':old})

def event_detail(request, pk):
    ev = get_object_or_404(Event, pk=pk)
    reg = None
    if request.user.is_authenticated:
        reg = Registration.objects.filter(user=request.user, event=ev).first()
    return render(request, 'events/detail.html', {'event':ev, 'registration': reg})

@login_required
def register_event(request, pk):
    ev = get_object_or_404(Event, pk=pk, is_active=True)
    reg, created = Registration.objects.get_or_create(user=request.user, event=ev)

    if created or not reg.qr_image or not reg.invitation_image:
        # QR payload — faqat UUID (PII yo'q). Skan qilinganda backendda izlanadi.
        payload = f"REG:{str(reg.id)}"
        qr_png = generate_qr_png(payload)

        # QR faylini saqlash
        qr_path = os.path.join(settings.MEDIA_ROOT, 'qrcodes', f'{reg.id}.png')
        os.makedirs(os.path.dirname(qr_path), exist_ok=True)
        with open(qr_path, 'wb') as f:
            f.write(qr_png)
        reg.qr_image.name = f'qrcodes/{reg.id}.png'

        # User va event tafsilotlari
        profile = getattr(request.user, 'external_profile', None)
        user_fullname = request.user.first_name or request.user.username
        email = request.user.email or (profile.email if profile else '')
        when_str = f"{localtime(ev.start_at).strftime('%Y-%m-%d %H:%M')} - {localtime(ev.end_at).strftime('%H:%M')}"
        where_str = ev.location
        room_str = ev.room or ''
        user_photo_path = (profile.photo_local.path if (profile and profile.photo_local) else "")

        # Taklifnomani qurish (endi qr_text ham beriladi)
        invite_png = build_invitation(
            user_fullname,
            email,
            ev.title,
            when_str,
            where_str,
            room_str,
            user_photo_path,
            qr_png,
            payload   # bu yerda qo‘shimcha argument — qr_text
        )

        # Faylga saqlash
        inv_path = os.path.join(settings.MEDIA_ROOT, 'invites', f'{reg.id}.png')
        os.makedirs(os.path.dirname(inv_path), exist_ok=True)
        with open(inv_path, 'wb') as f:
            f.write(invite_png)
        reg.invitation_image.name = f'invites/{user_fullname}.png'
        reg.save()

    messages.success(request, "Ro'yxatdan o'tdingiz! Taklifnomangiz tayyor.")
    return redirect('events:detail', pk=ev.pk)


@login_required
def my_events(request):
    regs = Registration.objects.filter(user=request.user).select_related('event').order_by('-created_at')
    return render(request, 'events/my_events.html', {'registrations': regs})

@staff_member_required   # faqat admin/staff foydalanuvchilar kira oladi
def create_event(request):
    if request.method == "POST":
        form = EventForm(request.POST, request.FILES)
        if form.is_valid():
            ev = form.save(commit=False)
            ev.published_by = request.user   # kim yaratganini belgilash
            ev.save()
            messages.success(request, "Event muvaffaqiyatli yaratildi!")
            return redirect("events:detail", pk=ev.pk)
    else:
        form = EventForm()
    return render(request, "events/create_event.html", {"form": form})