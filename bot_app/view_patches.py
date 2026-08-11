# bot_app/view_patches.py
"""
Patch script to update bot_app views for category/FAQ filtering by selected bot.
"""

import re


def patch_bot_manage_view():
    """Patch bot_manage_view to filter by selected bot"""
    file_path = r'd:\Desktop Projects 2025\pharmacy_system_bot\bot_app\views.py'
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find the bot_manage_view function and replace pharmacy filtering with bot filtering
    # Pattern: pharmacy = request.user.app_user.pharmacy
    old_pattern = r'(def bot_manage_view\(request\):.*?)(pharmacy = request\.user\.app_user\.pharmacy)'
    
    new_code = r'\1selected_bot = request.selected_bot\n    if not selected_bot:\n        messages.warning(request, "Please create a bot first to manage categories and FAQs.")\n        return redirect("bot_app:bot_settings")\n    pharmacy = request.user.app_user.pharmacy'
    
    content = re.sub(old_pattern, new_code, content, flags=re.DOTALL)
    
    # Replace FAQCategory.objects.filter(pharmacy=pharmacy to filter(bot=selected_bot
    content = re.sub(
        r'FAQCategory\.objects\.filter\(\s*pharmacy=pharmacy,',
        'FAQCategory.objects.filter(bot=selected_bot,',
        content
    )
    
    # Replace FAQ.objects.filter(pharmacy=pharmacy to filter(bot=selected_bot
    content = re.sub(
        r'FAQ\.objects\.filter\(\s*pharmacy=pharmacy,',
        'FAQ.objects.filter(bot=selected_bot,',
        content
    )
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Patched bot_manage_view for bot filtering")


def patch_category_create():
    """Patch category_create to assign to selected bot"""
    file_path = r'd:\Desktop Projects 2025\pharmacy_system_bot\bot_app\views.py'
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Add bot assignment when creating categories
    # Look for FAQCategory.objects.create(pharmacy=
    pattern = r'(FAQCategory\.objects\.create\(\s*)(pharmacy=)'
    replacement = r'\1bot=request.selected_bot, \2'
    
    content = re.sub(pattern, replacement, content)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Patched category_create for bot assignment")


def patch_faq_create():
    """Patch faq_create to assign to selected bot"""
    file_path = r'd:\Desktop Projects 2025\pharmacy_system_bot\bot_app\views.py'
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Add bot assignment when creating FAQs
    # Look for FAQ.objects.create(pharmacy=
    pattern = r'(FAQ\.objects\.create\(\s*)(pharmacy=)'
    replacement = r'\1bot=request.selected_bot, \2'
    
    content = re.sub(pattern, replacement, content)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Patched faq_create for bot assignment")


def patch_ownership_verification():
    """Patch update/delete views to verify bot ownership"""
    file_path = r'd:\Desktop Projects 2025\pharmacy_system_bot\bot_app\views.py'
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # For FAQCategory get_object_or_404
    pattern = r'(get_object_or_404\(FAQCategory,\s*pk=pk,\s*pharmacy=pharmacy)(\))'
    replacement = r'\1, bot=request.selected_bot\2'
    content = re.sub(pattern, replacement, content)
    
    # For FAQ get_object_or_404
    pattern = r'(get_object_or_404\(FAQ,\s*pk=pk,\s*pharmacy=pharmacy)(\))'
    replacement = r'\1, bot=request.selected_bot\2'
    content = re.sub(pattern, replacement, content)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Patched category/FAQ update/delete for ownership verification")


if __name__ == '__main__':
    print("Applying patches for bot_app views...")
    patch_bot_manage_view()
    patch_category_create()
    patch_faq_create()
    patch_ownership_verification()
    print("\n🎉 All bot_app patches applied successfully!")
