from setuptools import setup, find_packages

setup(
    long_description_content_type="text/markdown",
    long_description=open("readme.md", "r").read(),
    name="ouilookup",
    version="0.42",
    description="lookup the ieee's oui table",
    author="Pascal Eberlein",
    author_email="pascal@eberlein.io",
    url="https://github.com/smthnspcl/ouilookup",
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.7',
    ],
    keywords="oui mac lookup",
    packages=find_packages(),
    include_package_data=True,
    entry_points={'console_scripts': ['ouilookup = ouilookup.__main__:main']},
    install_requires=open("requirements.txt").readlines()
)