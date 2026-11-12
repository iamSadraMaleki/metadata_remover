import os
import sys
import logging
from PIL import Image
from PIL.PngImagePlugin import PngInfo
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import threading
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

class MetadataRemoverGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("AI Image Metadata Remover")
        self.root.geometry("700x550")
        self.root.resizable(False, False)
        
        # Set icon if available
        try:
            self.root.iconbitmap(default='icon.ico')
        except:
            pass
        
        # Variables
        self.image_path = tk.StringVar()
        self.status_var = tk.StringVar(value="Ready")
        self.progress_var = tk.DoubleVar(value=0)
        
        # Create GUI
        self.create_widgets()
        
        # Center window
        self.center_window()
        
    def center_window(self):
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def create_widgets(self):
        # Main frame with padding
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(
            main_frame, 
            text="🔍 AI Image Metadata Remover",
            font=('Arial', 18, 'bold')
        )
        title_label.pack(pady=(0, 20))
        
        # Subtitle
        subtitle_label = ttk.Label(
            main_frame,
            text="Remove hidden metadata from AI-generated images",
            font=('Arial', 10)
        )
        subtitle_label.pack(pady=(0, 30))
        
        # File selection frame
        file_frame = ttk.LabelFrame(main_frame, text="Select Image", padding="15")
        file_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Path entry and browse button
        path_frame = ttk.Frame(file_frame)
        path_frame.pack(fill=tk.X)
        
        self.path_entry = ttk.Entry(
            path_frame, 
            textvariable=self.image_path,
            font=('Arial', 10),
            state='readonly'
        )
        self.path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        browse_btn = ttk.Button(
            path_frame,
            text="📁 Browse",
            command=self.browse_file,
            width=12
        )
        browse_btn.pack(side=tk.RIGHT)
        
        # File info frame
        info_frame = ttk.LabelFrame(main_frame, text="File Information", padding="15")
        info_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Info labels
        self.info_labels = {}
        info_items = [
            ("File Name:", "filename"),
            ("File Size:", "filesize"),
            ("Image Format:", "format"),
            ("Dimensions:", "dimensions")
        ]
        
        for i, (label_text, key) in enumerate(info_items):
            frame = ttk.Frame(info_frame)
            frame.pack(fill=tk.X, pady=2)
            
            label = ttk.Label(frame, text=label_text, width=15, anchor='w')
            label.pack(side=tk.LEFT)
            
            value_label = ttk.Label(frame, text="-", anchor='w')
            value_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
            self.info_labels[key] = value_label
        
        # Action buttons frame
        action_frame = ttk.Frame(main_frame)
        action_frame.pack(fill=tk.X, pady=(0, 20))
        
        self.remove_btn = ttk.Button(
            action_frame,
            text="🗑️ Remove Metadata",
            command=self.remove_metadata_thread,
            state='disabled',
            width=20
        )
        self.remove_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.clear_btn = ttk.Button(
            action_frame,
            text="🔄 Clear",
            command=self.clear_all,
            width=12
        )
        self.clear_btn.pack(side=tk.LEFT)
        
        # Progress bar
        self.progress_bar = ttk.Progressbar(
            main_frame,
            variable=self.progress_var,
            maximum=100,
            length=400,
            mode='determinate'
        )
        self.progress_bar.pack(fill=tk.X, pady=(0, 10))
        
        # Status bar
        status_frame = ttk.Frame(main_frame)
        status_frame.pack(fill=tk.X, pady=(10, 0))
        
        status_label = ttk.Label(
            status_frame,
            textvariable=self.status_var,
            font=('Arial', 9),
            relief=tk.SUNKEN,
            padding=5
        )
        status_label.pack(fill=tk.X)
        
        # Log area
        log_frame = ttk.LabelFrame(main_frame, text="Log", padding="10")
        log_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        
        # Text widget with scrollbar
        text_frame = ttk.Frame(log_frame)
        text_frame.pack(fill=tk.BOTH, expand=True)
        
        self.log_text = tk.Text(
            text_frame,
            height=8,
            font=('Consolas', 8),
            wrap=tk.WORD,
            state='disabled'
        )
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=self.log_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text.config(yscrollcommand=scrollbar.set)
        
        # Clear log button
        clear_log_btn = ttk.Button(
            log_frame,
            text="Clear Log",
            command=self.clear_log,
            width=10
        )
        clear_log_btn.pack(pady=(5, 0))
        
    def browse_file(self):
        file_path = filedialog.askopenfilename(
            title="Select an image file",
            filetypes=[
                ("Image files", "*.jpg *.jpeg *.png *.webp *.bmp *.tiff *.tif"),
                ("All files", "*.*")
            ]
        )
        
        if file_path:
            self.image_path.set(file_path)
            self.display_file_info(file_path)
            self.remove_btn.config(state='normal')
            self.log_message(f"✅ File loaded: {os.path.basename(file_path)}")
            self.status_var.set(f"File loaded: {os.path.basename(file_path)}")
    
    def display_file_info(self, file_path):
        try:
            # File name
            self.info_labels['filename'].config(text=os.path.basename(file_path))
            
            # File size
            size = os.path.getsize(file_path)
            if size < 1024:
                size_str = f"{size} B"
            elif size < 1024 * 1024:
                size_str = f"{size/1024:.1f} KB"
            else:
                size_str = f"{size/(1024*1024):.1f} MB"
            self.info_labels['filesize'].config(text=size_str)
            
            # Image info
            img = Image.open(file_path)
            self.info_labels['format'].config(text=img.format or "Unknown")
            self.info_labels['dimensions'].config(text=f"{img.width} × {img.height} px")
            
        except Exception as e:
            self.log_message(f"❌ Error reading file info: {str(e)}")
            self.status_var.set("Error reading file")
    
    def remove_metadata_thread(self):
        # Run in separate thread to prevent UI freezing
        thread = threading.Thread(target=self.remove_metadata)
        thread.daemon = True
        thread.start()
    
    def remove_metadata(self):
        image_path = self.image_path.get()
        
        if not image_path or not os.path.exists(image_path):
            messagebox.showerror("Error", "Please select a valid image file.")
            return
        
        # Disable buttons
        self.remove_btn.config(state='disabled')
        self.clear_btn.config(state='disabled')
        self.status_var.set("Processing...")
        self.progress_var.set(0)
        
        try:
            self.log_message("🔄 Starting metadata removal...")
            self.progress_var.set(20)
            
            # Open the image
            self.log_message(f"📂 Opening: {os.path.basename(image_path)}")
            img = Image.open(image_path)
            self.progress_var.set(40)
            
            # Get original format
            img_format = img.format
            self.log_message(f"📷 Format: {img_format}")
            self.progress_var.set(60)
            
            # Remove metadata by creating new image
            self.log_message("🗑️ Removing metadata...")
            
            # Convert and create new image without metadata
            if img.mode in ('RGBA', 'LA', 'P'):
                if img.mode == 'P':
                    img = img.convert('RGBA')
                new_img = Image.new(img.mode, img.size)
                new_img.putdata(img.getdata())
            else:
                new_img = Image.new(img.mode, img.size)
                new_img.putdata(img.getdata())
            
            self.progress_var.set(80)
            
            # Save without metadata
            file_ext = os.path.splitext(image_path)[1].lower()
            
            self.log_message(f"💾 Saving cleaned image...")
            
            if file_ext in ['.png']:
                new_img.save(image_path, format='PNG', optimize=True)
            elif file_ext in ['.jpg', '.jpeg']:
                new_img.save(image_path, format='JPEG', quality=95, optimize=True)
            elif file_ext in ['.webp']:
                new_img.save(image_path, format='WEBP', quality=95, lossless=False)
            elif file_ext in ['.bmp']:
                new_img.save(image_path, format='BMP')
            elif file_ext in ['.tiff', '.tif']:
                new_img.save(image_path, format='TIFF')
            else:
                new_img.save(image_path, format=img_format)
            
            self.progress_var.set(100)
            
            # Success message
            self.log_message("✅ Metadata removed successfully!")
            self.status_var.set("✅ Complete! Metadata removed.")
            
            # Update file info
            self.display_file_info(image_path)
            
            messagebox.showinfo(
                "Success",
                f"✅ Metadata removed successfully from:\n{os.path.basename(image_path)}"
            )
            
        except Exception as e:
            error_msg = f"❌ Error: {str(e)}"
            self.log_message(error_msg)
            self.status_var.set("❌ Error occurred")
            messagebox.showerror("Error", f"Failed to remove metadata:\n{str(e)}")
            
        finally:
            # Re-enable buttons
            self.remove_btn.config(state='normal')
            self.clear_btn.config(state='normal')
    
    def clear_all(self):
        self.image_path.set("")
        for key in self.info_labels:
            self.info_labels[key].config(text="-")
        self.progress_var.set(0)
        self.status_var.set("Ready")
        self.remove_btn.config(state='disabled')
        self.log_message("🔄 Cleared all fields")
    
    def clear_log(self):
        self.log_text.config(state='normal')
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state='disabled')
    
    def log_message(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_msg = f"[{timestamp}] {message}\n"
        
        self.log_text.config(state='normal')
        self.log_text.insert(tk.END, formatted_msg)
        self.log_text.see(tk.END)
        self.log_text.config(state='disabled')
        
        # Also log to console
        logger.info(message)

def main():
    root = tk.Tk()
    app = MetadataRemoverGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()