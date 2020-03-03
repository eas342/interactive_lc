const data = source.data;
const rad = r.value;
const x = data['x']
const y = data['y']

const data_p = source_planet.data;
const r_show = data_p['r'];
const x_p = data_p['x']
const y_p = data_p['y']

const t_now = t.value;
const t_show = data_p['time_now']
const f_show = data_p['flux_now']
const a_o_r = 6.0
const b = 0.2
const period = 24.

function lcFunction(x_fun, rad_fun) {
      return 0.1 * rad_fun * Math.sin(x_fun/ 0.5) + 99.5
}

r_show[0] = rad * 1.0;
x_p[0] = Math.sin(t_now * 6.28 / period) * a_o_r * 10.0;
y_p[0] = Math.cos(t_now * 6.28 / period) * b * 10.0;
t_show[0] = t_now;
f_show[0] = lcFunction(t_now, rad);

for (var i = 0; i < x.length; i++) {
    y[i] = lcFunction(x[i], rad);
}

source.change.emit();
source_planet.change.emit();
