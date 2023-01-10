from setuptools import setup

setup(name='cbpi4_TimeProportionalControl',
      version='0.0.1',
      description='CraftBeerPi Plugin for Time Proportional Kettle temperature control',
      author='Mike Rotskoff',
      author_email='mrotskoff@gmail.com',
      url='',
      include_package_data=True,
      package_data={
        # If any package contains *.txt or *.rst files, include them:
      '': ['*.txt', '*.rst', '*.yaml'],
      'cbpi4_TimeProportionalControl': ['*','*.txt', '*.rst', '*.yaml']},
      packages=['cbpi4_TimeProportionalControl'],
     )