# Generated by Django 4.2.3 on 2023-07-11 11:44

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("social_media_content", "0003_tags_post_tags"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="post",
            options={"ordering": ["-created"]},
        ),
    ]
