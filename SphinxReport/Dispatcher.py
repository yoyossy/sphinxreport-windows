import os, sys, re, shelve, traceback, cPickle, types, itertools

from SphinxReport.ResultBlock import ResultBlock, ResultBlocks
from SphinxReport import DataTree
from SphinxReport.Component import *
from SphinxReport import Utils
from SphinxReport import Cache

VERBOSE=True

from odict import OrderedDict as odict

class Dispatcher(Component):
    """Dispatch the directives in the ``:report:`` directive
    to a :class:`Tracker`, class:`Transformer` and :class:`Renderer`.
    
    The dispatcher has three passes:

    1. Collect data from a :class:`Tracker`

    2. Transform data from a :class:`Transformer`

    3. Render data with a :class:`Renderer`

    This class adds the following options to the :term:`render` directive.

       :term:`groupby`: group data by :term:`track` or :term:`slice`.

    """

    def __init__(self, tracker, renderer, transformers = None ):
        '''render images using an instance of a :class:`Tracker.Tracker`
        to obtain data, an optional :class:`Transformer` to transform
        the data and a :class:`Renderer.Renderer` to render the output.
        '''
        Component.__init__(self)

        self.debug("starting dispatcher '%s': tracker='%s', renderer='%s', transformer:='%s'" % \
                  (str(self), str(tracker), str(renderer), str(transformers) ) )

        self.tracker = tracker
        # add reference to self for access to tracks
        self.tracker.dispatcher = self
        self.renderer = renderer
        self.transformers = transformers

        try:
            if tracker.cache:
                self.cache = Cache.Cache( Cache.tracker2key(tracker) )
            else:
                self.cache = {}
        except AttributeError:
            self.cache = Cache.Cache( Cache.tracker2key(tracker) )

        self.data = DataTree.DataTree()

    def __del__(self):
        pass

    def getCaption( self ):
        """return a caption string."""
        return self.__doc__

    def parseArguments(self, *args, **kwargs ): 
        '''argument parsing.'''

        self.groupby = kwargs.get("groupby", "slice")
        self.nocache = "nocache" in kwargs

        try: self.mInputTracks = [ x.strip() for x in kwargs["tracks"].split(",")]
        except KeyError: self.mInputTracks = None

        try: self.mInputSlices = [ x.strip() for x in kwargs["slices"].split(",")]
        except KeyError: self.mInputSlices = None
        
        try: self.mColumns = [ x.strip() for x in kwargs["columns"].split(",")]
        except KeyError: self.mColumns = None

        self.tracker_options = kwargs.get( "tracker" , None )
        
    def getData( self, path ):
        """get data for track and slice. Save data in persistent cache for further use.

        For functions, path should be an empty tuple.
        """

        if path:
            key = DataTree.path2str(path)
        else:
            key = "all"

        result, fromcache = None, False
        if not self.nocache or self.tracker_options:
            try:
                result = self.cache[ key ]
                fromcache = True
            except KeyError:
                pass

        kwargs = {}
        if self.tracker_options:
            kwargs['options'] = self.tracker_options
        
        if result == None:
            try:
                result = self.tracker( *path, **kwargs )
            except Exception, msg:
                self.warn( "exception for tracker '%s', path '%s': msg=%s" % (str(self.tracker),
                                                                              DataTree.path2str(path), 
                                                                              msg) )
                if VERBOSE: self.warn( traceback.format_exc() )
                raise
        
        if not self.nocache and not fromcache:
            self.cache[key] = result

        return result

    def getDataPaths( self, obj ):
        '''determine data paths from a tracker.

        If obj is a function, returns True and an empty list.

        returns False and a list of lists.
        '''
        data_paths = []
        
        if hasattr( obj, 'paths' ):
            data_paths = getattr( obj, 'paths' )
        elif hasattr( obj, 'getPaths' ):
            data_paths = obj.getPaths()

        if not data_paths:
            if hasattr( obj, 'tracks' ):
                data_paths = [ getattr( obj, 'tracks' ) ]
            elif hasattr( obj, 'getTracks' ):
                data_paths = [ obj.getTracks() ]
            else: 
                # is a function
                return True, []

            # get slices
            if hasattr( obj, 'slices' ):
                data_paths.append( getattr( obj, 'slices' ) )
            elif hasattr( obj, 'getSlices' ):
                data_paths.append( obj.getSlices() )
                
        # sanity check on data_paths. 

        # 1. Replace strings with one-element tuples
        # 2. Remove empty levels in the paths
        to_remove = []
        for x,y in enumerate(data_paths):
            if type(y) in types.StringTypes: data_paths[x]=[y,]
            if len(y) == 0: to_remove.append(x)
            
        for x in to_remove[::-1]:
            del data_paths[x]

        return False, data_paths

    def filterDataPaths( self, datapaths ):
        '''filter *datapaths*.

        returns the filtered data paths.
        '''
        
        if not datapaths: return

        def _filter( all_entries, input_list ):
            # need to preserve type of all_entries
            result = []
            search_entries = map(str, all_entries )
            m = dict( zip( search_entries, all_entries) )
            for s in input_list:
                if s in search_entries:
                    # collect exact matches
                    result.append( all_entries[search_entries.index(s)] )
                elif s.startswith("r(") and s.endswith(")"):
                    # collect pattern matches:
                    # remove r()
                    s = s[2:-1] 
                    # remove flanking quotation marks
                    if s[0] in ('"', "'") and s[-1] in ('"', "'"): s = s[1:-1]
                    rx = re.compile( s )
                    result.extend( [ all_entries[y] for y,x in enumerate( search_entries ) if rx.search( str(x) ) ] )
            return result

        if self.mInputTracks:
            datapaths[0] = _filter( datapaths[0], self.mInputTracks )
        
        if self.mInputSlices:
            if len(datapaths) < 2:
                raise ValueError( "slice filtering for `%s` without slices" % (self.mInputSlices))
            datapaths[1] = _filter( datapaths[1], self.mInputSlices )

        return datapaths

    def collect( self ):
        '''collect all data.

        Data is stored in a multi-level dictionary (DataTree)
        '''

        self.data = odict()

        is_function, datapaths = self.getDataPaths(self.tracker)
        
        # if function, no datapaths
        if is_function:
            d = self.getData( () )

            # save in data tree as leaf
            DataTree.setLeaf( self.data, ("all",), d )

            self.debug( "%s: collecting data finished for function." % (self.tracker))
            return

        # if no tracks, error
        if len(datapaths) == 0 or len(datapaths[0]) == 0:
            self.warn( "%s: no tracks found - no output" % self.tracker )
            raise ValueError( "no tracks found from %s" % self.tracker )
        
        # filter data paths
        datapaths = self.filterDataPaths( datapaths )

        # if no tracks, error
        if len(datapaths) == 0 or len(datapaths[0]) == 0:
            self.warn( "%s: no tracks remain after filtering - no output" % self.tracker )
            raise ValueError( "no tracks found from %s" % self.tracker )

        all_paths = list(itertools.product( *datapaths ))
        self.debug( "%s: collecting data started for %i data paths" % (self.tracker, 
                                                                       len( all_paths) ) )

        self.data = odict()
        for path in all_paths:
            
            d = self.getData( path )

            # ignore empty data sets
            if d == None: continue

            # save in data tree as leaf
            DataTree.setLeaf( self.data, path, d )

        self.debug( "%s: collecting data finished for %i data paths" % (self.tracker, 
                                                                       len( all_paths) ) )

    def transform(self): 
        '''call data transformers and group tree
        '''
        for transformer in self.transformers:
            self.debug( "%s: applying %s" % (self.renderer, transformer ))
            self.data = transformer( self.data )

    def group( self ):
        '''rearrange data tree for grouping.

        and set group level.
        '''

        data_paths = DataTree.getPaths( self.data )
        nlevels = len(data_paths)

        # get number of levels required by renderer
        try:
            renderer_nlevels = self.renderer.nlevels
        except AttributeError:
            renderer_nlevels = 0
        
        if self.groupby == "none":
            self.group_level = renderer_nlevels
        
        elif self.groupby == "track":
            # track is first level
            self.group_level = 0
            # add pseudo levels, if there are not enough levels
            # to group by track
            if nlevels == renderer_nlevels:
                d = odict()
                for x in data_paths[0]: d[x] = odict( ((x, self.data[x]),))
                self.data = d

        elif self.groupby == "slice":
            # rearrange tracks and slices in data tree
            if nlevels <= 2 :
                warn( "grouping by slice, but only %i levels in data tree - all are grouped" % nlevels)
                self.group_level = -1
            else:
                self.data = DataTree.swop( self.data, 0, 1)
                self.group_level = 0
            
        elif self.groupby == "all":
            # group everthing together
            self.group_level = -1
        else:
            # neither group by slice or track ("ungrouped")
            self.group_level = -1

    def prune( self ):
        '''prune data tree.

        Remove all empty leaves.

        Remove all levels from the data tree that are
        superfluous, i.e. levels that contain only a single label
        all labels in the hierarchy below are the same.
       
        Ignore both the first and last level for this analyis.
        '''

        # remove all empty leaves        
        DataTree.removeEmptyLeaves( self.data )

        # prune superfluous levels
        data_paths = DataTree.getPaths( self.data )
        nlevels = len(data_paths)

        # get number of levels required by renderer
        try:
            renderer_nlevels = self.renderer.nlevels
        except AttributeError:
            renderer_nlevels = 0
        
        # do not prune for renderers that want all data
        if renderer_nlevels < 0: return

        levels_to_prune = []

        for level in range( 1, nlevels-1):

            # check for single label in level
            if len(data_paths[level]) == 1:
                label = data_paths[level][0]
                prefixes = DataTree.getPrefixes( self.data, level )
                keep = False
                for prefix in prefixes:
                    leaves = DataTree.getLeaf( self.data, prefix )
                    if len(leaves) > 1 or label not in leaves:
                        keep = True
                        break
                if not keep: levels_to_prune.append( (level, label) )


        levels_to_prune.reverse()

        # only prune to the minimum of levels required by renderer at most
        #levels_to_prune = levels_to_prune[:nlevels - renderer_nlevels]
        for level, label in levels_to_prune:
            self.debug( "pruning level %i from data tree: label='%s'" % (level, label) )
            DataTree.removeLevel( self.data, level )

    def render( self ):
        '''supply the :class:`Renderer.Renderer` with the data to render. 
        
        The data supplied will depend on the ``groupby`` option.

        return resultblocks
        '''
        self.debug( "%s: rendering data started for %i items" % (self,
                                                                 len(self.data)))
        
        results = ResultBlocks( title="main" )

        # get number of levels required by renderer
        try:
            renderer_nlevels = self.renderer.nlevels
        except AttributeError:
            renderer_nlevels = 0

        data_paths = DataTree.getPaths( self.data )
        nlevels = len(data_paths)

        group_level = self.group_level

        self.debug( "%s: rendering data started. levels=%i, required levels>=%i, group_level=%i, data_paths=%s" %\
                        (self, nlevels, 
                         renderer_nlevels,
                         group_level,
                         str(data_paths)[:100]))

        if nlevels < renderer_nlevels:
            # add some dummy levels if levels is not enough
            d = self.data
            for x in range( renderer_nlevels - nlevels):
                d = odict( (("all", d ),))
            results.append( self.renderer( d, path = ("all",) ) )

        elif group_level < 0 or renderer_nlevels < 0:
            # no grouping
            results.append( self.renderer( self.data, path = () ) )
        else:
            # group at level group_level
            paths = list(itertools.product( *data_paths[:group_level+1] ))
            for path in paths:
                work = DataTree.getLeaf( self.data, path )
                if not work: continue
                try:
                    results.append( self.renderer( work, path = path ))
                except:
                    results.append( ResultBlocks( Utils.buildException( "rendering" ) ) )

        if len(results) == 0:
            self.warn("tracker returned no data.")
            raise ValueError( "tracker returned no data." )

        self.debug( "%s: rendering data finished with %i blocks" % (self.tracker, len(results)))

        return results

    def __call__(self, *args, **kwargs ):

        try: self.parseArguments( *args, **kwargs )
        except: return ResultBlocks(ResultBlocks( Utils.buildException( "parsing" ) ))

        self.debug( "profile: started: tracker: %s" % (self.tracker))

        try: self.collect()
        except: return ResultBlocks(ResultBlocks( Utils.buildException( "collection" ) ))

        self.debug( "profile: finished: tracker: %s" % (self.tracker))

        data_paths = DataTree.getPaths( self.data )
        self.debug( "%s: after collection: %i data_paths: %s" % (self,len(data_paths), str(data_paths)))
        
        # transform data
        try: self.transform()
        except: return ResultBlocks(ResultBlocks( Utils.buildException( "transformation" ) ))

        data_paths = DataTree.getPaths( self.data )
        self.debug( "%s: after transformation: %i data_paths: %s" % (self,len(data_paths), str(data_paths)))

        # remove superfluous levels
        try: self.prune()
        except: return ResultBlocks(ResultBlocks( Utils.buildException( "pruning" ) ))

        data_paths = DataTree.getPaths( self.data )
        self.debug( "%s: after pruning: %i data_paths: %s" % (self,len(data_paths), str(data_paths)))

        # remove group plots
        try: self.group()
        except: return ResultBlocks(ResultBlocks( Utils.buildException( "grouping" ) ))

        data_paths = DataTree.getPaths( self.data )
        self.debug( "%s: after grouping: %i data_paths: %s" % (self,len(data_paths), str(data_paths)))

        self.debug( "profile: started: renderer: %s" % (self.renderer))

        try: result = self.render()
        except: return ResultBlocks(ResultBlocks( Utils.buildException( "rendering" ) ))

        self.debug( "profile: finished: renderer: %s" % (self.renderer))

        return result
        
    def getTracks( self ):
        '''return tracks used by the dispatcher.
        
        used for re-constructing call to cache.
        '''
        return self.tracks

    def getSlices( self ):
        '''return slices used by the dispatcher.
        
        used for re-constructing call to cache.
        '''
        return self.slices
