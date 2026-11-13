# Copyright © 2026 Christopher Snow
"""Capture the same executed figures at two reading sizes; never rerun source."""
import io, textwrap
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator, FixedLocator
from matplotlib.container import BarContainer

def capture_figures():
    wide, narrow = [], []
    for number in plt.get_fignums():
        figure=plt.figure(number)
        image=io.StringIO();figure.savefig(image,format='svg',metadata={'Date':None})
        wide.append(image.getvalue())
        figure.set_size_inches(2.6,3.6)
        # A side colour scale squeezes a phone scatter plot. Reposition the
        # same mappable and colour scale; retain its data and normalisation.
        colour_scale=next((item.colorbar for ax in figure.axes for item in ax.collections
                           if getattr(item,'colorbar',None) is not None),None)
        if colour_scale is not None and len(figure.axes)==2:
            mappable=colour_scale.mappable;primary=mappable.axes
            label=colour_scale.ax.get_ylabel() or colour_scale.ax.get_xlabel()
            colour_scale.remove();primary.set_position([.24,.47,.71,.49])
            scale_ax=figure.add_axes([.24,.14,.71,.045])
            scale=figure.colorbar(mappable,cax=scale_ax,orientation='horizontal')
            scale.set_label(textwrap.fill(label,22),fontsize=15)
        for ax in figure.axes:
            ax.set_xlabel(textwrap.fill(ax.get_xlabel(),16),fontsize=15)
            ax.set_ylabel(textwrap.fill(ax.get_ylabel(),16),fontsize=15)
            ax.set_title(textwrap.fill(ax.get_title(),22),fontsize=15)
            ax.tick_params(axis='both',labelsize=14)
            # Keep categorical locations; reduce only continuous tick density.
            small_bars=next((b for b in ax.containers if isinstance(b,BarContainer) and 1<=len(b)<=6),None)
            if small_bars is not None:
                ax.set_xticks([bar.get_x()+bar.get_width()/2 for bar in small_bars])
            elif not ax.xaxis.units and not isinstance(ax.xaxis.get_major_locator(),FixedLocator):
                ax.xaxis.set_major_locator(MaxNLocator(nbins=3))
            legend=ax.get_legend()
            if legend:
                handles,labels=ax.get_legend_handles_labels()
                title=legend.get_title().get_text()
                ax.legend(handles,[textwrap.fill(s,16) for s in labels],title=textwrap.fill(title,16),
                          loc='upper center',bbox_to_anchor=(.5,-.38),ncol=1,fontsize=14,title_fontsize=14,frameon=False)
        # Tight bounding boxes retain labels and the external legend.
        image=io.StringIO();figure.savefig(image,format='svg',metadata={'Date':None},pad_inches=.18 if colour_scale is not None else .1)
        narrow.append(image.getvalue())
    return wide,narrow
