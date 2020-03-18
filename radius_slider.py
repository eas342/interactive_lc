import numpy as np

from bokeh.layouts import row, column
from bokeh.models import CustomJS, Slider
from bokeh.plotting import figure, output_file, show, ColumnDataSource
import pdb

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

x = np.linspace(-1.5,1.5,512) ## time (hours)
y = light_c(x)#np.zeros_like(x) ## flux
r = [1.0] ## planet radius
marker_size = [2.0] ## size of time marker
time_now = [0.0] ## time of interest
flux_now = [0.0] ## flux of interest
marker_size = [10.0] ## marker size

xCircle = [0.0]
yCircle = [2.0]

axes_font_size = "16pt"

source = ColumnDataSource(data=dict(x=x, y=y))
planet_dict = dict(r=r,x=xCircle,y=yCircle,time_now=time_now,flux_now=flux_now,marker_size=marker_size)
source_planet = ColumnDataSource(data=planet_dict)

plot1 = figure(y_range=(97.5, 100.2), plot_width=400, plot_height=400)

plot1.line('x', 'y', source=source, line_width=3, line_alpha=0.6)
plot1.circle('time_now','flux_now',size='marker_size',source=source_planet,color='green')

plot1.xaxis.axis_label = "Time from Central Transit (hours)"
plot1.yaxis.axis_label = "Relative Brightness (%)"
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

plot2.circle('x','y',radius='r',source=source_planet,color='black',line_color='blue')
#plot2.line('x2', 'y2', source=source_polar, line_width=3, line_alpha=0.6)
plot2.xgrid.visible = False
plot2.ygrid.visible = False
plot2.xaxis.axis_label = "X Size (Earth Radii)"
plot2.yaxis.axis_label = "Y Size (Earth Radii)"
plot2.xaxis.axis_label_text_font_size = axes_font_size
plot2.yaxis.axis_label_text_font_size = axes_font_size

t_slider = Slider(start=-1.5, end=1.5, value=0, step=0.01, title='Time')
r_slider = Slider(start=0.0, end=2.0, value=r[0], step=.01, title="Radius (Earth Radii)")

with open ("lc_functions.js", "r") as js_file:
    js_code = js_file.read()

callback = CustomJS(args=dict(source=source, source_planet=source_planet, r=r_slider,t=t_slider),
                    code=js_code)
#    


r_slider.js_on_change('value', callback)
t_slider.js_on_change('value', callback)

## Remove the toolbars
plot1.toolbar_location = None
plot2.toolbar_location = None

layout = row(
    plot1,plot2,
    column(t_slider,r_slider),
)

output_file("slider_radius.html", title="Radius Slider", mode='inline')

show(layout)
