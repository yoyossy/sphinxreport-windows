"""Mixin classes for Renderers that plot.
"""

import os, sys, re, math, tempfile


from SphinxReport.ResultBlock import ResultBlock, ResultBlocks
from SphinxReportPlugins.Renderer import Renderer, Matrix
from SphinxReport.odict import OrderedDict as odict
from SphinxReport import Utils
from SphinxReport import Stats

from rpy2.robjects import r as R
import rpy2.robjects as ro
import rpy2.robjects.numpy2ri

from docutils.parsers.rst import directives

def parseRanges(r):
    '''given a string in the format "x,y", 
    return a tuple of values (x,y).

    missing values are set to None.
    '''

    if not r: return r
    r = [ x.strip() for x in r.split(",")]
    if r[0] == "": r[0] = None
    else: r[0] = float(r[0])
    if r[1] == "": r[1] = None
    else: r[1] = float(r[1])
    return r

def getCurrentRDevice():
    '''return the numerical device id of the current device.'''
    #R.dev_off()
    #return R.dev_cur().values()[0]
    return R["dev.cur"]()[0]

class Plotter(object):
    """Base class for Renderers that do simple 2D plotting.

    This mixin class provides convenience function for :class:`Renderer.Renderer`
    classes that do 2D plotting.

    The base class takes care of counting the plots created,
    provided that the methods :meth:`startPlot` and :meth:`endPlot`
    are called appropriately. It then inserts the appropriate place holders.

    This class adds the following options to the :term:`report` directive:

       :term:`logscale`: apply logscales one or more axes.

       :term:`xtitle`: add a label to the X axis

       :term:`ytitle`: add a label to the Y axis

       :term:`title`:  title of the plot
       
       :term:`add-title`: add title to each plot

       :term:`legend-location`: specify the location of the legend

       :term:`as-lines`: do not plot symbols

       :term:`xrange`: restrict plot a part of the x-axis

       :term:`yrange`: restrict plot a part of the y-axis

    With some plots default layout options will result in plots 
    that are misaligned (legends truncated, etc.). To fix this it might
    be necessary to increase plot size, reduce font size, or others.
    The following options will be passed on the matplotlib to permit
    this control.

       :term:`mpl-figure`: options for matplotlib
           ``figure`` calls().

       :term:`mpl-legend`: options for matplotlib
           ``legend`` calls().

       :term:`mpl-subplot`: options for matplotlib
           ``subplots_adjust`` calls().
           
       :term:`mpl-rc`: general environment settings for matplotlib.
          See the matplotlib documentation. Multiple options can be
          separated by ;, for example 
          ``:mpl-rc: figure.figsize=(20,10);legend.fontsize=4``

    """

    mLegendFontSize = 8
    # number of chars to use to reduce legend font size
    mMaxLegendSize = 100

    ## maximum number of rows per column. If there are more,
    ## the legend is split into multiple columns
    mLegendMaxRowsPerColumn = 30

    options = (
        ('logscale',  directives.unchanged),
        ('title',  directives.unchanged),
        ('add-title',  directives.flag),
        ('xtitle',  directives.unchanged),
        ('ytitle',  directives.unchanged),
        ('xrange',  directives.unchanged),
        ('yrange',  directives.unchanged),
        ('zrange', directives.unchanged),
        ('mpl-figure',  directives.unchanged),
        ('mpl-legend',  directives.unchanged),
        ('mpl-subplot',  directives.unchanged),
        ('mpl-rc',  directives.unchanged), 
        ('as-lines', directives.flag),
        ('legend-location',  directives.unchanged),
        )

    def __init__(self, *args, **kwargs ):
        """parse option arguments."""

        self.mFigure = 0
        self.mColors = "bgrcmk"
        self.mSymbols = ["g-D","b-h","r-+","c-+","m-+","y-+","k-o","g-^","b-<","r->","c-D","m-h"]
        self.mMarkers = "so^>dph8+x"

        self.logscale = kwargs.get("logscale", None )
        self.title = kwargs.get("title", None )
        self.add_title = "add-title" in kwargs
        self.xlabel = kwargs.get("xtitle", None )
        self.ylabel = kwargs.get("ytitle", None )

        # substitute '-' in SphinxReport-speak for ' ' in matplotlib speak
        self.legend_location = re.sub("-", " ", kwargs.get("legend-location", "outer-top"))

        self.width = kwargs.get("width", 0.50 )
        self.mAsLines = "as-lines" in kwargs
        self.xrange = parseRanges(kwargs.get("xrange", None ))
        self.yrange = parseRanges(kwargs.get("yrange", None ))
        self.zrange = parseRanges(kwargs.get("zrange", None ))

        if self.mAsLines:
            self.mSymbols = []
            for y in ("-",":","--"):
                for x in "gbrcmyk":
                    self.mSymbols.append( y+x )


    def startPlot( self ):
        R.x11()
                        
    def endPlot( self, work, path ):
        # currently: collects only single plots.
        figid = getCurrentRDevice()
        blocks = ResultBlocks( ResultBlock( "\n".join( ("#$rpl %i$#" % (figid), "")), 
                                            title = "/".join(map(str, path)) ) )
        return blocks

class LinePlot( Renderer, Plotter ):
    '''create a line plot.

    This :class:`Renderer` requires at least three levels:

    line / data / coords.

    This is a base class that provides several hooks for
    derived classes.

    initPlot()

    for line, data in work:
        initLine()

        for coords in data:
            xlabel, ylabels = initCoords()
            for ylabel in ylabels:
                addData( xlabel, ylabel )
            finishCoords()
        finishLine()

    finishPlot()
    '''
    nlevels = 3

    def __init__(self, *args, **kwargs):
        Renderer.__init__(self, *args, **kwargs )
        Plotter.__init__(self, *args, **kwargs )

    def initPlot(self, fig, work, path ):
        '''initialize plot.'''
 
        self.legend = []
        self.plots = []
        self.xlabels = []
        self.ylabels = []

    def addData( self, 
                 line, label,
                 xlabel, ylabel,
                 xvals, yvals, 
                 nplotted ):

        s = self.mSymbols[nplotted % len(self.mSymbols)]
        
        self.plots.append( plt.plot( xvals,
                                     yvals,
                                     s ) )
        
        self.ylabels.append(ylabel)
        self.xlabels.append(xlabel)

    def initCoords( self, label, coords ):
        '''hook for code working a collection of coords.

        should return a single key for xvalues and 
        one or more keys for y-values.
        '''
        keys = coords.keys()
        return keys[0], keys[1:]

    def render(self, work, path ):
        
        # R.graphics_off()
        self.legend = []
        self.xlabels = []

        nplotted = 0

        for line, data in work.iteritems():

            for label, coords in data.iteritems():
                
                # sanity check on data
                try: keys = coords.keys()
                except AttributeError:
                    self.warn("could not plot %s - coords is not a dict: %s" % (label, str(coords) ))
                    continue
                
                if len(keys) <= 1:
                    self.warn("could not plot %s: not enough columns: %s" % (label, str(coords) ))
                    continue

                xlabel, ylabels = self.initCoords( label, coords)
                
                xvals = coords[xlabel]
                for ylabel in ylabels:
                    yvals = coords[ylabel]
                    R.plot( xvals, yvals )
                    # self.addData( line, label, xlabel, ylabel, xvals, yvals, nplotted )
                    nplotted += 1

                    if len(ylabels) > 1:
                        self.legend.append( "/".join((line,label,ylabel) ))
                    else:
                        self.legend.append( "/".join((line,label) ))
                                
                self.xlabels.append(xlabel)

        figid = getCurrentRDevice()
        blocks = ResultBlocks( ResultBlock( "\n".join( ("#$rpl %i$#" % (figid), "")), 
                                            title = "/".join(path) ) )

        return blocks

class BoxPlot( Renderer, Plotter ):
    """Write a set of box plots.
    
    This :class:`Renderer` requires two levels.

    labels[dict] / data[array]
    """
    options = Renderer.options + Plotter.options

    nlevels = 2

    def __init__(self, *args, **kwargs):
        Renderer.__init__(self, *args, **kwargs )
        Plotter.__init__(self, *args, **kwargs )

    def render(self, work, path ):

        self.startPlot()

        plts, legend = [], []
        all_data = []

        for line, data in work.iteritems():

            assert len(data) == 1, "multicolumn data not supported yet: %s" % str(data)

            for label, values in data.iteritems():
                assert Utils.isArray( values ), "work is of type '%s'" % values
                d = [ x for x in values if x != None ]
                if len(d) > 0:
                    all_data.append( ro.FloatVector( d ) )
                    legend.append( "/".join((line,label)))

        R.boxplot( all_data )

        return self.endPlot( work, path )

class SmoothScatterPlot(Renderer, Plotter):
    """A smoothed scatter plot.

    See R.smoothScatter.

    This :class:`Renderer` requires one levels:

    coords[dict]
    """
    options = Renderer.options + Plotter.options +\
        ( ('bins', directives.unchanged), )
    
    nlevels = 1

    def __init__(self, *args, **kwargs):
        Renderer.__init__(self, *args, **kwargs )
        Plotter.__init__(self, *args, **kwargs )

        self.nbins = kwargs.get("nbins", "128" )
        if self.nbins:
            if "," in self.nbins: self.nbins=map(int, self.nbins.split(","))
            else: self.nbins=int(self.nbins)

    def render(self, work, path ):
        
        self.startPlot()
        nplotted = 0

        xlabels, ylabels = [], []

        if len(work) < 2:
            raise ValueError( "requiring two coordinates, only got %s" % str(work.keys()))

        xlabel, ylabel = work.keys()[:2]
        xvals, yvals = Stats.filterNone( work.values()[:2])

        if len(xvals) == 0 or len(yvals) == 0:
            raise ValueError("no data" )

        # apply log transformation on data not on plot
        if self.logscale:
            if "x" in self.logscale:
                xvals = R.log10(xvals)
            if "y" in self.logscale:
                yvals = R.log10(yvals)
                
        R.smoothScatter( xvals, yvals, 
                         xlab=xlabel, ylab=ylabel,
                         nbin = self.nbins )

        return self.endPlot( work, path )
