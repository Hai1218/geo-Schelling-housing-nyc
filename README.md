# GeoSchelling Model (Points & Polygons)

### Adopted from GeoSchelling Points
[![](https://img.youtube.com/vi/iLMU6jfmir8/0.jpg)](https://www.youtube.com/watch?v=iLMU6jfmir8)

## Summary

This is a gis integrated version of a simplified Schelling example. 

### GeoSpace

Census Tracts 2020 of New York County (Manhattan)
![](/geo_schelling_points/data/demo.png)

### GeoAgent

As this crude version is adopted from a simplied geoschelling model - the current form jas 2 types of agents but they need to be modify to minic housing and population dynamic. 

As it stands, the two types of GeoAgents are: people(Points) and regions(Census Tract). Each person resides in a randomly assigned region, and checks the color ratio of its region against a pre-defined "happiness" threshold at every time step. If the ratio falls below a certain threshold (e.g., 40%), the agent is found to be "unhappy", and randomly moves to another region. People are represented as points, with locations randomly chosen within their regions. The color of a region depends on the color of the majority population it contains (i.e., point in polygon calculations).

## How to run
To run the model interactively, run `mesa runserver` in this directory. e.g.

```bash
mesa runserver
```

Then open your browser to [http://127.0.0.1:8521/](http://127.0.0.1:8521/) and press `Start`.
