
import os
import secrets
import cloudinary
import cloudinary.uploader
from flask import current_app
from werkzeug.utils import secure_filename

def get_cloudinary_config():
    """
    Returns True if Cloudinary env vars are set, else False.
    Also configures the cloudinary library if keys are present.
    """
    cloud_name = os.environ.get("CLOUDINARY_CLOUD_NAME")
    api_key = os.environ.get("CLOUDINARY_API_KEY")
    api_secret = os.environ.get("CLOUDINARY_API_SECRET")

    if cloud_name and api_key and api_secret:
        cloudinary.config(
            cloud_name=cloud_name,
            api_key=api_key,
            api_secret=api_secret
        )
        return True
    return False

def save_image_file(file_storage, folder="uploads"):
    """
    Saves image to Cloudinary (if configured) OR Local Disk (fallback).
    
    Args:
        file_storage: The file object from request.files['name']
        folder: 'uploads' (items) or 'avatars' (user profiles)
        
    Returns:
        str: A full URL (if Cloudinary) OR a Filename (if Local).
    """
    if not file_storage:
        return None

    filename = secure_filename(file_storage.filename)
    if not filename:
        return None

    # 1. Try Cloudinary
    if get_cloudinary_config():
        try:
            # We explicitly specify the folder in Cloudinary
            res = cloudinary.uploader.upload(file_storage, folder=f"inventory_app/{folder}")
            return res.get("secure_url")
        except Exception as e:
            # If upload fails, log it and fall back to local? 
            # Or maybe just print error and continue to local.
            print(f"Cloudinary upload failed: {e}")

    # 2. Fallback to Local Storage
    # Generate unique name
    timestamp = secrets.token_hex(8)
    _, ext = os.path.splitext(filename)
    new_filename = f"{timestamp}{ext}" # 1234abcd.jpg
    
    # Check if folder is 'uploads' or 'avatars' to match existing logic
    # Existing logic in main.py put items in 'static/uploads'
    # Existing logic in profile.py put items in 'static/avatars'
    
    # We will return JUST the filename so the existing code (mostly) works, 
    # BUT we need to distinguish between URL and Filename in the template.
    
    target_dir = os.path.join(current_app.root_path, "static", folder)
    os.makedirs(target_dir, exist_ok=True)
    
    save_path = os.path.join(target_dir, new_filename)
    file_storage.save(save_path)
    
    return new_filename
