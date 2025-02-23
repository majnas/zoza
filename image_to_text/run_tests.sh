#!/bin/bash
ls
python -m pytest test.py --durations=0 -v -W ignore::DeprecationWarning -W ignore::UserWarning
