# -*- coding: utf-8 -*-
"""SuperDARN data support for grdex files(Alpha Level!)

Parameters
----------
platform : string
    'superdarn'
name : string
    'grdex'
tag : string
    'north' or 'south' for Northern/Southern hemisphere data

Note
----
Requires davitpy and pydarn to load SuperDARN files.
Uses environment variables set by davitpy to download files
from Virginia Tech SuperDARN data servers. Pydarn routines
are used to load SuperDARN data.

This material is based upon work supported by the 
National Science Foundation under Grant Number 1259508. 

Any opinions, findings, and conclusions or recommendations expressed in this 
material are those of the author(s) and do not necessarily reflect the views 
of the National Science Foundation.

Warnings
--------
Cleaning only removes entries that have 0 vectors, grdex files
are constituted from what it is thought to be good data.

"""

from __future__ import print_function
from __future__ import absolute_import
import sys
import os

import pandas as pds
import numpy as np

import pysat

def list_files(tag='north', sat_id=None, data_path=None, format_str=None):
    """Return a Pandas Series of every file for chosen satellite data

    Parameters
    -----------
    tag : (string)
        Denotes type of file to load.  Accepted types are 'north' and 'south'.
        (default='north')
    sat_id : (string or NoneType)
        Specifies the satellite ID for a constellation.  Not used.
        (default=None)
    data_path : (string or NoneType)
        Path to data directory.  If None is specified, the value previously
        set in Instrument.files.data_path is used.  (default=None)
    format_str : (string or NoneType)
        User specified file format.  If None is specified, the default
        formats associated with the supplied tags are used. (default=None)

    Returns
    --------
    pysat.Files.from_os : (pysat._files.Files)
        A class containing the verified available files
    """

    if format_str is None and tag is not None:
        if tag == 'north' or tag == 'south':
            hemi_fmt = ''.join(('{year:4d}{month:02d}{day:02d}.', tag, '.grdex'))
            return pysat.Files.from_os(data_path=data_path, format_str=hemi_fmt)
        else:
            estr = 'Unrecognized tag name for SuperDARN, north or south.'
            raise ValueError(estr)                  
    elif format_str is None:
        estr = 'A tag name must be passed to SuperDARN.'
        raise ValueError (estr)
    else:
        return pysat.Files.from_os(data_path=data_path, format_str=format_str)
           

def load(fnames, tag=None, sat_id=None):
    import pydarn
    if len(fnames) <= 0 :
        return pysat.DataFrame(None), pysat.Meta(None)
    elif len(fnames)==1:
        
        #b = pydarn.sdio.sdDataOpen(pysat.datetime(1980,1,1), 
        #                            src='local', 
        #                            eTime=pysat.datetime(2050,1,1),
        #                            fileName=fnames[0])
        
        myPtr = pydarn.sdio.sdDataPtr(sTime=pysat.datetime(1980,1,1),
                          eTime=pysat.datetime(2250,1,1),
                          hemi=tag)  
        myPtr.fType, myPtr.dType = 'grdex', 'dmap'                 
        myPtr.ptr = open(fnames[0],'r')
                                                                                            
        #data_list = pydarn.sdio.sdDataReadAll(myPtr)
        in_list = []
        in_dict = {'stid':[],
            'channel':[],
            'noisemean':[],
            'noisesd':[],
            'gsct':[],
            'nvec':[],
            'pmax':[],
            'start_time':[],
            'end_time':[],
            'vemax':[],
            'vemin':[],
            'pmin':[],
            'programid':[],
            'wmax':[],
            'wmin':[],
            'freq':[]}
        
        #for info in data_list:
        while True:
            info = pydarn.dmapio.readDmapRec(myPtr.ptr)   
            info = pydarn.sdio.sdDataTypes.gridData(dataDict=info)
            if info.channel is None:
                break 
                   
            drift_frame = pds.DataFrame.from_records(info.vector.__dict__, 
                                                     nrows=len(info.pmax),
                                                     index=info.vector.index)
            drift_frame['partial'] = 1
            drift_frame.drop('index', axis=1, inplace=True)
            drift_frame.index.name = 'index'
            sum_vec = 0
            for nvec in info.nvec:
                #in_frame = drift_frame.iloc[0:nvec]
                #drift_frame = drift_frame.iloc[nvec:]
                in_list.append(drift_frame.iloc[sum_vec:sum_vec+nvec])
                sum_vec += nvec

            in_dict['stid'].extend(info.stid)
            in_dict['channel'].extend(info.channel)
            in_dict['noisemean'].extend(info.noisemean)
            in_dict['noisesd'].extend(info.noisesd)
            in_dict['gsct'].extend(info.gsct)
            in_dict['nvec'].extend(info.nvec)
            in_dict['pmax'].extend(info.pmax)
            in_dict['start_time'].extend([info.sTime]*len(info.pmax))
            in_dict['end_time'].extend([info.eTime]*len(info.pmax))
            in_dict['vemax'].extend(info.vemax)
            in_dict['vemin'].extend(info.vemin)
            in_dict['pmin'].extend(info.pmin)
            in_dict['programid'].extend(info.programid)
            in_dict['wmax'].extend(info.wmax)
            in_dict['wmin'].extend(info.wmin)
            in_dict['freq'].extend(info.freq)

        output = pds.DataFrame(in_dict)
        output['vector'] = in_list
        output.index = output.start_time
        output.drop('start_time', axis=1, inplace=True)
        myPtr.ptr.close()
        return output, pysat.Meta()
    else:
        raise ValueError('Only one filename currently supported.')

                                        
#def default(ivm):
#
#    return
            
def clean(self):
    # remove data when there are no vectors
    idx, = np.where(self['nvec'] > 0)
    self.data = self.data.iloc[idx]

    return  
    
def download(date_array, tag, sat_id, data_path, user=None, password=None):
    """
    Download SuperDARN data from Virginia Tech organized for loading by pysat.

    """

    import sys
    import os
    import pysftp
    import pydarn
    
    if user is None:
        user = os.environ['DBREADUSER']
    if password is None:
        password = os.environ['DBREADPASS']
        
    with pysftp.Connection(
            os.environ['VTDB'], 
            username=user,
            password=password) as sftp:
            
        for date in date_array:
            myDir = '/data/'+date.strftime("%Y")+'/grdex/'+tag+'/'
            fname = date.strftime("%Y%m%d")+'.' + tag + '.grdex'
            local_fname = fname+'.bz2'
            saved_fname = os.path.join(data_path,local_fname) 
            full_fname = os.path.join(data_path,fname) 
            try:
                print('Downloading file for '+date.strftime('%D'))
                sys.stdout.flush()
                sftp.get(myDir+local_fname, saved_fname)
                os.system('bunzip2 -c '+saved_fname+' > '+ full_fname)
                os.system('rm ' + saved_fname)
            except IOError:
                print('File not available for '+date.strftime('%D'))


 
         
def load_orig(fnames, tag=None):
    import pydarn
    if len(fnames) <= 0 :
        return pysat.DataFrame(None), pysat.Meta(None)
    elif len(fnames)==1:
        b = pydarn.sdio.sdDataOpen(pysat.datetime(1980,1,1), 
                                    src='local', 
                                    eTime=pysat.datetime(2050,1,1),
                                    fileName=fnames[0])
                                    
        data_list = pydarn.sdio.sdDataReadAll(b)
        sys.stdout.flush()
        in_dict = []
        for info in data_list:
            arr = np.arange(len(info.stid))
            drift_frame = pds.DataFrame(info.vector.__dict__, 
                                    #index=[info.vector.mlon, info.vector.mlat])
                                    index=info.vector.index)
            drift_frame.index.name = 'index'
            drift_frame.sort(inplace=True)
            #drift_frame.index.names=['mlon', 'mlat']
            for i in arr:
                nvec = info.nvec[i]
                in_frame = drift_frame.iloc[0:nvec]
                drift_frame = drift_frame.iloc[nvec:]
                in_dict.append({'stid':info.stid[i],
                            'channel':info.channel[i],
                            'noisemean':info.noisemean[i],
                            'noisesd':info.noisesd[i],
                            'gsct':info.gsct[i],
                            'nvec':info.nvec[i],
                            'pmax':info.pmax[i],
                            'vector':in_frame,
                            'start_time':info.sTime,
                            'end_time':info.eTime,
                            'vemax':info.vemax[i],
                            'vemin':info.vemin[i],
                            'pmin':info.pmin[i],
                            'programid':info.programid[i],
                            'wmax':info.wmax[i],
                            'wmin':info.wmin[i],
                            'freq':info.freq[i]})
        output = pds.DataFrame(in_dict)
        output.index = output.start_time
        output.drop('start_time', axis=1, inplace=True)
        return output, pysat.Meta()
    else:
        raise ValueError('Only one filename currently supported.')
                 
                                 
#
#
#def test3():
#    b = pydarn.sdio.sdDataOpen(pysat.datetime(1980,1,1), 
#                                src='local', 
#                                eTime=pysat.datetime(2050,1,1),
#                                fileName=fnames[0])
#                                
#    data_list = pydarn.sdio.sdDataReadAll(b)
#    print 'building dataframe'
#    sys.stdout.flush()
#    in_frame=[]
#    names=['stid','channel','noisemean','noisesd','gsct','nvec','pmax','vector',
#            'start_time','end_time','vemax','vemin','pmin','programid',
#            'wmax','wmin','freq']
#    
#    in_dict={}    
#    for name in names:
#        in_dict[name]=[]
#
#    for info in data_list:
#
#        drift_frame = pds.DataFrame(info.vector.__dict__, 
#                                index=[info.vector.mlon, info.vector.mlat])
#        drift_frame.index.names=['mlon', 'mlat']
#        in_dict['stid'].extend(info.stid)
#        in_dict['channel'].extend(info.channel)
#        in_dict['noisemean'].extend(info.noisemean)
#        in_dict['noisesd'].extend(info.noisesd)
#        in_dict['gsct'].extend(info.gsct)
#        in_dict['nvec'].extend(info.nvec)
#        in_dict['pmax'].extend(info.pmax)
#        in_dict['start_time'].extend([info.sTime]*len(info.stid))
#        in_dict['end_time'].extend([info.eTime]*len(info.stid))
#        in_dict['vemax'].extend(info.vemax)
#        in_dict['vemin'].extend(info.vemin)
#        in_dict['pmin'].extend(info.pmin)
#        in_dict['programid'].extend(info.programid)
#        in_dict['wmax'].extend(info.wmax)
#        in_dict['wmin'].extend(info.wmin)
#        in_dict['freq'].extend(info.freq)
#        for nvec in info.nvec:
#            in_frame.append(drift_frame.iloc[0:nvec])
#            drift_frame = drift_frame.iloc[nvec:]
#    in_dict['vector'] = in_frame
#    output = pds.DataFrame(in_dict)
#    output.index = output.start_time
#    output.drop('start_time', axis=1, inplace=True) 
