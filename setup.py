from setuptools import setup


setup(name='fig',
    python_requires='>=3.8',
    version='0.0.1',
    description='File Grouper (FIG)',
    url='https://github.com/RoyBebru/file-grouper-fig',
    author='Roy Bebru',
    author_email='RoyBebru@Gmail.Com',   ### Script Name After Installation
    license='MIT',                       #     ### Import module which must be called
    include_package_data=True,           #     #       ### Function call from module
    packages=["fig"],                    #     #       #
    entry_points = {'console_scripts': 'fig = fig.fig:main'})
