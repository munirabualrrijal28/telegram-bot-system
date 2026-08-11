"""
Migration 0008: Create the GroupItem model.
This replaces the broken M2M (medicines/attachments) approach with a simple
FK-based model — no join table, works on all environments.
"""

import uuid
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bot_app', '0007_remove_pagegroup_attachments'),
    ]

    operations = [
        migrations.CreateModel(
            name='GroupItem',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=255)),
                ('description', models.TextField(blank=True)),
                ('image', models.ImageField(blank=True, null=True, upload_to='group_item_images/')),
                ('order', models.PositiveIntegerField(default=0, help_text='Display order within the group')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('group', models.ForeignKey(
                    help_text='Group this item belongs to',
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='items',
                    to='bot_app.pagegroup',
                )),
            ],
            options={
                'db_table': 'bot_group_item',
                'ordering': ['order', 'created_at'],
            },
        ),
    ]
