---
layout: strava_post
title: "TMB #8 Test Pavia"
date: 2022-10-03 13:48:17 +0200
assets_folder: /assets/tmb/2022-10-3-tmb-8-test-pavia
tags: tmb hiking
thumbnail: /assets/thumbnail.jpg
visible: 1
---
[//]: # "TMB #8 Test Pavia"


{% leaflet_map {"zoom" : 13,
                  "center": [45.215736, 9.157566],
                 "divId" : "map_size" } %}
    {% leaflet_geojson "/assets/tmb/2022-10-3-tmb-8-test-pavia/gps_data.geojson" %}

{% endleaflet_map %}





{% include strava_table.html distance="18.93" elevation_gain="96" moving_time="3:25:16" elapsed_time="3:47:50" %}

[![](/assets/strava.jpg)](https://www.strava.com/activities/7910103296)



[//]: # ( ![image tooltip here](/assets/image.png) )