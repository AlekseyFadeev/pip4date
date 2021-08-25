import argparse
import os
import re
from bisect import bisect_left
from datetime import datetime
from typing import Tuple, List, Any
from warnings import warn

import requests
from tabulate import tabulate

parser = argparse.ArgumentParser(description='PyPI filtering by date')
parser.add_argument('package', type=str, nargs='+',
                    help='Package name(s) or path to requirements file (if -r is enabled)')
parser.add_argument('date', type=str,
                    help='The date for which you need actual packages. Format: YYYY-MM-DD')
parser.add_argument('-r', '--requirements', dest='req', action='store_true',
                    help='Put this flag on if you want to pass packages argument as the path to requirements.txt file')
parser.add_argument('-l', '--list', dest='list_show', action='store_true',
                    help='With this option no package installation will be performed, but the table with versions and '
                         'release dates will be displayed')
parser.add_argument('-o', '--output', dest='output', type=str,
                    help='With this option no package installation will be performed, but uutput file with new '
                         'requirements will be created')


def binary_search(a: List, x: Any, lo: int = 0, hi: int = None) -> int:
    if hi is None:
        hi = len(a)
    pos = bisect_left(a, x, lo, hi)
    return pos if pos != hi else -1


def get_ver(package_name: str, package_date: str) -> Tuple[str, str]:
    res = requests.get(f'https://pypi.org/pypi/{package_name}/json')
    d = res.json()
    releases = list(d['releases'].keys())
    releases = [r for r in releases if d['releases'][r]]
    release_dates = [datetime.strptime(d['releases'][r][0]['upload_time'], '%Y-%m-%dT%H:%M:%S') for r in releases]
    release_by_date = sorted(zip(release_dates, releases))
    release_dates, releases = zip(*release_by_date)

    date_parsed = datetime.strptime(package_date, '%Y-%m-%d')
    fit_index = binary_search(release_dates, date_parsed)
    if fit_index == 0:
        v_ind = 0
        warn(
            f'Package {package_name} did not exist at the requested time! Getting the first version {releases[v_ind]} '
            f'uploaded '
            f'at {release_dates[v_ind]} available at PyPI.')
    else:
        v_ind = fit_index - 1 if fit_index != -1 else fit_index

    actual_ver = releases[v_ind]
    actual_date = str(release_dates[v_ind])

    return actual_ver, actual_date


args = parser.parse_args()

assert re.match(r'20\d\d-[0-1]\d-[0-3]\d', args.date) is not None, \
    'Invalid date! Please, provide correct date in format YYYY-MM-DD'

if not args.req:
    packages = args.package if isinstance(args.package, list) else [args.package]
else:
    packages = []
    with open(args.req) as f:
        lines = f.readlines()
        for line in lines:
            p = line.rstrip().split('=')[0]
            packages.append(p)

packages_ver_and_date = [(p, *get_ver(p, args.date)) for p in packages]

if args.output is not None:
    with open(args.output, 'w') as f:
        f.writelines([f'{p[0]}=={p[1]}\n' for p in packages_ver_and_date])
elif args.list_show:
    print(f'\nActual packages for date {args.date}:\n')
    print(tabulate(packages_ver_and_date, headers=['Package', 'Version', 'Release date']))
else:
    os.system('pip install --upgrade pip')
    for p in packages_ver_and_date:
        print(f'Installing {p[0]} ver {p[1]}, released at {p[2]}...')
        os.system(f'pip install {p[0]}=={p[1]}')
