import setuptools

if __name__ == '__main__':
    setuptools.setup(
        name='lepo',
        version='0.0.0',
        url='https://github.com/akx/lepo',
        author='Aarni Koskela',
        author_email='akx@iki.fi',
        maintainer='Aarni Koskela',
        maintainer_email='akx@iki.fi',
        license='MIT',
        install_requires=['Django', 'iso8601', 'jsonschema', 'marshmallow'],
        packages=setuptools.find_packages('.', exclude=(
            'lepo_tests',
            'lepo_tests.*',
        )),
        include_package_data=True,
    )
