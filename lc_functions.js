const data = source.data;
const rad = r.value;
const x = data['x']
const y = data['y']

const data_p = source_planet.data;
const r_show = data_p['r'];
const x_p = data_p['x']

const t_now = t.value;
const t_show = data_p['time_now']
const f_show = data_p['flux_now']

r_show[0] = rad * 1.0;
x_p[0] = t_now;
t_show[0] = t_now;
f_show[0] = rad * Math.sin(t_now / 0.5) + 99.5

for (var i = 0; i < x.length; i++) {
    y[i] = rad * Math.sin(x[i] / 0.5) + 99.5;
}

source.change.emit();
source_planet.change.emit();
