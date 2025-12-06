from setuptools import setup, find_packages
import os

# Read the contents of README file
with open('README.md', 'r', encoding='utf-8') as f:
    long_description = f.read()

# Read requirements
with open('requirements.txt', 'r') as f:
    requirements = f.read().splitlines()

# Get version from package
version = {}
with open(os.path.join('weather_charts', '__init__.py'), 'r') as f:
    exec(f.read(), version)

setup(
    name='weather-charts',
    version=version.get('__version__', '1.0.0'),
    author='Weather Charts Team',
    author_email='support@weathercharts.com',
    description='A Python package to fetch weather data and generate beautiful charts',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/yourusername/weather-charts-py',
    packages=find_packages(),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering :: Visualization',
        'Topic :: Scientific/Engineering :: Atmospheric Science',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.7',
    install_requires=requirements,
    extras_require={
        'web': ['flask>=2.0.0', 'flask-cors>=3.0.0'],
        'plotly': ['plotly>=5.0.0'],
        'dev': [
            'pytest>=6.0.0',
            'pytest-cov>=3.0.0',
            'black>=22.0.0',
            'flake8>=4.0.0',
            'mypy>=0.900',
            'sphinx>=4.0.0',
            'twine>=4.0.0',
        ],
    },
    entry_points={
        'console_scripts': [
            'weather-charts=weather_charts.cli:main',
        ],
    },
    include_package_data=True,
    keywords='weather, charts, visualization, meteorology, openweather, forecast',
    project_urls={
        'Bug Reports': 'https://github.com/yourusername/weather-charts-py/issues',
        'Source': 'https://github.com/yourusername/weather-charts-py',
        'Documentation': 'https://weather-charts.readthedocs.io/',
    },
)