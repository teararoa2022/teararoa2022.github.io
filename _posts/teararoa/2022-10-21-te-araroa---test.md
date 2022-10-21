---
layout: strava_post
title: "Te Araroa - test!!"
date: 2022-10-21 03:06:45 +0200
assets_folder: /assets/teararoa/2022-10-21-te-araroa---test
tags: teararoa hiking
thumbnail: /assets/thumbnail.jpg
comments: true
visible: 1
---


{% leaflet_map {"zoom" : 12,
                  "center": [-36.845839999999995, 174.7691965],
                 "divId" : "map_size" } %}
    {% leaflet_geojson "/assets/teararoa/2022-10-21-te-araroa---test/gps_data.geojson" %}

{% endleaflet_map %}





{% include strava_table.html distance="1.25" elevation_gain="8" moving_time="0:11:55" elapsed_time="0:13:16" %}

[![](/assets/strava.jpg)](https://www.strava.com/activities/7996199549)

