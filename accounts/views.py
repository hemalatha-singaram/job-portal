import random
from datetime import timedelta

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.mail import send_mail
from django.shortcuts import redirect, render
from django.utils import timezone

from candidate.models import CandidateProfile

User = get_user_model()


def _role_matches(user, role):
    if role == "student":
        return CandidateProfile.objects.filter(user=user).exists()
    if role == "recruiter":
        return user.is_staff or user.groups.filter(name="Recruiters").exists()
    return False


def _send_sms(phone, code):
    # Optional real SMS delivery through Twilio. Without credentials, the code is printed to the dev console.
    import os
    sid = os.environ.get("TWILIO_ACCOUNT_SID")
    token = os.environ.get("TWILIO_AUTH_TOKEN")
    from_number = os.environ.get("TWILIO_FROM_NUMBER")
    if not (sid and token and from_number):
        print(f"[CampusHire SMS DEMO] Verification code for {phone}: {code}")
        return
    import base64
    from urllib.parse import urlencode
    from urllib.request import Request, urlopen
    payload = urlencode({"To": phone, "From": from_number, "Body": f"CampusHire verification code: {code}. Expires in 10 minutes."}).encode()
    auth = base64.b64encode(f"{sid}:{token}".encode()).decode()
    req = Request(f"https://api.twilio.com/2010-04-01/Accounts/{sid}/Messages.json", data=payload, headers={"Authorization": f"Basic {auth}"})
    with urlopen(req, timeout=10):
        pass


def forgot_password(request):
    role = request.GET.get("role", "student") if request.method == "GET" else request.POST.get("role", "student")
    if role not in {"student", "recruiter"}:
        role = "student"
    if request.method == "POST":
        contact = request.POST.get("contact", "").strip()
        user = User.objects.filter(email__iexact=contact).first()
        delivery = "email"
        if not user and role == "student":
            profile = CandidateProfile.objects.select_related("user").filter(phone=contact).first()
            if profile:
                user = profile.user
                delivery = "phone"
        if not user or not _role_matches(user, role):
            messages.error(request, "No account was found for that email/phone and role.")
            return render(request, "accounts/forgot_password.html", {"role": role})

        code = f"{random.randint(0, 999999):06d}"
        request.session["reset_email"] = user.email
        request.session["reset_role"] = role
        request.session["reset_code"] = code
        request.session["reset_expires"] = (timezone.now() + timedelta(minutes=10)).timestamp()
        if delivery == "phone":
            _send_sms(contact, code)
        else:
            send_mail("CampusHire password reset code", f"Your CampusHire verification code is {code}. It expires in 10 minutes.", None, [user.email], fail_silently=False)
        request.session["reset_delivery"] = delivery
        request.session["reset_contact"] = contact
        return redirect("verify_reset_code")
    return render(request, "accounts/forgot_password.html", {"role": role})


def verify_reset_code(request):
    role = request.session.get("reset_role", "student")
    email = request.session.get("reset_email")
    contact = request.session.get("reset_contact", email)
    delivery = request.session.get("reset_delivery", "email")
    if not email or not request.session.get("reset_code"):
        messages.error(request, "Please request a new verification code.")
        return redirect(f"forgot_password?role={role}")
    if request.method == "POST":
        code = request.POST.get("code", "").strip()
        expires = request.session.get("reset_expires", 0)
        if timezone.now().timestamp() > float(expires):
            messages.error(request, "That code has expired. Please request a new one.")
            return redirect(f"forgot_password?role={role}")
        if code != request.session.get("reset_code"):
            messages.error(request, "Incorrect verification code.")
            return render(request, "accounts/verify_code.html", {"email": contact, "role": role, "delivery": delivery})
        request.session["reset_verified"] = True
        return redirect("set_new_password")
    return render(request, "accounts/verify_code.html", {"email": contact, "role": role, "delivery": delivery})


def set_new_password(request):
    if not request.session.get("reset_verified"):
        return redirect(f"forgot_password?role={request.session.get('reset_role', 'student')}")
    email = request.session.get("reset_email")
    role = request.session.get("reset_role", "student")
    user = User.objects.filter(email__iexact=email).first()
    if not user or not _role_matches(user, role):
        messages.error(request, "Account could not be verified.")
        return redirect(f"forgot_password?role={role}")
    if request.method == "POST":
        password = request.POST.get("password", "")
        confirm = request.POST.get("confirm_password", "")
        if len(password) < 8:
            messages.error(request, "Password must contain at least 8 characters.")
        elif password != confirm:
            messages.error(request, "Passwords do not match.")
        else:
            user.set_password(password)
            user.save(update_fields=["password"])
            for key in ["reset_email", "reset_role", "reset_code", "reset_expires", "reset_verified", "reset_delivery", "reset_contact"]:
                request.session.pop(key, None)
            messages.success(request, "Password updated successfully. You can now log in.")
            return redirect("candidate_login" if role == "student" else "recruiter_login")
    return render(request, "accounts/set_password.html", {"email": email, "role": role})
