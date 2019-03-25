from setuptools import setup

setup(
    name='randomizer',
    version='0.1.0',
    description='Generate random values for tests.',
    author='Vladimir Tsyuman',
    author_email='vladimir.tsyuman@gmail.com',
    include_package_data=True,
    packages=['randomizer'],
    install_requires=[
        'faker'
    ],
    entry_points={
        'pytest11': [
            'randomizer = randomizer.pytest_plugin'
        ]
    },
    classifiers=[
        'Framework :: Pytest'
    ]
)
