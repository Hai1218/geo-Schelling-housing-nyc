import random
import numpy as np
import mesa_geo as mg
from shapely.geometry import Point


class PersonAgent(mg.GeoAgent):
    def __init__(self, unique_id, model, geometry, crs, income_level, region_id):
        super().__init__(unique_id, model, geometry, crs)
        self.income_level = income_level
        self.region_id = region_id
        self.move_count = 0
        self.happiness = True
        self.is_displaced = False
        self.displacement_count = 0

    @property
    def housing_quality_threshold(self):
        return 0.3 + 0.05 * self.income_level

    @property
    def maximum_affordable_rent(self):
        return 500 + 20 * self.income_level

    def step(self):
        current_region = self.model.space.get_region_by_id(self.region_id)
        if current_region.housing_quality < self.housing_quality_threshold or \
           current_region.rent_price > self.maximum_affordable_rent:
            self.happiness = False
        else:
            self.happiness = True

        if not self.happiness:
            self.move_to_suitable_region()

    def move_to_suitable_region(self):
        # Look for a suitable region
        suitable_regions = [region for region in self.model.space.regions if
                            region.housing_quality >= self.housing_quality_threshold and
                            region.rent_price <= self.maximum_affordable_rent]
        if suitable_regions:
            new_region = random.choice(suitable_regions)
            self.model.space.remove_person_from_region(self)
            self.model.space.add_person_to_region(self, new_region.unique_id)
            self.move_count += 1
            self.region_id = new_region.unique_id
            self.update_happiness()
        else:
            self.is_displaced = True
            self.displacement_count += 1

    def update_happiness(self):
        self.happiness = True



class RegionAgent(mg.GeoAgent):
    init_num_people: int
    num_people : int
    def __init__(self, 
                 unique_id, 
                 model, 
                 geometry, 
                 crs, 
                 init_num_people=5,
                 rent_regulated = True, 
                 rent_discount=0.1, 
                 base_decay_constant=0.01, 
                 decay_differential=0.005):
        

        super().__init__(unique_id, 
                         model, 
                         geometry, 
                         crs 
                         )
        self.init_num_people = init_num_people
        self.num_people = self.init_num_people
        self.rent_regulated = random.choice([True, False])
        self.initial_quality = random.uniform(50, 100)
        self.housing_quality = self.initial_quality
        self.renovations = 0
        # Set decay constants based on whether the region is rent-regulated
        if self.rent_regulated:
            self.decay_constant = base_decay_constant
        else:
            self.decay_constant = base_decay_constant + decay_differential
        self.steps = 0  # Initialize a step counter


    @property
    def average_ami(self):
        # Calculate the average AMI including neighboring regions
        self_and_neighbors = [self] + list(self.model.space.get_neighbors(self, radius=1000, include_agents=False))
        all_residents = []
        for region in self_and_neighbors:
            all_residents.extend(self.model.space.get_agents_within_region(region))
        
        if all_residents:
            return np.mean([resident.income_level for resident in all_residents])
        return 0

    def random_point(self):
        min_x, min_y, max_x, max_y = self.geometry.bounds
        while not self.geometry.contains(
            random_point := Point(
                random.uniform(min_x, max_x), random.uniform(min_y, max_y)
            )
        ):
            continue
        return random_point
       
    def rent_price(self):
        # Calculate rent price, applying a discount if the region is rent regulated
        base_rent = 500 + 10 * self.average_ami
        return base_rent * (1 - self.rent_discount) if self.rent_regulated else base_rent
    
    def step(self):
        # Increment step counter
        self.steps += 1
        # Calculate exponential decay
        self.housing_quality = self.initial_quality * np.exp(-self.decay_constant * self.steps)
        if self.housing_quality <= 10:  # Assuming a threshold for renovation
            self.renovate()

    def renovate(self):
        # Resets housing quality and increments renovations counter
        self.housing_quality = self.initial_quality
        self.renovations += 1
        self.steps = 0  # Reset step counter after renovation

    def get_neighbors(self, distance):
        # Find neighboring regions within a certain distance
        return self.model.space.get_neighbors(self, distance, include_agents=False)
    
    def add_person(self, person):
        self.num_people += 1

    def remove_person(self, person):
        self.num_people -= 1
