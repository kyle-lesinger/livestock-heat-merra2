"""
Standard plotting configuration for MERRA-2 gridded data visualization.

This module provides standardized plotting parameters and helper functions
to ensure consistent, high-quality visualizations across all notebooks.

Key principles:
- Show grid cell edges to emphasize discrete ~55km resolution data
- Maintain geographic context with state boundaries
- Use consistent colormaps and styling
- Make it clear this is gridded climate data, not continuous fields
"""

import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature

# =============================================================================
# Standard Plot Parameters
# =============================================================================

# Grid cell visualization (Method 5: Grid edges + boundaries)
GRID_PARAMS = {
    'edgecolors': 'white',      # Show grid cell boundaries
    'linewidth': 0.2,           # Thin lines, visible but not overwhelming
    'alpha': 0.95,              # Slight transparency to see grid edges better
    'transform': ccrs.PlateCarree()
}

# Geographic extent for US Lower 48
US_EXTENT = [-125, -66, 24, 49]  # [lon_min, lon_max, lat_min, lat_max]

# Map features
MAP_FEATURES = {
    'states': {
        'linewidth': 0.5,
        'edgecolor': 'black',
        'facecolor': 'none'
    },
    'coastline': {
        'linewidth': 0.8
    }
}

# Gridlines
GRIDLINE_PARAMS = {
    'draw_labels': True,
    'linewidth': 0.5,
    'alpha': 0.5,
    'linestyle': '--'
}

# =============================================================================
# Standard Colormaps and Value Ranges
# =============================================================================

VARIABLE_STYLES = {
    'T2M': {
        'cmap': 'RdYlBu_r',
        'vmin': 15,
        'vmax': 35,
        'label': 'Temperature (°C)',
        'description': '2-meter air temperature'
    },
    'VPD': {
        'cmap': 'YlOrRd',
        'vmin': 0,
        'vmax': 4,
        'label': 'VPD (kPa)',
        'description': 'Vapor pressure deficit'
    },
    'SFMC': {
        'cmap': 'Blues',
        'vmin': 0,
        'vmax': 50,
        'label': 'Surface Soil Moisture (kg/m²)',
        'description': 'Surface soil moisture (0-5cm)'
    },
    'RZMC': {
        'cmap': 'Blues',
        'vmin': 0,
        'vmax': 200,
        'label': 'Root Zone Soil Moisture (kg/m²)',
        'description': 'Root zone soil moisture (0-100cm)'
    },
    'GWETROOT': {
        'cmap': 'BrBG',
        'vmin': 0,
        'vmax': 1,
        'label': 'Root Zone Wetness',
        'description': 'Root zone wetness fraction (0-1)'
    },
    'PRECIP_TOTAL': {
        'cmap': 'viridis',
        'vmin': 0,
        'vmax': 10,
        'label': 'Precipitation (mm/hr)',
        'description': 'Total precipitation rate'
    },
    'region_mask': {
        'cmap': 'tab10',
        'vmin': 0.5,
        'vmax': 10.5,
        'label': 'Region ID',
        'description': 'US Region mask (10 regions)'
    }
}

# =============================================================================
# Helper Functions
# =============================================================================

def setup_map_axis(ax=None, extent=US_EXTENT, add_states=True, add_coastline=True,
                   add_gridlines=True, projection=ccrs.PlateCarree()):
    """
    Set up a map axis with standard features.

    Parameters
    ----------
    ax : matplotlib.axes.Axes, optional
        Existing axis to configure. If None, creates new figure.
    extent : list, optional
        Geographic extent [lon_min, lon_max, lat_min, lat_max]
    add_states : bool, default True
        Add state boundaries
    add_coastline : bool, default True
        Add coastline
    add_gridlines : bool, default True
        Add lat/lon gridlines with labels
    projection : cartopy.crs, default PlateCarree
        Map projection

    Returns
    -------
    ax : cartopy.mpl.geoaxes.GeoAxes
        Configured map axis
    """
    if ax is None:
        fig = plt.figure(figsize=(12, 8))
        ax = plt.axes(projection=projection)

    # Add map features
    if add_states:
        ax.add_feature(cfeature.STATES, **MAP_FEATURES['states'])
    if add_coastline:
        ax.add_feature(cfeature.COASTLINE, **MAP_FEATURES['coastline'])

    # Set extent
    ax.set_extent(extent, crs=ccrs.PlateCarree())

    # Add gridlines
    if add_gridlines:
        gl = ax.gridlines(**GRIDLINE_PARAMS)
        gl.top_labels = False
        gl.right_labels = False

    return ax


def plot_merra2_variable(data, variable, lon, lat, ax=None, title=None,
                         colorbar=True, **kwargs):
    """
    Plot a MERRA-2 variable with standard styling.

    Parameters
    ----------
    data : xarray.DataArray or numpy.ndarray
        Data to plot (2D: lat × lon)
    variable : str
        Variable name (must be in VARIABLE_STYLES)
    lon : array-like
        Longitude coordinates
    lat : array-like
        Latitude coordinates
    ax : matplotlib.axes.Axes, optional
        Existing axis. If None, creates new map axis.
    title : str, optional
        Plot title. If None, uses variable description.
    colorbar : bool, default True
        Add colorbar
    **kwargs : dict
        Additional parameters to override defaults

    Returns
    -------
    im : matplotlib.collections.QuadMesh
        The pcolormesh object
    ax : cartopy.mpl.geoaxes.GeoAxes
        The map axis
    """
    if variable not in VARIABLE_STYLES:
        raise ValueError(f"Unknown variable '{variable}'. Available: {list(VARIABLE_STYLES.keys())}")

    # Get variable style
    style = VARIABLE_STYLES[variable].copy()

    # Merge grid params with variable-specific params
    plot_params = GRID_PARAMS.copy()
    plot_params.update({
        'cmap': style.pop('cmap'),
        'vmin': style.pop('vmin'),
        'vmax': style.pop('vmax')
    })

    # Override with user kwargs
    plot_params.update(kwargs)

    # Setup axis
    if ax is None:
        ax = setup_map_axis()

    # Plot data
    im = ax.pcolormesh(lon, lat, data, **plot_params)

    # Add title
    if title is None:
        title = style['description']
    ax.set_title(title, fontsize=12, fontweight='bold')

    # Add colorbar
    if colorbar:
        cbar = plt.colorbar(im, ax=ax, orientation='horizontal', pad=0.05, shrink=0.7)
        cbar.set_label(style['label'], fontsize=11)

    return im, ax


def get_variable_style(variable):
    """
    Get plotting style parameters for a variable.

    Parameters
    ----------
    variable : str
        Variable name

    Returns
    -------
    style : dict
        Style parameters (cmap, vmin, vmax, label, description)
    """
    if variable not in VARIABLE_STYLES:
        raise ValueError(f"Unknown variable '{variable}'. Available: {list(VARIABLE_STYLES.keys())}")
    return VARIABLE_STYLES[variable].copy()


def create_comparison_plot(data_list, variable_list, lon, lat, titles=None,
                          nrows=1, ncols=None, figsize=None):
    """
    Create a multi-panel comparison plot.

    Parameters
    ----------
    data_list : list of arrays
        List of 2D data arrays to plot
    variable_list : list of str
        List of variable names (same length as data_list)
    lon : array-like
        Longitude coordinates
    lat : array-like
        Latitude coordinates
    titles : list of str, optional
        Custom titles for each panel
    nrows : int, default 1
        Number of rows
    ncols : int, optional
        Number of columns. If None, computed from len(data_list) and nrows
    figsize : tuple, optional
        Figure size. If None, computed automatically

    Returns
    -------
    fig : matplotlib.figure.Figure
        The figure
    axes : array of axes
        Array of map axes
    """
    n_plots = len(data_list)
    if ncols is None:
        ncols = int(np.ceil(n_plots / nrows))

    if figsize is None:
        figsize = (6 * ncols, 5 * nrows)

    fig, axes = plt.subplots(
        nrows, ncols,
        figsize=figsize,
        subplot_kw={'projection': ccrs.PlateCarree()}
    )

    # Flatten axes if needed
    if n_plots > 1:
        axes = np.atleast_1d(axes).flatten()
    else:
        axes = [axes]

    # Plot each panel
    for i, (data, var) in enumerate(zip(data_list, variable_list)):
        title = titles[i] if titles is not None else None
        plot_merra2_variable(data, var, lon, lat, ax=axes[i], title=title)

    # Hide extra axes
    for j in range(i + 1, len(axes)):
        axes[j].set_visible(False)

    plt.tight_layout()
    return fig, axes


# =============================================================================
# Usage Examples (in docstring)
# =============================================================================

"""
Usage Examples
--------------

1. Quick plot with defaults:
    import plot_config as pc
    im, ax = pc.plot_merra2_variable(t2m_data, 'T2M', lons, lats)
    plt.show()

2. Manual plot with standard grid params:
    import plot_config as pc

    fig, ax = plt.subplots(figsize=(12, 8), subplot_kw={'projection': ccrs.PlateCarree()})
    ax = pc.setup_map_axis(ax)

    style = pc.get_variable_style('T2M')
    im = ax.pcolormesh(
        lons, lats, t2m_data,
        cmap=style['cmap'],
        vmin=style['vmin'],
        vmax=style['vmax'],
        **pc.GRID_PARAMS
    )
    plt.colorbar(im, ax=ax, label=style['label'])
    plt.show()

3. Multi-panel comparison:
    fig, axes = pc.create_comparison_plot(
        [t2m_june, t2m_july, t2m_august],
        ['T2M', 'T2M', 'T2M'],
        lons, lats,
        titles=['June 2020', 'July 2020', 'August 2020'],
        ncols=3
    )
    plt.show()

4. Custom colormap range:
    im, ax = pc.plot_merra2_variable(
        t2m_data, 'T2M', lons, lats,
        vmin=0, vmax=40  # Override default range
    )
"""
