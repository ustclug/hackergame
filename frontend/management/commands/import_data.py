import markdown
import pathlib
import shutil
import traceback
import uuid
import yaml

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db.transaction import atomic

from server.challenge.interface import Challenge
from server.context import Context

UUID_NAMESPACE = uuid.uuid5(
    namespace=uuid.UUID('dcd82ef8-ab13-4942-829c-41aa47f1708b'),
    name=settings.SECRET_KEY,
)


class Command(BaseCommand):
    help = '从题目仓库导入数据'

    def add_arguments(self, parser):
        parser.add_argument('challenges_dir', type=pathlib.Path)
        parser.add_argument('media_dir', type=pathlib.Path)
        parser.add_argument('--dry-run', action='store_true')

    # noinspection PyAttributeOutsideInit
    @atomic
    def handle(self, challenges_dir, media_dir, dry_run=False, **options):
        self.challenges_dir = challenges_dir
        self.media_dir = media_dir
        self.dry_run = dry_run
        context = Context(elevated=True)
        old_challenges = {i.name: i for i in Challenge.get_all(context)}
        new_challenges = {}
        for path in challenges_dir.iterdir():
            if not path.is_dir() or path.name.startswith('.'):
                continue
            # noinspection PyBroadException
            try:
                challenge = self.parse_challenge(path, media_dir)
            except Exception as e:
                msg = traceback.format_exception_only(type(e), e)[0].strip()
                self.stdout.write(self.style.ERROR(f'{path.name}: {msg}'))
            else:
                new_challenges[challenge['name']] = challenge
        self.stdout.write(f'Parsed {len(new_challenges)} challenges')
        for name in new_challenges:
            if name in old_challenges:
                if not dry_run:
                    old_challenges[name].update(**new_challenges[name])
                self.stdout.write(f'{name}: ' + self.style.WARNING('updated'))
            else:
                if not dry_run:
                    Challenge.create(context, **new_challenges[name])
                self.stdout.write(f'{name}: ' + self.style.SUCCESS('created'))
        for name in old_challenges:
            if name not in new_challenges:
                if not dry_run:
                    old_challenges[name].delete()
                self.stdout.write(f'{name}: ' + self.style.NOTICE('deleted'))

    def parse_challenge(self, path, media_dir):
        # default values
        challenge = {
            'enabled': True,
            'name': path.name,
            'category': None,
            'url': None,
            'prompt': 'flag{...}',
            'index': 0,
            'flags': [],
        }
        readme = path / 'README.md'
        with readme.open() as f:
            challenge.update(next(yaml.safe_load_all(f)))
        lines = readme.read_text().splitlines(keepends=True)
        lines = lines[lines.index('---\n', 1) + 1:]
        challenge['detail'] = markdown.markdown(''.join(lines),
                                                extensions=['codehilite'])
        files = path / 'files'
        if files.is_dir():
            target = media_dir / str(uuid.uuid5(UUID_NAMESPACE,
                                                challenge['name']))
            if not self.dry_run:
                shutil.rmtree(target, ignore_errors=True)
                shutil.copytree(files, target)
            if challenge['url'] and challenge['url'].startswith('files/'):
                challenge['url'] = (pathlib.Path('/media') / target.name
                                    / challenge['url'][6:])
        return challenge
