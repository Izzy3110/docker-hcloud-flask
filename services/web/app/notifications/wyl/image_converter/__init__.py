import os.path
from PIL import Image


class ImageConverter:
    def __init__(self):
        pass

    @staticmethod
    def output_path_(input_path):
        filename_base = os.path.splitext(os.path.basename(input_path))[0]
        filename_target = f"{filename_base}.jpg"
        return os.path.join(os.path.dirname(input_path), filename_target)

    class Webp:
        def __init__(self, image_path, output_path=None):
            self.image_path = image_path
            self.output_path = output_path if output_path is not None else ImageConverter.output_path_(image_path)

        def process_img(self, img, img_format='JPEG', options=None):
            options = options or {}  # Ensure options is a dictionary
            save_params = {'format': img_format}
            if img_format == 'JPEG' and 'quality' in options:
                save_params['quality'] = options['quality']
            if img_format in ('JPEG', 'gif'):
                img = img.convert("RGB")
            img.save(self.output_path, **save_params)

        def convert_img(self, target_format):
            allowed_target_formats = ["jpg", "png", "gif"]
            if target_format not in allowed_target_formats:
                return
            if target_format == "jpg":
                self.to_jpg()
            if target_format == "png":
                self.to_png()
            if target_format == "gif":
                self.to_gif()

        def to_jpg(self, quality=95):
            try:
                # Open the WebP image
                with Image.open(self.image_path) as img:
                    # Convert the image to RGB (JPG doesn't support alpha channel)
                    self.process_img(
                        img,
                        img_format='JPEG',
                        options={
                            "quality": quality
                        }
                    )
                print(f"Converted {self.image_path} to {self.output_path} (Quality: {quality})")
            except Exception as e:
                print(f"Error converting {self.image_path} to JPG: {e}")

        def to_png(self):
            try:
                # Open the WebP image
                with Image.open(self.image_path) as img:
                    self.process_img(
                        img,
                        img_format='PNG'
                    )
                print(f"Converted {self.image_path} to {self.output_path}")
            except Exception as e:
                print(f"Error converting {self.image_path} to PNG: {e}")

        def to_gif(self):
            try:
                # Open the WebP image
                with Image.open(self.image_path) as img:
                    # Convert to RGB if WebP has an alpha channel (GIF doesn't support alpha transparency)
                    self.process_img(
                        img,
                        img_format='GIF'
                    )
                print(f"Converted {self.image_path} to {self.output_path}")
            except Exception as e:
                print(f"Error converting {self.image_path} to GIF: {e}")


def convert_webp_to_jpg(input_path, output_path=None, quality=95):
    """
    Converts a WebP image to JPG format.

    Parameters:
        input_path (str): Path to the input WebP file.
        output_path (str) - optional: Path to save the output JPG file.
        quality (int): Quality of the output JPG (default is 95).

    Returns:
        None
    """
    if output_path is None:
        filename_base = os.path.splitext(os.path.basename(input_path))[0]
        filename_target = f"{filename_base}.jpg"
        filepath_target = os.path.join(os.path.dirname(input_path), filename_target)
        output_path = filepath_target

    try:
        # Open the WebP image
        with Image.open(input_path) as img:
            # Convert the image to RGB (JPG doesn't support alpha channel)
            rgb_image = img.convert("RGB")
            # Save as JPG
            rgb_image.save(output_path, "JPEG", quality=quality)
        print(f"Converted {input_path} to {output_path} (Quality: {quality})")
    except Exception as e:
        print(f"Error converting {input_path} to JPG: {e}")


def convert_webp_to_png(input_path, output_path=None):
    """
    Converts a WebP image to PNG format.

    Parameters:
        input_path (str): Path to the input WebP file.
        output_path (str): Path to save the output PNG file.

    Returns:
        None
    """

    if output_path is None:
        filename_base = os.path.splitext(os.path.basename(input_path))[0]
        filename_target = f"{filename_base}.png"
        filepath_target = os.path.join(os.path.dirname(input_path), filename_target)
        output_path = filepath_target

    try:
        # Open the WebP image
        with Image.open(input_path) as img:
            # Save as PNG (PNG supports transparency if present in WebP)
            img.save(output_path, "PNG")
        print(f"Converted {input_path} to {output_path}")
    except Exception as e:
        print(f"Error converting {input_path} to PNG: {e}")


def convert_webp_to_gif(input_path, output_path=None):
    """
    Converts a WebP image to GIF format.

    Parameters:
        input_path (str): Path to the input WebP file.
        output_path (str): Path to save the output GIF file.

    Returns:
        None
    """

    if output_path is None:
        filename_base = os.path.splitext(os.path.basename(input_path))[0]
        filename_target = f"{filename_base}.gif"
        filepath_target = os.path.join(os.path.dirname(input_path), filename_target)
        output_path = filepath_target

    try:
        # Open the WebP image
        with Image.open(input_path) as img:
            # Convert to RGB if WebP has an alpha channel (GIF doesn't support alpha transparency)
            if img.mode == "RGBA":
                img = img.convert("RGB")
            # Save as GIF
            img.save(output_path, "GIF")
        print(f"Converted {input_path} to {output_path}")
    except Exception as e:
        print(f"Error converting {input_path} to GIF: {e}")
