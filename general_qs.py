#!/usr/bin/env python

import random
import numpy
import sys
import argparse
import copy

class Organism:
  '''A class to contain an organism'''
  def __init__(self, cellID, ai_prob = 0.5, coop_prob = 0.5, neigh_prop = 0.6, parent=None, empty=False, lineage = 'evolvable'):
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
      population_orgs.select_dict[self.lineage] += 1
      if (random.random() < self.coop_prob):
        #organism will test whether there are enough ai neighbors to produce
        neighbors = self.findNeighbors()
        neighbor_ai = 0.0
        for neighbor_id in neighbors:
          if population_orgs.orgs[neighbor_id].ai_produce:
            neighbor_ai += 1
        if (neighbor_ai/8.0) >= self.neigh_prop:
          self.points += production_cost
          #tell the population that public good was produced and should be given to neighbors
          return neighbors
          
      

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
        if i == cell_x and j == cell_y:
          ##This means that both reproduction and public goods won't consider the focal organism, perhaps not ideal, unsure
          continue
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
  def __init__(self, popsize, proportions):
    assert sum(proportions.values())<=1.0, "Proportions of starting organisms can't exceed 1.0"
    self.currentUpdate = 0
    self.orgs = []
    self.pop_size = popsize
    #dictionary to count the bonuses and costs for each type of organism
    self.select_dict = {'defector':0, 'wt':0, 'uncond':0, 'empty':0}

    
    non_empty = 0
    for i in range(popsize):
      number = random.random()
      non_empty += 1
      if number < proportions['wt']:
        self.orgs.append(self.makeOrg("wt"))
      elif number < proportions['wt']+proportions['defector']:
        self.orgs.append(self.makeOrg("defector"))
      elif number < (proportions['wt']+proportions['defector']+proportions['unconditional']):
        self.orgs.append(self.makeOrg("unconditional"))
      elif number < (proportions['wt']+proportions['defector']+proportions['unconditional']+proportions['ancestor']):
        self.orgs.append(self.makeOrg("ancestor"))
      else:
        self.orgs.append(self.makeOrg("empty"))
        non_empty -=1
      self.select_dict[self.orgs[-1].lineage] += self.orgs[-1].points
                      
    if non_empty < 1:
      #seed with an organism from the group with highest proportion or the ancestor if all are zero
      max_key = max(proportions, key=proportions.get)
      if proportions[max_key] == 0.0:
        self.orgs[0] = self.makeOrg("ancestor")
      else:
        self.orgs[0]= (self.makeOrg(max_key))
      self.select_dict[self.orgs[-1].lineage] += self.orgs[-1].points
                        


  def makeOrg(self, org_type = "ancestor"):
    '''A function to make a new organism based on type
    ancestor = AI 0.0 Coop_Prob 0.0 Neigh_Prop 0.0
    wt = AI 1.0 Coop_Prob 0.1 Neigh_Prop 0.6
    unconditional = AI 0 Coop_Prob 0.1 Neigh_Prop 0
    defector = AI 0 Coop_Prob 0.0 Neigh_Prop 1.0'''
    if org_type == "ancestor":
      newOrg = Organism(len(self.orgs), ai_prob = 0.0, coop_prob = 0.0, neigh_prop = 0.0, lineage='ancestor')
    elif org_type == "wt":
      newOrg = Organism(len(self.orgs), ai_prob = 1.0, coop_prob = 0.5, neigh_prop = 0.6, lineage='wt')
    elif org_type == "unconditional":
      newOrg = Organism(len(self.orgs), ai_prob = 0.0, coop_prob = 0.5, neigh_prop = 0.0, lineage='uncond')
    elif org_type == "defector":
      newOrg = Organism(len(self.orgs), ai_prob = 0.0, coop_prob = 0.0, neigh_prop = 1.0, lineage = 'defector')
    elif org_type == "empty":
      newOrg= Organism(len(self.orgs), empty = True, lineage = 'empty')
    else:
      print "Invalid organism selected, making ancestor"
      newOrg = Organism(len(self.orgs), ai_prob = 0.0, coop_prob = 0.0, neigh_prop = 0.0, lineage = 'ancestor')
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
    self.select_dict[newOrg.lineage] += newOrg.points


  def update(self):
    '''A function that runs a single update'''
    self.currentUpdate+=1
    for org in self.orgs:
      if not org.empty:
        result = org.update()
      if result: #organism produced public good and needs to give to neighbors
        assert isinstance(result, list), "Result returned by organism must be a list"
        #track the decrease to the producer
        self.select_dict[org.lineage] += production_cost
        for neighbor_id in result:
          neighbor = self.orgs[neighbor_id]
          self.select_dict[neighbor.lineage] += public_good_points
          neighbor.points += public_good_points

    for org in self.orgs:
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

    if total == 0:
      return 0, 0, 0 , 0, 0
    else:
      return (ai_prob_sum/total), (coop_prob_sum/total), (neigh_prop_sum/total), (repo_age_sum/total), total

def parseArgs(parser):
  '''A function for parsing the arguments.'''
  parser.add_argument('pop_x', help="the x value for the population size", type=int)
  parser.add_argument('pop_y', help="the y value for the population size", type=int)
  parser.add_argument('seed', help="the random seed", type=int)
  parser.add_argument('--mutation_sd', help='set the standard deviation of mutations, 0 to turn off mutations, 0.1 by default', type=float, default=0.1)
  parser.add_argument('filename', help='the prefix filename to save data to')
  parser.add_argument('--proportion_wt', help="the starting proportion of the population that should be the wildtype organism", type=float, default=0.0)
  parser.add_argument('--proportion_def', help="the starting proportion of the population that should be the defector organism", type=float, default=0.0)
  parser.add_argument('--proportion_uncond', help="the starting proportion of the population that should be the unconditional cooperator organism", type=float, default=0.0)
  parser.add_argument('--proportion_ancestor', help="the starting proportion of the population that should be the ancestor organism", type=float, default=0.0)
  parser.add_argument('--signal_cost', help="the cost of using autoinducers, should be a negative number", type=float, default=-1.0)
  parser.add_argument('--production_cost', help="the cost of producing the public good, should be negative", type=float, default=-5.0)
  parser.add_argument('--public_good_points', help='the bonus neighbors are rewarded when an organism produces the public good, should be positive', type=float, default=4.9)
  parser.add_argument('--num_updates', help="the number of updates the experiment should run for", type=int, default=10000)
  args = parser.parse_args()
  return args



parser = argparse.ArgumentParser(description='Simulate evolution of quorum sensing controlled public goods')
args = parseArgs(parser)
seed = args.seed
random.seed(seed)
numpy.random.seed(seed)
filename = args.filename
num_updates = args.num_updates
pop_x = args.pop_x
pop_y = args.pop_y
pop_size = pop_x*pop_y
mutation_sd = args.mutation_sd
signal_cost = args.signal_cost
production_cost = args.production_cost
public_good_points = args.public_good_points
proportions = {'wt':args.proportion_wt, 'defector':args.proportion_def, 'unconditional':args.proportion_uncond, 'ancestor':args.proportion_ancestor}

data_file = open(filename+str(seed)+".dat", 'w')
data_file.write("Update AI_Prob Coop_Prob Num_Neigh Avg_Repo_Age Total Select_Def Select_WT Select_Uncond\n")
data_file.close()
population_orgs = Population(pop_size,proportions)

for u in range(num_updates):
    
  population_orgs.update()
  if u%100 == 0:

      #grab current averages
    ai_prob, coop_prob, neigh_prop, age_avg, total = population_orgs.recordStats()
    print "Update: ", u, " AI Prob: ", ai_prob, " Coop Prob: ", coop_prob, " Neighbor Prop: ", neigh_prop, " Avg Repo Age: ", age_avg, " Total Orgs: ", total
    data_file = open(filename+str(seed)+".dat", 'a')
    data_file.write('{} {} {} {} {} {} {} {} {}\n'.format(u, ai_prob, coop_prob, neigh_prop, age_avg, total, population_orgs.select_dict['defector'], population_orgs.select_dict['wt'], population_orgs.select_dict['uncond']))
    population_orgs.select_dict = population_orgs.select_dict.fromkeys(population_orgs.select_dict, 0)
    data_file.close()
    if total == 0:
      break







