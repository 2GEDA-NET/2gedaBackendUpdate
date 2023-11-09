from PIL import ImageEnhance
from PIL import Image


def add_watermark(watermark_path, main_image_path):
    main_image = Image.open(main_image_path)
    watermark = Image.open(watermark_path)

    watermark = watermark.resize((100, 100))
    transparency = 0.5  
    watermark = ImageEnhance.Brightness(watermark).enhance(transparency)
    output_image = main_image.copy()
    position = (10, 10)  
    output_image.paste(watermark, position, watermark)
    output_image.save('output_image_with_watermark.jpg')



