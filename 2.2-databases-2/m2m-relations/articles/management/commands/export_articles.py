import json
import os
from django.core.management.base import BaseCommand
from articles.models import Article

from django.conf import settings 


class Command(BaseCommand):
    help = 'Экспорт статей в JSON файл articles.json' 

    def handle(self, *args, **options):
        articles = Article.objects.all() 
        data = [] 

        for article in articles:
            scopes = article.scopes.all() 
            tags = [] 
            for scope in scopes:
                tags.append({
                    'name': scope.tag.name,
                    'is_main': scope.is_main
                })

            data.append({
                'title': article.title,
                'text': article.text,
                'published_at': article.published_at.isoformat(),
                'image': str(article.image),  
                'tags': tags,
                'video_url': article.video_url
            })
      
        file_path = os.path.join(settings.BASE_DIR, 'articles.json') 

        with open(file_path, 'w', encoding='utf-8') as f: 
            json.dump(data, f, indent=4, ensure_ascii=False) 

        self.stdout.write(self.style.SUCCESS(f'Успешно сохранили {len(articles)} статей в articles.json')) 