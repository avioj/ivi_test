from setuptools import setup

setup(
    name='bdd-reporter',
    version='0.1.0',
    description='BDD reporter for python tests.',
    author='Vladimir Tsyuman',
    author_email='vladimir.tsyuman@gmail.com',
    include_package_data=True,
    packages=['bdd_reporter'],
    install_requires=[
        'pytest'
    ],
    entry_points={
        'pytest11': [
            'bdd_reporter = bdd_reporter.pytest_plugin'
        ]
    },
    classifiers=[
        'Framework :: Pytest'
    ]
)
