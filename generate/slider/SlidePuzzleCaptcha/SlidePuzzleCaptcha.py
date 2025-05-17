import os
import random
import uuid

from PIL import Image, ImageDraw
import argparse

def generate_slider_captcha(bg_images_dir, slides_dir, output_dir):
    # 确保输出目录存在
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    if not os.path.exists(slides_dir):
        os.makedirs(slides_dir)
    if not os.path.exists(bg_images_dir):
        os.makedirs(bg_images_dir)

    # 随机选择背景图片
    bg_image_path = random.choice(
        [os.path.join(bg_images_dir, f) for f in os.listdir(bg_images_dir) if f.endswith(('.png', '.jpg', '.jpeg'))])
    bg_image = Image.open(bg_image_path).convert("RGBA")
    bg_image_original= Image.open(bg_image_path).convert("RGBA")
    # 随机选择滑块图片
    slide_image_path = random.choice(
        [os.path.join(slides_dir, f) for f in os.listdir(slides_dir) if f.endswith(('.png', '.jpg', '.jpeg'))])
    slide_image = Image.open(slide_image_path).convert("RGBA")


    slide_width, slide_height = slide_image.size
    # 设置滑块最大尺寸为背景宽高的 1/5（可调整）
    max_slide_width = bg_image_original.width / 5
    max_slide_height = slide_height/(slide_width/max_slide_width)
    # 等比缩放滑块图像
    slide_image = slide_image.resize((random.randint(max_slide_width, max_slide_width), random.randint(max_slide_height, max_slide_height)))
    # 获取滑块的尺寸
    slide_width, slide_height = slide_image.size

    # 随机生成滑块的起始位置（确保滑块完全在背景内）
    bg_width, bg_height = bg_image.size
    x = random.randint(0, bg_width - slide_width)
    y = random.randint(0, bg_height - slide_height)

    # 创建一个遮罩图像用于抠图
    mask = Image.new("L", bg_image.size, 0)
    mask.paste(slide_image.split()[-1], (x, y))

    # 将背景图片的对应区域设置为透明
    bg_image.putalpha(mask)

    random_hash = str(uuid.uuid4())
    filename = f"bg_image_with_gap_{random_hash}.png"
    # 保存抠图后的背景图片
    #bg_image.save(os.path.join(output_dir,filename))
    # 裁剪出滑块对应的缺口区域
    gap_area = (x, y, x + slide_width, y + slide_height)
    gap_image = bg_image.crop(gap_area)

    # 创建一个纯透明背景，用于仅保留缺口部分
    transparent_background = Image.new("RGBA", gap_image.size, (0, 0, 0, 0))

    # 提取 alpha 遮罩（非透明区域即为缺口）
    alpha_mask = gap_image.split()[3]

    # 将缺口部分保留，其他设置为透明
    transparent_background.paste(gap_image, (0, 0), mask=alpha_mask)

    # 保存缺口图像（只保留滑块形状，无背景）
    gap_filename = f"gap_only_{random_hash}.png"
    transparent_background.save(os.path.join(output_dir, gap_filename), format="PNG")



    # 保存最终的验证码图片
    final_image = Image.new("RGBA", (bg_width, bg_height), (255, 255, 255, 0))
    final_image.paste(bg_image_original, (0, 0))
    #slide_image 应该设置稍微白色透明，并且有边框轮空
    # 将 slide_image 转换为可操作像素数据的模式
    slide_data = slide_image.getdata()
    new_data = []

    for pixel in slide_data:
        r, g, b, a = pixel
        # 判断是否为“接近白色”（RGB 接近 255,255,255）
        if r > 10 and g > 10 and b > 10:
            new_data.append((r, g, b, 160))
        else:
            new_data.append((r, g, b, 0))

    # 更新图像数据
    slide_image.putdata(new_data)
    final_image.paste(slide_image, (x, y), slide_image)
    filename = f"captcha_image_{random_hash}.png"
    final_image.save(os.path.join(output_dir, filename))

    print(f"验证码生成完成，保存在 {output_dir} 目录下。")


# 设置目录路径
bg_images_dir = "bg-images"  # 背景图片目录
slides_dir = "slides"  # 滑块图片目录
output_dir = "output"  # 输出目录

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="生成滑块验证码")
    parser.add_argument("--quantity", type=int, default=1, help="生成的验证码数量")
    parser.add_argument("--bg_images_dir", type=str, default="bg-images", help="背景图片目录")
    parser.add_argument("--slides_dir", type=str, default="slides", help="滑块图片目录")
    parser.add_argument("--output_dir", type=str, default="output", help="输出目录")

    args = parser.parse_args()

    # 批量生成验证码
    # for i in range(args.quantity):
    #     generate_slider_captcha(
    #         bg_images_dir=args.bg_images_dir,
    #         slides_dir=args.slides_dir,
    #         output_dir=args.output_dir
    #     )
    #     print(f"已生成第 {i + 1} 个验证码")
    for i in range(11):
        generate_slider_captcha(
            bg_images_dir=r"bg-images",
            slides_dir=r"slides",
            output_dir=r"../../../images/slides/slides"
        )
        print(f"已生成第 {i + 1} 个验证码")