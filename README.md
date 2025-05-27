Python program that creates a dynamic image collage viewer with the following features:
Key Features:

Real-time Directory Monitoring: Automatically detects when images are added or removed from the selected directory
Random Rotation: Continuously rotates through images in a random order
Adaptive Grid Layout: Automatically calculates optimal grid layout based on window size and number of images
Multiple Format Support: Handles JPG, PNG, GIF, BMP, TIFF, and WebP formats
Responsive Design: Adapts to window resizing and maintains aspect ratios

How to Use:

Install Requirements: You'll need to install Pillow (PIL) if you haven't already:
bashpip install Pillow

Run the Program: Execute the script and use the GUI controls:

Click "Select Directory" to choose your image folder
Click "Start/Stop" to begin/pause the rotation
The collage will automatically update as you add/remove images



Program Behavior:

Rotation Interval: Images change every 2 seconds (configurable)
Maximum Images: Shows up to 12 images at once (configurable)
File Monitoring: Checks for new/deleted files every 2 seconds
Error Handling: Skips corrupted or unreadable image files
Performance: Uses threading to keep the GUI responsive
Crops all images to perfect squares using center cropping
Removes excess width or height while preserving central portion
Resizes to exact square dimensions


No Gaps Layout: The grid layout
Eliminates all padding/spacing between images
Places images directly adjacent to each other
Centers the entire grid on the canvas
Customization Options:
You can modify these variables in the __init__ method:

self.max_images: Number of images displayed simultaneously
self.rotation_interval: Time between image rotations
self.supported_formats: Image file formats to include

The program creates a black-background collage that continuously shuffles through your images, perfect for displaying a dynamic photo slideshow that stays fresh as you add new pictures to your directory!
