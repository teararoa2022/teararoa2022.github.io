---
layout: strava_post
title:  "First Hike"
date:   2022-08-11 14:40:39 +0200
gps_data: ""
categories: jekyll update
tags: hiking teararoa
visible: 1
---
# Test
{% leaflet_map {"zoom" : 13 } %}
    {% leaflet_marker {"latitude" : 34.296184,
                       "longitude" : -117.211329,
                       "popupContent": "Arrowhead Pinacles Trail"} %} 
    {% leaflet_geojson "/assets/Afternoon_Hike.geojson" %}

{% endleaflet_map %}

{% leaflet_map { "center" : [63.0694,  -151.0074],
                 "zoom" : 7,
                 "providerBasemap": "OpenTopoMap" } %}
    {}
{% endleaflet_map %}
