---
layout: trekking
title: Switzerland
title_long: Switzerland
tag: switzerland
permalink: /switzerland/
order: 7
---

{% leaflet_map {"zoom" : 7,
"center": [46.8307, 8.5265],
"divId" : "map_size" } %}
{% leaflet_geojson "/assets/switzerland/switzerland.geojson" %}
{% endleaflet_map %}
<br />
