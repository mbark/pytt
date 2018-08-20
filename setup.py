from setuptools import setup
setup(
    name='pytt',
    version='1.0.0',
    packages=['pytt'],
    entry_points={
        'console_scripts': [
            'pytt = pytt.__main__:main'
        ]
    })
