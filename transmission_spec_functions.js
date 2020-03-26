const data = source.data;
const w = data['w']
const rad = data['rad']

const data_lc = source_lc.data
const time = data_lc['t']
const a_o_r = 6.0 // semi-major axis
const b = 0.2 // impact parameter
const period = 24. // orbital period
const u_lin = 0.2 // linear limb darkening

function area_intersect(z_fun,r_fun) {
      if (z_fun >= 1.0 + r_fun) {
            f = 0.0
      } else if (z_fun < 1.0 - r_fun) {
            f = r_fun * r_fun
      } else {
            x1 = (1.0 - r_fun * r_fun + z_fun * z_fun) / (2.0 * z_fun)
            theta1 = Math.acos(x1)
            theta2 = Math.acos((z_fun - x1)/r_fun)
            Aint = theta1 + theta2 * r_fun * r_fun - Math.sqrt(1.0 - x1 * x1) * z_fun
            f = Aint / Math.PI
      }
      return f
}

// approximate limb darkening by ignoring variations over planet
function limb_dark(z_fun,r_fun) {
      C = 1.0 / (1.0 - u_lin / 6.0)
      if (z_fun >= 1.0 + r_fun) {
            f = 1.0
      } else if (z_fun < 1.0) {
            mu = Math.sqrt(1.0 - z_fun * z_fun)
            f = C * (1.0 - u_lin * (1.0 - mu))
      } else {
            f = C * (1.0 - u_lin)
      }
      return f
}

function lcFunction(t_fun, rad_fun) {
      x_proj = a_o_r * Math.sin(t_fun * 2.0 * Math.PI / period)
      y_proj = b * Math.cos(t_fun * 2.0 * Math.PI / period)
      z = Math.sqrt(x_proj * x_proj + y_proj * y_proj)
      r_p_rs = rad_fun / 10.0
      f = 1.0 - area_intersect(z, r_p_rs) * limb_dark(z,r_p_rs)
      return f * 100.0
}

for (var i = 0; i < w.length; i++) {
      rad[i] = r_slider_list[i].value
      
      //const f = data_lc['f ']
      const f = data_lc['f'+' '+String(i)]
      for (var j = 0; j < time.length; j++) {
            f[j] = lcFunction(time[j], rad[i]) - 1.5 * i;
      }
}


source.change.emit();
source_lc.change.emit();

