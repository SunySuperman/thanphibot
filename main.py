from telegram import Update
from telegram.ext import MessageHandler, filters, ApplicationBuilder, CommandHandler, ContextTypes
import requests
import re
import json
import random
import secrets
import base64
import os
import datetime
import subprocess
import urllib.request
from io import BytesIO
import aiohttp
s = requests.Session()

print('Bot đang hoạt động')
# Constants
security_device_fingerprint = "7e0700fe594926a4bf24fad7ece64221"
TELEGRAM_TOKEN = "6428474178:AAEbLuIMXBHF-BKx6j1bmSK_0po7mtvd_WE"
VOUCHER_URL = "https://shopee.vn/api/v2/voucher_wallet/save_voucher"
COOKIE = "SPC_ST=.dkI4YjYycUJjazQ4bVRDQw2EbvdAELMkeqCk6Bj5c/5iEHBWoW1tTm9nBPMnhe93981yquPQerZlnF+qn98GkMRer0Y7GGJnRJ0xPqzZ+YyhJx8MRb6BNEBE22H4A3KICGOR9cWDpGEFlNKzjia/GJvyLR44MwSkqh8BvUOwVYDasZxt6Y5i9mHUpve9TFFL5TJvKwLA+SSeyBadqW73uA=="

async def banmoi(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /banmoi command to check voucher status"""
    url = "https://mall.shopee.vn/api/v2/welcome_package_v2/get_promotions"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Linux; Android 9; MI 8 Lite Build/PKQ1.181007.001; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/124.0.6367.82 Mobile Safari/537.36 Shopee Beeshop locale/vi version=1233 appver=32414 rnver=1714113514 app_type=1 platform=web_android os=28'
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            data = await response.json()

            output_lines = []

            for voucher in data['data']['vouchers']:
                reward_value = voucher.get('reward_value', 0)
                if reward_value is not None:
                    formatted_reward_value = "Mã giảm {:,.0f}đ".format(reward_value / 100000)
                else:
                    formatted_reward_value = ""
                percentage_claimed = voucher.get('percentage_claimed', 0)
                percentage_used = voucher.get('percentage_used', 0)
                await update.message.reply_text(f"{voucher['icon_text']} | {voucher['voucher_code']} | {voucher.get('sub_icon_text', '')} | {formatted_reward_value} | Đã sử dụng {percentage_used}% | Đã nhận {percentage_claimed}%")

async def vandon(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /vandon command to check voucher status"""
    cookie = update.message.text.split(" ")[1]
    with open('cookie.txt', 'a') as f:
        f.write(f"{cookie}\n")
    
    # Define a list of user agents as a constant
    MACOS_USER_AGENTS =[
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 12_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 Shopee Beeshop locale/vi version=1233 appver=32414 rnver=1714113514 app_type=1 platform=web_mac os=12.2',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 Shopee Beeshop locale/vi version=1233 appver=32414 rnver=1714113514 app_type=1 platform=web_mac os=11.6',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 Shopee Beeshop locale/vi version=1233 appver=32414 rnver=1714113514 app_type=1 platform=web_mac os=10.15.7',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 Shopee Beeshop locale/vi version=1233 appver=32414 rnver=1714113514 app_type=1 platform=web_mac os=10.14.6',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 Shopee Beeshop locale/vi version=1233 appver=32414 rnver=1714113514 app_type=1 platform=web_mac os=10.13.6',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 Shopee Beeshop locale/vi version=1233 appver=32414 rnver=1714113514 app_type=1 platform=web_mac os=10.12.6',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 Shopee Beeshop locale/vi version=1233 appver=32414 rnver=1714113514 app_type=1 platform=web_mac os=10.11.6',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 Shopee Beeshop locale/vi version=1233 appver=32414 rnver=1714113514 app_type=1 platform=web_mac os=10.10.5'
    ]

    def get_random_user_agent() -> str:
        return random.choice(MACOS_USER_AGENTS)
    try:
        url = "https://shopee.vn/api/v4/order/get_all_order_and_checkout_list"
        params = {"limit": 10, "offset": 0}
        headers = {"Cookie": cookie, "User-Agent": get_random_user_agent()}
        response_data = requests.get(url, headers=headers, params=params).json()

        # Check for errors
        if response_data['error'] == 9:
            await update.message.reply_text('Tài khoản đã bị cấm hoặc cookie đã hết hạn.')
        elif response_data['error'] == 0:
            # Process orders
            for order in response_data['data']['order_data']['details_list']:
                order_id = order.get('info_card', {}).get('order_id')
                try:
                    url = f"https://mall.shopee.vn/api/v4/order/buyer/get_logistics_info?order_id={order_id}"
                    payload = ""
                    headers = {
                        'Cookie': cookie,
                        'User-Agent': get_random_user_agent()
                        }

                    response = requests.request("GET", url, headers=headers, data=payload).json()
                    s.cookies.clear()
                    try:
                        time_display1 = response['data']['time_display']['type']
                        time_display2 = response['data']['time_display']['time']
                        dt = datetime.datetime.fromtimestamp(time_display2)
                        # Format the date and time in Vietnamese format
                        vietnamese_date_format = "T%w, %d Tháng %m %Y"
                        vietnamese_date_string = dt.strftime(vietnamese_date_format)

                        await update.message.reply_text(f'{time_display1} {vietnamese_date_string}\n')
                    except:
                        carrier_name = response['data']['carrier_name']
                        tracking_number = response['data']['tracking_number']
                        await update.message.reply_text(f'Thông tin\nVận chuyển bởi {carrier_name}\n\n'
                                                    f'Mã vận đơn - {tracking_number}\n\n')

                    description_list = []
                    ctime_list = []
                    for location in response['data']['tracking_info_list']:
                        description_list.append(location['description'])
                        ctime_list.append(location['ctime'])
                    for i in range(len(description_list)):
                        description = description_list[i]
                        ctime = ctime_list[i]
                        dt = datetime.datetime.fromtimestamp(ctime)

                        # Format the date and time in Vietnamese format
                        ctime_date_format = "%d Tháng %m  %H:%M"
                        ctime_date_string = dt.strftime(ctime_date_format)
                        await update.message.reply_text(f'{ctime_date_string} | {description.strip()}\n')

                except Exception as e:
                    print(f"Error: {e}")
                
    except Exception as e:
        await update.message.reply_text('Lỗi, liên hệ t.me/cuccungplus: {str(e)}')           
async def donhang(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /donhang command to check voucher status"""
    mavd = update.message.text.split(" ")[1]
    with open('cookie.txt', 'a') as f:
        f.write(f"{mavd}\n")
    cookie = mavd

    # Define a list of user agents as a constant
    MACOS_USER_AGENTS =[
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 12_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 Shopee Beeshop locale/vi version=1233 appver=32414 rnver=1714113514 app_type=1 platform=web_mac os=12.2',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 Shopee Beeshop locale/vi version=1233 appver=32414 rnver=1714113514 app_type=1 platform=web_mac os=11.6',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 Shopee Beeshop locale/vi version=1233 appver=32414 rnver=1714113514 app_type=1 platform=web_mac os=10.15.7',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 Shopee Beeshop locale/vi version=1233 appver=32414 rnver=1714113514 app_type=1 platform=web_mac os=10.14.6',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 Shopee Beeshop locale/vi version=1233 appver=32414 rnver=1714113514 app_type=1 platform=web_mac os=10.13.6',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 Shopee Beeshop locale/vi version=1233 appver=32414 rnver=1714113514 app_type=1 platform=web_mac os=10.12.6',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 Shopee Beeshop locale/vi version=1233 appver=32414 rnver=1714113514 app_type=1 platform=web_mac os=10.11.6',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 Shopee Beeshop locale/vi version=1233 appver=32414 rnver=1714113514 app_type=1 platform=web_mac os=10.10.5'
    ]

    def get_random_user_agent() -> str:
        return random.choice(MACOS_USER_AGENTS)

    try:
        url = "https://shopee.vn/api/v4/order/get_all_order_and_checkout_list"
        params = {"limit": 10, "offset": 0}
        headers = {"Cookie": cookie, "User-Agent": get_random_user_agent()}
        response_data = requests.get(url, headers=headers, params=params).json()

        # Check for errors
        if response_data['error'] == 9:
            await update.message.reply_text('Tài khoản đã bị cấm hoặc cookie đã hết hạn.')
        elif response_data['error'] == 0:
            # Process orders
            for order in response_data['data']['order_data']['details_list']:
                order_id = order.get('info_card', {}).get('order_id')
                try:
                    url = f"https://shopee.vn/api/v4/order/get_order_detail?order_id={order_id}"
                    headers = {"Cookie": cookie, "User-Agent": get_random_user_agent()}
                    response_data = requests.get(url, headers=headers).json()

                    s.cookies.clear()
                    tinhtrang = response_data['data']['status']['list_view_text']['text']
                    if tinhtrang == "order_list_text_to_ship_ship_by_date_not_calculated":
                        tinhtrang = 'Đơn hàng đang được xử lý bởi Shopee'
                    elif tinhtrang == "order_list_text_to_ship_order_shipbydate":
                        tinhtrang = 'Đơn hàng đang được xử lý bởi người bán'
                    elif tinhtrang == "order_list_text_cancelled_by_buyer":
                        tinhtrang = 'Đơn hàng đã huỷ bởi người mua'
                    elif tinhtrang == 'order_list_text_to_receive_non_cod':
                        #tinhtrang = 'Đơn hàng đã hoàn thành\nCảm ơn bạn đã mua sắm tại Shopee!'
                        tinhtrang = 'Đơn hàng đang trong quá trình vận chuyển'
                    elif tinhtrang == 'order_list_text_to_receive_cod_not_delivered':
                        tinhtrang = 'Đơn hàng đang trong quá trình vận chuyển'
                    elif tinhtrang == 'order_list_text_cancelled_by_system':
                        tinhtrang = 'Đơn hàng đã huỷ bởi hệ thống'
                    elif tinhtrang == 'order_list_text_cancelled_by_seller':
                        tinhtrang = 'Đơn hàng đã huỷ bởi nguời bán'
                    else:
                        tinhtrang = tinhtrang
                    madonhang = response_data['data']['processing_info']['order_sn']
                    giatien = response_data['data']['info_card']['parcel_cards'][0]['payment_info']['total_price']
                    giatien2 = giatien / 100000
                    formatted_amount = f"{giatien2:,.0f}".replace(',', '.')

                    tennguoinhan = response_data['data']['address']['shipping_name']
                    formatted_sdt = response_data['data']['address']['shipping_phone']
                    sdt = f"(+{formatted_sdt[:2]}) {formatted_sdt[2:]}"
                    diachi = response_data['data']['address']['shipping_address']

                    tenshop = response_data['data']['info_card']['parcel_cards'][0]['shop_info']['shop_name']
                    idshop = response_data['data']['info_card']['parcel_cards'][0]['shop_info']['shop_id']

                    item_ids = []
                    item_names = []
                    model_names = []
                    shop_ids = []
                    for parcel_card in response_data['data']['info_card']['parcel_cards']:
                        for item_group in parcel_card['product_info']['item_groups']:
                            for item in item_group['items']:
                                item_ids.append(item['item_id'])
                                item_names.append(item['name'])
                                model_names.append(item['model_name'])
                                shop_ids.append(item['shop_id'])
                    await update.message.reply_text(
                        f"Mã đơn hàng: {madonhang}\n"
                        f"Tình trạng: {tinhtrang}\n"
                        f"\n-------ĐỊA CHỈ NHẬN HÀNG---------\n"
                        f"{tennguoinhan}\n"
                        f"{sdt}\n"
                        f"{diachi}\n"
                        f"\n-------SHOP---------\n"
                        f"Tên Shop: {tenshop}\n"
                        f"Shop ID: {idshop}\n\n")

                    for i, (item_id, item_name, model_name, shop_id) in enumerate(zip(item_ids, item_names, model_names, shop_ids)):
                        await update.message.reply_text(
                            f"Sản phẩm {i+1}:\n"
                            f"Tên sản phẩm: {item_name}\n"
                            f"Phân loại: {model_name}\n"
                            f"Liên kết: https://shopee.vn/product/{shop_id}/{item_id}\n\n"
                            f"Vui lòng thanh toán {formatted_amount}đ khi nhận hàng.\n"
                        )

                    checkmvd = response_data['data']['shipping']['tracking_number']
                    if checkmvd == "":
                        await update.message.reply_text("\n-------VẬN CHUYỂN---------\n"
                            "Liên hệ với nhà bán để xác nhận đơn hàng\n")
                    else:
                        title = response_data['data']['shipping']['masked_carrier']['text']
                        hinhthuc = response_data['data']['payment_method']['payment_channel_name']['text']
                        donvivc = response_data['data']['shipping']['fulfilment_carrier']['text']
                        mavandon = response_data['data']['shipping']['tracking_number']
                        tinhtrang_item = response_data['data']['shipping']['tracking_info']['description']

                        await update.message.reply_text(
                            f"\n-------VẬN CHUYỂN---------\nHình thức vận chuyển: {title} ({hinhthuc})\nĐơn vị vận chuyển: {donvivc}\nMã vận đơn: {mavandon}\nThông tin: {tinhtrang_item}\n"
                        )
                except Exception as e:
                    await update.message.reply_text(f"'Lỗi, liên hệ t.me/cuccungplus': {str(e)}")

        else:
            await update.message.reply_text('Bạn chưa có đơn hàng nào.\n')
    except Exception as e:
        await update.message.reply_text('Lỗi, liên hệ t.me/cuccungplus: {str(e)}')
    
async def thongbao(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /thongbao command to check voucher status"""
    gone = update.message.text.split(" ")[1]
    #print(gone)
    with open('thongbao.txt', 'a') as f:
        f.write(f"{gone}\n")
    url = "https://mall.shopee.vn/api/v4/notification/get_notifications"
    params = {
        "action_cate":4,
        "limit":10
        }
    payload = ""
    def get_client_ip(headers, trusted_proxy_count=2):
        x_forwarded_for = headers.get("X-Forwarded-For")
        if x_forwarded_for:
            ips = [ip.strip() for ip in x_forwarded_for.split(",")]
            return ips[trusted_proxy_count - 1]
        return None
    headers = {
      "X-Forwarded-For": "1.2.3.4,172.16.1.101,28.178.124.142,198.40.10.101",
      "Cookie": gone,
      "User-Agent": "Android app Shopee appver=32414 app_type=1 platform=native_android os=28 Cronet/102.0.5005.61"
    }

    data = requests.get(url, params=params, headers=headers, data=payload).json()
    try:
        for action in data['data']['actions']:
            title = action['title']
            content = action['content']
            createtime = action['createtime']
            dt = datetime.datetime.fromtimestamp(createtime)
            timeclaim = dt.strftime("%H:%M:%S, ngày %d-%m-%Y")
            hex_string = content
            hex_string2 = title
            decoded_bytes = bytes.fromhex(hex_string)
            decoded_bytes2 = bytes.fromhex(hex_string2)
            decoded_string = decoded_bytes.decode("utf-8")
            decoded_string2 = decoded_bytes2.decode("utf-8")
            text = decoded_string
            text2 = decoded_string2
            decoded_string_text = re.sub(r"<b>|</b>", "", text)
            decoded_string_text2 = re.sub(r"<b>|</b>", "", text2)
            await update.message.reply_text(f'{decoded_string_text2}\n{decoded_string_text}\n{timeclaim}\n\n')

    except:
        await update.message.reply_text(f'Tài khoản đã bị cấm hoặc cookie đã hết hạn.')
    
async def vouncher(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /vc command to check voucher status"""
    voucher_code = update.message.text.split(" ")[1]
    with open('voucher_code.txt', 'a') as f:
        f.write(f"{voucher_code}\n")
    payload = json.dumps({"voucher_code": f"{voucher_code}", "need_user_voucher_status": True})
    headers = {
        "X-Forwarded-For": "27.75.226.25",
        "Cookie": COOKIE,
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(VOUCHER_URL, headers=headers, data=payload)
        response.raise_for_status()  # Raise an exception for 4xx or 5xx status codes
        response_data = response.json()
        tinhtrang = response_data["data"]["voucher"]["percentage_used"]
        start_time = response_data["data"]["voucher"]["start_time"]
        end_time = response_data["data"]["voucher"]["end_time"]
        await update.message.reply_text(f"Voucher {voucher_code} đã được sử dụng {tinhtrang}%")
    except requests.RequestException as e:
        await update.message.reply_text(f"Error: {e}")
    except json.JSONDecodeError as e:
        await update.message.reply_text(f"Error parsing JSON response: {e}")


async def check_user(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    #"""Handle /check command"""
    MACOS_USER_AGENTS =[
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 12_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 Shopee Beeshop locale/vi version=1233 appver=32414 rnver=1714113514 app_type=1 platform=web_mac os=12.2',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 Shopee Beeshop locale/vi version=1233 appver=32414 rnver=1714113514 app_type=1 platform=web_mac os=11.6',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 Shopee Beeshop locale/vi version=1233 appver=32414 rnver=1714113514 app_type=1 platform=web_mac os=10.15.7',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 Shopee Beeshop locale/vi version=1233 appver=32414 rnver=1714113514 app_type=1 platform=web_mac os=10.14.6',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 Shopee Beeshop locale/vi version=1233 appver=32414 rnver=1714113514 app_type=1 platform=web_mac os=10.13.6',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 Shopee Beeshop locale/vi version=1233 appver=32414 rnver=1714113514 app_type=1 platform=web_mac os=10.12.6',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 Shopee Beeshop locale/vi version=1233 appver=32414 rnver=1714113514 app_type=1 platform=web_mac os=10.11.6',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 Shopee Beeshop locale/vi version=1233 appver=32414 rnver=1714113514 app_type=1 platform=web_mac os=10.10.5'
    ]

    def get_random_user_agent() -> str:
        return random.choice(MACOS_USER_AGENTS)
    
    def convert_phone_to_intl(phone):
        if len(phone) == 10:
            return convert_vn_phone_to_intl(phone)
        elif len(phone) == 9:
            return convert_vn_phone_to_intl("0" + phone)
        else:
            return phone
    
    def convert_vn_phone_to_intl(vn_phone):
        if not vn_phone.startswith("0") or len(vn_phone) != 10:
            return vn_phone

        intl_phone = f"{VN_COUNTRY_CODE}{vn_phone[1:]}"
        return intl_phone

    def identify_input(input_string):
        email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        phone_pattern = r"^\d{9,12}$"
        username_pattern = r"^[a-zA-Z0-9_]+$"

        if re.match(email_pattern, input_string):
            return "email"
        elif re.match(phone_pattern, input_string):
            return "phone"
        elif re.match(username_pattern, input_string):
            return "username"
        else:
            return "unknown"
        
    nhap = update.message.text
    inputs = [nhap]
    with open('user.txt', 'a') as f:
        f.write(f"{nhap}\n")
    for input_string in inputs:
        dinhdang = (f"{identify_input(nhap)}")
    if dinhdang == 'username':
        url = "https://shopee.vn/api/v4/account/login_by_password"

        payload = json.dumps({
          "username": nhap,
          "password": "08428467285068b426356b9b0d0ae1e80378d9137d5e559e5f8377dbd6dde29f",
          "support_ivs": True,
          "client_identifier": {
            "security_device_fingerprint": security_device_fingerprint
          }
        })
        headers = {
          'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.2 Safari/605.1.15',
          'Content-Type': 'application/json'
        }
        response = requests.post(url, headers=headers, data=payload).json()
        error= response['error']
        if error == 2:
            await update.message.reply_text(f'{nhap} -> Tài khoản đang hoạt động')
        elif error == 9:
            await update.message.reply_text(f'{nhap} -> Tài khoản đã bị cấm')
        else:
            await update.message.reply_text(f'Error System')
                
    elif dinhdang == 'phone':
        phone_numbers = [input_string]
        VN_COUNTRY_CODE = "84"
        for phone in phone_numbers:
            phoneformat = convert_phone_to_intl(phone)
        operation = random.choice([i for i in range(1, 16) if i not in [3,5,6,11,15]])
        url1 = "https://mall.shopee.vn/api/v4/otp/get_settings_v2"

        payload1 = json.dumps({
          "operation": operation,
          "phone": phoneformat,
          "app_installation_status": {
            "installed_channels": [],
            "not_installed_channels": []
          },
          "supported_channels": [
            0,
            1,
            2,
            5
          ],
          "support_session": True
        })
        headers1 = {
          'User-Agent': get_random_user_agent(),
          'Content-Type': 'application/json'
        }

        try:
            response1 = s.post(url1, headers=headers1, data=payload1).json()
            s.cookies.clear()
            preferred_channel = response1['data']['preferred_channel']
            if preferred_channel == 2:
                await update.message.reply_text(f'Số {nhap} chưa được đăng ký. Bạn có thể sử dụng!')
            else:
                url = "https://shopee.vn/api/v4/account/login_by_password"

                payload = json.dumps({
                    "phone": phoneformat,
                    "password": "08428467285068b426356b9b0d0ae1e80378d9137d5e559e5f8377dbd6dde29f",
                    "support_ivs": True,
                    "client_identifier": {
                    "security_device_fingerprint": security_device_fingerprint
                    }
                })
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.2 Safari/605.1.15',
                    'Content-Type': 'application/json'
                }
                response = requests.post(url, headers=headers, data=payload).json()
                error= response['error']
                if error == 2:
                    await update.message.reply_text(f'{nhap} -> Tài khoản đang hoạt động')
                elif error == 9:
                    await update.message.reply_text(f'{nhap} -> Tài khoản đã bị cấm')
                else:
                    await update.message.reply_text(f'Bạn đã kiểm tra quá nhiều lần. Vui lòng quay lại sau.')
        except Exception as e:
            await update.message.reply_text('Lỗi, liên hệ t.me/cuccungplus: {str(e)}')
            
    elif dinhdang == 'email':
        url = "https://shopee.vn/api/v4/account/login_by_password"

        payload = json.dumps({
            "email": nhap,
            "password": "08428467285068b426356b9b0d0ae1e80378d9137d5e559e5f8377dbd6dde29f",
            "support_ivs": True,
            "client_identifier": {
            "security_device_fingerprint":security_device_fingerprint
            }
        })
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.2 Safari/605.1.15',
            'Content-Type': 'application/json'
        }
        response = requests.post(url, headers=headers, data=payload).json()
        #print(response)
        error= response['error']
        if error == 2:
            await update.message.reply_text(f'{nhap} -> Tài khoản đang hoạt động')
        elif error == 9:
            await update.message.reply_text(f'{nhap} ->Tài khoản đã bị cấm')
        else:
            await update.message.reply_text(f'Error System')

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /start command"""
    await update.message.reply_text(f"Xin chào {update.effective_user.first_name}")

async def help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /help command"""
    await update.message.reply_text(f"Xin chào {update.effective_user.first_name}\n\nCác lệnh để sử dụng BOT:\n\n"
                                    "1. Kiểm tra tình trạng vouncher người mới\nVD: /vouncher BANMOI...\n\n"
                                    "2. Kiểm tra thông báo của tài khoản (Đơn hàng đã được xác nhận chưa, có bị huỷ không, ...)\nVD: /thongbao SPC_ST=.dk...\n\n"
                                    "3. Kiểm tra số lượt sử dụng mã của banner Shopee (Freeship, 50.000, 60.000)\nVD: /banmoi\n\n"
                                    "4. Kiểm tra tài khoản có còn hoạt động không hay đã bị cấm\nVD: username/số điện thoại/email đều được\n\n"
                                    "5. Kiểm tra đơn hàng (Tất cả các thông tin về đơn hàng)\nVD: /donhang SPC_ST=.dk...\n\n"
                                    "6. Kiểm tra vận chuyển\nVD: /vandon SPC_ST=.dk...")
    
app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("help", help))
app.add_handler(CommandHandler("vouncher", vouncher))
app.add_handler(CommandHandler("thongbao", thongbao))
app.add_handler(CommandHandler("banmoi", banmoi))
app.add_handler(CommandHandler("donhang", donhang))
app.add_handler(CommandHandler("vandon", vandon))
app.add_handler(MessageHandler(filters.TEXT, check_user))
app.run_polling()
