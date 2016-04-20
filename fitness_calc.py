#!/usr/bin/env python                                                          

import random
import numpy
import sys
import copy
import math

WORLD_X = 100
WORLD_Y = 100
WORLD_SIZE = WORLD_X * WORLD_Y
wildtype_quorum = 0.6 #the proportion of neighbors that need to be wt for wt to produce
production_cost = -5
signal_cost = -1
reward = 4.9
coop_prob = 0.5

class Organism:
    '''A Class to contain an organism'''
    def __init__(self, lineage, cell_ID):
        self.points = 0
        self.fitness = 0
        self.lineage = lineage
        self.cell_ID = cell_ID
        

        


def findNeighbors(id):
    cellID = id
    radius = 1
    cell_x = cellID % WORLD_X
    cell_y = (cellID - cell_x)/WORLD_X
    neighbor_ids = []
    for i in range(cell_x-radius, cell_x+radius+1):
        for j in range(cell_y-radius, cell_y+radius+1):
            if i == cell_x and j == cell_y:
                continue
            if i<0:
                x = WORLD_X + i
            elif i>=WORLD_X:
                x = i-WORLD_X
            else:
                x = i

            if j<0:
                y = WORLD_Y + j
            elif j>=WORLD_Y:
                y = j-WORLD_Y
            else:
                y = j

            neighbor_ids.append(y*WORLD_X+x)

    return neighbor_ids

def calculateFitnesses(def_prop, wt_prop, uncond_prop):

    #container variables for tracking how many of each type have benefitted from a public good
    bonus_defector = 0.0
    bonus_wildtype = 0.0
    bonus_uncond = 0.0
    bonus_empty = 0.0
    bonus_total = 0.0
    quorum_hits = 0.0
    empty_prop = 1-(def_prop+wt_prop+uncond_prop)
#a list for holding all the organisms
    world = []
#create random grid of the organisms
    real_def = 0.0
    real_wt = 0.0
    real_uncond = 0.0
    real_empty = 0.0
    #shuffle instead of add things randomly
    for i in range(WORLD_SIZE):
        number = random.random()
        if number < def_prop:
            world.append(Organism("defector", i))
            real_def += 1
        elif (number >= def_prop) and (number < (def_prop+wt_prop)):
            world.append(Organism("wildtype", i))
            real_wt +=1
        elif (number >= (def_prop+wt_prop)) and (number < (def_prop+wt_prop+uncond_prop)):
            world.append(Organism("uncond", i))
            real_uncond += 1
        else:
            world.append(Organism("empty", i))
            real_empty += 1


#go through and figure out how many of each type will a bonus
            #enumerate!
    for org in world:
        if org.lineage == "empty":
            continue
        elif org.lineage == "defector":
            continue
        elif org.lineage == "uncond":
            neighbor_ids = findNeighbors(org.cell_ID)
            #pay cost
            org.points += production_cost
            for neighbor_id in neighbor_ids:
                neighbor = world[neighbor_id]
                if neighbor.lineage == "defector":
                    neighbor.points += reward
                elif neighbor.lineage == "uncond":
                    neighbor.points += reward
                elif neighbor.lineage == "wildtype":
                    neighbor.points += reward
                elif neighbor.lineage == "empty":
                    neighbor.points += reward
        elif org.lineage == "wildtype":
            #autoinducer cost
            neighbor_ids = findNeighbors(org.cell_ID)
            #first find out if wt produces
            if random.random() < coop_prob:
                wt_neigh_num = sum(world[neighbor].lineage=="wildtype" for neighbor in neighbor_ids)
                if wt_neigh_num/8.0 >= wildtype_quorum:
                    quorum_hits += 1
                #pay cost
                    org.points += production_cost
                #bonus to neighbors
                    for neighbor_id in neighbor_ids:
                        neighbor = world[neighbor_id]
                        if neighbor.lineage == "defector":
                            neighbor.points += reward
                        elif neighbor.lineage == "uncond":
                            neighbor.points += reward
                        elif neighbor.lineage == "wildtype":
                            neighbor.points += reward
                        elif neighbor.lineage == "empty":
                            neighbor.points += reward



    sum_fitnesses = {"defector":0, "wildtype":0, "uncond":0, "empty":0}
    #go through and calculate fitnesses
    for org in world:
        
        if org.points <= 0:
            org.fitness = 0
        
        if org.lineage == "wildtype":
            if org.points >= 11:
                org.fitness = 1
            elif org.points > 0 and org.points < 11:
                gens = math.ceil(11.0/org.points)
                org.fitness = 1/gens

        else:
            if org.points >= 10:
                org.fitness = 1
                
            elif org.points > 0 and org.points < 10:
            #need to calc generation time to get fitness
                gens = math.ceil(10.0/org.points)
                org.fitness = 1/gens
            
        sum_fitnesses[org.lineage]+=org.fitness

    avg_def, avg_wt, avg_uncond, avg_empty = 0, 0, 0, 0
    # I actually want fitness propotion per organism
    if def_prop:
        avg_def = sum_fitnesses["defector"]/(WORLD_SIZE*def_prop)
    if wt_prop:
        avg_wt = sum_fitnesses["wildtype"]/(WORLD_SIZE*wt_prop)
    if uncond_prop:
        avg_uncond = sum_fitnesses["uncond"]/(WORLD_SIZE*uncond_prop)
    if empty_prop:
        avg_empty = sum_fitnesses["empty"]/(WORLD_SIZE*empty_prop)
    
    if avg_def > 0:
        relative_wt_def = float(avg_wt)/avg_def
    else:
        relative_wt_def = 0
    return '{} {} {} {} {}'.format(avg_def, avg_wt,  avg_uncond, avg_empty, relative_wt_def)


    

def main():
#take in proportions of each type
        
    datafile = open("fitness_calcs_def_wt.dat", 'w')
    datafile.write("treatment rep def_bonus wt_bonus uncond_bonus empty_bonus relative_wt_def def_prop wt_prop uncond_prop\n")
    
    wt_props = [0.1, 0.2, 0.3, 0.4, 0.5, 0.54, 0.56, 0.58, 0.6, 0.7, 0.8, 0.9]
    def_props = [0.9, 0.8, 0.7, 0.6, 0.5, 0.46, 0.44, 0.42, 0.4, 0.3, 0.2, 0.1]
    uncond_props = [0.0, 0.0, 0.0, 0.0,0.0, 0.0, 0.0, 0.0, 0.0, 0.0,0.0,0.0]

    assert len(def_props) == len(wt_props) and len(wt_props) == len(uncond_props), "Unequal number of proportions"



    reps = 20
    
    for p in range(len(def_props)):
        for r in range(reps):
#            print r
            fitnesses = calculateFitnesses(def_props[p], wt_props[p], uncond_props[p])
            data_line = 'def{}_wt{}_uncond{} '.format(def_props[p], wt_props[p], uncond_props[p])+str(r)+" "+fitnesses+' {} {} {}\n'.format(def_props[p], wt_props[p], uncond_props[p])
            datafile.write(data_line)
            

main()
