'''This document contains a number of sample trackers.'''

import sys, os, re, random

from SphinxReport.Tracker import Tracker, Status
from SphinxReport.odict import OrderedDict as odict

def BarData(): return dict( [("bar1", 20), ("bar2", 10)] )

class LabeledDataExample( Tracker ):
    slices = ("slice1", "slice2")
    tracks = ("track1", "track2", "track3")
    def __call__(self, track, slice = None):
        if slice == "slice1":
            return odict( (("column1", 10),
                           ("column2", 20 ),) )
        elif slice == "slice2":
            return odict ( (("column1", 20),
                            ("column2", 10),
                            ("column3", 5),) )

class LabeledDataLargeExample( Tracker ):
    slices = ("slice1", "slice2")
    tracks = [ "track%i" % x for x in range(0,100) ]
    def __call__(self, track, slice = None):
        if slice == "slice1":
            return odict( (("column1", 10),
                           ("column2", 20 ),) )
        elif slice == "slice2":
            return odict ( (("column1", 20),
                            ("column2", 10),
                            ("column3", 5),) )

class LabeledDataWithErrorsExample( Tracker ):
    slices = ("slice1", "slice2")
    tracks = ("track1", "track2", "track3")
    def __call__(self, track, slice = None):
        if slice == "slice1":
            return odict( ( 
                    ("column1", dict( ( ('data', 20), 
                                        ('error', 1), 
                                        ) ) ),
                    ("column2", dict( ( ('data', 10), 
                                        ('error', 2),
                                        ) ) ),
                    )) 
        elif slice == "slice2":
            return odict( ( 
                    ("column1", dict( ( ('data', 20), 
                                        ('error', 3),
                                        ) )),
                    ("column2", dict( ( ('data', 10), 
                                        ('error', 4))) ),
                    ("column3", dict( ( ('data', 30), 
                                        ('error', 5))) ),
                    ) )

class LabeledDataWithErrorsAndLabelsExample( Tracker ):
    slices = ("slice1", "slice2")
    tracks = ("track1", "track2", "track3")
    def __call__(self, track, slice = None):
        if slice == "slice1":
            return odict( ( 
                    ("column1", dict( ( ('data', 20), 
                                        ('error',5), 
                                        ('label','**' ) ) )),
                    ("column2", dict( ( ('data', 10), 
                                        ('error',2), 
                                        ('label', '*' ) ) ) )
                    )) 
        elif slice == "slice2":
            return odict( ( 
                    ("column1", dict( ( ('data', 20), 
                                        ('error',5),
                                        ('label','***' ) ) )),
                    ("column2", dict( ( ('data', 10), 
                                        ('error',1))) ),
                    ("column3", dict( ( ('data', 30), 
                                        ('error',4))) ),
                    ) )

class SingleColumnDataExample( Tracker ):
    '''return a single column of data.'''
    slices = ("slice1", "slice2")
    tracks = ("track1", "track2", "track3")
    def __call__(self, track, slice = None):
        s = [random.randint(0,20) for x in range(40)]
        random.shuffle( s )
        return odict( (("data", s),) )

class ArrayDataExample( Tracker ):
    '''return two arrays of data.'''
    
    slices = [ "slice%i" % x for x in range(0,2) ]
    tracks = [ "track%i" % x for x in range(0,3) ]

    def __call__(self, track, slice = None):

        scale = (3-int(track[-1])) 
        
        data = odict( (("x", range(0,50)),
                       ("y", [ x * scale for x in range(0,50) ] ) ) )
        
        return data

class SingleColumnDataLargeExample( Tracker ):
    '''return a single column of data.'''
    slices = ("slice1", "slice2")
    tracks = [ "track%i" % x for x in range(0,20) ]
    def __call__(self, track, slice = None):
        s = [random.randint(0,20) for x in range(40)]
        random.shuffle( s )
        return odict( (("data", s),) )


class SingleColumnDataWithErrorExample( Tracker ):
    '''return a single column of data.'''
    slices = ("slice1", "slice2")
    tracks = ("track1", "track2", "track3")
    def __call__(self, track, slice = None):
        s = [random.randint(0,20) for x in range(40)]
        e = [random.randint(0,3) for x in range(40)]
        random.shuffle( s )
        return odict( (("data", s),
                       ("error", e) ) )

class SingleColumnDataExampleWithoutSlices( Tracker ):
    '''return a single column of data.'''
    tracks = ("track1", "track2", "track3")
    def __call__(self, track, slice = None):
        s = [random.randint(0,20) for x in range(40)]
        random.shuffle( s )
        return odict( (("data", s),) )

class MultipleColumnDataExample( Tracker ):
    '''multiple columns each with a column with data.'''
    mColumns = [ "col1", "col2", "col3" ]
    slices = ("slice1", "slice2")
    tracks = ("track1", "track2")
    def __call__(self, track, slice = None):
        data = []
        if slice == "slice1":
            for x in range(len(self.mColumns)-1):
                data.append( [ y + random.gauss( 0, 0.2 ) for y in range(20) ] )
        elif slice == "slice2":
            for x in range(len(self.mColumns)):
                data.append( [ y + random.gauss( 0, 0.5 ) for y in range(20) ] )
        return odict( zip(self.mColumns, data) )

class MultipleColumnDataFullExample( Tracker ):
    '''multiple columns each with a column with data.'''
    mColumns = [ "col1", "col2", "col3" ]
    slices = ("slice1", "slice2")
    tracks = ("track1", "track2")
    def __call__(self, track, slice = None):
        data = []
        if slice == "slice1":
            for x in range(len(self.mColumns)):
                data.append( [ y + random.gauss( 0, 0.2 ) for y in range(20) ] )
        elif slice == "slice2":
            for x in range(len(self.mColumns)):
                data.append( [ y + random.gauss( 0, 0.5 ) for y in range(20) ] )
        return odict( zip(self.mColumns, data) )

class ErrorInTracker1( Tracker ):
    '''A tracker that creates an error - exception while collecting data.'''
    slices = ("slice1", "slice2")
    tracks = ("track1", "track2")
    def __call__(self, track, slice = None):
        raise ValueError("testing: could not collect data")
    
class ErrorInTracker2( Tracker ):
    '''A tracker that creates an error - problems while returning tracks.'''
    slices = ("slice1", "slice2")
    def getTracks( self ):
        raise ValueError( "testing: could not build tracks" )
    def __call__(self, track, slice = None):
        return odict( (("data", range(0,10)),) )

class ErrorInTracker3( Tracker ):
    '''A tracker that creates an error - problems while returning tracks.'''
    slices = ("slice1", "slice2")
    tracks = ("track1", "track2")
    def __call__(self, track, slice = None):
        return None

class LabeledDataTest( Tracker ):
    slices = ("slice1", "slice2")
    tracks = ("track1", "track2", "track3")

    def __call__(self, track, slice = None):
        if slice == "slice1":
            return odict( (("column1", 10),
                           ("column2", 20 ),) )
        elif slice == "slice2":
            return odict ( (("column1", 20),
                            ("column2", 10),
                            ("column3", 5),) )
    
class StatusTracker( Status ):
    tracks = ("track1", "track2", "track3")
    
    def testTest1( self, track ):
        '''test1 passes'''
        return "PASS", 0.5

    def testTest2( self, track ):
        '''test2 fails - 
        A large test.'''
        return "FAIL", 2

    def testTest3( self, track ):
        '''test3 gives a warning'''
        return "WARN", "a string"

    def testTest4( self, track ):
        '''test4 is not available/applicable'''
        return "NA", None


def getSingleValue(): return 12
    
