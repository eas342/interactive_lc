import numpy as np

from bokeh.layouts import row, column
from bokeh.models import CustomJS, Slider
from bokeh.plotting import figure, output_file, show, ColumnDataSource
import pdb

def light_c(t,aOr=6.,b=0.2,r=0.1,p=24.0):
    x = aOr * np.sin(t * np.pi * 2. / p)
    bp = b *  np.cos(t * np.pi * 2. / p)
    z = np.sqrt(x**2 + bp**2)
    return area_intersect(z,r)
    
def area_intersect(z,r):
    f = np.zeros_like(z)
    outside_pt = (z >= (1. + r))
    f[outside_pt] = 1.0
    
    inside_pt = (z <= (1. - r))
    f[inside_pt] = 1.0 - r**2
    
    intersect_pt = (z > (1.0 -r)) & (z < (1. + r)) 
    if np.sum(intersect_pt) > 0:
        x= (1. - r**2 + z[intersect_pt]**2)/(2. * z[intersect_pt])
        theta1 = np.arccos(x)
        theta2 = np.arccos((z[intersect_pt]-x)/r)
        Aint = theta1 + theta2 * r**2 - np.sqrt(1.0 - x**2) * z[intersect_pt]
        f[intersect_pt] = 1.0 - Aint / np.pi
    return f * 100.

x = np.linspace(-1.5,1.5,512) ## time (hours)
y = light_c(x)#np.zeros_like(x) ## flux
r = [1.0] ## planet radius
marker_size = [2.0] ## size of time marker
time_now = [0.0] ## time of interest
flux_now = [0.0] ## flux of interest
marker_size = [10.0] ## marker size

xCircle = [0.0]
yCircle = [2.0]

source = ColumnDataSource(data=dict(x=x, y=y))
planet_dict = dict(r=r,x=xCircle,y=yCircle,time_now=time_now,flux_now=flux_now,marker_size=marker_size)
source_planet = ColumnDataSource(data=planet_dict)

plot1 = figure(y_range=(97.5, 100.2), plot_width=400, plot_height=400)

plot1.line('x', 'y', source=source, line_width=3, line_alpha=0.6)
plot1.circle('time_now','flux_now',size='marker_size',source=source_planet,color='green')


plot2 = figure(x_range=(-20, 20),y_range=(-20, 20), plot_width=400, plot_height=400)
plot2.circle([0],[0],radius=10,color='yellow')
plot2.circle('x','y',radius='r',source=source_planet,color='black')
#plot2.line('x2', 'y2', source=source_polar, line_width=3, line_alpha=0.6)

t_slider = Slider(start=-1.5, end=1.5, value=0, step=0.01, title='Time')
r_slider = Slider(start=0.0, end=2.0, value=r[0], step=.01, title="Radius (Rjup)")

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
