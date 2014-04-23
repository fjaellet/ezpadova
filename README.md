ezPADOVA-2
==========

A python package that allows you to download PADOVA/PARSEC isochrones directly
from the [CMD](http://stev.oapd.inaf.it/cgi-bin/cmd) website.

Fork of original [ezpadova](https://github.com/mfouesneau/ezpadova) code
by [Morgan Fouesneau](https://github.com/mfouesneau)


Example usage
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
