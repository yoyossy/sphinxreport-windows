========
bar-plot
========

The :class:`SphinxReportPlugins.Plotter.BarPlot` class presents :term:`labeled values`
as overlapping bars.

.. report:: Trackers.LabeledDataExample
   :render: bar-plot
   :layout: row
   :width: 200

   A bar plot with overlapping bars.

Options
-------

:class:`SphinxReportPlugins.Plotter.BarPlot` understands the
:ref:`common plot options` and the following options:

.. glossary::
   :sorted:

   label
      string

      field to use for data labels. See :term:`labeled values with labels`
      
   error
      string

      field to use for error bars. See :term:`labeled values with errors`

================
stacked-bar-plot
================

The :class:`SphinxReportPlugins.Plotter.StackedBarPlot` class presents :term:`labeled values`
as stacked bars.

.. report:: Trackers.LabeledDataExample
   :render: stacked-bar-plot
   :layout: row
   :width: 200

   A bar plot with stacked bars.

====================
interleaved-bar-plot
====================

The :class:`SphinxReportPlugins.Plotter.InterleavedBarPlot` class presents :term:`labeled values`
as interleaved bars. Both *interleaved-bars* and *bars* can be used.

.. report:: Trackers.LabeledDataExample
   :render: interleaved-bar-plot
   :layout: row
   :width: 200

   A bar plot with interleaved bars.


Adding errors bars and labels
===============================

The :class:`SphinxReportPlugins.Plotter.InterleavedBarPlot` class presents :term:`labeled values`
as interleaved bars. Both *interleaved-bars* and *bars* can be used.

.. report:: Trackers.LabeledDataWithErrorsAndLabelsExample
   :render: bar-plot
   :error: error
   :layout: row
   :width: 200

   A bar plot with interleaved bars and errors

.. report:: Trackers.LabeledDataWithErrorsAndLabelsExample
   :render: interleaved-bar-plot
   :error: error
   :layout: row
   :width: 200

   A bar plot with interleaved bars and errors

.. report:: Trackers.LabeledDataWithErrorsAndLabelsExample
   :render: stacked-bar-plot
   :error: error
   :layout: row
   :width: 200
   
   A bar plot with interleaved bars and errors

.. report:: Trackers.LabeledDataWithErrorsAndLabelsExample
   :render: bar-plot
   :label: label
   :layout: row
   :width: 200

   A bar plot with interleaved bars and errors

.. report:: Trackers.LabeledDataWithErrorsAndLabelsExample
   :render: interleaved-bar-plot
   :label: label
   :layout: row
   :width: 200

   A bar plot with interleaved bars and errors

.. report:: Trackers.LabeledDataWithErrorsAndLabelsExample
   :render: stacked-bar-plot
   :label: label
   :layout: row
   :width: 200

   A bar plot with interleaved bars and errors


