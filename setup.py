from setuptools import setup, find_packages

setup(
    long_description=open("README.rst", "r").read(),
    name="pyoui",
    version="0.5",
    description="lookup the ieee's oui table by mac, mac prefix, org name or country",
    author="Pascal Eberlein",
    author_email="pascal@eberlein.io",
    url="https://github.com/smthnspcl/pyoui",
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
    entry_points={'console_scripts': ['pyoui = pyoui.__main__:main']},
    install_requires=open("requirements.txt").readlines()
)
