from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404

# Create your views here.
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from .models import ExternalUserProfile
import requests, os
from django.core.files.base import ContentFile

LOGIN_API = "https://acharyajava.uz/AcharyaInstituteUZB/api/authenticate"
USER_DETAILS_API = "https://acharyajava.uz/AcharyaInstituteUZB/api/getUserDetailsById/{}"
IMAGE_DOWNLOAD_API = "https://acharyajava.uz/AcharyaInstituteUZB/api/student/studentImageDownload"
ROLES_API = "https://acharyajava.uz/AcharyaInstituteUZB/api/findRoles/{}"

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        res = requests.post(LOGIN_API, json={"username": username, "password": password})
        if res.status_code == 200 and res.json().get("success"):
            data = res.json().get("data", {})
            token = data.get("token")
            user_id = data.get("userId")
            headers = {"Authorization": f"Bearer {token}"}

            # user details
            detail_res = requests.get(USER_DETAILS_API.format(user_id), headers=headers)
            if detail_res.status_code != 200:
                messages.error(request, "Profil ma'lumotlarini olishda xatolik")
                return redirect('login')
            info = detail_res.json().get("data", {})

            # roles
            role_res = requests.get(ROLES_API.format(user_id), headers=headers)
            role_name = role_short = role_id = ""
            if role_res.status_code == 200:
                rdata = role_res.json().get("data", [])
                if rdata:
                    role_name = rdata[0].get("role_name", "")
                    role_short = rdata[0].get("role_short_name", "")
                    role_id = rdata[0].get("role_id", "")

            # user create/update
            user, _ = User.objects.get_or_create(username=data.get("userName"))
            user.first_name = info.get("name", "")
            user.email = info.get("email", "") or ""
            user.save()

            profile, _ = ExternalUserProfile.objects.get_or_create(
                user=user,
                defaults={"external_user_id": str(user_id)}
            )
            profile.external_user_id = str(user_id)
            profile.preferred_name = info.get("preferredName", "") or ""
            profile.email = info.get("email", "") or ""
            profile.mobile = info.get("mobileNumber", "") or ""
            profile.usertype = info.get("usertype", "") or ""
            profile.emp_or_std_id = info.get("empOrStdId", "") or ""
            profile.role = role_name
            profile.role_short = role_short
            profile.role_id = str(role_id)

            # photo download faqat yangi bo‘lsa yoki localda yo‘q bo‘lsa
            image_path = info.get("photoAttachmentPath") or ""

            if image_path and (not profile.photo_local or profile.photo_path != image_path):
                image_url = f"{IMAGE_DOWNLOAD_API}?student_image_attachment_path={image_path}"
                img_response = requests.get(image_url, headers=headers)
                if img_response.status_code == 200:
                    filename = os.path.basename(image_path) or f"{user.username}.png"

                    # eski rasmni o‘chirib tashlash
                    if profile.photo_local:
                        profile.photo_local.delete(save=False)

                    profile.photo_local.save(filename, ContentFile(img_response.content), save=False)
                    profile.photo_path = image_path  # yangi pathni saqlaymiz
            profile.save()

            login(request, user)
            return redirect('events:public_list')
        messages.error(request, "Username yoki parol noto‘g‘ri!")
    return render(request, 'users/login.html')

@login_required
def profile_view(request):
    profile = get_object_or_404(ExternalUserProfile, user=request.user)
    return render(request, "users/profile.html", {"profile": profile})

def logout_view(request):
    logout(request)
    return redirect('events:public_list')
