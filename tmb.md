---
layout: trekking
title: TMB 
title_long: Tour du Mont Blanc - 2022
tag: tmb
permalink: /tmb/
order: 3
---

Half done unfortunately ;)

You can check the map below:

{% leaflet_map {"zoom" : 10,
                "center": [45.8414835, 6.878885000000001],
                "divId" : "map_size" } %}
    {% leaflet_geojson "/assets/tmb/tmb.geojson" %}
{% endleaflet_map %}

<br />
