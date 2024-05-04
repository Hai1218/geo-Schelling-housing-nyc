import random
import uuid
import mesa
import mesa_geo as mg
import numpy as np

from .agents import PersonAgent, RegionAgent
from .space import CensusTract


class GeoSchellingPoints(mesa.Model):
    def __init__(self, 
                 rent_discount=0.5, 
                 ):
        super().__init__()

        self.schedule = mesa.time.RandomActivation(self)
        self.space = CensusTract()
        self.datacollector = mesa.DataCollector(
            {"happy": "happy", "movement": "movement"}
        )


        # Set up the grid with patches for every census tract
        ac = mg.AgentCreator(RegionAgent, model=self)
        regions = ac.from_file(
            "data/nyct2020manhattan.geojson", unique_id="GEOID"
        )
        
        for region in regions:
            region.rent_regulated = random.choice([True, False])
            region.initial_quality = random.uniform(50, 10)

        self.space.add_regions(regions)
           
        for region in regions:
            for _ in range(region.init_num_people):
                person = PersonAgent(
                    unique_id=uuid.uuid4().int,
                    model=self,
                    crs=self.space.crs,
                    geometry=region.random_point(),
                    income_level=np.random.beta(2.5, 3.5),
                    region_id=region.unique_id,
                )
                self.space.add_person_to_region(person, region_id=region.unique_id)
                self.schedule.add(person)

        self.datacollector.collect(self)

    @property
    def unhappy(self):
        num_unhappy = 0
        for agent in self.space.agents:
            if isinstance(agent, PersonAgent) and agent.happiness == False:
                num_unhappy += 1
        return num_unhappy

    @property
    def happy(self):
        return self.space.num_people - self.unhappy
    

    @property
    def movement(self):
        num_movement = 0
        for agent in self.space.agents:
            if isinstance(agent, PersonAgent):
                num_movement += agent.move_count
        return num_movement

    @property
    def happy(self):
        return self.space.num_people - self.unhappy

    def step(self):
        self.schedule.step()
        self.datacollector.collect(self)

        if not self.unhappy:
            self.running = False
