# pysatIncubator: pysat development lab for instruments
[![Build Status](https://travis-ci.org/pysat/pysatIncubator.svg?branch=main)](https://travis-ci.org/pysat/pysatIncubator)
[![Coverage Status](https://coveralls.io/repos/github/pysat/pysatIncubator/badge.svg?branch=main)](https://coveralls.io/github/pysat/pysatIncubator?branch=main)
[![DOI](https://zenodo.org/badge/287392599.svg)](https://zenodo.org/badge/latestdoi/287392599)

# Installation

Currently, the main way to get pysatIncubator is through github.

```
git clone https://github.com/pysat/pysatIncubator.git
```

Change directories into the repository folder and run the setup.py file.  For a local install use the "--user" flag after "install".

```
cd pysatIncubator/
python setup.py install
```

Note: pre-1.0.0 version
------------------
pysatIncubator is currently in an initial development phase.  Much of the API is being built off of the upcoming pysat 3.0.0 software in order to streamline the usage and test coverage.  This version of pysat is planned for release later this year.  Currently, you can access the develop version of this through github:
```
git clone https://github.com/pysat/pysat.git
cd pysat
git checkout develop-3
python setup.py install
```
It should be noted that this is a working branch and is subject to change.

# Using with pysat

The instrument modules are portable and designed to be run like any pysat instrument.

```
import pysat
from pysatIncubator.instruments import champ_star

champ = pysat.Instrument(inst_module=champ_star)
```
Another way to use the instruments in an external repository is to register the instruments.  This only needs to be done the first time you load an instrument.  Afterward, pysat will identify them using the `platform` and `name` keywords.

```
import pysat

pysat.utils.registry.register('pysatIncubator.instruments.champ_star')
champ = pysat.Instrument('champ', 'star')
```

A note on empirical models
--------------------------
pysatIncubator allows users to interact with a number of upper atmospheric empirical models through the [pyglow](https://github.com/timduly4/pyglow) package.  However, pyglow currently requires manual install through git.  While pysatIncubator can be installed and used without pyglow, it should be installed by the user to access the pyglow methods.  Please follow the install instructions at https://github.com/timduly4/pyglow.

The methods that run empirical models can also be exported to any pysat instrument. For instance, to add thermal plasma predictions from the IRI model to the C/NOFS IVM instrument, one can invoke

```
import pysat
from pysatIncubator.methods import empirical

ivm = pysat.Instrument(platform='cnofs', name='ivm')
ivm.custom.attach(empirical.add_iri_thermal_plasma, 'modify',
               glat_label='glat',
               glong_label='glon', alt_label='altitude')
```
Once the custom function is added, the model will automatically be run when the dataset is loaded.
