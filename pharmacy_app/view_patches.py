# pharmacy_app/view_patches.py
"""
Temporary patch script to update medicine-related views for bot filtering.
Run this once to apply the changes, then delete this file.
"""

import re


def patch_attachments_page():
    """Patch the attachments_page view to filter by bot"""
    file_path = r'd:\Desktop Projects 2025\pharmacy_system_bot\pharmacy_app\views.py'
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find and replace the attachments_page function
    # Looking for the line that filters medicines
    old_pattern = r'(medicines_qs = Medicine\.objects\.filter\(\s*pharmacy=pharmacy\s*\))'
    
    # New code with bot filtering
    new_code = '''# Get selected bot from middleware
    selected_bot = request.selected_bot
    
    # Filter medicines by selected bot for data isolation
    if selected_bot:
        medicines_qs = Medicine.objects.filter(bot=selected_bot)
    else:
        medicines_qs = Medicine.objects.none()'''
    
    # Replace
    content = re.sub(old_pattern, new_code, content)
    
    # Also need to add bot assignment when creating medicines
    # Find medicine creation pattern
    med_create_pattern = r'(medicine\.pharmacy = pharmacy)'
    med_create_new = r'\1\n        medicine.bot = request.selected_bot  # Assign to selected bot'
    
    content = re.sub(med_create_pattern, med_create_new, content)
    
    # Write back
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Patched attachments_page and medicine creation")


def patch_medicine_queries():
    """Patch all medicine update/delete queries to filter by bot"""
    file_path = r'd:\Desktop Projects 2025\pharmacy_system_bot\pharmacy_app\views.py'
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Pattern for get_object_or_404(Medicine, pk=..., pharmacy=pharmacy)
    # Add bot=request.selected_bot
    pattern = r'(get_object_or_404\(Medicine,\s*pk=pk,\s*pharmacy=pharmacy)(\))'
    replacement = r'\1, bot=request.selected_bot\2  # Verify bot ownership'
    
    content = re.sub(pattern, replacement, content)
    
    # Also for Medicine.objects.get patterns
    pattern2 = r'(Medicine\.objects\.get\(pk=pk,\s*pharmacy=pharmacy)(\))'
    replacement2 = r'\1, bot=request.selected_bot\2  # Verify bot ownership'
    
    content = re.sub(pattern2, replacement2, content)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Patched medicine update/delete queries")


if __name__ == '__main__':
    print("Applying patches for bot filtering...")
    patch_attachments_page()
    patch_medicine_queries()
    print("\n🎉 All patches applied successfully!")
    print("You can now test the bot selector - medicines will be isolated per bot.")
