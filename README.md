EZPADOVA 
=========

A python package that allows you to download PADOVA/PARSEC isochrones directly
from their website (http://stev.oapd.inaf.it/cgi-bin/cmd).

:version: 0.1dev
:author: MF

Requirements
-------------

TODO list
--------
* test with parsec 1.1 (currently working with cmd2.3/2.5)
* make a full doc
* cleanup the mess


EXAMPLE USAGE
-------------

* Basic example of downloading a sequence of isochrones, plotting, saving
```python 
>>> r = cmd.get_t_isochrones(6.0, 7.0, 0.05, 0.02)
>>> import pylab as plt
>>> plt.scatter(r['logTe'], r['logL/Lo'], c=r['log(age/yr)'], edgecolor='None')
>>> plt.show()
>>> r.write('myiso.fits')
```

* getting only one isochrone
```python 
>>> r = cmd.get_one_isochrones(1e7, 0.02, phot='spitzer')
```
