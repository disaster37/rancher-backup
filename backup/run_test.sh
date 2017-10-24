#!/bin/sh

docker run --rm -ti -e 'PYTHONPATH=/code/src' -v $PWD:/code webcenter/nosetests-python2.7:latest bash -c "pip install --upgrade -r /code/requirements.txt && nosetests -w test/backup"