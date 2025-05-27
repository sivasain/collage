import os
import random
import time
import threading
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import math

class DynamicImageCollage:
    def __init__(self, root):
        self.root = root
        self.root.title("Dynamic Image Collage")
        self.root.geometry("1200x800")
        self.root.configure(bg='black')
        
        # Canvas for displaying images
        self.canvas = tk.Canvas(root, bg='black', highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Control frame
        self.control_frame = tk.Frame(root, bg='gray20', height=50)
        self.control_frame.pack(fill=tk.X, side=tk.BOTTOM)
        self.control_frame.pack_propagate(False)
        
        # Controls
        tk.Button(self.control_frame, text="Select Directory", 
                 command=self.select_directory, bg='gray30', fg='white').pack(side=tk.LEFT, padx=5, pady=5)
        
        self.status_label = tk.Label(self.control_frame, text="No directory selected", 
                                   bg='gray20', fg='white')
        self.status_label.pack(side=tk.LEFT, padx=10)
        
        tk.Button(self.control_frame, text="Start/Stop", 
                 command=self.toggle_rotation, bg='gray30', fg='white').pack(side=tk.RIGHT, padx=5, pady=5)
        
        # State variables
        self.image_directory = None
        self.image_files = []
        self.displayed_images = []
        self.is_running = False
        self.rotation_thread = None
        self.file_monitor_thread = None
        self.last_file_check = 0
        
        # Collage settings
        self.max_images = 12  # Maximum images to display at once
        self.rotation_interval = 2.0  # Seconds between rotations
        self.supported_formats = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp'}
        
        # Bind canvas resize event
        self.canvas.bind('<Configure>', self.on_canvas_resize)
        
    def select_directory(self):
        """Select directory containing images"""
        directory = filedialog.askdirectory(title="Select Image Directory")
        if directory:
            self.image_directory = Path(directory)
            self.update_image_list()
            self.status_label.config(text=f"Directory: {self.image_directory.name} ({len(self.image_files)} images)")
            
    def update_image_list(self):
        """Update the list of image files from the directory"""
        if not self.image_directory or not self.image_directory.exists():
            self.image_files = []
            return
            
        new_files = []
        for file_path in self.image_directory.iterdir():
            if file_path.is_file() and file_path.suffix.lower() in self.supported_formats:
                try:
                    # Quick check if file can be opened as image
                    with Image.open(file_path) as img:
                        new_files.append(file_path)
                except Exception:
                    continue  # Skip corrupted files
                    
        self.image_files = new_files
        random.shuffle(self.image_files)  # Randomize order
        
    def monitor_directory(self):
        """Monitor directory for file changes"""
        while self.is_running:
            if self.image_directory and self.image_directory.exists():
                # Check for file changes every 2 seconds
                current_time = time.time()
                if current_time - self.last_file_check > 2:
                    old_count = len(self.image_files)
                    self.update_image_list()
                    new_count = len(self.image_files)
                    
                    if new_count != old_count:
                        self.root.after(0, lambda: self.status_label.config(
                            text=f"Directory: {self.image_directory.name} ({new_count} images)"))
                        
                    self.last_file_check = current_time
                    
            time.sleep(0.5)
            
    def load_and_crop_to_square(self, file_path, square_size):
        """Load and crop image to square aspect ratio, then resize to target size"""
        try:
            with Image.open(file_path) as img:
                # Convert to RGB if necessary
                if img.mode in ('RGBA', 'LA', 'P'):
                    img = img.convert('RGB')
                
                # Crop to square aspect ratio (center crop)
                width, height = img.size
                if width > height:
                    # Image is wider - crop sides
                    left = (width - height) // 2
                    right = left + height
                    img = img.crop((left, 0, right, height))
                elif height > width:
                    # Image is taller - crop top/bottom
                    top = (height - width) // 2
                    bottom = top + width
                    img = img.crop((0, top, width, bottom))
                # If already square, no cropping needed
                
                # Resize to exact square size
                resized_img = img.resize((square_size, square_size), Image.Resampling.LANCZOS)
                return ImageTk.PhotoImage(resized_img)
                
        except Exception as e:
            print(f"Error loading image {file_path}: {e}")
            return None
            
    def calculate_grid_layout(self, canvas_width, canvas_height, num_images):
        """Calculate optimal grid layout for square images with no gaps"""
        if num_images == 0:
            return 0, 0, 0
            
        # Calculate grid dimensions
        aspect_ratio = canvas_width / canvas_height
        cols = max(1, int(math.sqrt(num_images * aspect_ratio)))
        rows = max(1, math.ceil(num_images / cols))
        
        # Calculate square size to fill canvas with no gaps
        square_size = min(canvas_width // cols, canvas_height // rows)
        
        return rows, cols, square_size
        
    def update_collage(self):
        """Update the collage with new random square images"""
        if not self.image_files:
            self.canvas.delete("all")
            self.canvas.create_text(self.canvas.winfo_width()//2, self.canvas.winfo_height()//2,
                                  text="No images found", fill="white", font=("Arial", 24))
            return
            
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        if canvas_width <= 1 or canvas_height <= 1:
            return
            
        # Clear canvas
        self.canvas.delete("all")
        
        # Select random images
        num_to_show = min(self.max_images, len(self.image_files))
        selected_files = random.sample(self.image_files, num_to_show)
        
        # Calculate layout
        rows, cols, square_size = self.calculate_grid_layout(
            canvas_width, canvas_height, num_to_show)
        
        if square_size <= 0:
            return
            
        # Calculate starting position to center the grid
        grid_width = cols * square_size
        grid_height = rows * square_size
        start_x = (canvas_width - grid_width) // 2
        start_y = (canvas_height - grid_height) // 2
        
        # Display square images with no gaps
        self.displayed_images = []
        
        for i, file_path in enumerate(selected_files):
            row = i // cols
            col = i % cols
            
            # Calculate position (no padding between images)
            x = start_x + col * square_size
            y = start_y + row * square_size
            
            # Load and crop image to square
            photo = self.load_and_crop_to_square(file_path, square_size)
            if photo:
                # Place image at exact position (top-left corner)
                image_id = self.canvas.create_image(x, y, image=photo, anchor=tk.NW)
                self.displayed_images.append((image_id, photo))  # Keep reference to prevent garbage collection
                
    def rotation_loop(self):
        """Main rotation loop"""
        while self.is_running:
            self.root.after(0, self.update_collage)
            time.sleep(self.rotation_interval)
            
    def toggle_rotation(self):
        """Start or stop the rotation"""
        if not self.image_files:
            messagebox.showwarning("Warning", "Please select a directory with images first!")
            return
            
        if self.is_running:
            self.stop_rotation()
        else:
            self.start_rotation()
            
    def start_rotation(self):
        """Start the rotation and monitoring"""
        self.is_running = True
        
        # Start rotation thread
        self.rotation_thread = threading.Thread(target=self.rotation_loop, daemon=True)
        self.rotation_thread.start()
        
        # Start file monitoring thread
        self.file_monitor_thread = threading.Thread(target=self.monitor_directory, daemon=True)
        self.file_monitor_thread.start()
        
        # Initial display
        self.update_collage()
        
    def stop_rotation(self):
        """Stop the rotation and monitoring"""
        self.is_running = False
        
    def on_canvas_resize(self, event):
        """Handle canvas resize events"""
        if self.is_running:
            # Delay update to avoid too frequent updates during resize
            self.root.after(100, self.update_collage)
            
    def on_closing(self):
        """Clean up when closing the application"""
        self.stop_rotation()
        self.root.destroy()

def main():
    root = tk.Tk()
    app = DynamicImageCollage(root)
    
    # Handle window closing
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    
    # Start the GUI
    root.mainloop()

if __name__ == "__main__":
    main()