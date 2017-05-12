import setuptools

if __name__ == '__main__':
    setuptools.setup(
        name='lepo',
        version='0.0.0',
        url='https://github.com/akx/lepo',
        author='Aarni Koskela',
        maintainer='Aarni Koskela',
        maintainer_email='akx@iki.fi',
        license='MIT',
        install_requires=['Django', 'openapi'],
        packages=setuptools.find_packages('.', exclude=('lepo_tests', 'tests',)),
        include_package_data=True,
    )
