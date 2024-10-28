import markdown.treeprocessors
import pathlib
import shutil
import subprocess
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


class ReplaceLinks(markdown.extensions.Extension):
    class Processor(markdown.treeprocessors.Treeprocessor):
        def __init__(self, md, files_url):
            super().__init__(md)
            self.files_url = files_url

        def run(self, root):
            for node in root.iter('a'):
                if node.attrib['href'].startswith('files/'):
                    node.attrib['href'] = str(self.files_url
                                              / node.attrib['href'][6:])
            for node in root.iter('img'):
                if node.attrib['src'].startswith('files/'):
                    node.attrib['src'] = str(self.files_url
                                             / node.attrib['src'][6:])
            for node in root.iter('a'):
                if node.attrib['href'].startswith(('http://', 'https://')):
                    node.attrib['target'] = '_blank'
                    node.attrib['rel'] = 'noopener'

    def __init__(self, files_url):
        super().__init__()
        self.files_url = files_url

    def extendMarkdown(self, md):
        processor = self.Processor(self, self.files_url)
        md.treeprocessors.register(processor, 'replacelinks', 0)


class Command(BaseCommand):
    help = '从题目仓库导入数据'

    def add_arguments(self, parser):
        parser.add_argument('challenges_dir', type=pathlib.Path)
        parser.add_argument('--dry-run', action='store_true')

    # noinspection PyAttributeOutsideInit
    @atomic
    def handle(self, challenges_dir, dry_run=False, **options):
        self.challenges_dir = challenges_dir.resolve()
        self.media_dir = pathlib.Path(settings.MEDIA_ROOT)
        self.dry_run = dry_run
        context = Context(elevated=True)
        old_challenges = {i.name: i for i in Challenge.get_all(context)}
        new_challenges = {}
        pathnames = {}
        for path in challenges_dir.iterdir():
            if not path.is_dir() or path.name.startswith('.') or path.name.startswith('_'):
                continue
            # noinspection PyBroadException
            try:
                challenge = self.parse_challenge(path)
            except Exception as e:
                msg = traceback.format_exception_only(type(e), e)[0].strip()
                self.stdout.write(self.style.ERROR(f'{path.name}: {msg}'))
            else:
                if challenge['enabled']:
                    new_challenges[challenge['name']] = challenge
                    pathnames[challenge['name']] = path.name
        self.stdout.write(f'Parsed {len(new_challenges)} challenges')
        for name in new_challenges:
            if name in old_challenges:
                self.stdout.write(f'{name} ({pathnames[name]}): ', ending='')
                if not dry_run:
                    old_challenges[name].update(**new_challenges[name])
                self.stdout.write(self.style.WARNING('updated'))
            else:
                self.stdout.write(f'{name} ({pathnames[name]}): ', ending='')
                if not dry_run:
                    Challenge.create(context, **new_challenges[name])
                self.stdout.write(self.style.SUCCESS('created'))
        for name in old_challenges:
            if name not in new_challenges:
                self.stdout.write(f'{name}: ', ending='')
                if not dry_run:
                    old_challenges[name].delete()
                self.stdout.write(self.style.NOTICE('deleted'))

    def parse_challenge(self, path):
        # default values
        challenge = {
            'enabled': True,
            'name': path.name,
            'category': None,
            'url_orig': None,
            'check_url_clicked': False,
            'prompt': 'flag{...}',
            'index': 0,
            'flags': [],
        }
        readme = path / 'README.md'
        with readme.open() as f:
            challenge.update(next(yaml.safe_load_all(f)))
        if challenge.get('url') and not challenge.get('url_orig'):
            challenge['url_orig'] = challenge['url']
            del challenge['url']
        lines = readme.read_text().splitlines(keepends=True)
        lines = lines[lines.index('---\n', 1) + 1:]
        if (path / 'pre-import-hook.sh').exists():
            subprocess.run([path / 'pre-import-hook.sh'], cwd=path, check=True)
        files_uuid = str(uuid.uuid5(UUID_NAMESPACE, challenge['name']))
        files_path = self.media_dir / files_uuid
        files_url = pathlib.Path('/media') / files_uuid
        files = path / 'files'
        if files.is_dir():
            if not self.dry_run:
                shutil.rmtree(files_path, ignore_errors=True)
                shutil.copytree(files, files_path)
        if challenge['url_orig'] and challenge['url_orig'].startswith('files/'):
            challenge['url_orig'] = str(files_url / challenge['url_orig'][6:])
        challenge['detail'] = markdown.markdown(
            ''.join(lines),
            extensions=['codehilite', 'fenced_code', 'md_in_html', ReplaceLinks(files_url)],
        )
        return challenge
