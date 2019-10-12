import pathlib
import shutil
import markdown

from django.core.management.base import BaseCommand
from django.db.transaction import atomic

from server.challenge.interface import Challenge
from server.user.interface import User
from server.context import Context
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
            if not dir.is_dir() or dir.name.startswith('.'):
                continue
            print(f'Processing {dir.name}...', end=' ')
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

            if not int(metadata.get('enabled', 0)):
                print('Not enabled')
                continue
            url = metadata['url']
            if url and not url.startswith('http://'):
                source = dir / url
                target = pathlib.Path(files_dir) / url
                shutil.copy(source, target)
                url = '/media/' + url

            if 'extrafile' in metadata:
                for file in metadata['extrafile'].split(', '):
                    source = dir / file
                    target = pathlib.Path(files_dir) / file
                    shutil.copy(source, target)

            flag_flags = metadata['flag'].split(', ')
            flag_scores = metadata['score'].split(', ')
            if len(flag_flags) > 1:
                flag_names = metadata['flagnames'].split(', ')
            else:
                flag_names = ['']

            flags = []
            for i in range(len(flag_flags)):
                if flag_flags[i].startswith('f"'):
                    assert flag_flags[i].startswith('f"flag{{')
                    assert flag_flags[i].endswith('}}"')
                    flag_type = 'expr'
                else:
                    assert flag_flags[i].startswith('flag{')
                    assert flag_flags[i].endswith('}')
                    flag_type = 'text'
                flags.append({
                    'name': flag_names[i],
                    'score': flag_scores[i],
                    'type': flag_type,
                    'flag': flag_flags[i],
                })

            Challenge.create(
                Context(root),
                name=metadata['title'],
                category=metadata['category'],
                detail=markdown.markdown(body, extensions=['fenced_code']),
                url=url,
                prompt='flag{...}',
                index=int(metadata['index']),
                enabled=True,
                flags=flags,
            )

            print('Succeeded')
