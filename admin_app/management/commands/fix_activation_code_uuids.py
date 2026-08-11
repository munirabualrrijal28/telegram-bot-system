from django.core.management.base import BaseCommand
from django.db import connection

class Command(BaseCommand):
    help = 'Fix corrupted UUID foreign keys in ActivationCode table'

    def handle(self, *args, **options):
        cursor = connection.cursor()
        
        try:
            # First, let's check for invalid UUIDs
            cursor.execute("""
                SELECT id, code, target_user_id, used_by_id 
                FROM admin_app_activationcode 
                WHERE target_user_id IS NOT NULL OR used_by_id IS NOT NULL
            """)
            
            rows = cursor.fetchall()
            fixed_count = 0
            
            for row in rows:
                code_id, code, target_user_id, used_by_id = row
                
                # Check if target_user_id is valid
                if target_user_id:
                    cursor.execute("SELECT COUNT(*) FROM app_user WHERE id = %s", [target_user_id])
                    if cursor.fetchone()[0] == 0:
                        self.stdout.write(f"Fixing code {code}: Invalid target_user_id {target_user_id}")
                        cursor.execute("UPDATE admin_app_activationcode SET target_user_id = NULL WHERE id = %s", [code_id])
                        fixed_count += 1
                
                # Check if used_by_id is valid
                if used_by_id:
                    cursor.execute("SELECT COUNT(*) FROM app_user WHERE id = %s", [used_by_id])
                    if cursor.fetchone()[0] == 0:
                        self.stdout.write(f"Fixing code {code}: Invalid used_by_id {used_by_id}")
                        cursor.execute("UPDATE admin_app_activationcode SET used_by_id = NULL WHERE id = %s", [code_id])
                        fixed_count += 1
            
            self.stdout.write(self.style.SUCCESS(f'Successfully fixed {fixed_count} corrupted foreign keys'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error: {str(e)}'))
