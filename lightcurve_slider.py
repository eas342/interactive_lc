import numpy as np
import sys
from bokeh.layouts import row, column
from bokeh.models import CustomJS, Slider
from bokeh.plotting import figure, output_file, show, ColumnDataSource
#from bokeh.models import LinearColorMapper
import pdb
import warnings
from json import JSONEncoder

if sys.version_info < (3,5):
    warnings.warn("Use a Python 3.5 or later for better results")

def limb_dark(z,r,u=0.2):
    """ Simple limb darkening law
        Ignores the variations across the planet
    """
    C = 1./ (1. - u/6.)
    
    f = np.zeros_like(z)
    outside_pt = (z >= (1. + r))
    f[outside_pt] = 1.0
    
    inside_pt = (z < 1.0)
    mu = np.sqrt(1. - z[inside_pt]**2)
    f[inside_pt] = C * (1.0 - u * (1. - mu))
    
    intersect_pt = (z >= 1.0) & (z < (1. + r))
    f[intersect_pt] = C * (1. - u)
    
    return f
    

def light_c(t,aOr=6.,b=0.2,r=0.1,p=24.0,u=0.2):
    x = aOr * np.sin(t * np.pi * 2. / p)
    bp = b *  np.cos(t * np.pi * 2. / p)
    z = np.sqrt(x**2 + bp**2)
    Aint = area_intersect(z,r)
    f = 1. - Aint * limb_dark(z,r,u=u)
    return f * 100.
    
def area_intersect(z,r):
    f = np.zeros_like(z)
    outside_pt = (z >= (1. + r))
    f[outside_pt] = 0.0
    
    inside_pt = (z <= (1. - r))
    f[inside_pt] = r**2
    
    intersect_pt = (z > (1.0 -r)) & (z < (1. + r)) 
    if np.sum(intersect_pt) > 0:
        x= (1. - r**2 + z[intersect_pt]**2)/(2. * z[intersect_pt])
        theta1 = np.arccos(x)
        theta2 = np.arccos((z[intersect_pt]-x)/r)
        Aint = theta1 + theta2 * r**2 - np.sqrt(1.0 - x**2) * z[intersect_pt]
        f[intersect_pt] = Aint / np.pi
    return f

class fixed_param(dict):
    def __init__(self,value):
        self.value = value


def lightcurve_slider(free_radius=True,free_impact=False):
    """
    Lightcurve slider to show lightcurve and projected view
    """
    
    
    x = np.linspace(-1.5,1.5,512) ## time (hours)
    y = light_c(x)#np.zeros_like(x) ## flux
    r = [1.0] ## planet radius
    marker_size = [2.0] ## size of time marker
    time_now = [0.0] ## time of interest
    flux_now = light_c(np.array(time_now)) ## flux of interest
    marker_size = [10.0] ## marker size

    xCircle = [0.0]
    yCircle = [2.0]

    axes_font_size = "14pt"

    source = ColumnDataSource(data=dict(x=x, y=y))
    planet_dict = dict(r=r,x=xCircle,y=yCircle,time_now=time_now,flux_now=flux_now,marker_size=marker_size)
    source_planet = ColumnDataSource(data=planet_dict)

    plot1 = figure(y_range=(97.5, 100.2), plot_width=400, plot_height=200)

    plot1.line('x', 'y', source=source, line_width=3, line_alpha=0.6)
    plot1.circle('time_now','flux_now',size='marker_size',source=source_planet,color='green')

    plot1.title.text = 'Lightcurve'
    plot1.xaxis.axis_label = "Time from Central Transit (hours)"
    plot1.yaxis.axis_label = "Brightness (%)"
    plot1.xaxis.axis_label_text_font_size = axes_font_size
    plot1.yaxis.axis_label_text_font_size = axes_font_size

    plot2 = figure(x_range=(-20, 20),y_range=(-20, 20), plot_width=400, plot_height=400)

    
    ## make a limb darkened star
    r_star = 10.0
    u_linear = 0.2 ## linear limb darkening parameter
    img_res = 256
    x_linear = np.linspace(-r_star * 2, r_star * 2, img_res)
    y_linear = np.linspace(-r_star * 2, r_star * 2, img_res)
    xx_grid, yy_grid = np.meshgrid(x_linear, y_linear)
    rr_grid = np.sqrt(xx_grid**2 + yy_grid**2) ## radius
    in_points = rr_grid < r_star ## only the points inside will be calculated
    mu = np.sqrt(r_star**2 - rr_grid[in_points]**2) ##mu
    f_star = np.zeros_like(rr_grid)
    f_star[in_points] = (1.0 - u_linear * (1.0 - mu)) / (1.0 - u_linear / 6.0)
    plot2.image(image=[f_star], x=-2 * r_star, y=-2 * r_star, dw=4 * r_star, dh=4 * r_star, palette="Inferno256", level="image")


    #plot2.circle([0],[0],radius=10,color='yellow')

    plot2.circle('x','y',radius='r',source=source_planet,color='black',line_color='cyan')
    #plot2.line('x2', 'y2', source=source_polar, line_width=3, line_alpha=0.6)
    plot2.xgrid.visible = False
    plot2.ygrid.visible = False
    plot2.xaxis.axis_label = "X Distance (Earth Radii)"
    plot2.yaxis.axis_label = "Y Distance (Earth Radii)"
    plot2.xaxis.axis_label_text_font_size = axes_font_size
    plot2.yaxis.axis_label_text_font_size = axes_font_size
    plot2.title.text = 'Star View'

    t_slider = Slider(start=-1.5, end=1.5, value=0, step=0.01, title='Time from Central Transit (hours)')
    r_slider = Slider(start=0.0, end=1.5, value=r[0], step=.01, title="Radius (Earth Radii)")
    b_slider = Slider(start=0.0, end=1.1, value=0.2, step=0.01, title="Impact Parameter")
    
    sliderList = [t_slider]
    if free_radius == True:
        sliderList.append(r_slider)
    if free_impact == True:
        sliderList.append(b_slider)
    
    with open ("lc_functions.js", "r") as js_file:
        js_code = js_file.read()

    js_args = dict(source=source, source_planet=source_planet, r=r_slider,t=t_slider,b_imp=b_slider)
    callback = CustomJS(args=js_args,
                        code=js_code)
    #    

    #if free_radius == True:
    for oneSlider in sliderList:
        oneSlider.js_on_change('value', callback)
    
    ## Remove the toolbars
    plot1.toolbar_location = None
    plot2.toolbar_location = None

    layout = row(
        column(plot1,plot2),
        column(sliderList),
    )
    
    outName = "slider_free_rad_{}_free_b_{}.html".format(free_radius,free_impact)
    output_file(outName, title="Radius Slider", mode='inline')

    show(layout)

w0 = 0.67

def calc_radii(w,wRange,thickness=0.3):
    """
    Simple function that converts an "atmospheric thickness" to a radius spectrum
    """
    rad = 0.8 - 1.0 * thickness * (w - w0) / wRange
    return rad

def scattering_slider():
    """
    Slider shows the planet, spectrum and lightcurves
    """
    w = np.array([  0.64   ,  0.61    , 0.57  ,   0.53   , 0.47     , 0.41 ])
    posx = np.zeros_like(w)
    posy = np.zeros_like(w)
    wRange = w[0] - w[-1]
    colors_array = np.array([  'red' ,'orange','yellow' ,'green',  'blue',  'violet'])
    thickness = 0.3 ## "atmospheric thickness"
    
    rad_arr = calc_radii(w,wRange,thickness)
    
    axes_font_size = "14pt"
    
    source = ColumnDataSource(data=dict(w=w, rad=rad_arr,posx=posx,posy=posy,colors=colors_array))
    
    plot1 = figure(x_range=(-1.3,1.3),y_range=(-1.3,1.3), plot_width=400, plot_height=400)
    
    plot1.scatter('posx','posy',radius='rad',source=source, line_width=3,
                  fill_color=None,line_color='colors')
    plot1.circle(0.0,0.0,radius=0.8,color='black')
    
    plot1.title.text = 'Planet View'
    plot1.xaxis.axis_label = "X Size (Earth Radii)"
    plot1.yaxis.axis_label = "Y Size (Earth Radii)"
    plot1.xaxis.axis_label_text_font_size = axes_font_size
    plot1.yaxis.axis_label_text_font_size = axes_font_size

    plot2 = figure(y_range=[0.77,1.15],plot_width=400, plot_height=400)
    plot2.line('w','rad',source=source)
    plot2.xaxis.axis_label = "Wavelength (microns)"
    plot2.yaxis.axis_label = "Radius (Earth Radii)"
    plot2.xaxis.axis_label_text_font_size = axes_font_size
    plot2.yaxis.axis_label_text_font_size = axes_font_size
    plot2.scatter('w','rad',source=source,line_width=None,fill_color='colors',size=12)
    
    t_slider = Slider(start=0, end=0.3, value=0.3, step=0.01, title='Atmospheric Thickness')
    
    sliderList = [t_slider]
    
    with open ("scattering_functions.js", "r") as js_file:
        js_code = js_file.read()
    
    js_args = dict(source=source, wRange=wRange,t=t_slider)
    callback = CustomJS(args=js_args,
                        code=js_code)
    
    for oneSlider in sliderList:
        oneSlider.js_on_change('value', callback)
    
    ## Remove the toolbars
    plot1.toolbar_location = None
    plot2.toolbar_location = None

    layout = row(
        column(plot1,plot2),
        column(sliderList),
    )

    output_file("slider_scattering.html", title="Radius Slider", mode='inline')

    show(layout)

if __name__ == "__main__":
    lightcurve_slider()
