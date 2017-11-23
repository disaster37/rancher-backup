from distutils.core import setup

version = 'develop'

setup(
  name = 'rancher-backup',
  packages = ['src'],
  version = version,
  description = 'Python library to perform backup on Rancher',
  author = 'Sebastien Langoureaux',
  author_email = 'linuxworkgroup@hotmail.com',
  url = 'https://github.com/disaster37/rancher-backup',
  download_url = 'https://github.com/disaster37/rancher-backup/tarball/%s' % (version,),
  keywords = ['rancher'],
  classifiers = [],
  install_requires = ["pyyaml", "Jinja2", "cattle"]
)