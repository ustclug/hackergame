from django.core.management.base import BaseCommand
import nacl.encoding
import nacl.signing

class Command(BaseCommand):
    help = '生成 libsodium (Ed25519) 签名密钥'

    def handle(self, *args, **options):

        key = nacl.signing.SigningKey.generate()
        private_key = key.encode(encoder=nacl.encoding.HexEncoder).decode()
        public_key = key.verify_key.encode(encoder=nacl.encoding.HexEncoder).decode()

        self.stdout.write('这是私钥，请放进 Hackergame 平台 conf/local_settings.py 的 PRIVATE_KEY：')
        self.stdout.write(private_key)
        self.stdout.write('这是公钥，可用于验证 token：')
        self.stdout.write(public_key)
