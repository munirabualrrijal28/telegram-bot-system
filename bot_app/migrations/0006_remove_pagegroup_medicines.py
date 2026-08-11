"""
Migration to remove the `medicines` ManyToManyField from PageGroup.
The join table `bot_page_group_medicines` may or may not exist on the target
database (it was never migrated on some environments), so we use a conditional
RunSQL that only drops it if it exists.
"""

from django.db import migrations


def drop_medicines_table_if_exists(apps, schema_editor):
    """Safely drop bot_page_group_medicines only if it exists."""
    db_alias = schema_editor.connection.alias
    with schema_editor.connection.cursor() as cursor:
        # For MySQL/MariaDB (used by AWS RDS)
        cursor.execute("""
            SELECT COUNT(*)
            FROM information_schema.tables
            WHERE table_schema = DATABASE()
            AND table_name = 'bot_page_group_medicines'
        """)
        exists = cursor.fetchone()[0]
        if exists:
            cursor.execute("DROP TABLE bot_page_group_medicines")


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('bot_app', '0005_alter_botsettings_start_keywords'),
    ]

    operations = [
        # Use state_operations to update Django's in-memory model state
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.RemoveField(
                    model_name='pagegroup',
                    name='medicines',
                ),
            ],
            database_operations=[
                migrations.RunPython(
                    drop_medicines_table_if_exists,
                    reverse_code=noop,
                ),
            ],
        ),
    ]
