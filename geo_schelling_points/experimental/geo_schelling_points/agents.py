import random

import mesa_geo as mg
from shapely.geometry import Point


class PersonAgent(mg.GeoAgent):
    SIMILARITY_THRESHOLD = 0.3

    def __init__(self, unique_id, model, geometry, crs, is_red, region_id):
        super().__init__(unique_id, model, geometry, crs)
        self.is_red = is_red
        self.region_id = region_id

    @property
    #Check if a people agent is unhappy 
    def is_unhappy(self):
        if self.is_red:
            return (
                self.model.space.get_region_by_id(self.region_id).red_pct
                < self.SIMILARITY_THRESHOLD
            )
            
            #(Pending) Need to check against the region agent to determine happiness 
            # like 
            # self.model.space.get_region_by_id(self.region_id).housing_quality
            # < self.SIMILARITY_THRESHOLD
        else:
            return (
                1 - self.model.space.get_region_by_id(self.region_id).red_pct
            ) < self.SIMILARITY_THRESHOLD

    def step(self):
        if self.is_unhappy:
            random_region_id = self.model.space.get_random_region_id()
            #new_region_id = self.model.space.get_new_region_id()
            #Need a space method that will get id for a region that has a certain level of income/afforability
            self.model.space.remove_person_from_region(self)
            self.model.space.add_person_to_region(self, region_id=random_region_id)


class RegionAgent(mg.GeoAgent):
    init_num_people: int
    red_cnt: int
    blue_cnt: int
    #REINVESTMENT_THRESHOLD = int
    #Renovated_housing_quality = float

    def __init__(self, unique_id, model, geometry, crs, init_num_people=5):
        super().__init__(unique_id, model, geometry, crs)
        self.init_num_people = init_num_people
        self.red_cnt = 0
        self.blue_cnt = 0
        #self.housing_quality = 0 

    @property
    def red_pct(self):
        if self.red_cnt == 0:
            return 0
        elif self.blue_cnt == 0:
            return 1
        else:
            return self.red_cnt / (self.red_cnt + self.blue_cnt)

    def random_point(self):
        min_x, min_y, max_x, max_y = self.geometry.bounds
        while not self.geometry.contains(
            random_point := Point(
                random.uniform(min_x, max_x), random.uniform(min_y, max_y)
            )
        ):
            continue
        return random_point

    def add_person(self, person):
        if person.is_red:
            self.red_cnt += 1
        else:
            self.blue_cnt += 1

    def remove_person(self, person):
        if person.is_red:
            self.red_cnt -= 1
        else:
            self.blue_cnt -= 1
            
    #def renovate(self):
    #   if self.housing_quality < REINVESTMENT_THRESHOLD:
    #       self.housing_quality = Renovated_housing_quality
