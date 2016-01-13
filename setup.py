from setuptools import setup, find_packages

setup(
    name='burgerking',
    version='0.0.1',
    description='a package manager for models',
    url='https://github.com/burger-king/burgerking',
    author='Francis Tseng, Matthew Conlen',
    author_email='f@frnsys.com, mpconlen@gmail.com',
    license='MIT',

    packages=find_packages(),
    install_requires=[
        'click',
    ],
    entry_points='''
        [console_scripts]
        bk=bkpm.cli:cli
    ''',
)