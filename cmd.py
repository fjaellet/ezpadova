"""
EZPADOVA -- A python package that allows you to download PADOVA isochrones
directly from their website

This small package provides a direct interface to the PADOVA/PARSEC isochrone
webpage (http://stev.oapd.inaf.it/cgi-bin/cmd).
It compiles the URL needed to query the website and retrives the data into a
python variable.
"""

import urllib
import urllib2
import zlib
import re
import numpy as np
from os.path import join

#available tracks
map_models = {
    'PA12S': ('parsec_CAF09_v1.2S', 'PARSEC version 1.2S'),
    'PA11': ('parsec_CAF09_v1.1', 'PARSEC version 1.1'),
    'PA10': ('parsec_CAF09_v1.0', 'PARSEC version 1.0'),
    '2010': ('gi10a', 'Marigo et al. (2008) + Girardi et al. (2010); (Case A)'),
    '2010b': ('gi10b', 'Marigo et al. (2008) + Girardi et al. (2010); (Case B)'),
    '2008': ('ma08', 'Marigo et al. (2008)'),
    '2002': ('gi2000', 'Basic set of Girardi et al. (2002)')
}


__def_args__ = {'binary_frac': 0.3,
                'binary_kind': 1,
                'binary_mrinf': 0.7,
                'binary_mrsup': 1,
                'cmd_version': 2.6,
                'dust_source': 'nodust',
                'dust_sourceC': 'nodustC',
                'dust_sourceM': 'nodustM',
                'eta_reimers': 0.2,
                'extinction_av': 0,
                'icm_lim': 4,
                'imf_file': 'tab_imf/imf_chabrier_lognormal.dat',
                'isoc_age': 1e7,
                'isoc_age0': 12.7e9,
                'isoc_dlage': 0.05,
                'isoc_dz': 0.0001,
                'isoc_kind': 'parsec_CAF09_v1.2S',
                'isoc_lage0': 6.6,
                'isoc_lage1': 10.13,
                'isoc_val': 1,
                'isoc_z0': 0.0001,
                'isoc_z1': 0.03,
                'isoc_zeta': 0.02,
                'isoc_zeta0': 0.008,
                'kind_cspecmag': 'aringer09',
                'kind_dust': 0,
                'kind_interp': 1,
                'kind_mag': 2,
                'kind_postagb': -1,
                'kind_pulsecycle': 0,
                'kind_tpagb': 3,
                'lf_deltamag': 0.2,
                'lf_maginf': 20,
                'lf_magsup': -20,
                'mag_lim': 26,
                'mag_res': 0.1,
                'output_evstage': 0,
                'output_gzip': 0,
                'output_kind': 0,
                'photsys_file': 'tab_mag_odfnew/tab_mag_bessell.dat',
                'photosys_version': 'yang',
                'submit_form': 'Submit'}


def file_type(filename, stream=False):
    """ Detect potential compressed file
    Returns the gz, bz2 or zip if a compression is detected, else None.
    """
    magic_dict = {
        "\x1f\x8b\x08": "gz",
        "\x42\x5a\x68": "bz2",
        "\x50\x4b\x03\x04": "zip"
        }
    max_len = max(len(x) for x in magic_dict)
    if not stream:
        with open(filename) as f:
            file_start = f.read(max_len)
        for magic, filetype in magic_dict.items():
            if file_start.startswith(magic):
                return filetype
    else:
        for magic, filetype in magic_dict.items():
            if filename[:len(magic)] == magic:
                return filetype

    return None

#map_carbon_stars = {
    #'loidl': ('loidl01', 'Loidl et al. (2001) (as in Marigo et al. (2008) \
#and Girardi et al. (2008))'),
    #'aringer': ('aringer09', "Aringer et al. (2009) (Note: The interpolation \
#scheme has been slightly improved w.r.t. to the paper's Fig. 19.")
#}

#map_interp = {
    #'default': 0,
    #'improved': 1
#}

#map_circum_Mstars = {
    #'nodustM': ('no dust', ''),
    #'sil': ('Silicates', 'Bressan et al. (1998)'),
    #'AlOx': ('100% AlOx', 'Groenewegen (2006)'),
    #'dpmod60alox40': ('60% Silicate + 40% AlOx', 'Groenewegen (2006)'),
    #'dpmod': ('100% Silicate', 'Groenewegen (2006)')
#}

#map_circum_Cstars = {
    #'nodustC': ('no dust', ''),
    #'gra': ('Graphites', 'Bressan et al. (1998)'),
    #'AMC': ('100% AMC', 'Groenewegen (2006)'),
    #'AMCSIC15': ('85% AMC + 15% SiC', 'Groenewegen (2006)')
#}

def __get_url_args(model=None, carbon=None, interp=None, Mstars=None,
    Cstars=None, dust=None, phot=None):
    """
    Update options in the URL query using internal shortcuts.
    """
    d = __def_args__.copy()

    # overwrite some parameters
    if model is not None:
        d['isoc_kind'] = map_models["%s" % model][0]

    # if carbon is not None:
    #     d['kind_cspecmag'] = map_carbon_stars[carbon][0]

    # if interp is not None:
    #     d['kind_interp'] = map_interp[interp]

    # if dust is not None:
    #     d['dust_source'] = map_circum_Mstars[dust]

    # if Cstars is not None:
    #     d['dust_source'] = map_circum_Cstars[Cstars]

    # if Mstars is not None:
    #     d['dust_source'] = map_circum_Mstars[Mstars]

    if phot is not None:
        d['photsys_file'] = 'tab_mag_odfnew/tab_mag_{0}.dat'.format(phot)

    return d


def __query_website(d):
    """
    Communicate with the CMD website.
    """

    webserver = 'http://stev.oapd.inaf.it'
    print('  Interrogating {0}...'.format(webserver))
    q = urllib.urlencode(d)
    # print('Query content: {0}'.format(q))
    c = urllib2.urlopen(webserver + '/cgi-bin/cmd', q).read()
    aa = re.compile('output\d+')
    fname = aa.findall(c)
    if len(fname) > 0:
        url = '{0}/~lgirardi/tmp/{1}.dat'.format(webserver, fname[0])
        print('  Downloading data...{0}'.format(url))
        bf = urllib2.urlopen(url)
        r = bf.read()
        typ = file_type(r, stream=True)
        if typ is not None:
            r = zlib.decompress(bytes(r), 15 + 32)
        return r
    else:
        print c
        raise RuntimeError('FATAL: Server Response is incorrect')


def get_t_isochrones(log_vals, metal, **kwargs):
    """
    Get a sequence of isochrones at constant Z.

    INPUTS
    ------
    logt0: float
        minimal value of log(t/yr)
    logt1: float
        maximal value of log(t/yr)
    dlogt: float
        step in log(t/yr) for the sequence
    metal: float
        metallicity (z) value to use

    KEYWORDS
    --------
    **kwargs updates the web query

    OUTPUTS
    -------
    r: str
       Return the string content of the data
    """

    logt0, logt1, dlogt = log_vals

    d = __get_url_args(**kwargs)
    d['isoc_val'] = 1
    d['isoc_zeta0'] = metal
    d['isoc_lage0'] = logt0
    d['isoc_lage1'] = logt1
    d['isoc_dlage'] = dlogt

    r = __query_website(d)

    return r


def read_params():
    '''
    Read input parameters from file.
    '''

    # Accept these variations of the 'true' flag.
    true_lst = ('True', 'true', 'TRUE')

    with open('in_params.dat', 'r') as f:
        # Iterate through each line in the file.
        for line in f:

            if not line.startswith("#") and line.strip() != '':
                reader = line.split()

                # Tracks.
                if reader[0] == 'ET':
                    evol_track = str(reader[1])

                # Photometric system.
                if reader[0] == 'PS':
                    phot_syst = str(reader[1])

                # Metallicity range/values.
                if reader[0] == 'MR':
                    z_vals = map(float, reader[1:4])
                    z_range = np.arange(*z_vals)
                if reader[0] == 'MV':
                    if reader[1] in true_lst:
                        z_range = map(float, reader[2:])

                # Age range.
                if reader[0] == 'AR':
                    a_vals = map(float, reader[1:4])

    return evol_track, phot_syst, z_range, a_vals


# Read input parameters from file.
evol_track, phot_syst, z_range, a_vals = read_params()

print 'Query CMD using: {}.\n'.format(map_models["%s" % evol_track][1])

# Run for given range in metallicity.
for metal in z_range:

    print 'z = {}'.format(metal)
    # Call function to get isochrones.
    r = get_t_isochrones(a_vals, metal, model=evol_track,
    phot=phot_syst)

    # Define file name according to metallicity value.
    file_name = join('isochrones/' + ('%0.6f' % metal) + '.dat')

    # Store in file.
    with open(file_name, 'w') as f:
        f.write(r)

print '\nAll done.'
