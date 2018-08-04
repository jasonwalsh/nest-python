from setuptools import
    find_packages,
    setup
)


setup(
    install_requires=[
        'Flask==1.0.2',
        'redis==2.10.6',
        'requests==2.19.1'
    ],
    name='nest-python',
    packages=find_packages()
)
