from PIL import Image, ImageDraw, ImageFont, ExifTags
from reportlab.pdfgen import canvas
import os

def create_thumbnail(input_path, output_path, name):
    # Load the image
    original_image = Image.open(input_path)

    # Handle orientation (rotate the image)
    try:
        for orientation in ExifTags.TAGS.keys():
            if ExifTags.TAGS[orientation] == 'Orientation':
                break
        exif = dict(original_image._getexif().items())
        if exif[orientation] == 3:
            original_image = original_image.rotate(180, expand=True)
        elif exif[orientation] == 6:
            original_image = original_image.rotate(270, expand=True)
        elif exif[orientation] == 8:
            original_image = original_image.rotate(90, expand=True)
    except (AttributeError, KeyError, IndexError):
        # No EXIF orientation info, do nothing
        pass

    # Resize the image to 3x4 (portrait)
    thumbnail = original_image.resize((300, 400))

    # Save the thumbnail
    thumbnail.save(output_path)

def create_pdf(images_by_folder, pdf_path, output_folder):
    c = canvas.Canvas(pdf_path, pagesize=(595, 842))  # A4 size in points
    
    # Set the margin and spacing
    margin = 20
    spacing = 10
    
    # Calculate the available width for each thumbnail
    available_width, available_height = c._pagesize
    available_width = available_width - 2 * margin
    
    # Set the size of the thumbnails
    thumbnail_width = 80
    thumbnail_height = 108
    
    # Iterate over folders and images
    for folder, images in images_by_folder.items():
        c.drawString(margin, available_height - margin, f"Folder: {folder}")
        
        # Initialize row variables
        x_position = margin
        y_position = available_height - margin - spacing - thumbnail_height
        row_width = 0
        
        for image_path, name in images:
            # Create the thumbnail
            output_path = f"{output_folder}{name}_thumbnail.jpg"
            create_thumbnail(image_path, output_path, name)

            # Check if the thumbnail fits in the current row
            if row_width + thumbnail_width > available_width:
                # Move to the next row
                y_position -= thumbnail_height + spacing
                x_position = margin
                row_width = 0
            
            # Draw the image on the PDF
            c.drawImage(output_path, x_position, y_position, width=thumbnail_width, height=thumbnail_height)
            
            # Update row variables
            x_position += thumbnail_width + spacing
            row_width += thumbnail_width + spacing
        
        # Move to the next row
        c.showPage()
    
    # Save the PDF
    c.save()

def main():
    input_folder = "image/"
    output_folder = "output_images/"
    pdf_path = "pdf/bukbir.pdf"
    
    # Create the output folder if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    # Dictionary to store images by folder
    images_by_folder = {}
    
    # Iterate over all files in the input folder
    for root, dirs, files in os.walk(input_folder):
        for file in files:
            # Get the full path of the file
            file_path = os.path.join(root, file)
            
            # Get the name of the image
            name = os.path.splitext(os.path.basename(file_path))[0]

            # Add the image to the dictionary, grouped by folder
            folder_name = os.path.basename(root)
            if folder_name not in images_by_folder:
                images_by_folder[folder_name] = []
            images_by_folder[folder_name].append((file_path, name))
    
    # Create thumbnails with names and a PDF from the thumbnails
    create_pdf(images_by_folder, pdf_path, output_folder)

if __name__ == "__main__":
    main()
