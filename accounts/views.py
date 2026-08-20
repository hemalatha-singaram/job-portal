"""Account helpers.

CampusHire intentionally does not use email OTPs. Registration activates the
account immediately and login uses the normal Django username/email + password
flow.  Password recovery is also disabled here rather than pretending that an
email service is configured when it is not.
"""

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.shortcuts import redirect

User = get_user_model()


def forgot_password(request):
    """Keep the old URL harmless for bookmarks; no OTP or email is generated."""
    messages.info(
        request,
        "Password recovery by email is disabled in this demo. Please contact the CampusHire administrator to reset an account password.",
    )
    role = request.GET.get("role", "student")
    return redirect("candidate_login" if role == "student" else "recruiter_login")
