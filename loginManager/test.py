from PIL import Image

def get_dominant_color(image_path):
    # 打开图片并转换为RGB模式
    image = Image.open(image_path).convert('RGB')
    
    
    # 获取图片中所有颜色及其像素数量
    colors = image.getcolors(image.size[0] * image.size[1])
    
    # 按像素数量排序，取前10个最大的颜色
    top_colors = sorted(colors, key=lambda x: x[0], reverse=True)[:250]
    
    # 计算每个颜色的亮度
    brightness_values = []
    for count, (r, g, b) in top_colors:
        brightness = 0.299 * r + 0.587 * g + 0.114 * b
        brightness_values.append((brightness, (r, g, b)))
    
    # 选择亮度值最大的颜色
    brightest_color = max(brightness_values, key=lambda x: x[0])[1]
    
    return f"#{brightest_color[0]:02X}{brightest_color[1]:02X}{brightest_color[2]:02X}"

# 示例：提取图片中最亮的颜色
image_path = 'bg/default.png'  # 替换为你的图片路径
brightest_color = get_dominant_color(image_path)
print(f"最亮的颜色的RGB值为: {brightest_color}")