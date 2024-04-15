import random
import uuid

import mesa
import mesa_geo as mg

from .agents import PersonAgent, RegionAgent
from .space import CensusTract


class GeoSchellingPoints(mesa.Model):
    def __init__(
        self, 
        red_percentage=0.5, 
        similarity_threshold=0.5,
        seed=None,
    ):
        
        super().__init__(seed=seed)
        self.red_percentage = red_percentage
        PersonAgent.SIMILARITY_THRESHOLD = similarity_threshold

        self.schedule = mesa.time.RandomActivation(self)
        self.space = CensusTract()

        self.datacollector = mesa.DataCollector(
            {"unhappy": "unhappy", "happy": "happy"}
        )

        # Set up the grid with patches for census tract
        ac = mg.AgentCreator(RegionAgent, model=self)
        regions = ac.from_file(
            "data/nyct2020manhattan.geojson", unique_id="GEOID"
        )
        self.space.add_regions(regions)
        
        
        # Set up agents
        # Iterate through regions (Census Tract)
        # For each region, place init_num_people of People agents
        # Within 
        for region in regions:
            for _ in range(region.init_num_people):
                person = PersonAgent(
                    unique_id=uuid.uuid4().int,
                    model=self,
                    crs=self.space.crs,
                    geometry=region.random_point(),
                    is_red=random.random() < self.red_percentage,
                    region_id=region.unique_id,
                )
                self.space.add_person_to_region(person, region_id=region.unique_id)
                self.schedule.add(person)

        self.datacollector.collect(self)

    @property
    #Check the # of unhappy people agents in the model
    def unhappy(self):
        num_unhappy = 0
        for agent in self.space.agents:
            if isinstance(agent, PersonAgent) and agent.is_unhappy:
                num_unhappy += 1
        return num_unhappy

    @property
    #Check the # of happy people agents in the model
    def happy(self):
        return self.space.num_people - self.unhappy

    def step(self):
        self.schedule.step()
        self.datacollector.collect(self)

        if not self.unhappy:
            self.running = False
