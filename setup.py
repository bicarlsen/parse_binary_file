import setuptools

with open('README.md', 'r') as f:
    long_desc = f.read()

# get __version__
exec(open('parse_binary_file/_version.py').read())

setuptools.setup(
    name='parse_binary_file',
    version = __version__,
    author='Brian Carlsen',
    author_email = 'carlsen.bri@gmail.com',
    description = 'Parse binary files by describing their structure.',
    long_description = long_desc,
    long_description_content_type = 'text/markdown',
    keywords = ['parse', 'binary', 'file'],
    url = 'https://github.com/bicarlsen/parse_binary_file.git',
    packages = setuptools.find_packages(),
    classifiers = [
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires = [],
    package_data = {
    },
)
