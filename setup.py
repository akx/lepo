import re
import setuptools

with open('./requirements.in') as f:
    install_requires = [l for l in f.readlines() if l and not l.startswith('#')]

with open('./lepo/__init__.py', 'r') as infp:
    version = re.search("__version__ = ['\"]([^'\"]+)['\"]", infp.read()).group(1)

if __name__ == '__main__':
    setuptools.setup(
        name='lepo',
        version=version,
        url='https://github.com/akx/lepo',
        author='Aarni Koskela',
        author_email='akx@iki.fi',
        maintainer='Aarni Koskela',
        maintainer_email='akx@iki.fi',
        license='MIT',
        install_requires=install_requires,
        packages=setuptools.find_packages('.', exclude=(
            'lepo_tests',
            'lepo_tests.*',
        )),
        include_package_data=True,
    )
