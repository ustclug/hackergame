import pathlib
import shutil
import markdown2

from django.core.management.base import BaseCommand
from django.db.transaction import atomic
from django.utils import timezone

from server.challenge.interface import Challenge
from server.submission.interface import Submission
from server.terms.interface import Terms
from server.trigger.interface import Trigger
from server.user.interface import User
from server.context import Context
from server.exceptions import NotFound
from server.submission.interface import SlowDown
from ...models import Account


class Command(BaseCommand):
    help = '从题目仓库导入数据'

    def add_arguments(self, parser):
        parser.add_argument('source_dir')
        parser.add_argument('files_dir')

    @atomic
    def handle(self, source_dir, files_dir, **options):
        root = User.create(Context(), group='other', nickname='root').user
        root.is_staff = True
        root.is_superuser = True
        root.save()
        root.refresh_from_db()
        Account.objects.create(provider='debug', identity='root', user=root)

        for dir in pathlib.Path(source_dir).iterdir():
            if dir.is_dir():
                print(f'Processing {dir.name}')
                for file in dir.iterdir():
                    if file.name.upper() == 'README.MD':
                        readme = file
                        break
                else:
                    print('Readme file not found')
                    continue

                with open(readme) as f:
                    lines = f.readlines()
                if lines[0] != '---\n':
                    print('Header not found in readme')
                    continue
                pos = lines.index('---\n', 1)
                headers = lines[1:pos]
                body = ''.join(lines[pos + 1:])
                metadata = {}
                for line in headers:
                    pos = line.find(':')
                    key = line[:pos].strip()
                    value = line[pos + 1:].strip()
                    metadata[key] = value

                if 'enabled' in metadata and int(metadata['enabled']):
                    url = metadata['url']
                    if url and not url.startswith('http://'):
                        target = pathlib.Path(files_dir) / url
                        shutil.copy(url, target)
                        url = '/media/' + url

                    flag_flags = metadata['flag'].split(',')
                    flag_scores = metadata['score'].split(',')
                    if len(flag_flags) > 1:
                        flag_names = metadata['flagnames'].split(',')
                    else:
                        flag_names = ['']

                    flags = []
                    for i in range(len(flag_flags)):
                        flags.append({
                            'name': flag_names[i],
                            'score': flag_scores[i],
                            'type': 'expr' if flag_flags[i].startswith('f"') else 'text',
                            'flag': flag_flags[i],
                        })
                
                    Challenge.create(
                        Context(root),
                        name=metadata['title'],
                        category=metadata['category'],
                        detail=markdown2.markdown(body),
                        url=url,
                        prompt='flag{...}',
                        index=int(metadata['index']),
                        enabled=True,
                        flags=flags,
                    )

                    print('Succeeded')
                else:
                    print('Not enabled')
