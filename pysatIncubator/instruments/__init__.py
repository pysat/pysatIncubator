__all__ = ['champ_star', 'demeter_iap', 'superdarn_grdex',
           'supermag_magnetometer']

for inst in __all__:
    exec("from pysatIncubator.instruments import {x}".format(x=inst))
