"""
Migration 0007: Remove the `attachments` ManyToManyField from PageGroup.
The join table `bot_page_group_attachments` was never created on the AWS
production database, so we conditionally drop it only if it exists.
"""

from django.db import migrations


def drop_attachments_table_if_exists(apps, schema_editor):
    """Safely drop bot_page_group_attachments only if it exists."""
    with schema_editor.connection.cursor() as cursor:
        cursor.execute("""
            SELECT COUNT(*)
            FROM information_schema.tables
            WHERE table_schema = DATABASE()
            AND table_name = 'bot_page_group_attachments'
        """)
        exists = cursor.fetchone()[0]
        if exists:
            cursor.execute("DROP TABLE bot_page_group_attachments")


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('bot_app', '0006_remove_pagegroup_medicines'),
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.RemoveField(
                    model_name='pagegroup',
                    name='attachments',
                ),
            ],
            database_operations=[
                migrations.RunPython(
                    drop_attachments_table_if_exists,
                    reverse_code=noop,
                ),
            ],
        ),
    ]
