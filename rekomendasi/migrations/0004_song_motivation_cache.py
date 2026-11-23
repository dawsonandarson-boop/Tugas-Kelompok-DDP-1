from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rekomendasi', '0003_alter_mood_options_lagu_bahasa_lagu_energy_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='SongMotivationCache',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('source', models.CharField(max_length=20)),
                ('external_id', models.CharField(max_length=60)),
                ('title', models.CharField(max_length=200)),
                ('artist', models.CharField(max_length=200)),
                ('song_type', models.CharField(max_length=40)),
                ('message', models.CharField(max_length=320)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name': 'Cache Motivasi Lagu',
                'verbose_name_plural': 'Cache Motivasi Lagu',
            },
        ),
        migrations.AddConstraint(
            model_name='songmotivationcache',
            constraint=models.UniqueConstraint(fields=('source', 'external_id'), name='unique_song_motivation_track'),
        ),
    ]
