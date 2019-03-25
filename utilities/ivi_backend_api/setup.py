from setuptools import setup

setup(
    name='ivi-backend-api',
    version='0.1.0',
    description='Ivi test backend api.',
    author='Vladimir Tsyuman',
    author_email='vladimir.tsyuman@gmail.com',
    include_package_data=True,
    packages=['ivi_backend_api'],
    install_requires=[
        'requests',
        'pytest',
        'dataclasses-json'
    ],
    entry_points={
        'pytest11': [
            'ivi_backend_api = ivi_backend_api.pytest_plugin'
        ]
    },
    classifiers=[
        'Framework :: Pytest'
    ]
)