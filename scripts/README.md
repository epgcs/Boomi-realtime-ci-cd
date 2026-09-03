
What should scripts/ contain?

Eventually something like:

scripts/                                                       
├── package.sh
├── deploy.sh
└── validate.sh
<  or  >
scripts/
├── package.py
├── deploy.py
└── validate.py
-----------------------------------------------------
For example, conceptually:

package.sh
    ↓
Create/package Boomi component

-----------------------------------------------------

deploy.sh
    ↓
Take packaged component
    ↓
Deploy to target environment

-----------------------------------------------------

validate.sh
    ↓
Check deployment
