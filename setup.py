from setuptools import setup, find_packages


requires = [
    'flask',
    'requests',
    'lxml',
    'cssselect',
    'redis',
]


setup(
    name='scrap',
    version='0.1',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=requires,
)
