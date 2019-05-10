import setuptools


with open('README.md') as f:
    readme = f.read()

with open('LICENSE') as f:
    license_file = f.read()

setuptools.setup(
    name='hankjbot',
    version='1.0.0',
    description='Telegram bot respresenting Hank Johnson, an Ingress character',
    long_description=readme,
    license=license_file,
    author='PascalRoose',
    author_email='pascalroose@outlook.com',
    url='https://github.com/PascalRoose/hankjbot'
)
