import numpy as np

class PlotHelper:
    """
    Helper class for creating consistent and styled matplotlib plots.
    """
    
    @staticmethod
    def style_axis(ax, title, xlabel=None, ylabel=None, grid=True, 
                   xlim=None, ylim=None, legend=False):
        """
        Apply consistent styling to an axis.
        
        Args:
            ax: Matplotlib axis object
            title (str): Plot title
            xlabel (str, optional): X-axis label
            ylabel (str, optional): Y-axis label
            grid (bool): Whether to show grid
            xlim (tuple, optional): X-axis limits (min, max)
            ylim (tuple, optional): Y-axis limits (min, max)
            legend (bool): Whether to show legend
        """
        ax.set_title(title, fontsize=12, fontweight='bold')
        if xlabel:
            ax.set_xlabel(xlabel, fontsize=10)
        if ylabel:
            ax.set_ylabel(ylabel, fontsize=10)
        if grid:
            ax.grid(True, alpha=0.3)
        if xlim:
            ax.set_xlim(xlim)
        if ylim:
            ax.set_ylim(ylim)
        if legend:
            ax.legend()
    
    @staticmethod
    def create_scatter(ax, x, y, title, xlabel, ylabel, 
                       color='blue', alpha=0.6, size=None, grid=True):
        """
        Create a scatter plot with consistent styling.
        
        Args:
            ax: Matplotlib axis object
            x: X-axis data
            y: Y-axis data
            title (str): Plot title
            xlabel (str): X-axis label
            ylabel (str): Y-axis label
            color (str): Point color
            alpha (float): Transparency (0-1)
            size: Point sizes (scalar or array)
            grid (bool): Whether to show grid
        """
        if size is not None:
            ax.scatter(x, y, s=size, alpha=alpha, c=color)
        else:
            ax.scatter(x, y, alpha=alpha, c=color)
        PlotHelper.style_axis(ax, title, xlabel, ylabel, grid=grid)
    
    @staticmethod
    def create_histogram(ax, data, title, xlabel, ylabel='Frequency',
                         bins=30, color='blue', alpha=0.7, vlines=None):
        """
        Create a histogram with consistent styling.
        
        Args:
            ax: Matplotlib axis object
            data: Data to plot
            title (str): Plot title
            xlabel (str): X-axis label
            ylabel (str): Y-axis label
            bins (int): Number of bins
            color (str): Bar color
            alpha (float): Transparency (0-1)
            vlines (dict, optional): Vertical lines to add, e.g., 
                                    {'mean': value, 'median': value}
        """
        ax.hist(data, bins=bins, color=color, alpha=alpha, edgecolor='black')
        PlotHelper.style_axis(ax, title, xlabel, ylabel, grid=True)
        
        # Add vertical lines if specified
        if vlines:
            colors = {'mean': 'red', 'median': 'green', 'mode': 'orange'}
            for label, value in vlines.items():
                line_color = colors.get(label, 'black')
                ax.axvline(value, color=line_color, linestyle='--', 
                          label=f'{label.capitalize()}: {value:.2f}')
            ax.legend()
    
    @staticmethod
    def create_bar(ax, categories, values, title, xlabel, ylabel,
                   color='blue', alpha=0.7, horizontal=False):
        """
        Create a bar chart with consistent styling.
        
        Args:
            ax: Matplotlib axis object
            categories: Category labels
            values: Bar heights/lengths
            title (str): Plot title
            xlabel (str): X-axis label
            ylabel (str): Y-axis label
            color (str or list): Bar color(s)
            alpha (float): Transparency (0-1)
            horizontal (bool): Whether to create horizontal bars
        """
        if horizontal:
            ax.barh(categories, values, color=color, alpha=alpha)
            ax.invert_yaxis()  # Highest value at top
        else:
            ax.bar(categories, values, color=color, alpha=alpha)
        
        PlotHelper.style_axis(ax, title, xlabel, ylabel, grid=True)
        
        # Rotate x-axis labels if vertical bars and many categories
        if not horizontal and len(categories) > 5:
            ax.tick_params(axis='x', rotation=45)
    
    @staticmethod
    def create_horizontal_bar(ax, labels, values, title, xlabel, ylabel=None,
                              color='blue', alpha=0.7, max_label_length=30):
        """
        Create a horizontal bar chart with truncated labels.
        
        Args:
            ax: Matplotlib axis object
            labels: Y-axis labels (will be truncated if too long)
            values: Bar lengths
            title (str): Plot title
            xlabel (str): X-axis label
            ylabel (str, optional): Y-axis label
            color (str): Bar color
            alpha (float): Transparency (0-1)
            max_label_length (int): Maximum label length before truncation
        """
        # Truncate long labels
        truncated_labels = [
            label[:max_label_length] + '...' if len(str(label)) > max_label_length else str(label)
            for label in labels
        ]
        
        y_pos = np.arange(len(labels))
        ax.barh(y_pos, values, color=color, alpha=alpha)
        ax.set_yticks(y_pos)
        ax.set_yticklabels(truncated_labels, fontsize=8)
        ax.invert_yaxis()
        
        PlotHelper.style_axis(ax, title, xlabel, ylabel, grid=True)
