const data = source.data;
const thickness = t.value
const w = data['w']
const w_0 = 0.67
const w_range = w[0] - w[w.length-1]
const rad = data['rad']

function radius_spec(w,thickness) {
      r = 0.8 - 1.0 * thickness * (w - w_0) / w_range
      
      return r
}

for (var i = 0; i < w.length; i++) {
    rad[i] = radius_spec(w[i],thickness)
}

source.change.emit();

