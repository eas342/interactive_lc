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

function area_intersect(z_fun,r_fun) {
      if (z_fun >= 1.0 + r_fun) {
            f = 1.0
      } else if (z_fun <= 1.0 - r_fun) {
            f = 1.0 - (r_fun * r_fun)
      } else {
            x1 = (1.0 - r_fun * r_fun + z_fun * z_fun) / (2.0 * z_fun)
            theta1 = Math.acos(x1)
            theta2 = Math.acos((z_fun - x1)/r_fun)
            Aint = theta1 + theta2 * r_fun * r_fun - Math.sqrt(1.0 - x1 * x1) * z_fun
            f = 1.0 - Aint / Math.PI
      }
      return f
}

function lcFunction(t_fun, rad_fun) {
      x_proj = a_o_r * Math.sin(t_fun * 2.0 * Math.PI / period)
      y_proj = b * Math.cos(t_fun * 2.0 * Math.PI / period)
      z = Math.sqrt(x_proj * x_proj + y_proj * y_proj)
      return area_intersect(z, rad_fun / 10.0) * 100.0
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
