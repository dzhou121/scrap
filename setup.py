from setuptools import setup, find_packages


requires = [
    'flask',
    'flask-restful',
    'requests',
    'lxml',
    'cssselect',
    'redis',
    'simplejson',
    'gevent',
    'nose',
    'mox',
]


setup(
    name='scrap',
    version='0.1',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=requires,
    entry_points="""
    [console_scripts]
    scrap-scraper = scrap.cmd.scraper:main
    scrap-api = scrap.cmd.api:main
    """,
)
