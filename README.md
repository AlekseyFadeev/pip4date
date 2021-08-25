# pip4date
Simple script to install PyPI packages actual for the given date

Examples:

`python3 pip4date.py numpy pandas scikit-learn 2018-03-15 -l`


Actual packages for date 2018-03-15:

| Package   |      Version      |  Release date |
|----------|:-------------:|------:|
| numpy |  1.14.2 | 2018-03-12 17:49:21 |
| pandas |    0.22.0   |   2017-12-31 12:37:46 |
| scikit-learn | 0.19.1 |    2017-10-23 15:28:44 |

Without "-l" flags those package versions will be installed via pip.

<br>

Also you can generate new **requirements.txt** based on results simply by using "-o" flag:

`python3 pip4date.py numpy pandas scikit-learn 2018-03-15 -o requirements.txt`

<br>
If you want to read package names from existing requirements.txt file, just use the following syntax:

`python3 pip4date.py requirements.txt 2018-03-15 -r`
