#!/usr/bin/env python

import random
import numpy
import sys
import copy

class Organism:
  '''A class to contain an organism'''
  def __init__(self, cellID, ai_prob = 0.5, coop_prob = 0.5, neigh_prop = 0.6, parent=None, empty=False, lineage = -1):
    self.age = 0
    self.generation = 0
    self.ai_prob = ai_prob
    self.coop_prob = coop_prob
    self.neigh_prop = neigh_prop
    self.ai_produce = False
    self.empty = empty
    self.ID = cellID
    self.lineage = lineage
    self.repo_age = 0
    self.points = 0
    if not self.empty:
      if parent:
        self.ai_prob = parent.ai_prob
        self.coop_prob = parent.coop_prob
        self.neigh_prop = parent.neigh_prop
        self.mutate()
        self.repo_age = parent.age
        self.lineage = parent.lineage
        parent.generation += 1
        parent.repo_age = parent.age
        self.generation = parent.generation
        parent.mutate()
        parent.points = 0
        parent.age = 0
      else:
        #If this organism isn't being mutated, we need to set it's ai_produce here
        self.ai_produce = (random.random() < self.ai_prob)
        if self.ai_produce:
          self.points = signal_cost
        
  def __repr__(self):
    # Using string formatting
    return "empty: {}, ID: {}, points: {}\n".format(self.empty, self.ID,  self.points)

  def update(self):
    '''Determines if organism cooperates and gives public good to neighbors'''
    if not self.empty:
      self.age += 1
      self.points += 1
      if (random.random() < self.coop_prob):
        #organism will test whether there are enough ai neighbors to produce
        neighbors = self.findNeighbors()
        neighbor_ai = 0.0
        for neighbor_id in neighbors:
          if population_orgs.orgs[neighbor_id].ai_produce:
            neighbor_ai += 1
        if (neighbor_ai/8.0) >= self.neigh_prop:
          #produce the public good!
          self.points += production_cost
          for neighbor_id in neighbors:
            population_orgs.orgs[neighbor_id].points += public_good_points
          
      

  def mutate(self):
    if mutation_sd:
      self.ai_prob = numpy.random.normal(self.ai_prob, mutation_sd)
      self.coop_prob = numpy.random.normal(self.coop_prob, mutation_sd)
      self.neigh_prop = numpy.random.normal(self.neigh_prop, mutation_sd)
      
    #will this organism be a signaler based on new ai_prob?
    self.ai_produce = (random.random() < self.ai_prob)
    if self.ai_produce:
      self.points = signal_cost


    
      
  def findNeighbors(self):
    cellID = self.ID
    radius = 1
    world_x = pop_x
    world_y = pop_y
    cell_x = cellID % world_x
    cell_y = (cellID - cell_x)/world_x
    neighbor_ids = []
    for i in range(cell_x-radius, cell_x+radius+1):
      for j in range(cell_y-radius, cell_y+radius+1):
        if i<0:
          x = world_x + i
        elif i>=world_x:
          x = i-world_x
        else:
          x = i

        if j<0:
          y = world_y + j
        elif j>=world_y:
          y = j-world_y
        else:
          y = j

        neighbor_ids.append(y*world_x+x)

    return neighbor_ids

        
class Population:
  '''A class to contain the population and do stuff'''
  def __init__(self, popsize, ancestor = "default"):
    self.currentUpdate = 0
    self.orgs = []
    self.pop_size = popsize
    

    for i in range(popsize):
      if i%2 == 0:
        self.orgs.append(self.makeOrg("defector"))
      else:
        self.orgs.append(self.makeOrg("wt"))


  def makeOrg(self, org_type = "default"):
    '''A function to make a new organism based on type
    default = AI 0.5 Coop_Prob 0.5 Neigh_Prop 0.6
    wt = AI 1.0 Coop_Prob 0.1 Neigh_Prop 0.6
    unconditional = AI 0 Coop_Prob 0.1 Neigh_Prop 0
    defector = AI 0 Coop_Prob 0.0 Neigh_Prop 1.0'''
    if org_type == "default":
      newOrg = Organism(len(self.orgs), lineage = 0)
    elif org_type == "wt":
      newOrg = Organism(len(self.orgs), ai_prob = 1.0, coop_prob = 0.5, neigh_prop = 0.6)
    elif org_type == "unconditional":
      newOrg = Organism(len(self.orgs), ai_prob = 0.0, coop_prob = 0.5, neigh_prop = 0.0)
    elif org_type == "defector":
      newOrg = Organism(len(self.orgs), ai_prob = 0.0, coop_prob = 0.0, neigh_prop = 1.0)
    return newOrg

  def reproduceOrg(self, org):
    '''A helper function to reproduce a host organism.'''
    ## Time to reproduce
    ## Returns list of neighbor indices
    dead_neighbor = False
    neighbors = org.findNeighbors()
    for ID in neighbors:
      if self.orgs[ID].empty:
        dead_neighbor = ID
        break
    if dead_neighbor:
      position = dead_neighbor
    else:
      position = random.choice(neighbors)
    newOrg = Organism(position, parent = org)

    self.orgs[position] = newOrg

  def update(self):
    '''A function that runs a single update'''
    self.currentUpdate+=1
    for org in self.orgs:
      if not org.empty:
        result = org.update()
        if org.points >= 10:
          self.reproduceOrg(org)

  def recordStats(self):
    '''A function to calculate the average ai_prob, coop_prob, and neigh_prop in the population'''
    total = 0
    ai_prob_sum = 0.0
    coop_prob_sum = 0.0
    neigh_prop_sum = 0.0
    repo_age_sum = 0.0
    for org in self.orgs:
      if not org.empty:
        ai_prob_sum += org.ai_prob
        coop_prob_sum += org.coop_prob
        neigh_prop_sum += org.neigh_prop
        repo_age_sum += org.repo_age
        total+=1

    return (ai_prob_sum/total), (coop_prob_sum/total), (neigh_prop_sum/total), (repo_age_sum/total)


if len(sys.argv) < 4 or sys.argv[1] == "--help":
  print "usage: pop_x pop_y seed mutation_sd"
else:

  seed = int(sys.argv[3])
  random.seed(seed)
  numpy.random.seed(seed)
  filename = "comp_def_wt_"
  num_updates = 100000
  pop_x = int(sys.argv[1])
  pop_y = int(sys.argv[2])
  pop_size = pop_x*pop_y
  mutation_sd = float(sys.argv[4])
  ancestor = "default" #this isn't being used in competitions
  signal_cost = -1
  production_cost = -5
  public_good_points = 4.9

  data_file = open(filename+str(seed)+".dat", 'w')
  data_file.write("Update AI_Prob Coop_Prob Num_Neigh Avg_Repo_Age\n")
  data_file.close()
  population_orgs = Population(pop_size, ancestor)

  for u in range(num_updates):

    population_orgs.update()
    if u%100 == 0:

      #grab current averages
      ai_prob, coop_prob, neigh_prop, age_avg = population_orgs.recordStats()
      print "Update: ", u, " AI Prob: ", ai_prob, " Coop Prob: ", coop_prob, " Neighbor Prop: ", neigh_prop, " Avg Repo Age: ", age_avg
      data_file = open(filename+str(seed)+".dat", 'a')
      data_file.write('{} {} {} {} {}\n'.format(u, ai_prob, coop_prob, neigh_prop, age_avg))
      data_file.close()







