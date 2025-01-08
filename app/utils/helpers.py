import base64

def get_image_base64(image_path):
    with open(image_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode()
    return encoded_string

def create_image_html(base64_string, width='auto', height='auto'):
    return f"""
    <div style="display:flex;justify-content:center;">
        <img src="data:image/png;base64,{base64_string}" style="width:{width};height:{height};max-width:100%;">
    </div>
    """

def human_format(num):
    magnitude = 0
    sign = '-' if num < 0 else ''
    num = abs(num)
    while abs(num) >= 1000:
        magnitude += 1
        num /= 1000.0
    return f'{sign}${num:.2f}{["", "K", "M", "B", "T"][magnitude]}'


def human_format1(num):
    magnitude = 0
    while abs(num) >= 1000:
        magnitude += 1
        num /= 1000.0
    return '{:.2f}{}'.format(num, ['', 'K', 'M', 'B'][magnitude])


def custom_price_format(num):
    if num < 0.0000001:
        return f"${num:.9f}".rstrip('0').rstrip('.')
    elif num < 0.000001:
        return f"${num:.8f}".rstrip('0').rstrip('.')
    elif num < 0.00001:
        return f"${num:.7f}".rstrip('0').rstrip('.')
    elif num < 0.0001:
        return f"${num:.6f}".rstrip('0').rstrip('.')
    elif num < 0.001:
        return f"${num:.5f}".rstrip('0').rstrip('.')
    elif num < 0.01:
        return f"${num:.4f}"
    elif num < 0.1:
        return f"${num:.3f}"
    elif num < 1:
        return f"${num:.2f}"
    else:
        return f"${num:.2f}"