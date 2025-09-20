from PIL import Image, ImageDraw, ImageFont
import random
import string
import os
import math

numcr = int(input("input cols number (also rows. for nice work type >5 number)"))


def generate_masked_text_images(
        message,
        cols=numcr,
        rows=numcr,
        font_path=None,
        font_size=36,
        spacing=0,
        output_base="base.png",
        output_mask="mask.png"):

    russian_upper = "АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ"
    russian_lower = "абвгдеёжзийклмнопрстуфхцчшщъыьэюя"
    punctuation = "!@#$%^&*()_+-=[]{}|;:,.<>?/`~ "

    all_chars = (
            string.ascii_letters +
            string.digits +
            russian_upper +
            russian_lower +
            punctuation
    )

    try:
        font = ImageFont.truetype(font_path, font_size) if font_path else ImageFont.load_default()
    except:
        font = ImageFont.load_default()

    max_w = max_h = 0
    for char in all_chars + message:
        bbox = font.getbbox(char)
        char_w = bbox[2] - bbox[0]
        char_h = bbox[3] - bbox[1]
        if char_w > max_w: max_w = char_w
        if char_h > max_h: max_h = char_h

    cell_w = max_w + spacing
    cell_h = max_h

    max_chars = cols * rows
    if len(message) > max_chars:
        raise ValueError(f"Message too long for {cols}x{rows} grid (max {max_chars} chars).")

    width = cols * cell_w
    height = rows * cell_h
    base = Image.new("RGB", (width, height), "white")
    mask = Image.new("RGBA", (width, height), (0, 0, 0, 255))
    draw = ImageDraw.Draw(base)
    mask_draw = ImageDraw.Draw(mask)

    start_col = max(0, (cols - len(message)) // 2)
    positions = []
    for i, char in enumerate(message):
        row = random.randint(0, rows - 1)
        col = start_col + i
        if char.isalpha():
            char = char.upper() if random.choice([True, False]) else char.lower()
        positions.append((col, row, char))

    random.shuffle(positions)
    secret_map = {(r, c): char for c, r, char in positions}

    secret_boxes = []
    for row in range(rows):
        for col in range(cols):
            x = col * cell_w
            y = row * cell_h

            if (row, col) in secret_map:
                char = secret_map[(row, col)]
            else:
                char = random.choice(all_chars)
                if char.isalpha():
                    char = char.upper() if random.choice([True, False]) else char.lower()

            bbox = font.getbbox(char)
            char_w = bbox[2] - bbox[0]
            char_h = bbox[3] - bbox[1]
            y_offset = (cell_h - char_h) / 2
            draw.text((x, y + y_offset), char, font=font, fill="black")

            if (row, col) in secret_map:
                x1 = x + char_w
                y1 = y + y_offset + char_h + 10
                secret_boxes.append((x, y + y_offset, x1, y1))

    for box in secret_boxes:
        expanded_box = (
            max(box[0] - 1, 0),
            max(box[1] - 1, 0),
            min(box[2] + 1, width),
            min(box[3] + 1, height)
        )
        mask_draw.rectangle(expanded_box, fill=(0, 0, 0, 0))

    base.save(output_base)
    mask.save(output_mask)
    print(f"Saved base: {output_base}")
    print(f"Saved mask: {output_mask}")


if __name__ == "__main__":
    secret = input(f"Enter secret message (1-{numcr} chars): ")
    generate_masked_text_images(
        secret,
        font_path="arial.ttf",
        output_base="base.png",
        output_mask="mask.png"
    )
