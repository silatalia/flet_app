import flet as ft
import requests
import json
import uuid
import re
import socket
from datetime import datetime, timedelta

# ✅ تعيين مهلة عامة لكل طلبات الشبكة (10 ثواني)
socket.setdefaulttimeout(10)

# ===================== قائمة المنتجات =====================
fakka_products = [
    "Fakka_2.5_Unite", "Fakka_4.25_Unite", "Fakka_5_Unite",
    "Fakka_6_NewUnite", "Fakka_7_Unite", "Fakka_9_Unite",
    "Fakka_10_Unite", "Fakka_10_NewUnite", "Fakka_10.5_Unite",
    "Fakka_11.5_Unite", "Fakka_12_Unite", "Fakka_12.5_Unite",
    "Fakka_13_Unite", "Fakka_13.5_Unite", "Fakka_15_Unite",
    "Fakka_15_NewUnite", "Fakka_15.5_Unite", "Fakka_16.5_Unite",
    "Fakka_17.5_Unite", "Fakka_19.5_NewUnite", "Fakka_20_Unite",
    "Fakka_26_Unite"
]

mared_products = ["Mared_10_Minuts", "Mared_10_Flexs", "Mared_10_Social"]
all_products = fakka_products + mared_products

product_names = {
    "Fakka_2.5_Unite": "فكة 2.5 جنيه",
    "Fakka_4.25_Unite": "فكة 4.25 جنيه",
    "Fakka_5_Unite": "فكة 5 جنيه",
    "Fakka_6_NewUnite": "فكة 6 جنيه",
    "Fakka_7_Unite": "فكة 7 جنيه",
    "Fakka_9_Unite": "فكة 9 جنيه",
    "Fakka_10_Unite": "فكة 10 جنيه",
    "Fakka_10_NewUnite": "فكة 10 جنيه (new)",
    "Fakka_10.5_Unite": "فكة 10.5 جنيه",
    "Fakka_11.5_Unite": "فكة 11.5 جنيه",
    "Fakka_12_Unite": "فكة 12 جنيه",
    "Fakka_12.5_Unite": "فكة 12.5 جنيه",
    "Fakka_13_Unite": "فكة 13 جنيه",
    "Fakka_13.5_Unite": "فكة 13.5 جنيه",
    "Fakka_15_Unite": "فكة 15 جنيه",
    "Fakka_15_NewUnite": "فكة 15 جنيه (new)",
    "Fakka_15.5_Unite": "فكة 15.5 جنيه",
    "Fakka_16.5_Unite": "فكة 16.5 جنيه",
    "Fakka_17.5_Unite": "فكة 17.5 جنيه",
    "Fakka_19.5_NewUnite": "فكة 19.5 جنيه",
    "Fakka_20_Unite": "فكة 20 جنيه",
    "Fakka_26_Unite": "فكة 26 جنيه",
    "Mared_10_Minuts": "مارد 10 دقايق",
    "Mared_10_Flexs": "مارد 10 فليكس",
    "Mared_10_Social": "مارد 10 سوشيال"
}

# ===================== دوال API =====================
def get_seamless_and_msisdn():
    url = "http://mobile.vodafone.com.eg/checkSeamless/realms/vf-realm/protocol/openid-connect/auth"
    params = {'client_id': "cash-app"}
    headers = {
        'User-Agent': "okhttp/4.12.0",
        'Connection': "Keep-Alive",
        'Accept-Encoding': "gzip",
        'x-agent-operatingsystem': "16",
        'clientId': "AnaVodafoneAndroid",
        'Accept-Language': "ar",
        'x-agent-device': "Samsung SM-A165F",
        'x-agent-version': "2025.11.1",
        'x-agent-build': "1063",
        'digitalId': "",
        'device-id': "b26ba335813fad21",
        'If-Modified-Since': "Thu, 02 Apr 2026 09:09:07 GMT"
    }
    try:
        resp = requests.get(url, params=params, headers=headers, timeout=8)
        if resp.status_code != 200:
            return None, None
        data = resp.json()
        seamless_token = data.get("seamlessToken")
        raw_msisdn = data.get("msisdn")
        if raw_msisdn:
            if raw_msisdn.startswith('1'):
                formatted_msisdn = '0' + raw_msisdn
            else:
                formatted_msisdn = raw_msisdn
        else:
            formatted_msisdn = None
        return seamless_token, formatted_msisdn
    except:
        return None, None

def get_access_token(seamless_token):
    url = "https://mobile.vodafone.com.eg/auth/realms/vf-realm/protocol/openid-connect/token"
    payload = {
        'grant_type': "password",
        'client_secret': "b86e30a8-ae29-467a-a71f-65c73f2ff5e3",
        'client_id': "cash-app"
    }
    headers = {
        'User-Agent': "okhttp/4.12.0",
        'Accept': "application/json, text/plain, */*",
        'Accept-Encoding': "gzip",
        'silentLogin': "true",
        'CRP': "false",
        'seamlessToken': seamless_token,
        'firstTimeLogin': "true",
        'x-agent-operatingsystem': "16",
        'clientId': "AnaVodafoneAndroid",
        'Accept-Language': "ar",
        'x-agent-device': "Samsung SM-A165F",
        'x-agent-version': "2025.11.1",
        'x-agent-build': "1063",
        'digitalId': "",
        'device-id': "b26ba335813fad21"
    }
    try:
        response = requests.post(url, data=payload, headers=headers, timeout=8)
        if response.status_code != 200:
            return None
        data = response.json()
        return data.get('access_token')
    except:
        return None

def extract_balance(data):
    try:
        if 'description' in data:
            desc = data['description']
            match = re.search(r'(\d+\.?\d*)', desc)
            if match:
                return float(match.group(1))
        if 'characteristics' in data:
            for char in data['characteristics']:
                if char.get('name') == 'balance':
                    return float(char.get('value', 0))
        if 'paymentMethod' in data:
            payment = data['paymentMethod']
            if 'characteristic' in payment:
                for char in payment['characteristic']:
                    if char.get('name') == 'balance':
                        return float(char.get('value', 0))
            if 'balance' in payment:
                return float(payment['balance'])
        if 'balance' in data:
            return float(data['balance'])
        return None
    except:
        return None

def get_balance(access_token, msisdn, pin_code):
    url = f"https://mobile.vodafone.com.eg/services/dxl/pm/paymentMethod/{msisdn}"
    headers = {
        "pinCode": pin_code,
        "X-Request-ID": str(uuid.uuid4()),
        "X-App-StackTrace": "",
        "device-id": "b26ba335813fad21",
        "Content-Type": "application/json",
        "api-version": "v2",
        "msisdn": msisdn,
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/json",
        "Accept-Language": "ar",
        "x-agent-operatingsystem": "16",
        "x-agent-device": "Samsung SM-A165F",
        "x-agent-version": "2025.11.1",
        "x-agent-build": "1063",
        "digitalId": "",
        "Connection": "close",
        "clientId": "AnaVodafoneAndroid",
        "Host": "mobile.vodafone.com.eg",
        "Accept-Encoding": "gzip",
        "User-Agent": "okhttp/4.12.0"
    }
    params = {"@type": "DigitalWallet", "@referredType": "CashBalance"}
    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            balance = extract_balance(data)
            return True, data, balance
        return False, response.text, None
    except:
        return False, "خطأ في الاتصال", None

def recharge_product(access_token, sender_msisdn, receiver_number, pin_code, product_id):
    url_order = "https://mobile.vodafone.com.eg/services/dxl/pom/productOrder"
    payload_order = {
        "channel": {"name": "MobileApp"},
        "orderItem": [{
            "action": "insert",
            "id": product_id,
            "product": {
                "characteristic": [
                    {"name": "PaymentMethod", "value": "VFCash"},
                    {"name": "USE_EMONEY", "value": "False"},
                    {"name": "MerchantCode", "value": ""}
                ],
                "id": product_id,
                "relatedParty": [
                    {"id": sender_msisdn, "name": "MSISDN", "role": "Subscriber"},
                    {"id": receiver_number, "name": "Receiver", "role": "Receiver"}
                ]
            },
            "@type": product_id,
            "eCode": 0
        }],
        "relatedParty": [{"id": pin_code, "name": "pin", "role": "Requestor"}],
        "@type": "CashFakkaAndMared"
    }
    headers_order = {
        'User-Agent': "okhttp/4.12.0",
        'Connection': "Keep-Alive",
        'Accept': "application/json",
        'Accept-Encoding': "gzip",
        'Content-Type': "application/json",
        'api-host': "ProductOrderingManagement",
        'useCase': "CashFakkaAndMared",
        'api-version': "v2",
        'msisdn': sender_msisdn,
        'Authorization': f"Bearer {access_token}",
        'Accept-Language': "ar",
        'x-agent-operatingsystem': "16",
        'clientId': "AnaVodafoneAndroid",
        'x-agent-device': "Samsung SM-A165F",
        'x-agent-version': "2025.11.1",
        'x-agent-build': "1063",
        'digitalId': "",
        'device-id': "b26ba335813fad21"
    }
    try:
        response_order = requests.post(url_order, json=payload_order, headers=headers_order, timeout=15)
        try:
            result = response_order.json()
            if response_order.status_code == 200:
                if result.get('state') == 'Completed' or result.get('complete') or result.get('code') == '0000':
                    return True, result
                else:
                    return False, result.get('reason', 'فشل العملية')
            else:
                return False, response_order.text
        except:
            return False, "خطأ في الاستجابة"
    except:
        return False, "انتهت المهلة"

# ===================== واجهة Flet =====================
def main(page: ft.Page):
    page.title = "فكّة كاش 💰"
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.scroll = ft.ScrollMode.AUTO
    page.theme = ft.Theme(color_scheme_seed=ft.colors.GREEN)
    page.bgcolor = ft.colors.GREY_50

    # متغيرات الحالة
    seamless_token = None
    sender_msisdn = None
    access_token = None
    current_balance = None

    # عناصر التحكم
    status_text = ft.Text("📡 جاهز للتسجيل", size=14, color=ft.colors.BLUE)
    balance_text = ft.Text("💰 الرصيد: غير معروف", size=18, weight=ft.FontWeight.BOLD)
    
    pin_input = ft.TextField(
        label="الرقم السري للمحفظة (PIN)",
        password=True,
        can_reveal_password=True,
        width=300,
        hint_text="6 أرقام",
        max_length=6
    )
    
    receiver_input = ft.TextField(
        label="رقم المستلم (11 رقم)",
        width=300,
        hint_text="مثال: 01234567890",
        max_length=11
    )

    product_dropdown = ft.Dropdown(
        label="اختر المنتج",
        width=300,
        options=[ft.dropdown.Option(key=p, text=product_names.get(p, p)) for p in all_products]
    )

    result_text = ft.Text("", size=14)
    log_area = ft.Column(spacing=3, scroll=ft.ScrollMode.AUTO, height=150)

    def add_log(message, color=ft.colors.BLACK):
        log_area.controls.append(ft.Text(f"• {message}", size=12, color=color))
        if len(log_area.controls) > 50:
            log_area.controls.pop(0)
        page.update()

    def update_status(msg, color=ft.colors.BLUE):
        status_text.value = msg
        status_text.color = color
        page.update()

    def login(e):
        nonlocal seamless_token, sender_msisdn, access_token, current_balance
        
        if len(pin_input.value) != 6 or not pin_input.value.isdigit():
            result_text.value = "❌ الرقم السري يجب أن يكون 6 أرقام"
            result_text.color = ft.colors.RED
            page.update()
            return

        update_status("⏳ جاري تسجيل الدخول...", ft.colors.ORANGE)
        page.update()
        
        try:
            seamless_token, sender_msisdn = get_seamless_and_msisdn()
            if not seamless_token or not sender_msisdn:
                update_status("❌ فشل تسجيل الدخول - تأكد من بيانات الموبايل", ft.colors.RED)
                return

            access_token = get_access_token(seamless_token)
            if not access_token:
                update_status("❌ فشل الحصول على التوكن", ft.colors.RED)
                return

            update_status(f"✅ تم الدخول - {sender_msisdn}", ft.colors.GREEN)
            
            # جلب الرصيد
            success, data, balance = get_balance(access_token, sender_msisdn, pin_input.value)
            if success and balance is not None:
                current_balance = balance
                balance_text.value = f"💰 الرصيد: {balance:,.2f} جنيه"
                balance_text.color = ft.colors.GREEN
                add_log(f"✅ تم تسجيل الدخول - الرصيد: {balance:,.2f} جنيه", ft.colors.GREEN)
            else:
                balance_text.value = "💰 الرصيد: غير متاح"
                balance_text.color = ft.colors.RED
                add_log("⚠️ تم الدخول لكن فشل جلب الرصيد", ft.colors.ORANGE)
        except Exception as ex:
            update_status(f"❌ خطأ: {str(ex)[:30]}", ft.colors.RED)
        
        page.update()

    def recharge_action(e):
        nonlocal access_token, current_balance
        
        if not access_token:
            result_text.value = "❌ يرجى تسجيل الدخول أولاً"
            result_text.color = ft.colors.RED
            page.update()
            return

        if not product_dropdown.value:
            result_text.value = "❌ يرجى اختيار منتج"
            result_text.color = ft.colors.RED
            page.update()
            return

        if len(receiver_input.value) != 11 or not receiver_input.value.startswith("01") or not receiver_input.value.isdigit():
            result_text.value = "❌ رقم غير صحيح (يجب أن يبدأ بـ 01 ويتكون من 11 رقم)"
            result_text.color = ft.colors.RED
            page.update()
            return

        update_status("⏳ جاري الشحن...", ft.colors.ORANGE)
        page.update()
        
        success, result = recharge_product(
            access_token, 
            sender_msisdn, 
            receiver_input.value, 
            pin_input.value, 
            product_dropdown.value
        )
        
        if success:
            result_text.value = f"✅ تم شحن {product_names.get(product_dropdown.value, '')} بنجاح!"
            result_text.color = ft.colors.GREEN
            add_log(f"✅ شحن {product_names.get(product_dropdown.value, '')} → {receiver_input.value}", ft.colors.GREEN)
            
            # تحديث الرصيد
            success2, data2, balance2 = get_balance(access_token, sender_msisdn, pin_input.value)
            if success2 and balance2 is not None:
                current_balance = balance2
                balance_text.value = f"💰 الرصيد: {balance2:,.2f} جنيه"
                balance_text.color = ft.colors.GREEN
                add_log(f"💰 الرصيد المتبقي: {balance2:,.2f} جنيه", ft.colors.BLUE)
        else:
            result_text.value = f"❌ فشل الشحن: {result}"
            result_text.color = ft.colors.RED
            add_log(f"❌ فشل الشحن: {result}", ft.colors.RED)
        
        update_status("✅ جاهز", ft.colors.GREEN)
        page.update()

    def refresh_balance(e):
        nonlocal access_token, current_balance
        if not access_token:
            result_text.value = "❌ يرجى تسجيل الدخول أولاً"
            result_text.color = ft.colors.RED
            page.update()
            return

        update_status("⏳ جاري تحديث الرصيد...", ft.colors.ORANGE)
        success, data, balance = get_balance(access_token, sender_msisdn, pin_input.value)
        if success and balance is not None:
            current_balance = balance
            balance_text.value = f"💰 الرصيد: {balance:,.2f} جنيه"
            balance_text.color = ft.colors.GREEN
            result_text.value = "✅ تم تحديث الرصيد"
            result_text.color = ft.colors.GREEN
            add_log(f"💰 تحديث الرصيد: {balance:,.2f} جنيه", ft.colors.BLUE)
        else:
            result_text.value = "❌ فشل تحديث الرصيد"
            result_text.color = ft.colors.RED
        update_status("✅ جاهز", ft.colors.GREEN)
        page.update()

    # ===================== تصميم الواجهة =====================
    header = ft.Container(
        content=ft.Column([
            ft.Text("💳 فكّة كاش", size=30, weight=ft.FontWeight.BOLD, color=ft.colors.GREEN),
            ft.Text("شحن كروت فكة ومارد بسهولة", size=14, color=ft.colors.GREY_600),
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=2),
        padding=15,
        bgcolor=ft.colors.WHITE,
        border_radius=10,
        shadow=ft.BoxShadow(blur_radius=10, color=ft.colors.GREY_300)
    )

    login_section = ft.Container(
        content=ft.Column([
            ft.Text("🔐 تسجيل الدخول", size=18, weight=ft.FontWeight.BOLD),
            pin_input,
            ft.ElevatedButton("تسجيل الدخول", on_click=login, icon=ft.icons.LOGIN, width=200),
            status_text,
            balance_text,
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=8),
        padding=15,
        bgcolor=ft.colors.WHITE,
        border_radius=10,
        shadow=ft.BoxShadow(blur_radius=5, color=ft.colors.GREY_300)
    )

    recharge_section = ft.Container(
        content=ft.Column([
            ft.Text("📱 شحن المنتج", size=18, weight=ft.FontWeight.BOLD),
            receiver_input,
            product_dropdown,
            ft.Row([
                ft.ElevatedButton("شحن", on_click=recharge_action, icon=ft.icons.SEND, width=130),
                ft.ElevatedButton("تحديث", on_click=refresh_balance, icon=ft.icons.REFRESH, width=130, color=ft.colors.BLUE),
            ], alignment=ft.MainAxisAlignment.CENTER),
            result_text,
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=8),
        padding=15,
        bgcolor=ft.colors.WHITE,
        border_radius=10,
        shadow=ft.BoxShadow(blur_radius=5, color=ft.colors.GREY_300)
    )

    log_section = ft.Container(
        content=ft.Column([
            ft.Text("📋 سجل العمليات", size=14, weight=ft.FontWeight.BOLD),
            ft.Container(
                content=log_area,
                height=120,
                border=ft.border.all(1, ft.colors.GREY_300),
                border_radius=5,
                padding=8,
                bgcolor=ft.colors.GREY_50
            ),
        ]),
        padding=15,
        bgcolor=ft.colors.WHITE,
        border_radius=10,
        shadow=ft.BoxShadow(blur_radius=5, color=ft.colors.GREY_300)
    )

    page.add(
        header,
        ft.Divider(height=5, color=ft.colors.TRANSPARENT),
        login_section,
        ft.Divider(height=5, color=ft.colors.TRANSPARENT),
        recharge_section,
        ft.Divider(height=5, color=ft.colors.TRANSPARENT),
        log_section,
        ft.Container(
            content=ft.Text("🔹 يتطلب تشغيل بيانات الهاتف (Mobile Data) بشريحة فودافون", size=10, color=ft.colors.GREY_500),
            padding=8
        )
    )

ft.app(target=main)