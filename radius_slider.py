import numpy as np

from bokeh.layouts import row, column
from bokeh.models import CustomJS, Slider
from bokeh.plotting import figure, output_file, show, ColumnDataSource

x = np.linspace(-5.,5,512) ## time (hours)
y = np.zeros_like(x) ## flux
r = np.array([0.0]) ## planet radius

xCircle = np.array([0.0])
yCircle = np.array([0.0])

source = ColumnDataSource(data=dict(x=x, y=y))
source_r = ColumnDataSource(data=dict(r=r,x=xCircle,y=yCircle))

plot1 = figure(y_range=(-10, 10), plot_width=400, plot_height=400)

plot1.line('x', 'y', source=source, line_width=3, line_alpha=0.6)

plot2 = figure(x_range=(-10, 10),y_range=(-10, 10), plot_width=400, plot_height=400)
plot2.circle([-5],[0],radius=10,color='yellow')
plot2.circle('x','y',radius='r',source=source_r,color='black')
#plot2.line('x2', 'y2', source=source_polar, line_width=3, line_alpha=0.6)

r_slider = Slider(start=0.0, end=10, value=0, step=.1, title="Radius (Rjup)")

callback = CustomJS(args=dict(source=source, source_r=source_r, r=r_slider),
                    code="""
    const data = source.data;
    const rad = r.value;
    const x = data['x']
    const y = data['y']
    const data_r = source_r.data;
    const r_show = data_r['r'];
    
    for (var i = 0; i < x.length; i++) {
        y[i] = rad * Math.sin(x[i] / 0.5) + 3;
    }
    r_show[0] = rad * 1.0;
    
    source.change.emit();
    source_r.change.emit();
""")
#    


#    const r_show = data_r['r'];
#        y[i] = rad*Math.sin(x[i] * 0.5) + 3;

#     const data = source.data;
#     const A = 1.0;
#     const k = 1.0;
#     const phi = 0.0;
#     const B = 1.0;
#     const x = data['x']
#     const y = data['y']
#
#     for (var i = 0; i < x.length; i++) {
#         y[i] = B + A*Math.sin(k*x[i]+phi);
#     }
#     source.change.emit();
# """)



r_slider.js_on_change('value', callback)

layout = row(
    plot1,plot2,
    column(r_slider),
)

output_file("slider_radius.html", title="Radius Slider", mode='inline')

show(layout)
