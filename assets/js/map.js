Array.prototype.stepSlice = function(b,e,s) {
    var n=[];
    for (var i=b; i<e; i+=s) {
        n.push(this[i]);
    }
    return n;
}

let sum = (array) => {
    let sum_ = 0
    for (let i=0; i<array.length; i+=1) {
        sum_ += array[i]
    }
    return sum_
}

let mean = (array) => {
    return sum(array) / array.length
}

let gps_data_location = document.getElementsByName('JSONData')[0].content;
console.log(gps_data_location)


const add_gps_data = async file => {
    const response = await fetch(file)
    const text = await response.text()
    const json = await JSON.parse(text)
    let points = await json['latlng']
    const resample_ratio = Math.max(Math.floor(points.length/200), 1)
    points = points.stepSlice(1, points.length, resample_ratio)
    L.polyline(points, {color: 'red'}).addTo(mymap);

    const lef = await points.map(point => L.point(point[0], point[1]))
    // lef.forEach(point => L.marker([point.x, point.y]).addTo(mymap))

    const x_points = lef.map(x => x.x)
    const y_points = lef.map(x => x.y)
    mymap.setView([mean(x_points), mean(y_points)], 11)
}


var mymap = L.map('mapid').setView([51.505, -0.09], 13);
L.tileLayer('https://api.mapbox.com/styles/v1/{id}/tiles/{z}/{x}/{y}?access_token={accessToken}', {
    attribution: 'Map data &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors, Imagery © <a href="https://www.mapbox.com/">Mapbox</a>',
    maxZoom: 18,
    id: 'mapbox/streets-v11',
    tileSize: 512,
    zoomOffset: -1,
    accessToken: 'pk.eyJ1IjoiZGVhdGlub3IiLCJhIjoiY2tpendodHo4MWM4MTJ0bngyaGxuZ3l0bSJ9.DNxxPJXPTTeCyqTCRJeDYQ\n'
}).addTo(mymap);
