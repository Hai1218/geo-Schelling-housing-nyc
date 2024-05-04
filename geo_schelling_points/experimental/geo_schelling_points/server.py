import mesa
import mesa_geo as mg
import xyzservices.providers as xyz
from .agents import PersonAgent, RegionAgent
from .model import GeoSchellingPoints



class HappyElement(mesa.visualization.TextElement):
    def render(self, model):
        return f"Happy agents: {model.happy}"


class MovementElement(mesa.visualization.TextElement):
    def render(self, model):
        return f"Total movements: {model.movement}"


model_params = {
    "rent_discount": mesa.visualization.Slider("% Discount", 0.1, 0.2, 0,3, 0.4),
}


def schelling_draw(agent):
    portrayal = {}
    if isinstance(agent, RegionAgent):
        if agent.housing_quality > 80:
            portrayal["color"] = "Blue"
        elif agent.housing_quality < 40:
            portrayal["color"] = "Red"
        else:
            portrayal["color"] = "Grey"
    elif isinstance(agent, PersonAgent):
        portrayal["radius"] = 1
        portrayal["shape"] = "circle"
        portrayal["color"] = "Red" if agent.income_level < 0.3 else "Blue"
    return portrayal


happy_element = HappyElement()
movement_element = MovementElement()
map_element = mg.visualization.MapModule(
    schelling_draw, tiles=xyz.CartoDB.Positron
)
happy_chart = mesa.visualization.ChartModule(
    [
        {"Label": "unhappy", "Color": "Orange"},
        {
            "Label": "happy",
            "Color": "Green",
        },
    ]
)
server = mesa.visualization.ModularServer(
    GeoSchellingPoints,
    [map_element, happy_element, movement_element, happy_chart],
    "Schelling",
    model_params,
)
