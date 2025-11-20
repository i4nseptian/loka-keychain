"""
signals.py - Django Signals untuk tracking login/logout
FIXED VERSION - Dengan error handling untuk CSRF
"""

from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.dispatch import receiver
from django.utils import timezone
from .models import LoginHistory


def parse_user_agent(user_agent_string):
    """
    Parse user agent string untuk mendapatkan info browser, OS, device
    """
    browser = "Unknown"
    os = "Unknown"
    device = "Desktop"
    
    if not user_agent_string:
        return browser, os, device
    
    # Detect Browser
    if "Chrome" in user_agent_string and "Edg" not in user_agent_string:
        browser = "Chrome"
    elif "Firefox" in user_agent_string:
        browser = "Firefox"
    elif "Safari" in user_agent_string and "Chrome" not in user_agent_string:
        browser = "Safari"
    elif "Edg" in user_agent_string:
        browser = "Edge"
    elif "Opera" in user_agent_string or "OPR" in user_agent_string:
        browser = "Opera"
    
    # Detect OS
    if "Windows" in user_agent_string:
        os = "Windows"
    elif "Mac OS" in user_agent_string:
        os = "MacOS"
    elif "Linux" in user_agent_string:
        os = "Linux"
    elif "Android" in user_agent_string:
        os = "Android"
        device = "Mobile"
    elif "iPhone" in user_agent_string or "iPad" in user_agent_string:
        os = "iOS"
        device = "Mobile" if "iPhone" in user_agent_string else "Tablet"
    
    return browser, os, device


@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    """
    Signal handler ketika user berhasil login
    Mencatat: user, waktu, IP address, device info
    FIXED: Dengan try-except untuk handle CSRF error
    """
    try:
        # Ambil IP address
        ip_address = request.META.get('HTTP_X_FORWARDED_FOR')
        if ip_address:
            ip_address = ip_address.split(',')[0].strip()
        else:
            ip_address = request.META.get('REMOTE_ADDR', '127.0.0.1')
        
        # Ambil user agent
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        
        # Parse user agent untuk info device
        browser, os, device = parse_user_agent(user_agent)
        
        # Ambil session key - PASTIKAN SESSION SUDAH ADA
        if not request.session.session_key:
            request.session.create()
        session_key = request.session.session_key
        
        # Get email dan name dari Django User
        user_email = getattr(user, 'email', '') or f'{user.username}@local.com'
        user_name = getattr(user, 'username', 'User')
        
        # Simpan ke database
        LoginHistory.objects.create(
            user=user,  # Django User untuk admin login
            user_email=user_email,
            user_name=user_name,
            ip_address=ip_address,
            user_agent=user_agent,
            session_key=session_key,
            browser=browser,
            os=os,
            device=device
        )
        
        # Print untuk debugging
        print(f"✅ LOGIN TRACKED: {user_name} ({user_email}) dari {ip_address} - {browser} on {os}")
    
    except Exception as e:
        # Jangan sampai error tracking mengganggu login
        print(f"⚠️ Login tracking error: {e}")
        import traceback
        traceback.print_exc()


@receiver(user_logged_out)
def log_user_logout(sender, request, user, **kwargs):
    """
    Signal handler ketika user logout
    Update waktu logout pada record terakhir
    FIXED: Dengan try-except untuk handle error
    """
    if user:
        try:
            # Cari login history terakhir yang belum ada logout_time
            login_record = LoginHistory.objects.filter(
                user=user,
                logout_time__isnull=True
            ).latest('login_time')
            
            # Update logout time
            login_record.logout_time = timezone.now()
            login_record.save()
            
            # Print untuk debugging
            duration = login_record.get_duration()
            print(f"🚪 LOGOUT TRACKED: {user.username} - Durasi sesi: {duration}")
            
        except LoginHistory.DoesNotExist:
            print(f"⚠️ No active login record found for {user.username}")
        except Exception as e:
            print(f"⚠️ Logout tracking error: {e}")