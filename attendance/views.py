from datetime import timezone

from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.timezone import now
from django.contrib import messages
from .models import Registration, AttendanceLog
from events.models import Event
from django.db.models import Q

@staff_member_required
def scan_page(request):
    # Oddiy variant: input maydonga QR dan olingan matnni qo'yish (REG:UUID)
    # Istasangiz html5-qrcode bilan kamera skanini qo'shamiz (quyida shablon).
    return render(request, 'attendance/scan.html')

@staff_member_required
def resolve_registration(request, reg_id):
    reg = get_object_or_404(Registration, pk=reg_id)
    user = reg.user
    profile = getattr(user, 'external_profile', None)
    context = {
        'registration': reg,
        'event': reg.event,
        'user_fullname': user.first_name or user.username,
        'email': user.email or (profile.email if profile else ''),
        'mobile': profile.mobile if profile else '',
        'role': profile.role if profile else '',
        'emp_or_std_id': profile.emp_or_std_id if profile else '',
        'photo': (profile.photo_local.url if (profile and profile.photo_local) else None),
    }
    return render(request, 'attendance/resolve.html', context)


@staff_member_required
def check_qr(request):
    code = request.GET.get("code")
    if not code:
        return JsonResponse({"success": False, "message": "QR kod topilmadi."})

    try:
        reg = Registration.objects.get(id=code.split(":")[-1])  # REG:uuid formatda bo'lsa
    except Registration.DoesNotExist:
        return JsonResponse({"success": False, "message": "❌ QR kod noto‘g‘ri."})

    # allaqachon skan qilingan bo‘lsa — qaytaramiz, lekin userni yubormaymiz
    if reg.attended:
        return JsonResponse({
            "success": False,
            "message": "❌ Bu QR allaqachon ishlatilgan."
        })

    # birinchi marta keldi → bazaga yozamiz va foydalanuvchini qaytaramiz
    reg.attended = True
    reg.attended_at = now()
    reg.save()

    return JsonResponse({
        "success": True,
        "user": {
            "user_id": reg.user.id,
            "name": reg.user.get_full_name() or reg.user.username,
            "email": reg.user.email,
            "username": reg.user.username,
            "attended_at": reg.attended_at.strftime("%H:%M:%S"),
        }
    })

@staff_member_required
def attended_list(request):
    users = [
        {
            "name": r.user.get_full_name(),
            "email": r.user.email,
            "username": r.user.username,
            "attended_at": r.attended_at.strftime("%Y-%m-%d %H:%M:%S"),
        }
        for r in Registration.objects.filter(attended=True).order_by("-attended_at")
    ]
    return JsonResponse({"users": users})


@staff_member_required
def clear_attendance(request):
    Registration.objects.filter(attended=True).update(attended=False, attended_at=None)
    return JsonResponse({"success": True})
@staff_member_required
def mark_attended(request, reg_id):
    reg = get_object_or_404(Registration, pk=reg_id)
    reg.attended = True
    reg.attended_at = now()
    reg.save()
    messages.success(request, f"{reg.user} attended.")
    return redirect('attendance:resolve', reg_id=reg.id)

@staff_member_required
def report(request):
    event_id = request.GET.get('event')
    q = Registration.objects.select_related('user','event')
    if event_id:
        q = q.filter(event_id=event_id)
    events = Event.objects.order_by('-start_at')
    return render(request, 'attendance/report.html', {'events':events, 'regs':q.order_by('-created_at')[:500]})


@staff_member_required
def attendance_logs(request):
    """Oxirgi 20 ta logni qaytaradi (JSON)"""
    logs = AttendanceLog.objects.select_related('user').order_by('-scanned_at')[:20]
    data = []
    for log in logs:
        data.append({
            "name": log.user.first_name or log.user.username,
            "email": log.user.email,
            "username": log.user.username,
            "time": log.scanned_at.strftime("%H:%M:%S"),
        })
    return JsonResponse({"logs": data})


@staff_member_required
def clear_logs(request):
    """Barcha loglarni tozalash"""
    AttendanceLog.objects.all().delete()
    return JsonResponse({"success": True})
